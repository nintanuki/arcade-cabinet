"""Configuration values for the Jezz Ball game."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


COLOR_PALETTE = {
	"black": (0, 0, 0),
	"open_field": (92, 92, 92),
	"grid_line": (255, 255, 255),
	"ball_red": (220, 40, 40),
	"ball_white": (245, 245, 245),
	"ball_outline": (120, 0, 0),
	"wall": (0, 0, 0),
	"wall_negative": (230, 65, 65),
	"wall_positive": (60, 130, 255),
	"cursor": (255, 255, 255),
	"text": (245, 245, 245),
	"text_prompt": (0, 230, 230),
	"warning": (255, 120, 120),
	"overlay": (0, 0, 0, 160),
}


class ScreenSettings:
	"""Display sizing and playfield layout for the Jezz Ball window."""

	WIDTH = 800
	HEIGHT = 600
	RESOLUTION = (WIDTH, HEIGHT)
	FPS = 60
	PLAYFIELD_LEFT = 40
	PLAYFIELD_TOP = 56
	PLAYFIELD_WIDTH = 720
	PLAYFIELD_HEIGHT = 496
	HUD_TOP_Y = 18
	HUD_BOTTOM_Y = 570


class ColorSettings:
	"""Color palette used throughout gameplay rendering."""

	BLACK = COLOR_PALETTE["black"]
	OPEN_FIELD = COLOR_PALETTE["open_field"]
	GRID_LINE = COLOR_PALETTE["grid_line"]
	BALL = COLOR_PALETTE["ball_red"]
	BALL_WHITE = COLOR_PALETTE["ball_white"]
	BALL_OUTLINE = COLOR_PALETTE["ball_outline"]
	WALL = COLOR_PALETTE["wall"]
	WALL_GROW_NEGATIVE = COLOR_PALETTE["wall_negative"]
	WALL_GROW_POSITIVE = COLOR_PALETTE["wall_positive"]
	CURSOR = COLOR_PALETTE["cursor"]
	TEXT = COLOR_PALETTE["text"]
	TEXT_PROMPT = COLOR_PALETTE["text_prompt"]
	WARNING = COLOR_PALETTE["warning"]
	OVERLAY = COLOR_PALETTE["overlay"]


class GridSettings:
	"""Grid sizing used for walls, capture logic, and background lines."""

	CELL_SIZE = 16
	WALL_THICKNESS = CELL_SIZE
	CURSOR_RADIUS = 5
	GRID_COLUMNS = ScreenSettings.PLAYFIELD_WIDTH // CELL_SIZE
	GRID_ROWS = ScreenSettings.PLAYFIELD_HEIGHT // CELL_SIZE


class ControlSettings:
	"""Controller mapping and analog cursor tuning."""

	BUTTON_A = 0
	BUTTON_X = 2
	BUTTON_SELECT = 6
	BUTTON_START = 7
	BUTTON_L1 = 4
	BUTTON_R1 = 5
	BUTTON_QUIT_COMBO = (7, 6, 4, 5)  # START + SELECT + L1 + R1
	AXIS_CURSOR_X = 0
	AXIS_CURSOR_Y = 1
	ANALOG_DEADZONE = 0.15
	CURSOR_SPEED = 360.0


class FontSettings:
	"""Font file paths and sizes for the HUD and overlays."""

	FILE = Path("font") / "Pixeled.ttf"
	HUD_SIZE = 11
	SMALL_SIZE = 9
	LARGE_SIZE = 18
	TITLE_SIZE = 36


class CRTSettings:
	"""CRT overlay asset and flicker tuning."""

	OVERLAY_IMAGE = Path("graphics") / "tv.png"
	SCANLINE_HEIGHT = 3
	ALPHA_RANGE = (68, 88)


class GameplaySettings:
	"""Core gameplay constants that are not tied to a single level."""

	WINDOW_TITLE = "Jezz Ball"
	BALL_RADIUS = 8
	BASE_BALL_SPEED = 170.0
	WALL_BUILD_SPEED = 280.0
	BALL_SPIN_RATE = 8.0
	BALL_SPIN_SPEED_MULTIPLIER = 1.5
	POINTS_PER_CLAIMED_CELL = 1
	LEVEL_CLEAR_BONUS = 500
	TIME_BONUS_PER_SECOND = 5


class AudioSettings:
	"""Global audio toggles, volumes, and the sound/music registry consumed by AudioManager."""

	_SOUND_DIR = Path("sound")
	_MUSIC_DIR = Path("music")

	# Standard template contract.
	MUTE = False
	MUTE_MUSIC = False
	# 0.6 base * 0.5 (the legacy MUSIC_HALF_VOLUME_TOGGLE) = 0.3.
	MUSIC_VOLUME = 0.3
	SFX_VOLUME = 0.0  # SFX volumes are intentionally muted; raise to re-enable.

	# Logical name -> filesystem path. Keys are what gameplay code
	# passes to ``AudioManager.play(name)``.
	SOUND_EFFECTS = {
		"wall_start":       _SOUND_DIR / "pong.ogg",
		"wall_complete":    _SOUND_DIR / "pong.ogg",
		"ball_hit_cursor":  _SOUND_DIR / "explosion.wav",
		"level_clear":      _SOUND_DIR / "score.ogg",
		"pause_in":         _SOUND_DIR / "sfx_sounds_pause2_in.wav",
		"pause_out":        _SOUND_DIR / "sfx_sounds_pause2_out.wav",
	}

	# Background tracks; one is chosen at random each time music starts.
	MUSIC_TRACKS = [
		_MUSIC_DIR / "pong_bg_music.ogg",
	]


@dataclass(frozen=True)
class LevelConfig:
	"""Level-specific progression values used when starting a stage."""

	area_needed_percent: int
	ball_count: int
	speed_multiplier: float
	lives: int
	time_limit_seconds: int | None


LEVELS: tuple[LevelConfig, ...] = (
	LevelConfig(area_needed_percent=70, ball_count=2, speed_multiplier=1.00, lives=3, time_limit_seconds=None),
	LevelConfig(area_needed_percent=72, ball_count=2, speed_multiplier=1.05, lives=3, time_limit_seconds=None),
	LevelConfig(area_needed_percent=74, ball_count=3, speed_multiplier=1.10, lives=3, time_limit_seconds=180),
	LevelConfig(area_needed_percent=75, ball_count=3, speed_multiplier=1.15, lives=3, time_limit_seconds=165),
	LevelConfig(area_needed_percent=76, ball_count=4, speed_multiplier=1.20, lives=3, time_limit_seconds=150),
	LevelConfig(area_needed_percent=77, ball_count=4, speed_multiplier=1.25, lives=3, time_limit_seconds=135),
	LevelConfig(area_needed_percent=78, ball_count=5, speed_multiplier=1.30, lives=3, time_limit_seconds=120),
	LevelConfig(area_needed_percent=79, ball_count=5, speed_multiplier=1.35, lives=3, time_limit_seconds=110),
	LevelConfig(area_needed_percent=80, ball_count=6, speed_multiplier=1.40, lives=3, time_limit_seconds=100),
	LevelConfig(area_needed_percent=80, ball_count=6, speed_multiplier=1.50, lives=2, time_limit_seconds=90),
)