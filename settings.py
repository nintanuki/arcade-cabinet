"""Configuration values for the top-level arcade launcher."""

from pathlib import Path


class ScreenSettings:
    """Display configuration for the launcher window."""

    WIDTH = 1280
    HEIGHT = 720
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60


class LauncherSettings:
    """Core launcher text and metadata."""

    WINDOW_TITLE = "Mr. Navarro's Arcade"


class ColorSettings:
    """Color palette used by launcher UI elements."""

    BLACK = (0, 0, 0)
    WHITE = (240, 240, 240)
    LIGHT_PURPLE = (210, 170, 255)
    LIGHT_BLUE = (150, 210, 255)
    YELLOW = (255, 230, 0)


class FontSettings:
    """Typography configuration for launcher text."""

    FILE = Path("font") / "Pixeled.ttf"
    TITLE_SIZE = 44
    SUBTITLE_SIZE = 14
    OPTION_SIZE = 24
    HINT_SIZE = 10


class MenuSettings:
    """Layout and copy for launcher menu rendering."""

    TITLE_TEXT = "MR. NAVARRO'S ARCADE"
    SUBTITLE_TEXT = "CHOOSE A GAME TO PLAY"
    TITLE_CENTER_Y = 180
    SUBTITLE_CENTER_Y = 285
    OPTIONS_LEFT_X = 250
    OPTIONS_START_Y = 390
    OPTION_SPACING = 70
    CURSOR_SYMBOL = ">"
    CURSOR_GAP = 20
    PREVIEW_BOX_X = 770
    PREVIEW_BOX_Y = 320
    PREVIEW_BOX_WIDTH = 320
    PREVIEW_BOX_HEIGHT = 240
    PREVIEW_BORDER_WIDTH = 2
    PREVIEW_BORDER_RADIUS = 22
    PREVIEW_INNER_PADDING = 12
    FOOTER_TEXT_LINE_1 = "PRESS SELECT ON CONTROLLER OR F11 ON KEYBOARD TO TOGGLE FULLSCREEN WHILE IN GAME."
    FOOTER_TEXT_LINE_2 = "PRESS START + SELECT + L1 + L2 OR CLOSE THE GAME WINDOW TO RETURN TO THIS MENU."
    FOOTER_LINE_1_CENTER_Y = 670
    FOOTER_LINE_2_CENTER_Y = 695


class ControlSettings:
    """Input mappings for keyboard and controller navigation."""

    CONTROLLER_BUTTON_A = 0
    CONTROLLER_BUTTON_SELECT = 6
    CONTROLLER_BUTTON_START = 7
    CONTROLLER_NAV_AXIS = 1
    CONTROLLER_AXIS_DEADZONE = 0.6


class CRTSettings:
    """CRT overlay effect tuning for the launcher screen."""

    OVERLAY_IMAGE = Path("dungeon-digger") / "graphics" / "tv.png"
    SCANLINE_HEIGHT = 3
    ALPHA_RANGE = (75, 90)


class GameSettings:
    """Game option metadata shown in the launcher menu."""

    OPTIONS = [
        ("Star Hero", Path("star-hero") / "main.py"),
        ("Dungeon Digger", Path("dungeon-digger") / "main.py"),
    ]

    PREVIEW_IMAGES = {
        "Star Hero": Path("graphics") / "star_hero_screenshot.png",
        "Dungeon Digger": Path("graphics") / "dungeon_digger_screenshot.png",
    }
