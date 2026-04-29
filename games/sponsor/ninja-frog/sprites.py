import pygame
from settings import (
    AssetPaths,
    ControllerSettings,
    PlayerSettings,
    ScreenSettings,
    EnemySettings
)


def load_frames(path, frame_width, frame_height):
    """
    Slice a horizontal spritesheet into a list of surfaces.
    Args:
    - path (str): The file path to the spritesheet image.
    - frame_width (int): The width of each individual frame in pixels.
    - frame_height (int): The height of each individual frame in pixels.
    Returns:
    - List[pygame.Surface]: A list of surfaces, each containing one frame of the animation
    """
    sheet = pygame.image.load(path).convert_alpha()
    num_frames = sheet.get_width() // frame_width
    return [
        sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        for i in range(num_frames)
    ]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game

        # --- Load animation frames ---
        self.animations = {
            'idle': load_frames(AssetPaths.PLAYER_IDLE, 32, 32),
            'run':  load_frames(AssetPaths.PLAYER_RUN,  32, 32),
            'jump': load_frames(AssetPaths.PLAYER_JUMP, 32, 32),
            'fall': load_frames(AssetPaths.PLAYER_FALL, 32, 32),
        }
        # Debug: print number of frames loaded for each animation
        for anim, frames in self.animations.items():
            print(f"Loaded {len(frames)} frames for animation '{anim}' from {getattr(AssetPaths, 'PLAYER_' + anim.upper())}")

        # --- Animation state ---
        self.current_anim = 'idle'
        self.frame_index = 0.0 # Use float for smooth animation timing
        self.facing_right = True # Track facing direction for flipping the sprite

        # --- Physics state ---
        self.velocity_y = PlayerSettings.INITIAL_VELOCITY_Y # Start with no vertical velocity
        self.on_ground = False # Track whether the player is on the ground for jumping and animation purposes

        # --- Set initial image and rect ---
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Float accumulators for position so fractional speeds aren't lost to truncation
        self.pos_x = float(x)
        self.pos_y = float(y)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def get_input(self, joysticks):
        """
        Check keyboard and controller input to determine movement.
        Args:
            joysticks (list of pygame.joystick.Joystick): List of initialized joystick objects to check for input.
        Returns:
            tuple: (moving_left, moving_right, running) booleans indicating movement direction and run state.
        """
        keys = pygame.key.get_pressed()

        joystick_x = 0.0
        jump_pressed = False
        dpad_x = 0
        dpad_y = 0
        run_pressed = False

        # Check all joysticks for input (supports multiple controllers)
        for joy in joysticks:
            x = joy.get_axis(ControllerSettings.MOVE_AXIS_X)
            if abs(x) > ControllerSettings.AXIS_DEADZONE:
                joystick_x = x
            jump_pressed |= joy.get_button(ControllerSettings.A_BUTTON)
            dpad_x, dpad_y = joy.get_hat(0)
            run_pressed |= joy.get_button(ControllerSettings.X_BUTTON)

        moving_left = (
            keys[pygame.K_LEFT] or keys[pygame.K_a]
            or joystick_x < -0.5 or dpad_x < 0
        )
        moving_right = (
            keys[pygame.K_RIGHT] or keys[pygame.K_d]
            or joystick_x > 0.5 or dpad_x > 0
        )

        # Run button: X on controller or F on keyboard
        run_pressed |= keys[pygame.K_f]

        # Move the player based on input.
        # Mutates self.pos_x instead of self.rect.x directly
        # to allow for fractional movement speeds without losing precision.
        speed_left = PlayerSettings.RUN_SPEED if run_pressed else PlayerSettings.LEFT_SPEED
        speed_right = PlayerSettings.RUN_SPEED if run_pressed else PlayerSettings.RIGHT_SPEED
        if moving_left and not moving_right:
            self.pos_x -= speed_left
            self.facing_right = False
        elif moving_right and not moving_left:
            self.pos_x += speed_right
            self.facing_right = True
        self.rect.x = int(round(self.pos_x))  # Use round to avoid left/right bias

        if (keys[pygame.K_SPACE] or jump_pressed) and self.on_ground:
            self.velocity_y = PlayerSettings.JUMP_STRENGTH
            self.on_ground = False

        return moving_left, moving_right, run_pressed # Return movement state for animation purposes

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def apply_gravity(self):
        """Apply gravity to the player's vertical velocity and update the rect's y position."""
        self.velocity_y += PlayerSettings.GRAVITY
        self.pos_y += self.velocity_y
        self.rect.y = int(round(self.pos_y))

    def handle_horizontal_collision(self):
        """Check for horizontal collisions and adjust the rect's position accordingly."""
        self.game.collision.resolve_horizontal(self.rect)
        # Always sync float accumulator to rect.x after collision resolution
        self.pos_x = float(self.rect.x)

    def handle_vertical_collision(self):
        """Check for vertical collisions and adjust the rect's position and velocity accordingly."""
        self.on_ground = False
        for solid_rect in self.game.collision.check_collision(self.rect):
            if self.velocity_y > 0 and self.rect.bottom > solid_rect.top:
                self.rect.bottom = solid_rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.pos_y = float(self.rect.y)
            elif self.velocity_y < 0 and self.rect.top < solid_rect.bottom:
                self.rect.top = solid_rect.bottom
                self.velocity_y = 0
                self.pos_y = float(self.rect.y)
        # Additional check: probe 1px below for ground.
        # This must run whenever we're not moving upward, NOT just when velocity_y == 0.
        # Gravity adds 0.5 to velocity_y every frame, so by the time we get here while
        # standing still, velocity_y is already > 0 and the previous `== 0` gate would
        # skip this branch -- leaving on_ground stuck at False and the animator showing
        # 'fall' instead of 'idle'/'run'. We also zero out velocity_y so gravity doesn't
        # silently accumulate frame after frame while grounded.
        if not self.on_ground and self.velocity_y >= 0:
            test_rect = self.rect.move(0, 1)
            for solid_rect in self.game.collision.check_collision(test_rect):
                if self.rect.bottom <= solid_rect.top + 1:
                    self.on_ground = True
                    self.velocity_y = 0
                    self.pos_y = float(self.rect.y)
                    break

    def handle_stomp(self):
        """Check for stomping on enemies and apply bounce effect."""
        for enemy in self.game.enemies:
            if self.velocity_y > 0 and self.rect.colliderect(enemy.rect):
                if self.rect.bottom <= enemy.rect.centery:
                    enemy.kill()
                    self.velocity_y = PlayerSettings.STOMP_BOUNCE

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def get_animation_state(self, moving_left, moving_right, running):
        """Pick the right animation based on physics and movement."""
        if not self.on_ground:
            return 'jump' if self.velocity_y < 0 else 'fall'
        if moving_left or moving_right:
            return 'run'  # Always use 'run' animation for any movement
        return 'idle'

    def animate(self, moving_left, moving_right, running):
        """Update the player's animation based on movement and physics state."""
        new_anim = self.get_animation_state(moving_left, moving_right, running)

        # Reset frame index when switching animations
        if new_anim != self.current_anim:
            self.current_anim = new_anim
            self.frame_index = 0.0

        frames = self.animations[self.current_anim]
        self.frame_index += PlayerSettings.ANIMATION_SPEED
        if self.frame_index >= len(frames):
            self.frame_index = 0.0

        frame = frames[int(self.frame_index)]

        # Flip horizontally when facing left
        self.image = frame if self.facing_right else pygame.transform.flip(frame, True, False)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, joysticks):
        """Update the player's state based on input, physics, and animation."""
        moving_left, moving_right, running = self.get_input(joysticks)
        self.handle_horizontal_collision()  # resolve X before touching Y
        # After collision, always sync float accumulator to avoid drift
        self.pos_x = float(self.rect.x)
        self.apply_gravity()
        self.handle_vertical_collision()
        self.handle_stomp()
        self.animate(moving_left, moving_right, running)


class Enemy(pygame.sprite.Sprite):
    """An enemy that moves back and forth, reversing direction when hitting a wall."""

    def __init__(self, x, y, game):
        """
        Initialize the enemy sprite.
        Args:
            x (int): The initial x-coordinate of the enemy.
            y (int): The initial y-coordinate of the enemy.
            game (GameManager): Reference to the main game manager for accessing collision and other game state
        """
        super().__init__()
        self.frames = load_frames(AssetPaths.ENEMY, EnemySettings.WIDTH, EnemySettings.HEIGHT)
        self.frame_index = 0.0
        self.direction = EnemySettings.INITIAL_DIRECTION
        self.velocity_y = EnemySettings.INITIAL_VELOCITY_Y

        # Scale first frame to 32x32 to set up rect
        self.image = pygame.transform.scale(self.frames[0], (EnemySettings.WIDTH, EnemySettings.HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.game = game
        # Float accumulator for vertical position
        self.pos_y = float(y)

    def apply_gravity(self):
        self.velocity_y += EnemySettings.GRAVITY
        self.pos_y += self.velocity_y
        self.rect.y = int(round(self.pos_y))

    def move(self):
        self.rect.x += EnemySettings.SPEED * self.direction

    def handle_horizontal_collision(self):
        hit = self.game.collision.resolve_horizontal(self.rect)
        if hit != 0:
            self.direction *= -1

    def handle_vertical_collision(self):
        for solid_rect in self.game.collision.check_collision(self.rect):
            if self.velocity_y > 0 and self.rect.bottom > solid_rect.top:
                self.rect.bottom = solid_rect.top
                self.velocity_y = 0
                self.pos_y = float(self.rect.y)

    def animate(self):
        self.frame_index += EnemySettings.ANIMATION_SPEED
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.0
        frame = self.frames[int(self.frame_index)]
        # Flip when moving right (snail naturally faces left)
        frame = pygame.transform.scale(frame, (EnemySettings.WIDTH, EnemySettings.HEIGHT))
        self.image = frame if self.direction == -1 else pygame.transform.flip(frame, True, False)

    def update(self):
        self.move()
        self.apply_gravity()
        self.handle_vertical_collision()
        self.handle_horizontal_collision()
        self.animate()