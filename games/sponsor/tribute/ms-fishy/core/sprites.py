from __future__ import annotations

import pygame
import random
from settings import (
    ColorSettings,
    DebugSettings,
    FishSettings,
    InputSettings,
    PlayerSettings,
    ScreenSettings,
)


def build_fish_surface(
    size: int,
    color: tuple[int, int, int],
    color2: tuple[int, int, int] | None = None,
    bow: bool = False,
) -> tuple[pygame.Surface, int, int]:
    """Return a right-facing fish surface and the fish body height.

    A drop shadow is always rendered below-right. When `color2` is supplied the
    body is filled with a vertical gradient from `color` (top/dorsal) to
    `color2` (bottom/belly); otherwise the body is a flat `color`.

    When `bow` is True, a small pink bow (two mirrored triangles meeting at a
    central point) is drawn above the body's top apex — Ms. Fishy's signature
    accessory. The canvas is grown vertically to accommodate it, so the body's
    rect placement is unaffected for callers that pass `bow=False`.

    Args:
        size: Conceptual fish body width in pixels.
        color: RGB body color, or the dorsal gradient color when color2 is given.
        color2: Optional belly gradient color; enables gradient fill when set.
        bow: Whether to draw the Ms. Fishy bow above the body apex.

    Returns:
        tuple[pygame.Surface, int, int]: A rendered fish surface, its body height,
            and the vertical pixel offset of the body from the canvas top
            (equals the bow height + gap when `bow=True`, otherwise 0).
    """
    body_height = max(1, int(size * FishSettings.BODY_HEIGHT_RATIO))
    tail_width = max(1, int(size * FishSettings.TAIL_WIDTH_RATIO))
    total_width = size + tail_width
    center_y = body_height // 2
    shadow = FishSettings.SHADOW_OFFSET

    # Bow geometry — computed up front so the canvas can be grown vertically
    # to fit the bow above the body. When bow is False, bow_offset_y is 0 and
    # the canvas dimensions match the original (non-bow) layout exactly.
    if bow:
        bow_half_width = max(1, int(size * PlayerSettings.BOW_WIDTH_RATIO * 0.5))
        bow_height = max(2, int(size * PlayerSettings.BOW_HEIGHT_RATIO))
        bow_gap = max(1, int(size * PlayerSettings.BOW_GAP_RATIO))
        bow_offset_y = bow_height + bow_gap
    else:
        bow_half_width = 0
        bow_height = 0
        bow_gap = 0
        bow_offset_y = 0

    # Canvas is expanded to accommodate the drop shadow in the bottom-right
    # and (when present) the bow rising above the body's top apex.
    image = pygame.Surface(
        (total_width + shadow, body_height + shadow + bow_offset_y),
        pygame.SRCALPHA,
    )

    tail_points = [
        (0, bow_offset_y),
        (0, bow_offset_y + body_height),
        (tail_width, bow_offset_y + center_y),
    ]
    body_points = [
        (tail_width, bow_offset_y + center_y),
        (tail_width + size // 2, bow_offset_y),
        (total_width, bow_offset_y + center_y),
        (tail_width + size // 2, bow_offset_y + body_height),
    ]

    # Drop shadow drawn first so the fish body renders cleanly on top.
    shadow_tail = [(x + shadow, y + shadow) for x, y in tail_points]
    shadow_body = [(x + shadow, y + shadow) for x, y in body_points]
    pygame.draw.polygon(image, (0, 0, 0, 100), shadow_tail)
    pygame.draw.polygon(image, (0, 0, 0, 100), shadow_body)

    if color2 is not None:
        # Gradient fill: horizontal scanlines clipped to the fish polygon shape
        # via an alpha mask so transparent corners stay transparent.
        mask_surf = pygame.Surface((total_width, body_height), pygame.SRCALPHA)
        mask_surf.fill((0, 0, 0, 0))
        mask_tail = [(x, y - bow_offset_y) for x, y in tail_points]
        mask_body = [(x, y - bow_offset_y) for x, y in body_points]
        pygame.draw.polygon(mask_surf, (255, 255, 255, 255), mask_tail)
        pygame.draw.polygon(mask_surf, (255, 255, 255, 255), mask_body)

        grad_surf = pygame.Surface((total_width, body_height), pygame.SRCALPHA)
        for y in range(body_height):
            t = y / max(1, body_height - 1)
            r = int(color[0] + (color2[0] - color[0]) * t)
            g = int(color[1] + (color2[1] - color[1]) * t)
            b = int(color[2] + (color2[2] - color[2]) * t)
            pygame.draw.line(grad_surf, (r, g, b, 255), (0, y), (total_width - 1, y))

        # Multiply alpha channels so gradient is transparent outside fish shape.
        grad_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        image.blit(grad_surf, (0, bow_offset_y))
    else:
        pygame.draw.polygon(image, color, tail_points)
        pygame.draw.polygon(image, color, body_points)

    eye_size = max(1, int(size * FishSettings.EYE_SIZE_RATIO))
    nose_x = total_width - 1
    diamond_center_x = tail_width + (size / 2)
    # Place eye halfway between the body's center and the nose.
    eye_center_x = int((diamond_center_x + nose_x) / 2)
    eye_x = min(total_width - eye_size, max(0, eye_center_x - eye_size // 2))
    eye_y = max(0, bow_offset_y + center_y - eye_size // 2)
    pygame.draw.rect(image, ColorSettings.BLACK, (eye_x, eye_y, eye_size, eye_size))

    if bow:
        # Two mirrored triangles meeting at a central apex — a stylized bow tie
        # sitting just above the body's top point. Drawn last so it renders on
        # top of the body shadow, with its own shadow underneath for depth.
        bow_cx = tail_width + size // 2
        bow_top = 0
        bow_bottom = bow_height
        bow_mid = bow_height // 2
        left_triangle = [
            (bow_cx - bow_half_width, bow_top),
            (bow_cx - bow_half_width, bow_bottom),
            (bow_cx, bow_mid),
        ]
        right_triangle = [
            (bow_cx + bow_half_width, bow_top),
            (bow_cx + bow_half_width, bow_bottom),
            (bow_cx, bow_mid),
        ]
        bow_shadow_left = [(x + shadow, y + shadow) for x, y in left_triangle]
        bow_shadow_right = [(x + shadow, y + shadow) for x, y in right_triangle]
        pygame.draw.polygon(image, (0, 0, 0, 100), bow_shadow_left)
        pygame.draw.polygon(image, (0, 0, 0, 100), bow_shadow_right)
        pygame.draw.polygon(image, PlayerSettings.BOW_COLOR, left_triangle)
        pygame.draw.polygon(image, PlayerSettings.BOW_COLOR, right_triangle)

    return image, body_height, bow_offset_y

class Player(pygame.sprite.Sprite):
    """Player-controlled fish that can move, collide, and grow in size."""

    def __init__(self, x, y):
        """Initialize the player sprite.

        Args:
            x: Starting x-coordinate in pixels.
            y: Starting y-coordinate in pixels.
        """
        super().__init__()
        starting_size = (
            DebugSettings.LARGE_PLAYER_SIZE
            if DebugSettings.START_LARGE_PLAYER
            else PlayerSettings.SIZE
        )
        # size is stored as float so fractional growth from PLAYER_GROWTH_COEFFICIENT
        # accumulates across multiple fish eaten instead of being discarded by int()
        # on every grow() call (e.g. eating a size-8 fish gives 0.8 px growth; int
        # would round that to 0 each time, making growth invisible for small fish).
        self.size = float(starting_size)
        self.base_image, _, self.bow_offset_y = build_fish_surface(
            int(self.size),
            PlayerSettings.COLOR_TOP,
            PlayerSettings.COLOR_BOTTOM,
            bow=True,
        )
        self.facing_direction = 1
        self.image = self.base_image
        # Use center positioning so callers can pass intuitive screen-center
        # coordinates without having to compensate for the surface's bow padding
        # or body width. grow() also re-anchors on center, so this matches.
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = self._build_mask()

        # Float position accumulators store sub-pixel position so that
        # velocities below 1 px/frame accumulate across frames instead of
        # being silently discarded by int() on every rect assignment.
        self._pos_x = float(self.rect.x)
        self._pos_y = float(self.rect.y)

        # Velocity components in pixels per frame, maintained across frames.
        # Separate from rect so acceleration and drag can be applied cleanly
        # before committing the result to the sprite rect.
        self.velocity_x = 0.0
        self.velocity_y = 0.0

    def _build_mask(self) -> pygame.mask.Mask:
        """Build a collision mask that excludes the bow pixels above the body.

        The bow is a purely visual accessory.  Zeroing its rows on a copy of
        the surface before building the mask means bow-contact never registers
        as a collision event — no growth, no game-over.
        """
        if self.bow_offset_y == 0:
            return pygame.mask.from_surface(self.image)
        # Clear the bow rows on a throwaway copy so they stay alpha-zero in
        # the mask without touching the rendered image that's blitted to screen.
        mask_surf = self.image.copy()
        mask_surf.fill((0, 0, 0, 0), (0, 0, mask_surf.get_width(), self.bow_offset_y))
        return pygame.mask.from_surface(mask_surf)

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
        self.mask = self._build_mask()

    def input(self, joysticks: list) -> None:
        """Accumulate directional input as acceleration on the velocity vector.

        Rather than moving the player a fixed amount each frame, held input
        adds ACCELERATION to the matching velocity component (capped at
        MAX_SPEED).  When input opposes the current velocity direction,
        COUNTER_ACCELERATION is used instead — a larger value so the player
        can actively brake and reverse faster than passive DRAG alone.  When
        input is released, DRAG is applied each frame to produce a gradual
        coast-to-stop that mimics water resistance.  The resulting velocity
        is committed to a float position accumulator (_pos_x/_pos_y) and
        then written to the sprite rect.

        Args:
            joysticks: Cached list of connected joystick instances from GameManager.
        """
        input_x = 0
        input_y = 0

        # Keyboard input — normalised to -1 / 0 / +1 so keyboard and
        # controller produce identical acceleration magnitudes.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            input_x -= 1
        if keys[pygame.K_RIGHT]:
            input_x += 1
        if keys[pygame.K_UP]:
            input_y -= 1
        if keys[pygame.K_DOWN]:
            input_y += 1

        # Controller input for movement — uses the cached joystick list passed
        # in from GameManager instead of re-querying pygame.joystick each frame.
        for joystick in joysticks:
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_X) < -InputSettings.JOY_TRIGGER_THRESHOLD:
                input_x -= 1
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_X) > InputSettings.JOY_TRIGGER_THRESHOLD:
                input_x += 1
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_Y) < -InputSettings.JOY_TRIGGER_THRESHOLD:
                input_y -= 1
            if joystick.get_axis(InputSettings.JOY_AXIS_LEFT_Y) > InputSettings.JOY_TRIGGER_THRESHOLD:
                input_y += 1

        # ------------------------------------------------------------------
        # VELOCITY PHYSICS
        # ------------------------------------------------------------------
        # Horizontal axis: accelerate toward MAX_SPEED, or apply water drag.
        if input_x != 0:
            # When input opposes the current velocity (e.g. pressing right
            # while moving left), use COUNTER_ACCELERATION — a higher value
            # that lets the player actively brake and reverse faster than
            # passive drag alone.  input_x * velocity_x < 0 detects this:
            # the signs are opposite when the two are pointing in different
            # directions.
            accel = (
                PlayerSettings.COUNTER_ACCELERATION
                if input_x * self.velocity_x < 0
                else PlayerSettings.ACCELERATION
            )
            self.velocity_x = max(
                -PlayerSettings.MAX_SPEED,
                min(PlayerSettings.MAX_SPEED,
                    self.velocity_x + input_x * accel),
            )
        else:
            # No input: multiply by DRAG (<1) each frame to simulate resistance.
            self.velocity_x *= PlayerSettings.DRAG
            # Once velocity is too small to notice, snap to zero to stop the
            # asymptotic drift that DRAG's geometric decay would otherwise cause.
            if abs(self.velocity_x) < PlayerSettings.STOP_THRESHOLD:
                self.velocity_x = 0.0

        # Vertical axis: identical physics to horizontal.
        if input_y != 0:
            accel = (
                PlayerSettings.COUNTER_ACCELERATION
                if input_y * self.velocity_y < 0
                else PlayerSettings.ACCELERATION
            )
            self.velocity_y = max(
                -PlayerSettings.MAX_SPEED,
                min(PlayerSettings.MAX_SPEED,
                    self.velocity_y + input_y * accel),
            )
        else:
            self.velocity_y *= PlayerSettings.DRAG
            if abs(self.velocity_y) < PlayerSettings.STOP_THRESHOLD:
                self.velocity_y = 0.0

        # Apply velocity to the float position accumulator, then write the
        # integer part to the sprite rect.  Using a float accumulator means
        # velocities below 1 px/frame still accumulate and eventually move the
        # fish, instead of being discarded by int() truncation every frame.
        self._pos_x += self.velocity_x
        self._pos_y += self.velocity_y
        self.rect.x = int(self._pos_x)
        self.rect.y = int(self._pos_y)

        # Flip sprite direction based on velocity, not raw input, and only
        # above FLIP_THRESHOLD so the fish doesn't flicker left/right while
        # coasting to a stop after the player releases the key.
        if self.velocity_x < -PlayerSettings.FLIP_THRESHOLD:
            self._set_facing_direction(-1)
        elif self.velocity_x > PlayerSettings.FLIP_THRESHOLD:
            self._set_facing_direction(1)

    def enforce_boundaries(self, screen_width, screen_height) -> None:
        """Clamp the player rect so it cannot leave the visible screen.

        Also zeroes the velocity component on any axis that was clamped and
        resyncs the float position accumulators.  Without zeroing velocity,
        the fish would need to "fight" the wall to turn around (the velocity
        model would keep trying to push it off-screen every frame).  Without
        resyncing the accumulators, the clamped rect position and the float
        position would diverge and cause a sudden snap when the player moves
        away from the wall.
        """
        clamped = False
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0.0
            clamped = True
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.velocity_x = 0.0
            clamped = True
        # Allow the bow to float above y=0; clamp on the body's top edge instead.
        if self.rect.top + self.bow_offset_y < 0:
            self.rect.top = -self.bow_offset_y
            self.velocity_y = 0.0
            clamped = True
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity_y = 0.0
            clamped = True

        # Only resync the float accumulators when the rect was actually moved
        # by a wall clamp.  Previously this ran unconditionally every frame,
        # which wiped the sub-pixel fractional part before it could accumulate
        # — causing right/down movement to never register at low velocities
        # (positive fractional offsets from an integer base never cross the
        # next integer boundary if the accumulator is reset each frame).
        if clamped:
            self._pos_x = float(self.rect.x)
            self._pos_y = float(self.rect.y)

    def grow(self, growth_amount: float) -> None:
        """Increase player size and rebuild sprite/mask while preserving center.

        Args:
            growth_amount: Number of pixels to add to conceptual fish size.
        """
        self.size = max(1.0, self.size + growth_amount)
        center = self.rect.center
        self.base_image, _, self.bow_offset_y = build_fish_surface(
            int(self.size),
            PlayerSettings.COLOR_TOP,
            PlayerSettings.COLOR_BOTTOM,
            bow=True,
        )
        self.rect = self.base_image.get_rect(center=center)
        self._set_facing_direction(self.facing_direction, force=True)

        # Resync float accumulators after the rect's topleft shifts due to the
        # increased sprite size; without this the accumulators would lag behind
        # and cause a position snap on the next input frame.
        self._pos_x = float(self.rect.x)
        self._pos_y = float(self.rect.y)

    def update(self, joysticks: list | None = None) -> None:
        """Advance player state by one frame.

        Args:
            joysticks: Cached list of connected joystick instances from GameManager.
        """
        self.input(joysticks or [])
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

        self.image, body_height, _ = build_fish_surface(size, random.choice(ColorSettings.FISH_PALETTE))

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

        # Track horizontal position as float so sub-pixel fish speeds do not
        # get truncated away by integer Rect assignment each frame.
        self._pos_x = float(self.rect.x)

        self.rect.y = random.randint(0, ScreenSettings.HEIGHT - body_height)

    def update(self):
        """Advance enemy fish position and remove it once it clears the screen."""
        self._pos_x += self.speed * self.direction
        self.rect.x = int(self._pos_x)
        
        # Kill if off-screen
        if self.rect.right < -50 or self.rect.left > ScreenSettings.WIDTH + 50:
            self.kill()