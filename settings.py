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

    WINDOW_TITLE = "CODING CLUB PYGAME ARCADE"
    MENU_MOVE_SOUND = Path("assets") / "sound" / "sfx_menu_move2.wav"
    MENU_SELECT_SOUND_CANDIDATES = (
        Path("assets") / "sound" / "sfx_menu_select3.wav",
    )


class ColorSettings:
    """Color palette used by launcher UI elements."""

    BLACK = (0, 0, 0)
    WHITE = (240, 240, 240)
    LIGHT_PURPLE = (210, 170, 255)
    LIGHT_BLUE = (150, 210, 255)
    YELLOW = (255, 230, 0)
    RED = (255, 80, 80)


class FontSettings:
    """Typography configuration for launcher text."""

    FILE = Path("assets") / "font" / "Pixeled.ttf"
    TITLE_SIZE = 44
    SUBTITLE_SIZE = 14
    OPTION_SIZE = 16
    HINT_SIZE = 10


class MenuSettings:
    """Layout and copy for launcher menu rendering."""

    TITLE_TEXT = "CODING CLUB PYGAME ARCADE"
    SUBTITLE_TEXT = "CHOOSE A GAME TO PLAY"
    TITLE_CENTER_Y = 140
    SUBTITLE_CENTER_Y = 245
    OPTIONS_LEFT_X = 250
    OPTIONS_START_Y = 320
    OPTION_SPACING = 30
    CAROUSEL_CENTER_X = 450
    CAROUSEL_CENTER_Y = 420
    CAROUSEL_VISIBLE_RADIUS = 2
    CAROUSEL_ITEM_SPACING = 44
    CAROUSEL_CURVE_X = 18
    CAROUSEL_SELECTED_SCALE = 1.25
    CAROUSEL_SCALE_STEP = 0.18
    CAROUSEL_MIN_SCALE = 0.75
    CAROUSEL_SELECTED_ALPHA = 255
    CAROUSEL_ALPHA_STEP = 70
    CAROUSEL_MIN_ALPHA = 90
    PREVIEW_BOX_X = 650
    PREVIEW_BOX_Y = 310
    PREVIEW_BOX_WIDTH = 320
    PREVIEW_BOX_HEIGHT = 240
    PREVIEW_BORDER_WIDTH = 2
    PREVIEW_BORDER_RADIUS = 22
    PREVIEW_INNER_PADDING = 12
    FOOTER_TEXT_LINE_1 = "PRESS SELECT ON CONTROLLER OR F11 ON KEYBOARD TO TOGGLE FULLSCREEN WHILE IN GAME."
    FOOTER_TEXT_LINE_2 = "PRESS START + SELECT + L1 + R1 OR CLOSE THE GAME WINDOW TO RETURN TO THIS MENU."
    FOOTER_LINE_1_CENTER_Y = 670
    FOOTER_LINE_2_CENTER_Y = 695
    NO_CONTROLLER_SUPPORT_TEXT = "NO CONTROLLER SUPPORT (KEYBOARD/MOUSE ONLY)"
    LIMITED_CONTROLLER_SUPPORT_TEXT = "LIMITED CONTROLLER SUPPORT"
    WONKY_PHYSICS_TEXT = "EXPECT WONKY PHYSICS, STILL WORKING ON IT"
    # Two stacked warning slots under the preview. Controller warnings (no /
    # limited, mutually exclusive) always take slot 1. Wonky-physics promotes
    # into slot 1 when no controller warning applies, otherwise it sits in
    # slot 2 directly beneath the controller line.
    WARNING_LINE_1_CENTER_Y = 585
    WARNING_LINE_2_CENTER_Y = 605
    UNDER_CONSTRUCTION_TEXT = "UNDER CONSTRUCTION"

class ControlSettings:
    """Input mappings for keyboard and controller navigation."""

    CONTROLLER_BUTTON_A = 0
    CONTROLLER_BUTTON_SELECT = 6
    CONTROLLER_BUTTON_START = 7
    CONTROLLER_NAV_AXIS = 1
    CONTROLLER_AXIS_DEADZONE = 0.6


class CRTSettings:
    """CRT overlay effect tuning for the launcher screen."""

    OVERLAY_IMAGE = Path("assets") / "graphics" / "tv.png"
    SCANLINE_HEIGHT = 3
    ALPHA_RANGE = (75, 90)


class GameSettings:
    """Game option metadata shown in the launcher menu."""

    OPTIONS = [
        ("Air Hockey", Path("games") / "air-hockey" / "main.py"),
        ("Breakout", Path("games") / "breakout" / "main.py"),
        ("Dungeon Digger", Path("games") / "dungeon-digger" / "main.py"),
        ("Dungeon Warrior", Path("games") / "dungeon-warrior" / "main.py"),
        ("Game of the Amazons", Path("games") / "game-of-the-amazons" / "main.py"),
        ("Jezz Ball", Path("games") / "jezz-ball" / "main.py"),
        ("Ninja Frog", Path("games") / "ninja-frog" / "main.py"),
        ("Pong", Path("games") / "pong" / "main.py"),
        ("Runner", Path("games") / "runner" / "main.py"),
        ("Snake", Path("games") / "snake" / "snake.py"),
        ("Space Invaders", Path("games") / "space-invaders" / "main.py"),
        ("Star Hero", Path("games") / "star-hero" / "main.py"),
        ("Tetris", Path("games") / "tetris" / "main.py"),
    ]

    PREVIEW_IMAGES = {
        "Air Hockey": Path("assets") / "previews" / "air_hockey.png",
        "Breakout": Path("assets") / "previews" / "breakout.png",
        "Dungeon Digger": Path("assets") / "previews" / "dungeon_digger.png",
        "Dungeon Warrior": Path("assets") / "previews" / "dungeon_warrior.png",
        "Game of the Amazons": Path("assets") / "previews" / "game_of_the_amazons.png",
        "Jezz Ball": Path("assets") / "previews" / "jezz_ball.png",
        "Ninja Frog": Path("assets") / "previews" / "ninja_frog.png",
        "Pong": Path("assets") / "previews" / "pong.png",
        "Runner": Path("assets") / "previews" / "runner.png",
        "Snake": Path("assets") / "previews" / "snake.png",
        "Space Invaders": Path("assets") / "previews" / "space_invaders.png",
        "Star Hero": Path("assets") / "previews" / "star_hero.png",
        "Tetris": Path("assets") / "previews" / "tetris.png",
    }

    LIMITED_CONTROLLER_SUPPORT_GAMES = {
        "Air Hockey",
        "Jezz Ball",
    }

    NO_CONTROLLER_SUPPORT_GAMES: set[str] = set()

    WONKY_PHYSICS_GAMES = {
        "Air Hockey",
        "Ninja Frog",
    }

    UNDER_CONSTRUCTION_GAMES = {
        "Dungeon Warrior",
        "Game of the Amazons",
        "Ninja Frog",
    }
