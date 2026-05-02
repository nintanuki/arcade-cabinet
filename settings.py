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
    # Horizontal gap between the JIL logo and the launcher title text. The
    # title group (logo + gap + title) is centered as a single unit, so this
    # value is what controls how tightly the two read together.
    JIL_LOGO_TITLE_SPACING = 20
    # Color of the placeholder rect drawn when the JIL logo file is missing.
    # Deliberately hotter than ColorSettings.RED so a missing-asset bug
    # cannot be visually confused with a normal red UI element.
    JIL_LOGO_PLACEHOLDER_COLOR = (255, 0, 0)


class ColorSettings:
    """Color palette used by launcher UI elements."""

    BLACK = (0, 0, 0)
    WHITE = (240, 240, 240)
    LIGHT_PURPLE = (210, 170, 255)
    LIGHT_BLUE = (150, 210, 255)
    CYAN = (80, 255, 255)
    YELLOW = (255, 230, 0)
    ORANGE = (255, 170, 80)
    RED = (255, 80, 80)
    GREEN = (80, 255, 80)


class FontSettings:
    """Typography configuration for launcher text."""

    FILE = Path("assets") / "font" / "Pixeled.ttf"
    TITLE_SIZE = 44
    SUBTITLE_SIZE = 12
    OPTION_SIZE = 16
    HINT_SIZE = 10
    # Description text rendered inside the preview box on category screens.
    # Smaller than option text so multi-line copy still fits the panel.
    DESCRIPTION_SIZE = 10


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
    # The carousel only kicks in when a menu has more than this many items.
    # Smaller menus render as a plain vertical list so 2-5 entries do not
    # waste the on-screen real estate the carousel illusion needs.
    CAROUSEL_THRESHOLD = 5
    LIST_ITEM_SPACING = 36
    LIST_CURSOR_TEXT = "> "
    PREVIEW_BOX_X = 650
    PREVIEW_BOX_Y = 310
    PREVIEW_BOX_WIDTH = 320
    PREVIEW_BOX_HEIGHT = 240
    PREVIEW_BORDER_WIDTH = 2
    PREVIEW_BORDER_RADIUS = 22
    PREVIEW_INNER_PADDING = 12
    # Vertical gap between wrapped description lines inside the preview box.
    DESCRIPTION_LINE_SPACING = 4
    # Phrases that should render in a non-default color when they appear in
    # a category description. Matched case-insensitively against word
    # boundaries, with longer phrases preferred when they overlap.
    DESCRIPTION_HIGHLIGHTS = {
        "Mr. Navarro": ColorSettings.LIGHT_PURPLE,
        "Coding Club": ColorSettings.LIGHT_PURPLE,
        "John I. Leonard": ColorSettings.ORANGE,
        "Python": ColorSettings.GREEN,
        "Pygame": ColorSettings.GREEN,
        "Clear Code": ColorSettings.LIGHT_BLUE,
        "YouTube": ColorSettings.RED,
    }
    FOOTER_TEXT_LINE_1 = "PRESS SELECT ON CONTROLLER OR F11 ON KEYBOARD TO TOGGLE FULLSCREEN WHILE IN GAME."
    FOOTER_TEXT_LINE_2 = "PRESS START + SELECT + L1 + R1 OR CLOSE THE GAME WINDOW TO RETURN TO THIS MENU."
    FOOTER_LINE_1_CENTER_Y = 670
    FOOTER_LINE_2_CENTER_Y = 695
    # Two stacked warning slots under the preview. The input-scheme label
    # (when set to anything other than STANDARD) takes slot 1; the optional
    # free-form note sits in slot 2 directly beneath it. If only the note is
    # present, it promotes into slot 1.
    ATTRIBUTION_LINE_CENTER_Y = 565
    # Vertical gap between wrapped caption lines under the preview. Captions
    # that fit in one line keep the original WARNING_LINE_*_CENTER_Y layout
    # intact; longer captions wrap and push the warning slots down.
    CAPTION_LINE_SPACING = -10
    WARNING_LINE_1_CENTER_Y = 585
    WARNING_LINE_2_CENTER_Y = 605
    UNDER_CONSTRUCTION_TEXT = "UNDER CONSTRUCTION"


class ControlSettings:
    """Input mappings for keyboard and controller navigation."""

    CONTROLLER_BUTTON_A = 0
    CONTROLLER_BUTTON_B = 1
    CONTROLLER_BUTTON_SELECT = 6
    CONTROLLER_BUTTON_START = 7
    CONTROLLER_NAV_AXIS = 1
    CONTROLLER_AXIS_DEADZONE = 0.6


class CRTSettings:
    """CRT overlay effect tuning for the launcher screen."""

    OVERLAY_IMAGE = Path("assets") / "graphics" / "tv.png"
    SCANLINE_HEIGHT = 3
    ALPHA_RANGE = (75, 90)


class InputSchemeSettings:
    """Identifiers and display labels for a game's input requirements.

    A game whose entry is missing from GameSettings.GAME_INPUT_SCHEMES, or
    whose entry is STANDARD, shows no input-scheme warning -- it is assumed
    to work fully with the cabinet controller and the keyboard fallbacks.
    Any other key renders the matching LABELS string in red under the
    attribution.
    """

    STANDARD = "standard"
    LIMITED_CONTROLLER = "limited_controller"
    NO_CONTROLLER = "no_controller"
    MOUSE_ONLY = "mouse_only"
    MOUSE_AND_KEYBOARD = "mouse_and_keyboard"
    KEYBOARD_ONLY = "keyboard_only"

    # None suppresses the warning line entirely (used for STANDARD). Any
    # other value renders below the attribution in red.
    LABELS = {
        STANDARD: None,
        LIMITED_CONTROLLER: "LIMITED CONTROLLER SUPPORT",
        NO_CONTROLLER: "NO CONTROLLER SUPPORT",
        MOUSE_ONLY: "MOUSE ONLY",
        MOUSE_AND_KEYBOARD: "MOUSE & KEYBOARD ONLY",
        KEYBOARD_ONLY: "KEYBOARD ONLY",
    }


class CategorySettings:
    """Leaf-category metadata for the launcher menu tree.

    Each category becomes a list of games. Sponsor games are bucketed by
    GameSettings.GAME_CATEGORIES; the STUDENT category is filled in at
    runtime from the discovered games/student/ folder. Descriptions are
    stored in natural sentence case and uppercased at render time so the
    pixel font shows them in caps without the source being shouty.
    """

    STUDENT = "student"
    ORIGINAL = "original"
    TRIBUTE = "tribute"
    TUTORIAL = "tutorial"

    LABELS = {
        STUDENT: "Student Games",
        ORIGINAL: "Original Games",
        TRIBUTE: "Tribute Games",
        TUTORIAL: "Tutorial Games",
    }

    DESCRIPTIONS = {
        STUDENT: (
            "Games created by John I. Leonard students. Build something "
            "with pygame in Coding Club and your game can show up here too."
        ),
        ORIGINAL: "Mr. Navarro's original games created in Pygame.",
        TRIBUTE: "Classic games re-created in Pygame.",
        TUTORIAL: (
            "These games were all created following tutorials by Clear "
            "Code on YouTube."
        ),
    }

    # Attribution shown under the preview when a sponsor game inside the
    # category is highlighted. Student games carry their own attribution
    # from their game.json manifest, so STUDENT is intentionally absent.
    ATTRIBUTIONS = {
        ORIGINAL: "ORIGINAL GAME BY MR. NAVARRO",
        TRIBUTE: "TRIBUTE GAME BY MR. NAVARRO",
        TUTORIAL: "MADE FOLLOWING CLEAR CODE TUTORIALS",
    }


class GroupSettings:
    """Non-leaf submenu metadata.

    A group is a tree node whose children are other categories or groups.
    Selecting one pushes a new menu frame containing its children. The
    description shows in the preview pane when the group is highlighted.
    """

    MR_NAVARRO = "mr_navarro"

    LABELS = {
        MR_NAVARRO: "Mr. Navarro's Games",
    }

    DESCRIPTIONS = {
        MR_NAVARRO: (
            "Games created by Mr. Navarro"
            " using the Pygame library in Python."
        )
    }

class MenuTreeSettings:
    """Top-level launcher navigation tree.

    Each entry in ROOT is a dict describing one row in the root menu. A
    category leaf carries games (filtered from GameSettings.GAME_CATEGORIES
    or discovered for STUDENT). A group entry carries a ``children`` list
    of further nodes; the launcher walks this tree at startup to build menu
    frames, so adding a new category is just data here plus an entry in
    CategorySettings.
    """

    KIND_CATEGORY = "category"
    KIND_GROUP = "group"

    ROOT = [
        {"kind": KIND_CATEGORY, "key": CategorySettings.STUDENT},
        {
            "kind": KIND_GROUP,
            "key": GroupSettings.MR_NAVARRO,
            "children": [
                {"kind": KIND_CATEGORY, "key": CategorySettings.ORIGINAL},
                {"kind": KIND_CATEGORY, "key": CategorySettings.TRIBUTE},
                {"kind": KIND_CATEGORY, "key": CategorySettings.TUTORIAL},
            ],
        },
    ]


class GameSettings:
    """Sponsor game metadata. Student games are discovered at runtime."""

    # Sponsor games are committed to the repo and curated here. Student
    # games live in a sibling folder that is .gitignored and discovered at
    # runtime (see StudentGameSettings and main.discover_student_games).
    OPTIONS = [
        ("Adventure", Path("games") / "sponsor" / "adventure" / "main.py"),
        ("Air Hockey", Path("games") / "sponsor" / "air-hockey" / "main.py"),
        ("Breakout", Path("games") / "sponsor" / "breakout" / "main.py"),
        ("Dungeon Digger", Path("games") / "sponsor" / "dungeon-digger" / "main.py"),
        ("Game of the Amazons", Path("games") / "sponsor" / "game-of-the-amazons" / "main.py"),
        ("Jezz Ball", Path("games") / "sponsor" / "jezz-ball" / "main.py"),
        ("Ninja Frog", Path("games") / "sponsor" / "ninja-frog" / "main.py"),
        ("Pazaak", Path("games") / "sponsor" / "pazaak" / "main.py"),
        ("Pong", Path("games") / "sponsor" / "pong" / "main.py"),
        ("Puzzle League", Path("games") / "sponsor" / "puzzle-league" / "main.py"),
        ("Runner", Path("games") / "sponsor" / "runner" / "main.py"),
        ("Snake", Path("games") / "sponsor" / "snake" / "snake.py"),
        ("Space Invaders", Path("games") / "sponsor" / "space-invaders" / "main.py"),
        ("Star Hero", Path("games") / "sponsor" / "star-hero" / "main.py"),
        ("Tetris", Path("games") / "sponsor" / "tetris" / "main.py"),
    ]

    PREVIEW_IMAGES = {
        "Adventure": Path("assets") / "previews" / "adventure.png",
        "Air Hockey": Path("assets") / "previews" / "air_hockey.png",
        "Breakout": Path("assets") / "previews" / "breakout.png",
        "Dungeon Digger": Path("assets") / "previews" / "dungeon_digger.png",
        "Game of the Amazons": Path("assets") / "previews" / "game_of_the_amazons.png",
        "Jezz Ball": Path("assets") / "previews" / "jezz_ball.png",
        "Ninja Frog": Path("assets") / "previews" / "ninja_frog.png",
        "Pazaak": Path("assets") / "previews" / "pazaak.png",
        "Pong": Path("assets") / "previews" / "pong.png",
        "Puzzle League": Path("assets") / "previews" / "puzzle_league.png",
        "Runner": Path("assets") / "previews" / "runner.png",
        "Snake": Path("assets") / "previews" / "snake.png",
        "Space Invaders": Path("assets") / "previews" / "space_invaders.png",
        "Star Hero": Path("assets") / "previews" / "star_hero.png",
        "Tetris": Path("assets") / "previews" / "tetris.png",
    }

    # Each sponsor game's category. The launcher derives the attribution
    # string at runtime from CategorySettings.ATTRIBUTIONS using this map,
    # so adding a game is just one entry here plus its OPTIONS row.
    GAME_CATEGORIES = {
        "Adventure": CategorySettings.ORIGINAL,
        "Air Hockey": CategorySettings.ORIGINAL,
        "Breakout": CategorySettings.TUTORIAL,
        "Dungeon Digger": CategorySettings.ORIGINAL,
        "Game of the Amazons": CategorySettings.TRIBUTE,
        "Jezz Ball": CategorySettings.TRIBUTE,
        "Ninja Frog": CategorySettings.ORIGINAL,
        "Pazaak": CategorySettings.TRIBUTE,
        "Pong": CategorySettings.TUTORIAL,
        "Puzzle League": CategorySettings.TRIBUTE,
        "Runner": CategorySettings.TUTORIAL,
        "Snake": CategorySettings.TUTORIAL,
        "Space Invaders": CategorySettings.TUTORIAL,
        "Star Hero": CategorySettings.ORIGINAL,
        "Tetris": CategorySettings.TUTORIAL,
    }

    # Brief per-game caption rendered in white above the warning slots.
    # Use it for a one-line tagline; the description preview-box space is
    # already filled by the category description, so this is the place
    # for game-specific copy. A missing entry simply hides the line.
    GAME_DESCRIPTIONS = {
        "Adventure": "ZELDA CLONE WITH TEXT BASED FLAVOR",
        "Air Hockey": "IT'S AIR HOCKEY, YOU KNOW WHAT AIR HOCKEY IS",
        "Breakout": "THE CLASSIC BLOCK-BREAKING ARCADE GAME",
        "Dungeon Digger": "DUNGEON CRAWLING RPG WITH TURN-BASED AND TEXT-BASED FLAVOR",
        "Game of the Amazons": "CLASSIC STRATEGY GAME USING CHESS PIECES",
        "Jezz Ball": "THE CLASSIC MICROSOFT GAME FOR WHEN THE INTERNET WAS DOWN",
        "Ninja Frog": "JUST ME MESSING AROUND WITH PLATFORMING MECHANICS",
        "Pazaak": "CARD GAME FROM STAR WARS: KNIGHTS OF THE OLD REPUBLIC, SIMILAR TO BLACKJACK",
        "Pong": "THE FIRST COMMERCIALLY SUCCESSFUL VIDEO GAME",
        "Puzzle League": "LIKE TETRIS ATTACK/PANEL DE PON OR POKEMON PUZZLE LEAGUE",
        "Runner": "THIS IS WHEN OBJECT-ORIENTED PROGRAMMING FINALLY CLICKED FOR ME",
        "Snake": "THE CLASSIC SNAKE GAME THAT ORIGINATED ON NOKIA PHONES",
        "Space Invaders": "CLASSIC ARCADE GAME, STAR HERO'S CODE IS BASED ON THIS ONE",
        "Star Hero": "THE FIRST PROPER GAME I EVER MADE, INSPIRED BY GALAGA AND STAR FOX",
        "Tetris": "THE GREATEST PUZZLE VIDEO GAME OF ALL TIME",
    }

    # Optional input-scheme tag per game. A game with no entry here, or
    # one set to STANDARD, shows no input-scheme warning. Anything else
    # renders the matching InputSchemeSettings.LABELS string in red.
    GAME_INPUT_SCHEMES = {
        "Air Hockey": InputSchemeSettings.LIMITED_CONTROLLER,
        "Jezz Ball": InputSchemeSettings.LIMITED_CONTROLLER,
    }

    # Optional free-form red note shown under the input-scheme line. Use
    # for anything game-specific that does not fit a stock warning, e.g.
    # "WONKY PHYSICS", "RESETS ON GAME OVER", "TWO PLAYER ONLY".
    GAME_NOTES = {
        "Air Hockey": "STILL WORKING ON IT - EXPECT WONKY PHYSICS",
        "Ninja Frog": "STILL WORKING ON IT - EXPECT WONKY PHYSICS",
    }

    UNDER_CONSTRUCTION_GAMES = {
        "Adventure",
        "Ninja Frog",
        "Pazaak",
        "Puzzle League",
    }


class StudentGameSettings:
    """Convention for student-contributed games discovered at runtime.

    Student games live under ``games/student/<folder>/`` and are .gitignored,
    so each cabinet keeps its own students' work without leaking to GitHub.
    The launcher scans the folder at startup and appends every directory
    containing ``ENTRY_FILENAME`` to the Student Games category. An optional
    ``MANIFEST_FILENAME`` next to the entry file overrides the auto-derived
    metadata; the schema is documented in ``games/student/README.md``.
    Every manifest field is optional; missing fields fall back to the
    launcher's defaults.
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
    MANIFEST_KEY_INPUT_SCHEME = "input_scheme"
    MANIFEST_KEY_NOTE = "note"
    MANIFEST_KEY_PREVIEW = "preview"
    MANIFEST_KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    MANIFEST_KEY_UNDER_CONSTRUCTION = "under_construction"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    KEY_NO_CONTROLLER = "no_controller_support"
    MANIFEST_KEY_LIMITED_CONTROLLER = "limited_controller_support"
    MANIFEST_KEY_WONKY_PHYSICS = "wonky_physics"
    MANIFEST_KEY_UNDER_CONSTRUCTION = "under_construction"
