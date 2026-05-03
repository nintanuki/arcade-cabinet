"""Configuration values for Puzzle League.

The settings module is the single source of truth for tunable constants,
asset paths, color choices, and input mappings. Gameplay code should not
hard-code values that belong here.

The module is organized into namespaced classes so call sites can import
the bundle they need without pulling unrelated knobs into scope. The
overall structure mirrors the conventions used by Star Hero and Dungeon
Digger so the project feels familiar to anyone bouncing between games
in the arcade cabinet.
"""

import os


class ColorSettings:
    """Named RGB values used by gameplay rendering and UI chrome."""

    # Base palette
    BLACK = (0, 0, 0)
    WHITE = (240, 240, 240)
    GRAY = (90, 90, 90)
    DARK_GRAY = (35, 35, 45)
    LIGHT_GRAY = (170, 170, 180)
    YELLOW = (255, 220, 60)
    RED = (255, 80, 80)
    GREEN = (60, 255, 100)
    BLUE = (80, 160, 255)
    CYAN = (80, 255, 255)
    PURPLE = (200, 120, 255)

    # Semantic aliases.
    SCREEN_BACKGROUND = (20, 18, 35)
    BOARD_BACKGROUND = (12, 10, 24)
    BOARD_BORDER = WHITE
    GRID_LINE = (40, 38, 60)
    CURSOR_OUTLINE = WHITE
    TEXT_DEFAULT = WHITE
    TEXT_TITLE = YELLOW
    TEXT_PROMPT = CYAN

    # Block colors. The keys double as block "type" identifiers used by
    # the match-detection logic — keep them stable.
    BLOCK_COLORS = {
        'red':    (240, 80, 80),
        'green':  (90, 220, 110),
        'blue':   (90, 150, 255),
        'yellow': (255, 220, 70),
        'purple': (200, 120, 255),
        'cyan':   (80, 230, 230),
    }


class ScreenSettings:
    """Display configuration for the game window."""

    WIDTH = 600
    HEIGHT = 800
    RESOLUTION = (WIDTH, HEIGHT)
    CENTER = (WIDTH // 2, HEIGHT // 2)
    FPS = 60
    TITLE = "Puzzle League"

    BG_COLOR = ColorSettings.SCREEN_BACKGROUND

    # CRT overlay tuning, kept in sync with sibling games.
    CRT_ALPHA_RANGE = (75, 90)
    CRT_SCANLINE_HEIGHT = 3


class BoardSettings:
    """Playfield dimensions and grid geometry.

    Tetris Attack / Panel de Pon / Pokemon Puzzle League use a 6-wide by
    12-tall visible grid with one extra hidden row at the bottom that
    stages the next line of blocks rising into view.
    """

    COLS = 6
    VISIBLE_ROWS = 12
    BUFFER_ROWS = 1  # Hidden row beneath the visible grid for previewing the next rise.
    TOTAL_ROWS = VISIBLE_ROWS + BUFFER_ROWS

    BLOCK_SIZE = 48  # Pixel size of one square block.

    BOARD_WIDTH = COLS * BLOCK_SIZE
    BOARD_HEIGHT = VISIBLE_ROWS * BLOCK_SIZE

    # Board is centered horizontally with a comfortable top margin so a
    # HUD has room to breathe above the playfield.
    BOARD_X = (ScreenSettings.WIDTH - BOARD_WIDTH) // 2
    BOARD_Y = 80

    BORDER_WIDTH = 3
    BORDER_RADIUS = 6


class BlockSettings:
    """Block visuals, type catalog, and clear/animation timing."""

    # Active block types. Subset of ColorSettings.BLOCK_COLORS — keeping
    # this list short reduces the chance of unwinnable boards on early
    # difficulties. Add a sixth type later if needed for higher levels.
    TYPES = ('red', 'green', 'blue', 'yellow', 'purple')

    INNER_PADDING = 4  # Pixels trimmed off each side when drawing a block face.
    HIGHLIGHT_ALPHA = 90

    # Match resolution timing (milliseconds).
    FLASH_DURATION_MS = 600    # How long matched blocks flash before popping.
    POP_INTERVAL_MS = 90       # Stagger between sequential block pops in a match.
    FALL_SPEED_PX_PER_FRAME = 8  # How fast blocks fall after a clear.

    # Swap animation duration (milliseconds). The two swapped blocks
    # slide between their cells over this window so the move reads as
    # an action instead of an instant teleport.
    SWAP_DURATION_MS = 90


class CursorSettings:
    """Cursor behavior — the 1x2 selection box that swaps adjacent blocks."""

    # The cursor highlights two horizontally-adjacent cells. The "anchor"
    # cell is the left half; the right half is anchor + (1, 0).
    WIDTH_IN_CELLS = 2
    HEIGHT_IN_CELLS = 1

    OUTLINE_WIDTH = 3
    BORDER_RADIUS = 4

    # Repeat behavior for held movement keys/d-pad. INITIAL_DELAY is the
    # pause before auto-repeat kicks in; REPEAT_INTERVAL is the gap
    # between repeats once it does. Both are milliseconds.
    INITIAL_DELAY_MS = 220
    REPEAT_INTERVAL_MS = 90


class RiseSettings:
    """Tuning for the constant upward scroll of the stack."""

    # Pixels the stack rises per second at the current difficulty. The
    # game ramps this up over time; the value here is the floor.
    BASE_RISE_SPEED_PX_PER_SEC = 12.0
    MAX_RISE_SPEED_PX_PER_SEC = 80.0

    # When the player holds the "rush" button the stack jumps up at a
    # much faster rate so they can force fresh blocks into play.
    RUSH_RISE_SPEED_PX_PER_SEC = 240.0

    # Score thresholds at which BASE rise speed steps up. Indexed by level.
    DIFFICULTY_STEP_SCORE = 2000
    SPEED_INCREMENT_PX_PER_SEC = 4.0

    # Grace period (ms) granted whenever the top row first becomes
    # occupied. The player has this long to clear something before a
    # game-over check actually fires. Mirrors the "warning + topout"
    # pattern from the source games.
    TOPOUT_GRACE_MS = 2500


class ScoreSettings:
    """Point values and chain/combo multipliers."""

    # Base points awarded per block cleared in a single match.
    POINTS_PER_BLOCK = 10

    # Combo bonus: extra points awarded when a single match clears more
    # than the minimum 3 blocks. Indexed by clear size starting at 4.
    COMBO_BONUS = {
        4: 50,
        5: 150,
        6: 300,
        7: 500,
        8: 800,
    }

    # Chain bonus: awarded when blocks falling from a previous clear
    # land into a new match without further player input. Indexed by
    # chain depth (2 = first chained match, 3 = next, ...).
    CHAIN_BONUS = {
        2: 100,
        3: 250,
        4: 500,
        5: 1000,
    }

    # File where the high score persists between sessions. The path is
    # relative to this settings module so the launcher can spawn the
    # game from any working directory.
    HIGH_SCORE_FILE = os.path.join(os.path.dirname(__file__), 'high_score.txt')
    DEFAULT_INITIALS = "AAA"


class FontSettings:
    """Font file path and pre-defined sizes."""

    FONT = os.path.join(os.path.dirname(__file__), 'assets', 'font', 'Pixeled.ttf')
    SMALL = 10
    MEDIUM = 18
    LARGE = 28
    HUGE = 40

    DEFAULT_COLOR = ColorSettings.TEXT_DEFAULT
    TITLE_COLOR = ColorSettings.TEXT_TITLE
    PROMPT_COLOR = ColorSettings.TEXT_PROMPT


class UISettings:
    """HUD layout and overlay timing."""

    # Score/HUD anchors. The score sits above the playfield, the level
    # indicator below it. Specific X coordinates are derived from the
    # board geometry so a future board-size change carries through.
    SCORE_LABEL_Y = 24
    SCORE_VALUE_Y = 48

    LEVEL_LABEL_Y = BoardSettings.BOARD_Y + BoardSettings.BOARD_HEIGHT + 16
    LEVEL_VALUE_Y = LEVEL_LABEL_Y + 24

    HIGH_SCORE_LABEL_Y = 24
    HIGH_SCORE_VALUE_Y = 48

    # Volume bar HUD (matches the pattern in Star Hero).
    VOLUME_DISPLAY_TIME_MS = 1000
    VOLUME_BAR_WIDTH = 150
    VOLUME_BAR_HEIGHT = 8

    # Title / pause / game over copy.
    TITLE_TEXT = "PUZZLE LEAGUE"
    SUBTITLE_TEXT = "PRESS START"
    PAUSE_TEXT = "PAUSED"
    GAME_OVER_TEXT = "GAME OVER"
    CONTINUE_PROMPT = "PRESS START TO TRY AGAIN"


class ControllerSettings:
    """Joystick button mappings.

    Standard Logitech-style mapping used across the arcade cabinet
    library. Real input handling is wired up later — these constants
    only define WHAT each button is, not what it does.
    """

    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    L1_BUTTON = 4
    R1_BUTTON = 5
    BACK_BUTTON = 6
    START_BUTTON = 7

    # Held simultaneously this chord exits the game from anywhere,
    # matching the arcade cabinet panel labels.
    QUIT_COMBO = (START_BUTTON, BACK_BUTTON, L1_BUTTON, R1_BUTTON)

    LEFT_STICK_X = 0
    LEFT_STICK_Y = 1
    JOYSTICK_DEADZONE = 0.4


class InputBindings:
    """Action -> input mapping placeholders.

    Each entry lists the keyboard keys and controller buttons that
    should trigger that action once input handling is implemented. The
    binding tables live here (rather than buried in main.py) so future
    rebind menus or per-game tweaks have a single place to look.
    """

    # Movement actions. Filled in once cursor + rise behavior land.
    MOVE_LEFT = ('LEFT', 'A_KEY', 'DPAD_LEFT', 'LEFT_STICK_LEFT')
    MOVE_RIGHT = ('RIGHT', 'D_KEY', 'DPAD_RIGHT', 'LEFT_STICK_RIGHT')
    MOVE_UP = ('UP', 'W_KEY', 'DPAD_UP', 'LEFT_STICK_UP')
    MOVE_DOWN = ('DOWN', 'S_KEY', 'DPAD_DOWN', 'LEFT_STICK_DOWN')

    # Gameplay actions.
    SWAP = ('SPACE', 'A_BUTTON')
    RUSH = ('LSHIFT', 'R1_BUTTON')   # Force the stack to rise faster.
    PAUSE = ('RETURN', 'START_BUTTON')
    QUIT_TO_LAUNCHER = ('ESCAPE', 'QUIT_COMBO')


class AudioSettings:
    """Audio mixer and volume defaults."""

    DEFAULT_MASTER_VOLUME = 0.5
    DEBUG_MUTE = False

    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    SOUND_DIR = os.path.join(ASSETS_DIR, 'sound')
    MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')

    # No bundled audio yet — leave the playlist empty so the audio
    # system can boot without missing-file errors.
    BGM_PLAYLIST = []


class AssetPaths:
    """Resolved filesystem paths for static graphics and overlay textures."""

    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    GRAPHICS_DIR = os.path.join(ASSETS_DIR, 'graphics')

    # CRT overlay used by ui/crt.py. The file does not exist yet — the
    # CRT class falls back to a transparent surface when missing.
    TV = os.path.join(GRAPHICS_DIR, 'tv.png')


class DebugSettings:
    """Toggles useful while iterating on gameplay."""

    SHOW_GRID = False        # Draw faint cell outlines on top of the playfield.
    SHOW_FPS = False         # Render the current FPS in the corner.
    PAUSE_RISE = False       # Freeze the stack rise for layout debugging.
    UNLIMITED_TIME = False   # Skip the topout check entirely.
