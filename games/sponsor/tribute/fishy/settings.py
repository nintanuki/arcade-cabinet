import os

class ColorSettings:
    """Class to hold all the color settings for the game."""
    BLACK = (0, 0, 0)
    NERO = (30, 30, 30)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    LIGHT_BLUE = (0, 255, 255)
    FOUNTAIN_BLUE = (102, 168, 176)
    DARK_TURQUOISE = (5, 195, 221) # AQUA BLUE

    BG_COLOR = DARK_TURQUOISE

class ScreenSettings:
    """Class to hold all the settings related to the screen."""
    WIDTH = 1280
    HEIGHT = 720
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60
    CRT_ALPHA_RANGE = (75, 90)
    CRT_SCANLINE_HEIGHT = 3
    TITLE = "Fishy"


class UiSettings:
    """UI text content and font-size settings for gameplay overlays."""

    GAME_OVER_TEXT = "GAME OVER"
    PAUSE_TEXT = "PAUSED"
    OVERLAY_FONT_SIZE = 52


class GameStateSettings:
    """Canonical state names for the game loop state machine."""

    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

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

class PlayerSettings:
    """Player-specific settings like movement speed."""
    SPEED = 3
    SIZE = (16, 16)
    COLOR = (255, 255, 0)
    # % of the eaten fish's size is added to the player
    PLAYER_GROWTH_COEFFICIENT = 0.10

class FishSettings:
    """Settings related to the fish enemies."""

    # NOTE: MAX_SIZE must be less than ScreenSettings.HEIGHT (720).
    # If MAX_SIZE >= 720, the spawn logic in sprites.py will pass a 
    # negative range to random.randint(), causing a ValueError.

    SPAWN_RATE = ScreenSettings.FPS // 5 # Frames between spawns
    MIN_SIZE = 8
    MAX_SIZE = ScreenSettings.HEIGHT // 3
    MIN_SPEED = 0.5
    MAX_SPEED = 3

    # Fish body height as a fraction of size; values < 1 flatten the fish vertically.
    BODY_HEIGHT_RATIO = 0.5
    # Fish tail width as a fraction of size.
    TAIL_WIDTH_RATIO = 0.33
    # Fish eye side length as a fraction of fish size.
    EYE_SIZE_RATIO = 0.12
    # Eye horizontal offset from the nose toward the tail-start, as fraction of size.
    EYE_NOSE_OFFSET_RATIO = 0.25

class FontSettings:
    """Font files, sizes, and text-color mappings for UI rendering."""

    FONT = os.path.join(
        os.path.dirname(__file__), 'assets', 'font', 'Pixeled.ttf'
    )

class AssetPaths:
    """Class to hold all the file paths for assets."""
    # __file__-relative so the project runs no matter the working directory
    # (e.g. when launched from the arcade cabinet launcher).
    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')
    MUSIC_DIR = os.path.join(AUDIO_DIR, 'music')

    TV = os.path.join(
        ASSETS_DIR, 'graphics', 'effects', 'tv.png'
    )


class AudioSettings:
    """Global audio toggles, volumes, and the sound/music registry consumed by AudioManager."""

    MUTE = False
    MUTE_MUSIC = False  # Keep music disabled while retaining sound effects.
    MUSIC_VOLUME = 1.0  # Background music volume in the range [0.0, 1.0].
    SFX_VOLUME = 1.0  # Sound effect volume in the range [0.0, 1.0].

    # Logical name -> filesystem path. Keys are what gameplay code passes to
    # ``AudioManager.play(name)``.
    SOUND_EFFECTS = {
        "pause_in": os.path.join(AssetPaths.AUDIO_DIR, 'sound', 'sfx_sounds_pause2_in.ogg'),
        "pause_out": os.path.join(AssetPaths.AUDIO_DIR, 'sound', 'sfx_sounds_pause2_out.ogg'),
    }

    # Background tracks; one is chosen at random each time music starts.
    MUSIC_TRACKS = [
        os.path.join(AssetPaths.MUSIC_DIR, '8bit-aquarium.mp3'),
    ]

class DebugSettings:
    """Settings related to debugging features."""