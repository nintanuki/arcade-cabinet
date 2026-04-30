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

    WINDOW_TITLE = "Coding Club Arcade"
    MENU_MOVE_SOUND = Path("assets") / "sound" / "sfx_menu_move2.wav"
    MENU_SELECT_SOUND_CANDIDATES = (
        Path("assets") / "sound" / "sfx_menu_select3.wav",
    )
    JIL_LOGO_PATH = Path("assets") / "graphics" / "jil_logo.webp"
    JIL_LOGO_POS = (50, 110)
    JIL_LOGO_SIZE = (59, 69)


class ColorSettings:
    """Color palette used by launcher UI elements."""

    BLACK = (0, 0, 0)
    WHITE = (240, 240, 240)
    LIGHT_PURPLE = (210, 170, 255)
    LIGHT_BLUE = (150, 210, 255)
    YELLOW = (255, 230, 0)
    RED = (255, 80, 80)
    GREEN = (80, 255, 80)


class FontSettings:
    """Typography configuration for launcher text."""

    FILE = Path("assets") / "font" / "Pixeled.ttf"
    TITLE_SIZE = 44
    SUBTITLE_SIZE = 14
    OPTION_SIZE = 16
    HINT_SIZE = 10


class MenuSettings:
    """Layout and copy for launcher menu rendering."""

    TITLE_TEXT = "CODING CLUB ARCADE"
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
    ATTRIBUTION_LINE_CENTER_Y = 565
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

    # Sponsor games are committed to the repo and curated here. Student games
    # live in a sibling folder that is .gitignored and discovered at runtime
    # (see StudentGameSettings and main.discover_student_games).
    OPTIONS = [
        ("Air Hockey", Path("games") / "sponsor" / "air-hockey" / "main.py"),
        ("Breakout", Path("games") / "sponsor" / "breakout" / "main.py"),
        ("Dungeon Digger", Path("games") / "sponsor" / "dungeon-digger" / "main.py"),
        ("Dungeon Warrior", Path("games") / "sponsor" / "dungeon-warrior" / "main.py"),
        ("Game of the Amazons", Path("games") / "sponsor" / "game-of-the-amazons" / "main.py"),
        ("Jezz Ball", Path("games") / "sponsor" / "jezz-ball" / "main.py"),
        ("Ninja Frog", Path("games") / "sponsor" / "ninja-frog" / "main.py"),
        ("Pong", Path("games") / "sponsor" / "pong" / "main.py"),
        ("Runner", Path("games") / "sponsor" / "runner" / "main.py"),
        ("Snake", Path("games") / "sponsor" / "snake" / "snake.py"),
        ("Space Invaders", Path("games") / "sponsor" / "space-invaders" / "main.py"),
        ("Star Hero", Path("games") / "sponsor" / "star-hero" / "main.py"),
        ("Tetrominos", Path("games") / "sponsor" / "tetrominos" / "main.py"),
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
        "Tetrominos": Path("assets") / "previews" / "tetrominos.png",
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

    GAME_ATTRIBUTIONS = {
        "Air Hockey": "TRIBUTE BY MR. NAVARRO",
        "Breakout": "MADE WITH CLEAR CODE TUTORIAL",
        "Dungeon Digger": "ORIGINAL BY MR. NAVARRO",
        "Dungeon Warrior": "ORIGINAL BY MR. NAVARRO",
        "Game of the Amazons": "TRIBUTE BY MR. NAVARRO",
        "Jezz Ball": "TRIBUTE BY MR. NAVARRO",
        "Ninja Frog": "ORIGINAL BY MR. NAVARRO",
        "Pong": "MADE WITH CLEAR CODE TUTORIAL",
        "Runner": "MADE WITH CLEAR CODE TUTORIAL",
        "Snake": "MADE WITH CLEAR CODE TUTORIAL",
        "Space Invaders": "MADE WITH CLEAR CODE TUTORIAL",
        "Star Hero": "ORIGINAL BY MR. NAVARRO",
        "Tetrominos": "MADE WITH CLEAR CODE TUTORIAL",
    }


class StudentGameSettings:
    """Convention for student-contributed games discovered at runtime.

    Student games live under ``games/student/<folder>/`` and are .gitignored,
    so each cabinet keeps its own students' work without leaking to GitHub.
    The launcher scans the folder at startup and appends every directory
    containing ``ENTRY_FILENAME`` to the menu. An optional ``MANIFEST_FILENAME``
    next to the entry file overrides the auto-derived metadata; the schema is
    documented in ``games/student/README.md``.
    """

    # Folder convention. ROOT is relative to the launcher's root_dir.
    ROOT = Path("games") / "student"
    ENTRY_FILENAME = "main.py"
    MANIFEST_FILENAME = "game.json"

    # Defaults applied when no manifest is present, or when a manifest omits
    # a field. The attribution intentionally invites the teacher to fill it
    # in via game.json -- see the example in games/student/README.md.
    DEFAULT_ATTRIBUTION = "CREATED BY UNKNOWN STUDENT"

    # Manifest keys recognized by the launcher. Anything else is ignored so
    # the schema stays forgiving for students experimenting with extras.
    MANIFEST_KEY_LABEL = "label"
    MANIFEST_KEY_ATTRIBUTION = "attribution"
    MANIFEST_KEY_PREVIEW = "preview"
    MANIFEST_KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    MANIFEST_KEY_UNDER_CONSTRUCTION = "under_construction"
