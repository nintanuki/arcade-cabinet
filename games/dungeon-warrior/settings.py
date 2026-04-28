import os


class ColorSettings:
    """Centralized named colors used throughout UI and gameplay rendering."""

    # Base color names
    WHITE = 'white'
    BLACK = 'black'
    YELLOW = 'yellow'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    CYAN = 'cyan'
    PURPLE = 'purple'
    GOLD = 'gold'
    DODGER_BLUE = 'dodgerblue'
    TAN = 'tan'
    FIREBRICK = 'firebrick'
    LIME_GREEN = 'limegreen'
    ORCHID = 'orchid'
    MEDIUM_ORCHID = 'mediumorchid'
    PLUM = 'plum'
    DARK_GRAY = 'darkgray'
    DIM_GRAY = 'dimgray'
    SADDLE_BROWN = 'saddlebrown'
    SLATE_GRAY = 'slategray'

    SCREEN_BACKGROUND = BLACK

    TEXT_DEFAULT = WHITE
    TEXT_ACTIVE_MESSAGE = YELLOW
    TEXT_TITLE = YELLOW
    TEXT_PROMPT = CYAN
    TEXT_GOLD = GOLD
    TEXT_WIN = GREEN
    TEXT_LOSS = RED
    TEXT_CONTINUE = CYAN
    TEXT_ERROR = RED
    TEXT_SELECTOR = YELLOW

    OVERLAY_BACKGROUND = BLACK

    BORDER_DEFAULT = WHITE
    BORDER_KEY_ACTIVE = GOLD
    BORDER_MAP_ACTIVE = GOLD
    BORDER_MESSAGE_SUCCESS = LIME_GREEN
    BORDER_MESSAGE_FAILURE = FIREBRICK
    BORDER_REPELLED = MEDIUM_ORCHID

class ScreenSettings:
    """Class to hold all the settings related to the screen."""
    WIDTH = 800
    HEIGHT = 600
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60
    CRT_ALPHA_RANGE = (75, 90)
    CRT_SCANLINE_HEIGHT = 3
    TITLE = "Dungeon Warrior"

class GridSettings:
    """Grid and tile scaling values used for map layout and sprite snapping."""

    RAW_TILE_SIZE = 16 # Source tile size in pixels.
    SCALE_FACTOR = 2 # Render scale multiplier applied to source tiles.
    TILE_SIZE = RAW_TILE_SIZE * SCALE_FACTOR # Effective in-game tile size.

class UISettings:
    """Layout coordinates and dimensions for game windows and HUD elements."""

    LEFT_MARGIN = 64
    TOP_MARGIN = 56
    GAP = GridSettings.TILE_SIZE

    BORDER_COLOR = ColorSettings.BORDER_DEFAULT
    BORDER_RADIUS = 5
    DOOR_UNLOCK_BORDER_FLASH_MS = 2500

    SIDEBAR_WIDTH = 200
    BOTTOM_LOG_HEIGHT = 150

    COLS = 14
    ROWS = 10
    ACTION_WINDOW_WIDTH = COLS * GridSettings.TILE_SIZE
    ACTION_WINDOW_HEIGHT = ROWS * GridSettings.TILE_SIZE

    ACTION_WINDOW_X = LEFT_MARGIN
    ACTION_WINDOW_Y = TOP_MARGIN

    SIDEBAR_X = ACTION_WINDOW_X + ACTION_WINDOW_WIDTH + GAP
    SIDEBAR_Y = TOP_MARGIN
    SIDEBAR_HEIGHT = ACTION_WINDOW_HEIGHT

    LOG_X = LEFT_MARGIN
    LOG_Y = ACTION_WINDOW_Y + ACTION_WINDOW_HEIGHT + GAP
    LOG_WIDTH = ACTION_WINDOW_WIDTH
    LOG_HEIGHT = BOTTOM_LOG_HEIGHT

    MAP_X = SIDEBAR_X
    MAP_Y = LOG_Y
    MAP_WIDTH = SIDEBAR_WIDTH
    MAP_HEIGHT = BOTTOM_LOG_HEIGHT
    MINIMAP_PADDING = 10

    SCORE_X = 72
    SCORE_Y = 20
    CURRENT_SCORE_X = SIDEBAR_X + 16
    CURRENT_SCORE_Y = SCORE_Y
    LEVEL_X = LEFT_MARGIN
    LEVEL_Y = ScreenSettings.HEIGHT - 34
    DUNGEON_NAME_Y = LEVEL_Y + 15

    # AUDIO MUTED indicator anchored to the top-right of the action window,
    # opposite the HIGH SCORE label. Used as a topright anchor when blitting.
    MUTE_RIGHT_X = ACTION_WINDOW_X + ACTION_WINDOW_WIDTH
    MUTE_Y = SCORE_Y

class GameSettings:
    """Global gameplay flow constants and persistence limits."""

    LEVEL_TRANSITION_MS = 2000
    LEADERBOARD_FILE = 'leaderboard.txt'
    LEADERBOARD_LIMIT = 10

    # Save system: ten slots, JSON files under saves/. SAVE_VERSION exists so
    # SaveManager can reject or migrate older save files if the schema ever
    # changes incompatibly.
    SAVES_DIR = 'saves'
    SAVE_VERSION = 1
    MAX_SAVE_SLOTS = 10
    MAX_PLAYER_NAME_LENGTH = 8
    GAME_OVER_CONTINUE_DELAY_MS = 650
    GAME_OVER_PROMPT_FADE_MS = 750
    DOOR_UNLOCK_MESSAGE_TYPE_SPEED = 0.12

    TREASURE_CONVERSION_DISPLAY_DELAY_MS = 2000
    TREASURE_CONVERSION_LINE_REVEAL_INTERVAL_MS = 520
    TREASURE_CONVERSION_TOTAL_REVEAL_DELAY_MS = 450
    TREASURE_CONVERSION_PROMPT_FADE_MS = 650
    TREASURE_CONVERSION_POST_MESSAGE_DELAY_MS = 450

    SHOP_DISPLAY_DELAY_MS = 200
    STATUS_EFFECT_TURN_BUFFER = 1

class WindowSettings:
    """Message window behavior and text layout settings."""

    MAX_MESSAGES = 5
    LINE_HEIGHT = 22
    TEXT_PADDING = 16
    WELCOME_MESSAGE = [
        "IT'S PITCH BLACK",
        "YOU CAN'T SEE A THING",
        "MAYBE YOU SHOULD LIGHT A TORCH?",
        "(B BUTTON ON CONTROLLER / F ON KEYBOARD)"]
    TYPING_SPEED = 0.25 # Characters advanced per frame in typewriter animation.

class InputSettings:
    """Controller button and axis mappings used by gameplay and menus.

    Constants are named after the physical button on the controller, not the
    action it performs. The only exception is JOY_BUTTON_QUIT_COMBO, which is
    a special multi-button chord rather than a single button.
    """

    JOY_BUTTON_A = 0
    JOY_BUTTON_B = 1
    JOY_BUTTON_X = 2
    JOY_BUTTON_Y = 3
    JOY_BUTTON_L1 = 4
    JOY_BUTTON_R1 = 5
    JOY_BUTTON_BACK = 6
    JOY_BUTTON_START = 7
    JOY_BUTTON_QUIT_COMBO = (7, 6, 4, 5)

    JOY_AXIS_LEFT_X = 0
    JOY_AXIS_LEFT_Y = 1
    JOY_AXIS_L2 = 4
    JOY_AXIS_R2 = 5
    JOY_TRIGGER_THRESHOLD = 0.5

class FontSettings:
    """Font files, sizes, and text-color mappings for UI rendering."""

    FONT = 'font/Pixeled.ttf'
    MESSAGE_SIZE = 8
    SCORE_SIZE = 12
    HUD_SIZE = 10
    ENDGAME_SIZE = 32
    DEFAULT_COLOR = ColorSettings.TEXT_DEFAULT
    LAST_MESSAGE_COLOR = ColorSettings.TEXT_ACTIVE_MESSAGE

    # WORD_COLORS = {
    #     "RUBY": ColorSettings.TREASURE_RUBY,
    #     "SAPPHIRE": ColorSettings.BLUE,
    #     "EMERALD": ColorSettings.TREASURE_EMERALD,
    #     "KEY": ColorSettings.YELLOW,
    #     "MONSTER": ColorSettings.PURPLE,
    #     "MONSTER REPELLENT": ColorSettings.PURPLE
    # }

class AudioSettings:
    """Global audio toggles and mixer-level defaults."""

    MUTE = False
    MUTE_MUSIC = False  # Keep music disabled while retaining sound effects.
    MUSIC_VOLUME = 1  # Background music volume in the range [0.0, 1.0].

class AssetPaths:
    """Class to hold all the file paths for game assets."""

    # Images
    BASE_DIR = os.path.dirname(__file__)
    GRAPHICS_DIR = os.path.join(BASE_DIR, 'graphics')

    # CRT Effect
    TV = os.path.join(GRAPHICS_DIR, 'tv.png')

    # World tiles (placeholder set used while world rendering is being wired up).
    # tile_0014.png is the brick wall, tile_0000.png is plain dirt floor.
    WALL_TILE = os.path.join(GRAPHICS_DIR, 'tile_0014.png')
    FLOOR_TILE = os.path.join(GRAPHICS_DIR, 'tile_0000.png')

        # Audio
    SOUND_DIR = os.path.join(BASE_DIR, 'sound')
    MOVE_SOUND = os.path.join(SOUND_DIR, 'sfx_movement_footstepsloop4_slow.ogg')
    BOUNDARY_SOUND = os.path.join(SOUND_DIR, 'wall_bump_sound_effect.ogg')
    COIN_SOUND = os.path.join(SOUND_DIR, 'sfx_coin_cluster3.ogg')
    MENU_MOVE_SOUND = os.path.join(SOUND_DIR, 'sfx_menu_move2.ogg')
    MENU_SELECT_SOUND = os.path.join(SOUND_DIR, 'sfx_menu_select3.ogg')

    # Music
    MUSIC_DIR = os.path.join(BASE_DIR, 'music')
    NORMAL_MUSIC_TRACKS = [
        os.path.join(MUSIC_DIR, 'Goblins_Den_(Regular).ogg'),
    ]
    CHASE_MUSIC = os.path.join(MUSIC_DIR, 'Goblins_Dance_(Battle).ogg')
    MUSIC_TRACKS = NORMAL_MUSIC_TRACKS

class DebugSettings:
    """Settings related to debugging features."""
    GRID = True # Draw tile outlines for visual debugging.
    MUTE = False # Force mute all sound output during testing.
    USE_TEST_INITIAL_INVENTORY = True # Start runs with ItemSettings.TEST_INITIAL_INVENTORY when enabled.
    SHOW_UI_FRAMES = True # Render the four UI window borders (toggle with F1).
    SHOW_DEBUG_PLAYER = True # Render the red placeholder player and accept its input.
    SHOW_CELL_LABEL = True # Print the active cell name inside the map window.

class DebugPlayerSettings:
    """Tunable values for the temporary red-square player used while wiring UI."""
    SPEED = 4.0 # Pixels per frame at full stick deflection / held key.
    STICK_DEADZONE = 0.2 # Ignore left-stick noise inside this radius.
    COLOR = ColorSettings.RED # Fill color for the placeholder player sprite.
    HITBOX_INSET = 6 # Per-side pixel slack: hitbox is TILE_SIZE - 2*INSET square.
