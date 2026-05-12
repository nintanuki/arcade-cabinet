"""Centralized configuration for Space Invaders.

Every tuning value the game cares about lives here. Sprites, the CRT
overlay, audio, and the main loop all import from this module instead of
hard-coding numbers. Grouping constants into ``*Settings`` classes makes
it obvious which subsystem a value belongs to and keeps tweaks safe.
"""

import os


# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------

class ColorSettings:
    """Named RGB colors used by sprites and the HUD."""

    OBSTACLE = (241, 79, 80)  # red-orange Space Invaders bunker color
    LASER = (255, 255, 255)
    SCORE_TEXT = (255, 255, 255)
    VICTORY_TEXT = (255, 255, 255)
    PAUSE_TEXT = (255, 255, 255)
    PAUSE_OVERLAY = (0, 0, 0, 140)  # translucent black behind PAUSED label
    BG_FILL = (30, 30, 30)  # dark grey behind sprites (mostly hidden by CRT)


# ---------------------------------------------------------------------------
# SCREEN / DISPLAY
# ---------------------------------------------------------------------------

class ScreenSettings:
    """Window geometry, frame pacing, and CRT overlay tuning."""

    WIDTH = 600
    HEIGHT = 600
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60  # main loop tick rate
    CRT_SCANLINE_HEIGHT = 3  # vertical pixels between CRT scanlines
    CRT_ALPHA_RANGE = (75, 90)  # min/max alpha for CRT flicker each frame


# ---------------------------------------------------------------------------
# CONTROLLER MAPPING
# ---------------------------------------------------------------------------

class ControllerSettings:
    """Button indices shared with the rest of the arcade cabinet."""

    A_BUTTON = 0
    BACK_BUTTON = 6  # also known as SELECT on the cabinet panel
    START_BUTTON = 7
    L1_BUTTON = 4
    R1_BUTTON = 5
    # Held simultaneously, this chord exits the game from anywhere, matching
    # the cabinet panel labels (L1 + R1 + START + SELECT).
    QUIT_COMBO = (START_BUTTON, BACK_BUTTON, L1_BUTTON, R1_BUTTON)
    JOYSTICK_DEADZONE = 0.4  # analog input below this magnitude is ignored


# ---------------------------------------------------------------------------
# PLAYER
# ---------------------------------------------------------------------------

class PlayerSettings:
    """Movement and weapon tuning for the player ship."""

    SPEED = 5  # pixels per frame at 60 FPS
    LIVES = 3
    LASER_COOLDOWN = 600  # milliseconds between consecutive shots
    LASER_SFX_VOLUME = 0.5


# ---------------------------------------------------------------------------
# ALIENS
# ---------------------------------------------------------------------------

class AlienSettings:
    """Grid geometry, point values, and shooting cadence for the alien wave."""

    ROWS = 6
    COLS = 8
    X_DISTANCE = 60  # horizontal spacing between aliens in pixels
    Y_DISTANCE = 48  # vertical spacing between alien rows in pixels
    X_OFFSET = 70  # left padding of the alien grid in pixels
    Y_OFFSET = 100  # top padding of the alien grid in pixels
    DESCEND_DISTANCE = 2  # pixels dropped when the wave touches a screen edge

    # Per-color point values; row 0 is yellow, rows 1-2 are green, rest are red.
    POINTS = {
        'yellow': 300,
        'green': 200,
        'red': 100,
    }

    LASER_INTERVAL_MS = 800  # alien laser timer period


# ---------------------------------------------------------------------------
# EXTRA (UFO)
# ---------------------------------------------------------------------------

class ExtraSettings:
    """Bonus UFO tuning."""

    SPEED = 3  # pixels per frame
    Y_POSITION = 80  # vertical pixel position the UFO streaks across at
    SPAWN_FRAMES_INITIAL = (40, 80)  # range used for first spawn timer
    SPAWN_FRAMES_NEXT = (400, 800)  # range used for subsequent spawns
    POINTS = 500


# ---------------------------------------------------------------------------
# LASERS
# ---------------------------------------------------------------------------

class LaserSettings:
    """Projectile dimensions and travel speeds."""

    WIDTH = 4
    HEIGHT = 20
    PLAYER_SPEED = -8  # negative = travels up the screen
    ALIEN_SPEED = 6  # positive = travels down the screen
    OFFSCREEN_MARGIN = 50  # pixels past the screen edge before a laser kills itself


# ---------------------------------------------------------------------------
# OBSTACLES
# ---------------------------------------------------------------------------

class ObstacleSettings:
    """Destructible bunker layout. Each ``x`` becomes a single colored block."""

    BLOCK_SIZE = 6  # pixel size of one bunker brick
    AMOUNT = 4  # number of bunkers evenly spaced along the bottom
    Y_START = 480  # top pixel row of every bunker
    X_START_DIVISOR = 15  # WIDTH / DIVISOR sets the per-bunker left padding

    SHAPE = [
        '  xxxxxxx',
        ' xxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxx     xxx',
        'xx       xx',
    ]


# ---------------------------------------------------------------------------
# AUDIO
# ---------------------------------------------------------------------------

class AudioSettings:
    """Volume levels and looping behavior for music + sound effects."""

    MUSIC_VOLUME = 0.2
    LASER_VOLUME = 0.5
    EXPLOSION_VOLUME = 0.3
    MUSIC_LOOPS = -1  # pygame.mixer flag for infinite looping


# ---------------------------------------------------------------------------
# FONT / HUD
# ---------------------------------------------------------------------------

class FontSettings:
    """Pixel font sizing for HUD text and the pause overlay."""

    SCORE_SIZE = 20
    PAUSE_SIZE = 20
    SCORE_TOPLEFT = (10, -10)  # negative y nudge keeps the cap-height aligned
    LIVES_TOP_MARGIN = 8  # vertical pixel offset of life icons
    LIVES_SPACING = 10  # horizontal pixels between two life icons
    LIVES_RIGHT_PADDING = 20  # pixels of right padding before the first life icon


# ---------------------------------------------------------------------------
# ASSET PATHS
# ---------------------------------------------------------------------------

class AssetPaths:
    """Filesystem locations for every bundled image, font, and sound."""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')
    FONT_DIR = os.path.join(ASSETS_DIR, 'font')
    GRAPHICS_DIR = os.path.join(ASSETS_DIR, 'graphics')

    # Graphics
    PLAYER = os.path.join(GRAPHICS_DIR, 'player.png')
    EXTRA = os.path.join(GRAPHICS_DIR, 'extra.png')
    ALIEN_RED = os.path.join(GRAPHICS_DIR, 'red.png')
    ALIEN_GREEN = os.path.join(GRAPHICS_DIR, 'green.png')
    ALIEN_YELLOW = os.path.join(GRAPHICS_DIR, 'yellow.png')
    TV = os.path.join(GRAPHICS_DIR, 'tv.png')

    # Font
    PIXEL_FONT = os.path.join(FONT_DIR, 'Pixeled.ttf')

    # Audio
    MUSIC = os.path.join(AUDIO_DIR, 'music.wav')
    LASER_SFX = os.path.join(AUDIO_DIR, 'laser.wav')
    EXPLOSION_SFX = os.path.join(AUDIO_DIR, 'explosion.wav')
    # Pause sounds are optional: callers must tolerate a missing file.
    PAUSE_IN_SFX = os.path.join(AUDIO_DIR, 'sfx_sounds_pause2_in.wav')
    PAUSE_OUT_SFX = os.path.join(AUDIO_DIR, 'sfx_sounds_pause2_out.wav')

    # Per-color alien lookup so sprite code can avoid manual string-joining.
    ALIENS_BY_COLOR = {
        'red': ALIEN_RED,
        'green': ALIEN_GREEN,
        'yellow': ALIEN_YELLOW,
    }
