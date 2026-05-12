"""Sprite classes for Space Invaders.

Everything that lives on the screen during gameplay is defined here:
the player ship, the alien wave, the UFO ``Extra``, lasers, and the
brick-sized ``Block`` that makes up each destructible bunker.
"""

import pygame

from settings import (
    AlienSettings,
    AssetPaths,
    ControllerSettings,
    ExtraSettings,
    LaserSettings,
    PlayerSettings,
)


# ---------------------------------------------------------------------------
# PLAYER
# ---------------------------------------------------------------------------

class Player(pygame.sprite.Sprite):
    """Horizontally-constrained ship controlled by keyboard or controller."""

    def __init__(self, pos, constraint, speed):
        """Set up the player ship and its laser group.

        Args:
            pos (tuple[int, int]): Initial midbottom position of the ship.
            constraint (int): Maximum x coordinate the ship may reach.
            speed (int): Horizontal pixels moved per frame.
        """
        super().__init__()
        self.image = pygame.image.load(AssetPaths.PLAYER).convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = speed
        self.max_x_constraint = constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = PlayerSettings.LASER_COOLDOWN

        self.lasers = pygame.sprite.Group()

        self.laser_sound = pygame.mixer.Sound(AssetPaths.LASER_SFX)
        self.laser_sound.set_volume(PlayerSettings.LASER_SFX_VOLUME)

    # ------------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------------

    def get_input(self):
        """Poll keyboard + controller each frame for movement and fire input.

        The horizontal axis is read from arrow keys, then overridden by any
        connected controller's D-pad / left analog stick. Fire input listens
        for ``Space`` and the controller A button so players can use either
        device without configuration.
        """
        keys = pygame.key.get_pressed()
        horizontal_input = 0

        if keys[pygame.K_RIGHT]:
            horizontal_input += 1
        elif keys[pygame.K_LEFT]:
            horizontal_input -= 1

        controller_fire = False
        # Poll every connected joystick so any controller can drive the ship
        # without us picking a "preferred" one.
        for joystick_index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(joystick_index)
            try:
                if not joystick.get_init():
                    joystick.init()
                # Prefer the D-pad because it gives a clean digital signal.
                if joystick.get_numhats() > 0:
                    hat_x, _ = joystick.get_hat(0)
                    if hat_x != 0:
                        horizontal_input = hat_x
                # Fall back to the analog stick if the D-pad is centered.
                if horizontal_input == 0 and joystick.get_numaxes() > 0:
                    axis_x = joystick.get_axis(0)
                    if abs(axis_x) >= ControllerSettings.JOYSTICK_DEADZONE:
                        horizontal_input = 1 if axis_x > 0 else -1
                if (joystick.get_numbuttons() > 0
                        and joystick.get_button(ControllerSettings.A_BUTTON)):
                    controller_fire = True
            except pygame.error:
                # Device disconnects can race with the polling call.
                continue

        if horizontal_input > 0:
            self.rect.x += self.speed
        elif horizontal_input < 0:
            self.rect.x -= self.speed

        if (keys[pygame.K_SPACE] or controller_fire) and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    # ------------------------------------------------------------------
    # WEAPON / CONSTRAINTS
    # ------------------------------------------------------------------

    def recharge(self):
        """Re-enable firing once ``laser_cooldown`` milliseconds have elapsed."""
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        """Clamp the ship inside the playfield horizontally."""
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        """Spawn a player-owned laser from the ship's center."""
        self.lasers.add(Laser(self.rect.center, LaserSettings.PLAYER_SPEED, self.rect.bottom))

    def update(self):
        """Run input, clamping, cooldown, and per-frame laser updates."""
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()


# ---------------------------------------------------------------------------
# ALIENS
# ---------------------------------------------------------------------------

class Alien(pygame.sprite.Sprite):
    """A single colored invader; many of these form the marching wave."""

    def __init__(self, color, x, y):
        """Load the colored sprite and assign its point value.

        Args:
            color (str): One of ``'red'``, ``'green'``, ``'yellow'``.
            x (int): Top-left pixel x coordinate.
            y (int): Top-left pixel y coordinate.
        """
        super().__init__()
        self.image = pygame.image.load(AssetPaths.ALIENS_BY_COLOR[color]).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.value = AlienSettings.POINTS[color]

    def update(self, direction):
        """Step the alien horizontally by ``direction`` pixels per frame."""
        self.rect.x += direction


class Extra(pygame.sprite.Sprite):
    """The UFO bonus target that occasionally streaks across the top."""

    def __init__(self, side, screen_width):
        """Spawn from a screen edge and travel inward at a fixed speed.

        Args:
            side (str): ``'right'`` or ``'left'`` — the edge to enter from.
            screen_width (int): Playfield width used to position the spawn.
        """
        super().__init__()
        self.image = pygame.image.load(AssetPaths.EXTRA).convert_alpha()

        # Offset the spawn slightly off-screen so the UFO slides in cleanly
        # instead of popping into view at the edge.
        offscreen_padding = 50
        if side == 'right':
            x = screen_width + offscreen_padding
            self.speed = -ExtraSettings.SPEED
        else:
            x = -offscreen_padding
            self.speed = ExtraSettings.SPEED

        self.rect = self.image.get_rect(topleft=(x, ExtraSettings.Y_POSITION))

    def update(self):
        """Slide horizontally by ``speed`` pixels per frame."""
        self.rect.x += self.speed


# ---------------------------------------------------------------------------
# LASER
# ---------------------------------------------------------------------------

class Laser(pygame.sprite.Sprite):
    """A simple rectangular projectile fired by the player or an alien."""

    def __init__(self, pos, speed, screen_height):
        """Create the laser surface and store its travel bounds.

        Args:
            pos (tuple[int, int]): Spawn center.
            speed (int): Pixels travelled per frame (negative = up).
            screen_height (int): Bottom-edge bound used for despawn checks.
        """
        super().__init__()
        self.image = pygame.Surface((LaserSettings.WIDTH, LaserSettings.HEIGHT))
        self.image.fill('white')
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.height_y_constraint = screen_height

    def destroy(self):
        """Despawn the laser once it has travelled past either screen edge."""
        margin = LaserSettings.OFFSCREEN_MARGIN
        if self.rect.y <= -margin or self.rect.y >= self.height_y_constraint + margin:
            self.kill()

    def update(self):
        """Advance the laser and despawn it when it leaves the playfield."""
        self.rect.y += self.speed
        self.destroy()


# ---------------------------------------------------------------------------
# OBSTACLE BLOCK
# ---------------------------------------------------------------------------

class Block(pygame.sprite.Sprite):
    """A single colored brick. Many bricks composed together form a bunker."""

    def __init__(self, size, color, x, y):
        """Build a solid-colored square at the given position.

        Args:
            size (int): Width and height of the brick in pixels.
            color (tuple[int, int, int]): RGB fill color.
            x (int): Top-left pixel x coordinate.
            y (int): Top-left pixel y coordinate.
        """
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
