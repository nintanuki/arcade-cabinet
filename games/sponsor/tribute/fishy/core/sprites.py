import pygame
import random
from settings import ColorSettings, FishSettings, InputSettings, PlayerSettings, ScreenSettings


def build_fish_surface(size: int, color: tuple[int, int, int]) -> tuple[pygame.Surface, int]:
    """Return a right-facing fish surface and the fish body height.

    Args:
        size: Conceptual fish body width in pixels.
        color: RGB color for the fish body and tail polygons.

    Returns:
        tuple[pygame.Surface, int]: A rendered fish surface and its body height.
    """
    body_height = max(1, int(size * FishSettings.BODY_HEIGHT_RATIO))
    tail_width = max(1, int(size * FishSettings.TAIL_WIDTH_RATIO))
    total_width = size + tail_width
    center_y = body_height // 2

    image = pygame.Surface((total_width, body_height), pygame.SRCALPHA)

    tail_points = [
        (0, 0),
        (0, body_height),
        (tail_width, center_y),
    ]
    body_points = [
        (tail_width, center_y),
        (tail_width + size // 2, 0),
        (total_width, center_y),
        (tail_width + size // 2, body_height),
    ]
    pygame.draw.polygon(image, color, tail_points)
    pygame.draw.polygon(image, color, body_points)

    eye_size = max(1, int(size * FishSettings.EYE_SIZE_RATIO))
    nose_x = total_width - 1
    diamond_center_x = tail_width + (size / 2)
    # Place eye halfway between the body's center and the nose.
    eye_center_x = int((diamond_center_x + nose_x) / 2)
    eye_x = min(total_width - eye_size, max(0, eye_center_x - eye_size // 2))
    eye_y = max(0, center_y - eye_size // 2)
    pygame.draw.rect(image, ColorSettings.BLACK, (eye_x, eye_y, eye_size, eye_size))

    return image, body_height

class Player(pygame.sprite.Sprite):
    """Player-controlled fish that can move, collide, and grow in size."""

    def __init__(self, x, y):
        """Initialize the player sprite.

        Args:
            x: Starting x-coordinate in pixels.
            y: Starting y-coordinate in pixels.
        """
        super().__init__()
        # size is stored as float so fractional growth from PLAYER_GROWTH_COEFFICIENT
        # accumulates across multiple fish eaten instead of being discarded by int()
        # on every grow() call (e.g. eating a size-8 fish gives 0.8 px growth; int
        # would round that to 0 each time, making growth invisible for small fish).
        self.size = float(PlayerSettings.SIZE[0])
        self.base_image, _ = build_fish_surface(int(self.size), PlayerSettings.COLOR)
        self.facing_direction = 1
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.image)

    def _set_facing_direction(self, direction: int, force: bool = False) -> None:
        """Apply sprite orientation so the fish faces travel direction.

        Args:
            direction: `1` for right-facing, `-1` for left-facing.
            force: Whether to rebuild orientation even if direction is unchanged.
        """
        if not force and direction == self.facing_direction:
            return

        center = self.rect.center
        self.facing_direction = direction
        if direction == 1:
            self.image = self.base_image
        else:
            self.image = pygame.transform.flip(self.base_image, True, False)

        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def input(self) -> None:
        """Apply keyboard and controller movement input to the player position."""
        move_x = 0
        move_y = 0

        # Keyboard input for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_x -= PlayerSettings.SPEED
        if keys[pygame.K_RIGHT]:
            move_x += PlayerSettings.SPEED
        if keys[pygame.K_UP]:
            move_y -= PlayerSettings.SPEED
        if keys[pygame.K_DOWN]:
            move_y += PlayerSettings.SPEED

        # Controller input for movement
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_X) < -InputSettings.JOY_TRIGGER_THRESHOLD:
                move_x -= PlayerSettings.SPEED
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_X) > InputSettings.JOY_TRIGGER_THRESHOLD:
                move_x += PlayerSettings.SPEED
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_Y) < -InputSettings.JOY_TRIGGER_THRESHOLD:
                move_y -= PlayerSettings.SPEED
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_Y) > InputSettings.JOY_TRIGGER_THRESHOLD:
                move_y += PlayerSettings.SPEED

        self.rect.x += move_x
        self.rect.y += move_y

        if move_x < 0:
            self._set_facing_direction(-1)
        elif move_x > 0:
            self._set_facing_direction(1)

    def enforce_boundaries(self, screen_width, screen_height) -> None:
        """Clamp the player rect so it cannot leave the visible screen."""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def grow(self, growth_amount: float) -> None:
        """Increase player size and rebuild sprite/mask while preserving center.

        Args:
            growth_amount: Number of pixels to add to conceptual fish size.
        """
        self.size = max(1.0, self.size + growth_amount)
        center = self.rect.center
        self.base_image, _ = build_fish_surface(int(self.size), PlayerSettings.COLOR)
        self.rect = self.base_image.get_rect(center=center)
        self._set_facing_direction(self.facing_direction, force=True)

    def update(self) -> None:
        """Advance player state by one frame."""
        self.input()
        self.enforce_boundaries(ScreenSettings.WIDTH, ScreenSettings.HEIGHT)

class Fish(pygame.sprite.Sprite):
    """Enemy fish sprite with directional movement and off-screen cleanup."""

    def __init__(self, side, size, speed):
        """Initialize one enemy fish.

        Args:
            side: Spawn side, either "left" or "right".
            size: Conceptual fish body width in pixels.
            speed: Horizontal speed in pixels per frame.
        """
        super().__init__()
        self.size = size  # stored directly for accurate area comparisons
        self.speed = speed
        self.direction = 1 if side == "left" else -1

        self.image, body_height = build_fish_surface(size, ColorSettings.RED)

        # Left-moving fish face left. Mirroring horizontally keeps the nose pointed
        # in the direction of travel and the tail fanning out behind it.
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        # Build a pixel mask from the drawn surface so collision checks ignore
        # the transparent corners of the bounding box.
        self.mask = pygame.mask.from_surface(self.image)

        # Spawn just off the edge of the screen on the correct side.
        if side == "left":
            self.rect.right = 0
        else:
            self.rect.left = ScreenSettings.WIDTH

        self.rect.y = random.randint(0, ScreenSettings.HEIGHT - body_height)

    def update(self):
        """Advance enemy fish position and remove it once it clears the screen."""
        self.rect.x += self.speed * self.direction
        
        # Kill if off-screen
        if self.rect.right < -50 or self.rect.left > ScreenSettings.WIDTH + 50:
            self.kill()