class ColorSettings:
    """Class to hold all the color constants used by overlays, board, and UI."""

    # Colors are defined as RGB tuples, and named after the closest matching color
    COLOR_WORDS = {
        "BLACK": (0, 0, 0),
        "GAINSBORO": (220, 220, 220),
        "WHITE_SMOKE": (240, 240, 240),
        "CREAM_CAN": (240, 200, 80),
        "DARK_GRAY": (170, 170, 170),
        "DUTCH_WHITE": (240, 217, 181),
        "BARLEY_CORN": (181, 136, 99),
        "NERO": (40, 40, 40),
        "ECLIPSE": (60, 60, 60),
        "YELLOW": (255, 255, 0),
        "WHITE": (255, 255, 255),
    }

    # CRT / overlay
    OVERLAY_BACKGROUND = COLOR_WORDS["BLACK"]
    SCREEN_BACKGROUND = COLOR_WORDS["BLACK"]

    # Window borders
    BORDER_DEFAULT = COLOR_WORDS["GAINSBORO"]

    # Text
    TEXT_DEFAULT = COLOR_WORDS["WHITE_SMOKE"]
    TEXT_TITLE = COLOR_WORDS["CREAM_CAN"]
    TEXT_LABEL = COLOR_WORDS["DARK_GRAY"]

    # Board tiles (warm chess.com-style palette modeled on the reference image)
    BOARD_LIGHT_TILE = COLOR_WORDS["DUTCH_WHITE"]
    BOARD_DARK_TILE = COLOR_WORDS["BARLEY_CORN"]

    # Pieces (placeholders for later)
    QUEEN_WHITE = COLOR_WORDS["WHITE_SMOKE"]
    QUEEN_BLACK = COLOR_WORDS["NERO"]
    ARROW = COLOR_WORDS["ECLIPSE"]


class GridSettings:
    """Grid and tile dimensions for the 10x10 board."""

    TILE_SIZE = 32
    COLS = 10
    ROWS = 10
    BOARD_PIXELS = COLS * TILE_SIZE  # 320


class UISettings:
    """Window and UI layout coordinates derived from the tile size.

    Every position is built up from a single grid unit (TILE_SIZE = 32),
    so changing the tile size or HUD width re-flows the whole layout.
    """

    # All outer margins and the gap between board and HUD are one tile.
    LEFT_MARGIN = GridSettings.TILE_SIZE
    TOP_MARGIN = GridSettings.TILE_SIZE
    BOTTOM_MARGIN = GridSettings.TILE_SIZE
    RIGHT_MARGIN = GridSettings.TILE_SIZE
    GAP = GridSettings.TILE_SIZE

    # The board window is the rounded-corner container around the 10x10 board.
    # BOARD_INNER_PADDING keeps the rounded border from clipping tile pixels.
    BOARD_INNER_PADDING = 8
    BOARD_WINDOW_SIZE = GridSettings.BOARD_PIXELS + 2 * BOARD_INNER_PADDING  # 336
    BOARD_WINDOW_X = LEFT_MARGIN  # 32
    BOARD_WINDOW_Y = TOP_MARGIN   # 32

    # Top-left pixel of the actual playable board (inside the inner padding).
    BOARD_ORIGIN_X = BOARD_WINDOW_X + BOARD_INNER_PADDING  # 40
    BOARD_ORIGIN_Y = BOARD_WINDOW_Y + BOARD_INNER_PADDING  # 40

    # HUD: thin sidebar to the right of the board.
    HUD_WIDTH = 200
    HUD_HEIGHT = BOARD_WINDOW_SIZE                                   # 336
    HUD_X = BOARD_WINDOW_X + BOARD_WINDOW_SIZE + GAP                 # 400
    HUD_Y = TOP_MARGIN                                               # 32
    HUD_TEXT_PADDING = 14

    # Window chrome
    BORDER_WIDTH = 2
    BORDER_RADIUS = 5


class ScreenSettings:
    """Class to hold all the settings related to the screen."""

    # Screen size derives from the layout above so the two can never disagree.
    WIDTH = UISettings.HUD_X + UISettings.HUD_WIDTH + UISettings.RIGHT_MARGIN     # 632
    HEIGHT = UISettings.TOP_MARGIN + UISettings.BOARD_WINDOW_SIZE + UISettings.BOTTOM_MARGIN  # 400
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60
    CRT_ALPHA_RANGE = (75, 90)
    CRT_SCANLINE_HEIGHT = 3
    TITLE = "Game of the Amazons"


class FontSettings:
    """Font sizes used by the HUD."""

    FONT = "assets/font/Pixeled.ttf" # Doesn't look good... not used right now
    HUD_TITLE_SIZE = 24
    HUD_LABEL_SIZE = 16
    HUD_VALUE_SIZE = 22


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


class AssetPaths:
    """File paths for game assets."""
    TV = "assets/graphics/tv.png"
    WHITE_QUEEN = "assets/graphics/white_queen.png"
