"""Controller and mouse enabled Jezz Ball implementation."""

from __future__ import annotations

from collections import deque
from enum import Enum, auto
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

import pygame

from ball import Ball
from wall import BuildingWall, Orientation

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.py"
SETTINGS_SPEC = importlib.util.spec_from_file_location("jezz_ball_settings", SETTINGS_PATH)
if SETTINGS_SPEC is None or SETTINGS_SPEC.loader is None:
    raise ImportError(f"Unable to load Jezz Ball settings from {SETTINGS_PATH}")
JEZZ_SETTINGS = importlib.util.module_from_spec(SETTINGS_SPEC)
sys.modules[SETTINGS_SPEC.name] = JEZZ_SETTINGS
SETTINGS_SPEC.loader.exec_module(JEZZ_SETTINGS)

CRTSettings = JEZZ_SETTINGS.CRTSettings
ColorSettings = JEZZ_SETTINGS.ColorSettings
ControlSettings = JEZZ_SETTINGS.ControlSettings
FontSettings = JEZZ_SETTINGS.FontSettings
GameplaySettings = JEZZ_SETTINGS.GameplaySettings
GridSettings = JEZZ_SETTINGS.GridSettings
LEVELS = JEZZ_SETTINGS.LEVELS
LevelConfig = JEZZ_SETTINGS.LevelConfig
AudioSettings = JEZZ_SETTINGS.AudioSettings
ScreenSettings = JEZZ_SETTINGS.ScreenSettings


PLAYFIELD = pygame.Rect(
    ScreenSettings.PLAYFIELD_LEFT,
    ScreenSettings.PLAYFIELD_TOP,
    ScreenSettings.PLAYFIELD_WIDTH,
    ScreenSettings.PLAYFIELD_HEIGHT,
)


class GameState(Enum):
    """Top-level screens and flow states for the game."""

    TITLE = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    INITIALS = auto()
    LEADERBOARD = auto()


class CRT:
    """CRT overlay renderer that adds a flickering screen treatment."""

    def __init__(self, screen: pygame.Surface, overlay_path: Path) -> None:
        """Load the overlay texture and retain the target display surface.

        Args:
            screen: Display surface the CRT pass is composited onto.
            overlay_path: Path to the overlay image used as the CRT mask.
        """
        self.screen = screen
        try:
            self.base_overlay = pygame.image.load(str(overlay_path)).convert_alpha()
            self.base_overlay = pygame.transform.scale(self.base_overlay, ScreenSettings.RESOLUTION)
        except (FileNotFoundError, pygame.error):
            self.base_overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)

    def draw(self) -> None:
        """Blit a scanlined CRT overlay over the finished frame."""
        overlay = self.base_overlay.copy()
        overlay.set_alpha(random.randint(*CRTSettings.ALPHA_RANGE))
        for y_position in range(0, ScreenSettings.HEIGHT, CRTSettings.SCANLINE_HEIGHT):
            pygame.draw.line(
                overlay,
                ColorSettings.BLACK,
                (0, y_position),
                (ScreenSettings.WIDTH, y_position),
                1,
            )
        self.screen.blit(overlay, (0, 0))


class AudioManager:
    """Load and control Jezz Ball music and sound effects."""

    def __init__(self) -> None:
        """Initialize mixer state, load audio assets, and start background music."""
        self.enabled = False
        self.sfx: dict[str, pygame.mixer.Sound] = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False
            return

        self._load_sounds()
        # Music is started when gameplay begins, not at init

    def _load_sounds(self) -> None:
        """Load all configured one-shot sound effects into memory."""
        sound_map = {
            "wall_start": AudioSettings.SFX_WALL_START,
            "wall_complete": AudioSettings.SFX_WALL_COMPLETE,
            "ball_hit_cursor": AudioSettings.SFX_BALL_HIT_CURSOR,
            "level_clear": AudioSettings.SFX_LEVEL_CLEAR,
            "pause_in": AudioSettings.SFX_PAUSE_IN,
            "pause_out": AudioSettings.SFX_PAUSE_OUT,
        }

        for key, path in sound_map.items():
            try:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(AudioSettings.SFX_VOLUME)
                self.sfx[key] = sound
            except (FileNotFoundError, pygame.error):
                continue

    def _start_music(self) -> None:
        """Start looping background music if the configured file is available."""
        if not self.enabled:
            return

        try:
            music_volume = AudioSettings.MUSIC_BASE_VOLUME
            if AudioSettings.MUSIC_HALF_VOLUME_TOGGLE:
                music_volume *= 0.5
            pygame.mixer.music.load(str(AudioSettings.MUSIC_PATH))
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
        except (FileNotFoundError, pygame.error):
            pass

    def restart_music(self) -> None:
        """Restart background music from the beginning if audio is enabled."""
        if not self.enabled:
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

        self._start_music()

    def stop_music(self) -> None:
        """Stop background music without tearing down the mixer."""
        if not self.enabled:
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    def play(self, sound_key: str) -> None:
        """Play a named one-shot effect when audio is available.

        Args:
            sound_key: Dictionary key for the preloaded effect.
        """
        if not self.enabled:
            return

        sound = self.sfx.get(sound_key)
        if sound is not None:
            sound.play()

    def shutdown(self) -> None:
        """Stop all playback and close the mixer device."""
        if not self.enabled:
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

        try:
            pygame.mixer.quit()
        except pygame.error:
            pass


class GameManager:
    """Coordinate input, wall building, capture logic, and rendering."""

    def __init__(self, start_fullscreen: bool = False) -> None:
        """Initialize runtime systems and load the first Jezz Ball level.

        Args:
            start_fullscreen: Whether the game should toggle fullscreen on launch.
        """
        pygame.init()
        pygame.joystick.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
        pygame.display.set_caption(GameplaySettings.WINDOW_TITLE)
        if start_fullscreen:
            pygame.display.toggle_fullscreen()

        self.clock = pygame.time.Clock()
        self.joysticks: list[object] = []
        self.refresh_joysticks()
        self.hud_font = self._load_font(FontSettings.HUD_SIZE)
        self.small_font = self._load_font(FontSettings.SMALL_SIZE)
        self.large_font = self._load_font(FontSettings.LARGE_SIZE)
        self.title_font = self._load_font(FontSettings.TITLE_SIZE)
        self.audio = AudioManager()
        self.crt = CRT(self.screen, CRTSettings.OVERLAY_IMAGE)

        self.running = True
        self.game_state = GameState.TITLE
        self.qualifies_for_leaderboard = False
        self.score = 0
        self.score_file_path = Path(__file__).resolve().parent / "high_score.txt"
        self.save_data: dict[str, object] = {"high_score": 0, "leaderboard": []}
        self.entering_initials = False
        self.initials = "AAA"
        self.initials_index = 0
        self.final_score_processed = False
        self.pending_score: int | None = None
        self.current_level_index = 0
        self.level_complete = False
        self.game_over = False
        self.game_paused = False
        self.controller_axis = pygame.Vector2()
        self.using_joystick: bool = False
        self.input_options = ["MOUSE", "CONTROLLER"]
        self.input_selection_index = 0
        self.selected_input_mode = "mouse"
        self.cursor_position = pygame.Vector2(PLAYFIELD.center)
        self.orientation = Orientation.VERTICAL
        self.building_wall: BuildingWall | None = None
        self.wall_rects: list[pygame.Rect] = []
        self.claimed_rects: list[pygame.Rect] = []
        self.solid_rects: list[pygame.Rect] = []
        self.level: LevelConfig = LEVELS[0]
        self.lives_left = self.level.lives
        self.time_remaining_seconds: float | None = None
        self.claimed_percent = 0.0
        self.wall_cells: list[list[bool]] = []
        self.claimed_cells: list[list[bool]] = []
        self.balls: list[Ball] = []
        self._load_scores()
        self.load_level(0)

        # Title screen bouncing ball
        title_speed = GameplaySettings.BASE_BALL_SPEED
        title_angle = random.uniform(15.0, 75.0)  # avoid perfectly horizontal/vertical
        self.title_ball_pos = pygame.Vector2(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2)
        self.title_ball_vel = pygame.Vector2(title_speed, 0).rotate(title_angle)
        self.title_ball_spin: float = 0.0
        self.title_ball_radius = GameplaySettings.BALL_RADIUS

    def quit_combo_pressed(self) -> bool:
        """Return True if START + SELECT + L1 + R1 are all held on any connected controller."""
        required = ControlSettings.BUTTON_QUIT_COMBO
        for joystick in self.joysticks:
            try:
                if all(joystick.get_button(btn) for btn in required):
                    return True
            except pygame.error:
                continue
        return False

    def _load_scores(self) -> None:
        """Load high score and leaderboard data from the local save file."""
        try:
            loaded = json.loads(self.score_file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = {"high_score": 0, "leaderboard": []}

        high_score = int(loaded.get("high_score", 0))
        leaderboard = loaded.get("leaderboard", [])
        if not isinstance(leaderboard, list):
            leaderboard = []

        cleaned_entries: list[dict[str, int | str]] = []
        for entry in leaderboard:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "AAA")).upper()[:3]
            score = int(entry.get("score", 0))
            cleaned_entries.append({"name": name, "score": score})

        self.save_data = {"high_score": high_score, "leaderboard": cleaned_entries}
        self._sort_and_trim_leaderboard()

    def _save_scores(self) -> None:
        """Persist high score and leaderboard data to disk."""
        self._sort_and_trim_leaderboard()
        self.score_file_path.write_text(
            json.dumps(self.save_data, indent=2),
            encoding="utf-8",
        )

    def _sort_and_trim_leaderboard(self) -> None:
        """Sort leaderboard entries and keep only the top ten scores."""
        leaderboard = self.save_data.get("leaderboard", [])
        if not isinstance(leaderboard, list):
            leaderboard = []

        leaderboard = sorted(
            leaderboard,
            key=lambda entry: int(entry.get("score", 0)) if isinstance(entry, dict) else 0,
            reverse=True,
        )[:10]

        self.save_data["leaderboard"] = leaderboard
        self.save_data["high_score"] = int(leaderboard[0]["score"]) if leaderboard else 0

    def _qualifies_for_leaderboard(self, score: int) -> bool:
        """Return whether the supplied score qualifies for leaderboard entry.

        Args:
            score: Final run score to evaluate.
        """
        leaderboard = self.save_data.get("leaderboard", [])
        if not isinstance(leaderboard, list):
            return score > 0
        if len(leaderboard) < 10:
            return score > 0
        return score > int(leaderboard[-1].get("score", 0))

    def _start_initial_entry(self) -> None:
        """Enter initials-capture mode for a qualifying score."""
        self.entering_initials = True
        self.initials = "AAA"
        self.initials_index = 0
        self.pending_score = self.score

    def _submit_initials(self) -> None:
        """Submit entered initials and persist the new leaderboard entry."""
        leaderboard = self.save_data.get("leaderboard", [])
        if not isinstance(leaderboard, list):
            leaderboard = []

        score_value = self.pending_score if self.pending_score is not None else self.score
        new_entry = {"name": self.initials, "score": int(score_value)}

        # Check for duplicate initials — only replace if new score is better
        duplicate_index = next(
            (i for i, e in enumerate(leaderboard) if e.get("name") == self.initials),
            None,
        )
        if duplicate_index is not None:
            if new_entry["score"] > leaderboard[duplicate_index]["score"]:
                leaderboard[duplicate_index] = new_entry
            # else keep old score, don't add duplicate
        else:
            leaderboard.append(new_entry)

        self.save_data["leaderboard"] = leaderboard
        self._save_scores()

        self.entering_initials = False
        self.pending_score = None
        self.final_score_processed = True
        self.game_state = GameState.LEADERBOARD

    def _finalize_non_qualifying_score(self) -> None:
        """Finalize run end-state when no initials entry is required."""
        current_high = int(self.save_data.get("high_score", 0))
        if self.score > current_high:
            self.save_data["high_score"] = self.score
            self._save_scores()
        self.final_score_processed = True

    def _advance_initials_cursor(self, direction: int) -> None:
        """Move the active initials character index left or right.

        Args:
            direction: ``-1`` moves left and ``1`` moves right.
        """
        self.initials_index = (self.initials_index + direction) % len(self.initials)

    def _cycle_initials_character(self, direction: int) -> None:
        """Cycle the selected initials character through alphabetic letters.

        Args:
            direction: ``1`` advances forward and ``-1`` moves backward.
        """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        current_character = self.initials[self.initials_index]
        current_index = alphabet.index(current_character) if current_character in alphabet else 0
        next_index = (current_index + direction) % len(alphabet)
        letters = list(self.initials)
        letters[self.initials_index] = alphabet[next_index]
        self.initials = "".join(letters)

    def _update_game_over_flow(self) -> None:
        """Initialize score submission state after a run ends."""
        if not self.game_over or self.final_score_processed or self.entering_initials:
            return

        if self._qualifies_for_leaderboard(self.score):
            self._start_initial_entry()
            return

        self._finalize_non_qualifying_score()

    def _load_font(self, size: int) -> pygame.font.Font:
        """Load the pixel font and fall back to a default font if necessary.

        Args:
            size: Font size in pixels.

        Returns:
            A ready-to-use font object.
        """
        try:
            return pygame.font.Font(str(FontSettings.FILE), size)
        except (FileNotFoundError, OSError):
            return pygame.font.SysFont(None, size)

    def refresh_joysticks(self) -> None:
        """Rebuild the connected joystick list to support hot plugging."""
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            if not joystick.get_init():
                joystick.init()
            self.joysticks.append(joystick)

    def load_level(self, level_index: int) -> None:
        """Reset stage state using the provided level progression entry.

        Args:
            level_index: Zero-based index into the configured level table.
        """
        self.current_level_index = level_index
        self.level = LEVELS[level_index]
        self.lives_left = self.level.lives
        self._reset_level_state()

    def _reset_level_state(self) -> None:
        """Clear walls and claimed space while preserving score and level number."""
        self.wall_cells = [
            [False for _ in range(GridSettings.GRID_COLUMNS)]
            for _ in range(GridSettings.GRID_ROWS)
        ]
        self.claimed_cells = [
            [False for _ in range(GridSettings.GRID_COLUMNS)]
            for _ in range(GridSettings.GRID_ROWS)
        ]
        self.building_wall = None
        self.orientation = Orientation.VERTICAL
        self.level_complete = False
        self.game_paused = False
        self.game_over = False
        self.final_score_processed = False
        self.entering_initials = False
        self.initials = "AAA"
        self.initials_index = 0
        self.pending_score = None
        self.time_remaining_seconds = (
            float(self.level.time_limit_seconds)
            if self.level.time_limit_seconds is not None
            else None
        )
        self.cursor_position = pygame.Vector2(PLAYFIELD.center)
        self._rebuild_solid_geometry()
        self.balls = [self._create_ball() for _ in range(self.level.ball_count)]
        self.claimed_percent = 0.0

    def _create_ball(self) -> Ball:
        """Create one ball positioned in an open cell with randomized travel direction.

        Returns:
            A new ball configured for the current level speed.
        """
        speed = GameplaySettings.BASE_BALL_SPEED * self.level.speed_multiplier
        while True:
            column = random.randint(4, GridSettings.GRID_COLUMNS - 5)
            row = random.randint(4, GridSettings.GRID_ROWS - 5)
            if self._is_cell_blocked(column, row):
                continue
            position = self._cell_center(column, row)
            angle = random.uniform(0.0, 360.0)
            velocity = pygame.Vector2(speed, 0).rotate(angle)
            return Ball(position=position, velocity=velocity)

    def _is_cell_blocked(self, column: int, row: int) -> bool:
        """Return whether a grid cell is occupied by a wall or claimed region.

        Args:
            column: Zero-based grid column.
            row: Zero-based grid row.

        Returns:
            ``True`` when the cell is not traversable.
        """
        if not (0 <= column < GridSettings.GRID_COLUMNS and 0 <= row < GridSettings.GRID_ROWS):
            return True
        return self.wall_cells[row][column] or self.claimed_cells[row][column]

    def _cell_center(self, column: int, row: int) -> pygame.Vector2:
        """Return the center point for a grid cell in playfield coordinates.

        Args:
            column: Zero-based grid column.
            row: Zero-based grid row.
        """
        return pygame.Vector2(
            PLAYFIELD.left + (column * GridSettings.CELL_SIZE) + (GridSettings.CELL_SIZE / 2),
            PLAYFIELD.top + (row * GridSettings.CELL_SIZE) + (GridSettings.CELL_SIZE / 2),
        )

    def _point_to_cell(self, point: pygame.Vector2) -> tuple[int, int]:
        """Convert a playfield point to the nearest valid grid cell.

        Args:
            point: Playfield-space point to convert.

        Returns:
            A ``(column, row)`` tuple clamped to the legal grid range.
        """
        column = int((point.x - PLAYFIELD.left) // GridSettings.CELL_SIZE)
        row = int((point.y - PLAYFIELD.top) // GridSettings.CELL_SIZE)
        column = max(0, min(GridSettings.GRID_COLUMNS - 1, column))
        row = max(0, min(GridSettings.GRID_ROWS - 1, row))
        return column, row

    def _snap_cursor_to_grid(self) -> None:
        """Clamp the cursor to the playfield and align it to the nearest cell center."""
        self.cursor_position.x = max(PLAYFIELD.left, min(PLAYFIELD.right - 1, self.cursor_position.x))
        self.cursor_position.y = max(PLAYFIELD.top, min(PLAYFIELD.bottom - 1, self.cursor_position.y))
        column, row = self._point_to_cell(self.cursor_position)
        self.cursor_position = self._cell_center(column, row)

    def _rects_from_grid(self, grid: list[list[bool]]) -> list[pygame.Rect]:
        """Merge occupied cells into row-span rectangles for rendering and collision.

        Args:
            grid: Boolean occupancy grid to convert into rectangles.

        Returns:
            List of rectangles covering all occupied cells.
        """
        rects: list[pygame.Rect] = []
        for row_index, row in enumerate(grid):
            start_column: int | None = None
            for column_index, is_filled in enumerate(row + [False]):
                if is_filled and start_column is None:
                    start_column = column_index
                elif not is_filled and start_column is not None:
                    rects.append(
                        pygame.Rect(
                            PLAYFIELD.left + (start_column * GridSettings.CELL_SIZE),
                            PLAYFIELD.top + (row_index * GridSettings.CELL_SIZE),
                            (column_index - start_column) * GridSettings.CELL_SIZE,
                            GridSettings.CELL_SIZE,
                        )
                    )
                    start_column = None
        return rects

    def _rebuild_solid_geometry(self) -> None:
        """Refresh cached wall, claimed, and combined solid rectangles from the grids."""
        combined_grid = [
            [
                self.wall_cells[row][column] or self.claimed_cells[row][column]
                for column in range(GridSettings.GRID_COLUMNS)
            ]
            for row in range(GridSettings.GRID_ROWS)
        ]
        self.wall_rects = self._rects_from_grid(self.wall_cells)
        self.claimed_rects = self._rects_from_grid(self.claimed_cells)
        self.solid_rects = self._rects_from_grid(combined_grid)

    def _mark_rect_on_grid(self, grid: list[list[bool]], rect: pygame.Rect) -> None:
        """Mark all grid cells touched by a rectangle as occupied.

        Args:
            grid: Occupancy grid to mutate.
            rect: Rectangle whose covered cells should be marked ``True``.
        """
        if rect.width <= 0 or rect.height <= 0:
            return

        left_column = max(0, (rect.left - PLAYFIELD.left) // GridSettings.CELL_SIZE)
        right_column = min(
            GridSettings.GRID_COLUMNS - 1,
            (rect.right - 1 - PLAYFIELD.left) // GridSettings.CELL_SIZE,
        )
        top_row = max(0, (rect.top - PLAYFIELD.top) // GridSettings.CELL_SIZE)
        bottom_row = min(
            GridSettings.GRID_ROWS - 1,
            (rect.bottom - 1 - PLAYFIELD.top) // GridSettings.CELL_SIZE,
        )

        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                grid[row][column] = True

    def _create_preview_rects(self) -> list[pygame.Rect]:
        """Return wall preview rectangles from the current cursor location.

        Returns:
            A list of one or two rectangles indicating the wall footprint.
        """
        if not PLAYFIELD.collidepoint(self.cursor_position):
            return []

        column, row = self._point_to_cell(self.cursor_position)
        if self._is_cell_blocked(column, row):
            return []

        if self.orientation is Orientation.VERTICAL:
            negative_cells = 0
            probe_row = row - 1
            while probe_row >= 0 and not self._is_cell_blocked(column, probe_row):
                negative_cells += 1
                probe_row -= 1

            positive_cells = 0
            probe_row = row + 1
            while probe_row < GridSettings.GRID_ROWS and not self._is_cell_blocked(column, probe_row):
                positive_cells += 1
                probe_row += 1

            x_pos = int(self._cell_center(column, row).x - (GridSettings.WALL_THICKNESS // 2))
            up_rect = pygame.Rect(
                x_pos,
                int(self._cell_center(column, row).y - (negative_cells * GridSettings.CELL_SIZE)),
                GridSettings.WALL_THICKNESS,
                negative_cells * GridSettings.CELL_SIZE,
            )
            down_rect = pygame.Rect(
                x_pos,
                int(self._cell_center(column, row).y),
                GridSettings.WALL_THICKNESS,
                positive_cells * GridSettings.CELL_SIZE,
            )
            return [rect for rect in (up_rect, down_rect) if rect.width > 0 and rect.height > 0]

        negative_cells = 0
        probe_column = column - 1
        while probe_column >= 0 and not self._is_cell_blocked(probe_column, row):
            negative_cells += 1
            probe_column -= 1

        positive_cells = 0
        probe_column = column + 1
        while probe_column < GridSettings.GRID_COLUMNS and not self._is_cell_blocked(probe_column, row):
            positive_cells += 1
            probe_column += 1

        y_pos = int(self._cell_center(column, row).y - (GridSettings.WALL_THICKNESS // 2))
        left_rect = pygame.Rect(
            int(self._cell_center(column, row).x - (negative_cells * GridSettings.CELL_SIZE)),
            y_pos,
            negative_cells * GridSettings.CELL_SIZE,
            GridSettings.WALL_THICKNESS,
        )
        right_rect = pygame.Rect(
            int(self._cell_center(column, row).x),
            y_pos,
            positive_cells * GridSettings.CELL_SIZE,
            GridSettings.WALL_THICKNESS,
        )
        return [rect for rect in (left_rect, right_rect) if rect.width > 0 and rect.height > 0]

    def _try_start_wall(self) -> None:
        """Begin building a wall from the current cursor position when placement is valid."""
        if self.game_over or self.level_complete or self.game_paused or self.building_wall is not None:
            return

        column, row = self._point_to_cell(self.cursor_position)
        if self._is_cell_blocked(column, row):
            return

        self.building_wall = BuildingWall(self._cell_center(column, row), self.orientation)
        self.audio.play("wall_start")

    def _toggle_orientation(self) -> None:
        """Flip the next wall placement between vertical and horizontal."""
        self.orientation = (
            Orientation.HORIZONTAL
            if self.orientation is Orientation.VERTICAL
            else Orientation.VERTICAL
        )

    def _toggle_pause(self) -> None:
        """Pause or resume gameplay while keeping the current level state intact."""
        if self.game_over or self.level_complete:
            return
        if self.game_paused:
            self.audio.play("pause_out")
        else:
            self.audio.play("pause_in")
        self.game_paused = not self.game_paused

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode for the current display surface."""
        pygame.display.toggle_fullscreen()

    def _lose_life(self) -> None:
        """Reduce the life counter and mark the game over state when it reaches zero."""
        self.building_wall = None
        self.lives_left -= 1
        self.audio.play("ball_hit_cursor")
        if self.lives_left <= 0:
            self.game_over = True
            self.game_state = GameState.GAME_OVER
            self.qualifies_for_leaderboard = self._qualifies_for_leaderboard(self.score)
            self.audio.stop_music()

    def _complete_wall(self) -> None:
        """Commit the finished wall, claim enclosed regions, and evaluate level completion."""
        if self.building_wall is None:
            return

        for rect in self.building_wall.get_segments():
            self._mark_rect_on_grid(self.wall_cells, rect.clip(PLAYFIELD))

        self.building_wall = None
        newly_claimed_cells = self._claim_enclosed_regions()
        self.score += newly_claimed_cells * GameplaySettings.POINTS_PER_CLAIMED_CELL
        self.audio.play("wall_complete")
        self._rebuild_solid_geometry()
        self.claimed_percent = self._calculate_claimed_percent()

        if self.claimed_percent >= self.level.area_needed_percent:
            self._complete_level()

    def _claim_enclosed_regions(self) -> int:
        """Flood fill from each ball and claim every unreachable open cell.

        Returns:
            Number of newly claimed cells added during this pass.
        """
        combined = [
            [
                self.wall_cells[row][column] or self.claimed_cells[row][column]
                for column in range(GridSettings.GRID_COLUMNS)
            ]
            for row in range(GridSettings.GRID_ROWS)
        ]
        visited = [
            [False for _ in range(GridSettings.GRID_COLUMNS)]
            for _ in range(GridSettings.GRID_ROWS)
        ]
        queue: deque[tuple[int, int]] = deque()

        for ball in self.balls:
            column, row = self._point_to_cell(ball.position)
            if combined[row][column] or visited[row][column]:
                continue
            queue.append((column, row))
            visited[row][column] = True

        while queue:
            column, row = queue.popleft()
            for delta_column, delta_row in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_column = column + delta_column
                next_row = row + delta_row
                if not (0 <= next_column < GridSettings.GRID_COLUMNS and 0 <= next_row < GridSettings.GRID_ROWS):
                    continue
                if combined[next_row][next_column] or visited[next_row][next_column]:
                    continue
                visited[next_row][next_column] = True
                queue.append((next_column, next_row))

        newly_claimed = 0
        for row in range(GridSettings.GRID_ROWS):
            for column in range(GridSettings.GRID_COLUMNS):
                if combined[row][column] or visited[row][column]:
                    continue
                self.claimed_cells[row][column] = True
                newly_claimed += 1

        return newly_claimed

    def _calculate_claimed_percent(self) -> float:
        """Return the percentage of the field that has been permanently claimed."""
        claimed_cells = sum(cell for row in self.claimed_cells for cell in row)
        total_cells = GridSettings.GRID_COLUMNS * GridSettings.GRID_ROWS
        return round((claimed_cells / total_cells) * 100.0, 1)

    def _complete_level(self) -> None:
        """Award the clear bonus and advance to the next level when possible."""
        self.level_complete = True
        self.score += GameplaySettings.LEVEL_CLEAR_BONUS
        self.audio.play("level_clear")
        if self.time_remaining_seconds is not None:
            self.score += int(self.time_remaining_seconds) * GameplaySettings.TIME_BONUS_PER_SECOND

    def _advance_level(self) -> None:
        """Move to the next configured level or stop on a final-game victory."""
        if self.current_level_index + 1 >= len(LEVELS):
            self.game_over = True
            self.game_state = GameState.GAME_OVER
            self.qualifies_for_leaderboard = self._qualifies_for_leaderboard(self.score)
            self.audio.stop_music()
            return

        self.load_level(self.current_level_index + 1)

    def _start_game(self) -> None:
        """Begin a fresh run from the title screen."""
        self.score = 0
        self.qualifies_for_leaderboard = False
        self.load_level(0)
        self.game_state = GameState.PLAYING
        # Music plays only during gameplay — kick it off here so the title
        # screen stays silent.
        self.audio.restart_music()

    def _cycle_input_mode(self, direction: int) -> None:
        """Move title-screen input mode selection by one slot."""
        self.input_selection_index = (self.input_selection_index + direction) % len(self.input_options)

    def _confirm_input_mode_and_start(self) -> None:
        """Apply selected input mode and start the game from title screen."""
        if self.input_options[self.input_selection_index] == "CONTROLLER":
            self.selected_input_mode = "controller"
            self.using_joystick = True
        else:
            self.selected_input_mode = "mouse"
            self.using_joystick = False
        self.controller_axis.update(0.0, 0.0)
        self._start_game()

    def _continue_from_game_over(self) -> None:
        """Advance from the game over screen to initials entry or the leaderboard."""
        if self.qualifies_for_leaderboard:
            self._start_initial_entry()
            self.game_state = GameState.INITIALS
        else:
            self._finalize_non_qualifying_score()
            self.game_state = GameState.LEADERBOARD

    def _restart_game(self) -> None:
        """Reset score and return the run to level one."""
        self.score = 0
        self.entering_initials = False
        self.initials = "AAA"
        self.initials_index = 0
        self.pending_score = None
        self.final_score_processed = False
        self.qualifies_for_leaderboard = False
        self.load_level(0)
        self.game_state = GameState.PLAYING
        self.audio.restart_music()

    def _update_cursor_with_analog(self, dt: float) -> None:
        """Apply left-stick movement to the on-screen cursor.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
        if self.selected_input_mode != "controller":
            self.using_joystick = False
            self.controller_axis.update(0.0, 0.0)
            return

        if self.joysticks:
            try:
                # Poll as a fallback for devices that don't reliably emit JOYAXISMOTION.
                self.controller_axis.x = self.joysticks[0].get_axis(ControlSettings.AXIS_CURSOR_X)
                self.controller_axis.y = self.joysticks[0].get_axis(ControlSettings.AXIS_CURSOR_Y)
            except pygame.error:
                pass

        ax = self.controller_axis.x if abs(self.controller_axis.x) >= ControlSettings.ANALOG_DEADZONE else 0.0
        ay = self.controller_axis.y if abs(self.controller_axis.y) >= ControlSettings.ANALOG_DEADZONE else 0.0
        if ax == 0.0 and ay == 0.0:
            self.using_joystick = False
            return
        self.using_joystick = True
        self.cursor_position.x += ax * ControlSettings.CURSOR_SPEED * dt
        self.cursor_position.y += ay * ControlSettings.CURSOR_SPEED * dt
        self._snap_cursor_to_grid()

    def _handle_time_limit(self, dt: float) -> None:
        """Tick down the level timer and penalize the player when it expires.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
        if self.time_remaining_seconds is None:
            return

        self.time_remaining_seconds = max(0.0, self.time_remaining_seconds - dt)
        if self.time_remaining_seconds > 0.0:
            return

        self._lose_life()
        if not self.game_over:
            self._reset_level_state()

    def _handle_joystick_hotplug(self, event: pygame.event.Event) -> bool:
        """Refresh the joystick cache when controllers are connected or removed.

        Args:
            event: Pygame event to inspect.

        Returns:
            ``True`` when the event was consumed.
        """
        if event.type not in {pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED}:
            return False
        self.refresh_joysticks()
        return True

    def _handle_keyboard(self, event: pygame.event.Event) -> None:
        """Process keyboard input for gameplay, pause, and fullscreen.

        Args:
            event: Key press event to interpret.
        """
        if event.key == pygame.K_ESCAPE:
            # ESC always exits the game and returns to the launcher, matching
            # the L1+R1+START+SELECT controller combo.
            self.running = False
            return
        if event.key == pygame.K_F11:
            # F11 toggles fullscreen from any screen so it parallels the
            # controller SELECT button which is also global.
            self._toggle_fullscreen()
            return
        if self.game_state == GameState.TITLE:
            if event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                self._cycle_input_mode(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s):
                self._cycle_input_mode(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._confirm_input_mode_and_start()
        elif self.game_state == GameState.GAME_OVER:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._continue_from_game_over()
        elif self.game_state == GameState.INITIALS:
            if event.key == pygame.K_LEFT:
                self._advance_initials_cursor(-1)
            elif event.key == pygame.K_RIGHT:
                self._advance_initials_cursor(1)
            elif event.key == pygame.K_UP:
                self._cycle_initials_character(1)
            elif event.key == pygame.K_DOWN:
                self._cycle_initials_character(-1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._submit_initials()
        elif self.game_state == GameState.LEADERBOARD:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
                self._restart_game()
        elif self.game_state == GameState.PLAYING:
            if event.key == pygame.K_F11:
                self._toggle_fullscreen()
            elif event.key == pygame.K_RETURN:
                if self.level_complete:
                    self._advance_level()
                else:
                    self._toggle_pause()
            elif event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_SPACE:
                self._toggle_orientation()

    def _handle_controller_button(self, event: pygame.event.Event) -> None:
        """Process controller buttons for wall building, pause, and fullscreen.

        Args:
            event: Controller button event to interpret.
        """
        if event.button == ControlSettings.BUTTON_SELECT:
            self._toggle_fullscreen()
        elif self.game_state == GameState.TITLE:
            if event.button in (ControlSettings.BUTTON_START, ControlSettings.BUTTON_A):
                self._confirm_input_mode_and_start()
            elif event.button == ControlSettings.BUTTON_X:
                self._cycle_input_mode(1)
        elif self.game_state == GameState.GAME_OVER:
            if event.button == ControlSettings.BUTTON_START:
                self._continue_from_game_over()
        elif self.game_state == GameState.INITIALS:
            if event.button in (ControlSettings.BUTTON_START, ControlSettings.BUTTON_A):
                self._submit_initials()
        elif self.game_state == GameState.LEADERBOARD:
            if event.button == ControlSettings.BUTTON_START:
                self._restart_game()
        elif self.game_state == GameState.PLAYING:
            if event.button == ControlSettings.BUTTON_START:
                if self.level_complete:
                    self._advance_level()
                else:
                    self._toggle_pause()
            elif event.button == ControlSettings.BUTTON_A:
                if self.level_complete:
                    self._advance_level()
                else:
                    self._try_start_wall()
            elif event.button == ControlSettings.BUTTON_X:
                self._toggle_orientation()

    def _handle_mouse_button(self, event: pygame.event.Event) -> None:
        """Process mouse clicks for wall placement and orientation changes.

        Args:
            event: Mouse button event to interpret.
        """
        if event.button == 1:
            self._try_start_wall()
        elif event.button == 3:
            self._toggle_orientation()

    def _process_events(self) -> None:
        """Poll and handle all pending Pygame events for one frame."""
        if self.quit_combo_pressed():
            self.close()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self._handle_joystick_hotplug(event):
                continue

            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_input_mode == "mouse" and not self.using_joystick:
                    self.cursor_position = pygame.Vector2(event.pos)
                    self._snap_cursor_to_grid()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.selected_input_mode == "mouse" and not self.using_joystick:
                    self.cursor_position = pygame.Vector2(event.pos)
                    self._snap_cursor_to_grid()
                if self.selected_input_mode == "mouse":
                    self._handle_mouse_button(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_controller_button(event)
            elif event.type == pygame.JOYAXISMOTION:
                if self.selected_input_mode == "controller" and self.game_state == GameState.PLAYING:
                    if event.axis == ControlSettings.AXIS_CURSOR_X:
                        self.controller_axis.x = event.value
                    elif event.axis == ControlSettings.AXIS_CURSOR_Y:
                        self.controller_axis.y = event.value
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if self.game_state == GameState.INITIALS:
                    if hat_x == -1:
                        self._advance_initials_cursor(-1)
                    elif hat_x == 1:
                        self._advance_initials_cursor(1)

                    if hat_y == 1:
                        self._cycle_initials_character(1)
                    elif hat_y == -1:
                        self._cycle_initials_character(-1)
                elif self.game_state == GameState.TITLE:
                    if hat_x == -1 or hat_y == 1:
                        self._cycle_input_mode(-1)
                    elif hat_x == 1 or hat_y == -1:
                        self._cycle_input_mode(1)

    def _update(self, dt: float) -> None:
        """Advance the active simulation state for one frame.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
        if self.game_state == GameState.TITLE:
            # Bounce the title ball around the full screen
            r = self.title_ball_radius
            self.title_ball_pos += self.title_ball_vel * dt
            if self.title_ball_pos.x - r < 0:
                self.title_ball_pos.x = r
                self.title_ball_vel.x *= -1
            elif self.title_ball_pos.x + r > ScreenSettings.WIDTH:
                self.title_ball_pos.x = ScreenSettings.WIDTH - r
                self.title_ball_vel.x *= -1
            if self.title_ball_pos.y - r < 0:
                self.title_ball_pos.y = r
                self.title_ball_vel.y *= -1
            elif self.title_ball_pos.y + r > ScreenSettings.HEIGHT:
                self.title_ball_pos.y = ScreenSettings.HEIGHT - r
                self.title_ball_vel.y *= -1
            speed_ratio = self.title_ball_vel.length() / max(1.0, GameplaySettings.BASE_BALL_SPEED)
            self.title_ball_spin = (self.title_ball_spin + GameplaySettings.BALL_SPIN_RATE * speed_ratio * dt) % (2 * math.pi)
            return

        if self.game_state != GameState.PLAYING:
            return

        self._update_cursor_with_analog(dt)

        if self.game_over or self.level_complete or self.game_paused:
            return

        for ball in self.balls:
            ball.update(dt, PLAYFIELD, self.solid_rects)

        if self.building_wall is not None:
            self.building_wall.update(dt, PLAYFIELD, self.solid_rects)
            if any(self.building_wall.collides_with_ball(ball) for ball in self.balls):
                self._lose_life()
            elif self.building_wall.complete:
                self._complete_wall()

        self._handle_time_limit(dt)

    def _draw_playfield(self) -> None:
        """Render the open field, claimed area, walls, building wall, and balls."""
        self.screen.fill(ColorSettings.BLACK)
        pygame.draw.rect(self.screen, ColorSettings.OPEN_FIELD, PLAYFIELD)

        for x_position in range(PLAYFIELD.left, PLAYFIELD.right + 1, GridSettings.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                ColorSettings.GRID_LINE,
                (x_position, PLAYFIELD.top),
                (x_position, PLAYFIELD.bottom),
                1,
            )
        for y_position in range(PLAYFIELD.top, PLAYFIELD.bottom + 1, GridSettings.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                ColorSettings.GRID_LINE,
                (PLAYFIELD.left, y_position),
                (PLAYFIELD.right, y_position),
                1,
            )

        for rect in self.claimed_rects:
            pygame.draw.rect(self.screen, ColorSettings.BLACK, rect)

        for rect in self.wall_rects:
            pygame.draw.rect(self.screen, ColorSettings.WALL, rect)

        if self.building_wall is not None:
            self.building_wall.draw(self.screen)

        for ball in self.balls:
            ball.draw(self.screen)

    def _draw_cursor(self) -> None:
        """Draw the placement preview line and cursor reticle."""
        preview_rects = self._create_preview_rects()
        for rect in preview_rects:
            pygame.draw.rect(self.screen, ColorSettings.CURSOR, rect, 1)

        center_x = int(self.cursor_position.x)
        center_y = int(self.cursor_position.y)
        arrow_half_length = 10
        arrow_head_size = 5

        if self.orientation is Orientation.VERTICAL:
            top_y = center_y - arrow_half_length
            bottom_y = center_y + arrow_half_length
            pygame.draw.line(
                self.screen,
                ColorSettings.BLACK,
                (center_x, top_y),
                (center_x, bottom_y),
                2,
            )
            pygame.draw.polygon(
                self.screen,
                ColorSettings.BLACK,
                [
                    (center_x, top_y - arrow_head_size),
                    (center_x - arrow_head_size, top_y + arrow_head_size),
                    (center_x + arrow_head_size, top_y + arrow_head_size),
                ],
            )
            pygame.draw.polygon(
                self.screen,
                ColorSettings.BLACK,
                [
                    (center_x, bottom_y + arrow_head_size),
                    (center_x - arrow_head_size, bottom_y - arrow_head_size),
                    (center_x + arrow_head_size, bottom_y - arrow_head_size),
                ],
            )
            return

        left_x = center_x - arrow_half_length
        right_x = center_x + arrow_half_length
        pygame.draw.line(
            self.screen,
            ColorSettings.BLACK,
            (left_x, center_y),
            (right_x, center_y),
            2,
        )
        pygame.draw.polygon(
            self.screen,
            ColorSettings.BLACK,
            [
                (left_x - arrow_head_size, center_y),
                (left_x + arrow_head_size, center_y - arrow_head_size),
                (left_x + arrow_head_size, center_y + arrow_head_size),
            ],
        )
        pygame.draw.polygon(
            self.screen,
            ColorSettings.BLACK,
            [
                (right_x + arrow_head_size, center_y),
                (right_x - arrow_head_size, center_y - arrow_head_size),
                (right_x - arrow_head_size, center_y + arrow_head_size),
            ],
        )

    def _draw_hud(self) -> None:
        """Render the score, lives, timer, and area-cleared readouts."""
        lives_text = self.hud_font.render(f"LIVES {self.lives_left}", False, ColorSettings.TEXT)
        score_text = self.hud_font.render(f"SCORE {self.score}", False, ColorSettings.TEXT)
        time_value = "--" if self.time_remaining_seconds is None else f"{int(self.time_remaining_seconds):03d}"
        time_text = self.hud_font.render(f"TIME {time_value}", False, ColorSettings.TEXT)
        area_text = self.hud_font.render(
            f"AREA CLEARED {self.claimed_percent:.1f} / {self.level.area_needed_percent}",
            False,
            ColorSettings.TEXT,
        )
        level_text = self.small_font.render(f"LEVEL {self.current_level_index + 1}", False, ColorSettings.TEXT)
        orientation_text = self.small_font.render(
            "VERT" if self.orientation is Orientation.VERTICAL else "HORIZ",
            False,
            ColorSettings.TEXT,
        )

        self.screen.blit(lives_text, (PLAYFIELD.left, ScreenSettings.HUD_TOP_Y))
        self.screen.blit(level_text, (PLAYFIELD.left, ScreenSettings.HUD_BOTTOM_Y))

        score_rect = score_text.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HUD_TOP_Y + 8))
        self.screen.blit(score_text, score_rect)

        time_rect = time_text.get_rect(topright=(PLAYFIELD.right, ScreenSettings.HUD_TOP_Y))
        self.screen.blit(time_text, time_rect)

        area_rect = area_text.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HUD_BOTTOM_Y + 4))
        self.screen.blit(area_text, area_rect)

        orientation_rect = orientation_text.get_rect(bottomright=(PLAYFIELD.right, ScreenSettings.HUD_BOTTOM_Y + 12))
        self.screen.blit(orientation_text, orientation_rect)

        # Joystick debug — remove once analog stick is confirmed working
        if self.joysticks:
            try:
                ax = self.joysticks[0].get_axis(0)
                ay = self.joysticks[0].get_axis(1)
                dbg = f"J {ax:.2f}/{ay:.2f} {'JOY' if self.using_joystick else 'MSE'}"
            except Exception:
                dbg = "J ERR"
        else:
            dbg = f"NO JOY (count={pygame.joystick.get_count()})"
        dbg_surf = self.hud_font.render(dbg, False, (255, 255, 0))
        self.screen.blit(dbg_surf, (PLAYFIELD.left, ScreenSettings.HUD_BOTTOM_Y + 12))

    def _draw_overlay_message(self) -> None:
        """Render pause and level-clear overlay text when needed."""
        if not (self.game_paused or self.level_complete):
            return

        overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)
        overlay.fill(ColorSettings.OVERLAY)
        self.screen.blit(overlay, (0, 0))

        if self.level_complete and self.current_level_index + 1 >= len(LEVELS):
            message = "YOU WIN"
            hint = "PRESS START TO CONTINUE"
        elif self.level_complete:
            message = "LEVEL CLEAR"
            hint = "PRESS START FOR NEXT LEVEL"
        else:
            message = "PAUSED"
            hint = "PRESS START OR ENTER TO RESUME"

        message_surface = self.large_font.render(message, False, ColorSettings.TEXT)
        hint_surface = self.small_font.render(hint, False, ColorSettings.TEXT)
        message_rect = message_surface.get_rect(center=PLAYFIELD.center)
        hint_rect = hint_surface.get_rect(center=(PLAYFIELD.centerx, PLAYFIELD.centery + 28))
        self.screen.blit(message_surface, message_rect)
        self.screen.blit(hint_surface, hint_rect)

    def _draw_title_screen(self) -> None:
        """Render the title screen with game name and input selection."""
        self.screen.fill(ColorSettings.BLACK)
        cx = ScreenSettings.WIDTH // 2
        cy = ScreenSettings.HEIGHT // 2

        # Bouncing ball
        r = self.title_ball_radius
        center = (int(self.title_ball_pos.x), int(self.title_ball_pos.y))
        pygame.draw.circle(self.screen, ColorSettings.BALL, center, r)
        wedge_points = [center]
        segments = 18
        for step in range(segments + 1):
            angle = self.title_ball_spin + (math.pi * (step / segments))
            wedge_points.append((
                int(self.title_ball_pos.x + math.cos(angle) * r),
                int(self.title_ball_pos.y + math.sin(angle) * r),
            ))
        pygame.draw.polygon(self.screen, ColorSettings.BALL_WHITE, wedge_points)
        pygame.draw.circle(self.screen, ColorSettings.BALL_OUTLINE, center, r, 1)

        title_surface = self.title_font.render("JEZZ BALL", False, ColorSettings.TEXT)
        title_rect = title_surface.get_rect(center=(cx, cy - 44))
        self.screen.blit(title_surface, title_rect)

        mouse_color = (255, 255, 0) if self.input_selection_index == 0 else ColorSettings.TEXT
        controller_color = (255, 255, 0) if self.input_selection_index == 1 else ColorSettings.TEXT
        mouse_surface = self.small_font.render(
            ("> " if self.input_selection_index == 0 else "  ") + "MOUSE",
            False,
            mouse_color,
        )
        controller_surface = self.small_font.render(
            ("> " if self.input_selection_index == 1 else "  ") + "CONTROLLER",
            False,
            controller_color,
        )
        self.screen.blit(mouse_surface, mouse_surface.get_rect(center=(cx, cy + 10)))
        self.screen.blit(controller_surface, controller_surface.get_rect(center=(cx, cy + 30)))

        prompt_surface = self.small_font.render("PRESS START/ENTER TO PLAY", False, ColorSettings.TEXT_PROMPT)
        prompt_rect = prompt_surface.get_rect(center=(cx, cy + 60))
        self.screen.blit(prompt_surface, prompt_rect)

    def _draw_game_over_screen(self) -> None:
        """Render the game over screen as a dim overlay over the last frame."""
        overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)
        overlay.fill(ColorSettings.OVERLAY)
        self.screen.blit(overlay, (0, 0))

        cx = ScreenSettings.WIDTH // 2
        cy = ScreenSettings.HEIGHT // 2

        won = self.current_level_index + 1 >= len(LEVELS) and self.level_complete
        message = "YOU WIN" if won else "GAME OVER"
        msg_surface = self.large_font.render(message, False, ColorSettings.TEXT)
        msg_rect = msg_surface.get_rect(center=(cx, cy - 40))
        self.screen.blit(msg_surface, msg_rect)

        score_surface = self.hud_font.render(f"SCORE  {self.score}", False, ColorSettings.TEXT)
        score_rect = score_surface.get_rect(center=(cx, cy))
        self.screen.blit(score_surface, score_rect)

        prompt_surface = self.small_font.render("PRESS START TO CONTINUE", False, ColorSettings.TEXT)
        prompt_rect = prompt_surface.get_rect(center=(cx, cy + 30))
        self.screen.blit(prompt_surface, prompt_rect)

    def _draw_initials_screen(self) -> None:
        """Render the initials entry screen for a qualifying high score."""
        overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)
        overlay.fill(ColorSettings.OVERLAY)
        self.screen.blit(overlay, (0, 0))

        cx = ScreenSettings.WIDTH // 2
        cy = ScreenSettings.HEIGHT // 2

        header_surface = self.large_font.render("NEW HIGH SCORE", False, ColorSettings.TEXT)
        header_rect = header_surface.get_rect(center=(cx, cy - 70))
        self.screen.blit(header_surface, header_rect)

        score_surface = self.hud_font.render(f"SCORE  {self.score}", False, ColorSettings.TEXT)
        score_rect = score_surface.get_rect(center=(cx, cy - 28))
        self.screen.blit(score_surface, score_rect)

        prompt_surface = self.small_font.render("ENTER YOUR INITIALS", False, ColorSettings.TEXT)
        prompt_rect = prompt_surface.get_rect(center=(cx, cy + 8))
        self.screen.blit(prompt_surface, prompt_rect)

        initials_surface = self.large_font.render(self.initials, False, ColorSettings.TEXT)
        initials_rect = initials_surface.get_rect(center=(cx, cy + 50))
        self.screen.blit(initials_surface, initials_rect)

        cursor_x_offset = (self.initials_index - 1) * 24
        caret_surface = self.small_font.render("^", False, ColorSettings.TEXT)
        caret_rect = caret_surface.get_rect(center=(cx + cursor_x_offset, cy + 76))
        self.screen.blit(caret_surface, caret_rect)

        hint_surface = self.small_font.render("DPAD/ARROWS TO CHANGE  START TO CONFIRM", False, ColorSettings.TEXT)
        hint_rect = hint_surface.get_rect(center=(cx, cy + 100))
        self.screen.blit(hint_surface, hint_rect)

    def _draw_leaderboard_screen(self) -> None:
        """Render the full leaderboard screen with top-ten entries."""
        self.screen.fill(ColorSettings.BLACK)
        cx = ScreenSettings.WIDTH // 2

        title_surface = self.large_font.render("LEADERBOARD", False, ColorSettings.TEXT)
        title_rect = title_surface.get_rect(center=(cx, 55))
        self.screen.blit(title_surface, title_rect)

        leaderboard = self.save_data.get("leaderboard", [])
        if isinstance(leaderboard, list):
            for index, entry in enumerate(leaderboard[:10], start=1):
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("name", "AAA"))
                score_value = int(entry.get("score", 0))
                row_surface = self.small_font.render(
                    f"{index:2}. {name}  {score_value}",
                    False,
                    ColorSettings.TEXT,
                )
                row_rect = row_surface.get_rect(center=(cx, 95 + (index - 1) * 18))
                self.screen.blit(row_surface, row_rect)

        prompt_surface = self.small_font.render("PRESS START TO PLAY AGAIN", False, ColorSettings.TEXT)
        prompt_rect = prompt_surface.get_rect(center=(cx, ScreenSettings.HEIGHT - 35))
        self.screen.blit(prompt_surface, prompt_rect)

    def _draw_frame(self) -> None:
        """Draw the full game frame and present it to the display."""
        if self.game_state == GameState.TITLE:
            self._draw_title_screen()
        elif self.game_state == GameState.GAME_OVER:
            self._draw_playfield()
            self._draw_hud()
            self._draw_game_over_screen()
        elif self.game_state == GameState.INITIALS:
            self._draw_playfield()
            self._draw_hud()
            self._draw_initials_screen()
        elif self.game_state == GameState.LEADERBOARD:
            self._draw_leaderboard_screen()
        else:
            self._draw_playfield()
            self._draw_cursor()
            self._draw_hud()
            self._draw_overlay_message()
        self.crt.draw()
        pygame.display.flip()

    def close(self) -> None:
        """Shut down Pygame and terminate the current process."""
        self.audio.shutdown()
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """Run the Jezz Ball main loop until the user exits."""
        while self.running:
            dt = self.clock.tick(ScreenSettings.FPS) / 1000.0
            self._process_events()
            self._update(dt)
            self._draw_frame()

        self.close()


if __name__ == "__main__":
    GameManager().run()
