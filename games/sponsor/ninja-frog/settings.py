class ColorSettings:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

class TileSettings:
    SIZE = 16
    COLUMNS = 20
    ROWS = 30

class ScreenSettings:
    # screen width is 1.5x the map width so that an entire row of tiles
    # is visible plus, this means the camera only moves vertically as the play climbs
    # but the player can see all of the level horizontally at all times
    WIDTH = TileSettings.SIZE * TileSettings.COLUMNS * 3 // 2   # 320 * 1.5 = 480
    HEIGHT = TileSettings.SIZE * TileSettings.ROWS     # 480
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60
    BACKGROUND_COLOR = ColorSettings.BLACK
    CRT_ALPHA_RANGE: tuple[int, int] = (75, 90)

class PlayerSettings:
    WIDTH = TileSettings.SIZE
    HEIGHT = TileSettings.SIZE
    COLOR = ColorSettings.RED
    GRAVITY = 0.5
    JUMP_STRENGTH = -10
    INITIAL_VELOCITY_Y = 0
    LEFT_SPEED = 1.5
    RIGHT_SPEED = 1.5
    RUN_SPEED = 2.8
    STOMP_BOUNCE = -7

    # Start in the bottom left corner of the map (adjusted for tile size)
    START_POS_X = 2 * TileSettings.SIZE
    START_POS_Y = 12 * TileSettings.SIZE
    INITIAL_POSITION = (START_POS_X, START_POS_Y)

    ANIMATION_SPEED = 0.15

class ControllerSettings:
    DPAD_INDEX = 0 # Assuming the first hat is the d-pad
    MOVE_AXIS_X = 0 # Left stick horizontal axis
    AXIS_DEADZONE = 0.25 # Deadzone for analog stick to prevent drift

    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    L1_BUTTON = 4
    R1_BUTTON = 5
    START_BUTTON = 7
    SELECT_BUTTON = 6

class CameraSettings:
    # Multiplier applied to the world view when zoom is enabled. 2.0 means the
    # visible window is half the screen's width/height in world space, then
    # scaled up 2x to fill the screen.
    ZOOM_FACTOR = 1.5
    # Whether the game starts in the zoomed-in gameplay view (True) or the
    # zoomed-out debug view that shows the entire level (False).
    ZOOM_ENABLED_DEFAULT = True

class EnemySettings:
    WIDTH = 38
    HEIGHT = 24
    SPEED = 1
    START_POS_X = 7 * TileSettings.SIZE
    START_POS_Y = 13 * TileSettings.SIZE
    INITIAL_POSITION = (START_POS_X, START_POS_Y)
    INITIAL_DIRECTION = -1
    ANIMATION_SPEED = 0.1
    INITIAL_VELOCITY_Y = 0
    GRAVITY = 0.5

import os

class AssetPaths:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TILE_WALL = os.path.join(BASE_DIR, 'graphics', 'Terrain', 'Terrain (16x16).png')
    PLAYER_IDLE = os.path.join(BASE_DIR, 'graphics', 'Main Characters', 'Ninja Frog', 'Idle (32x32).png')
    PLAYER_RUN = os.path.join(BASE_DIR, 'graphics', 'Main Characters', 'Ninja Frog', 'Run (32x32).png')
    PLAYER_JUMP = os.path.join(BASE_DIR, 'graphics', 'Main Characters', 'Ninja Frog', 'Jump (32x32).png')
    PLAYER_FALL = os.path.join(BASE_DIR, 'graphics', 'Main Characters', 'Ninja Frog', 'Fall (32x32).png')
    ENEMY = os.path.join(BASE_DIR, 'graphics', 'Enemies', 'Snail', 'Walk (38x24).png')
    TV = os.path.join(BASE_DIR, 'graphics', 'Other', 'TV.png')