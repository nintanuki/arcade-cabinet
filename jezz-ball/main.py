"""Controller and mouse enabled Jezz Ball implementation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
import importlib.util
import math
from pathlib import Path
import random
import sys

import pygame

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


class Orientation(Enum):
    """Wall orientations supported by the placement cursor."""

    VERTICAL = auto()
    HORIZONTAL = auto()


@dataclass
class Ball:
    """Moving ball that bounces off the playfield edges and solid regions."""

    position: pygame.Vector2
    velocity: pygame.Vector2
    radius: int = GameplaySettings.BALL_RADIUS
    spin_phase: float = 0.0

    @property
    def rect(self) -> pygame.Rect:
        """Return the current collision rectangle for the ball."""
        return pygame.Rect(
            int(self.position.x - self.radius),
            int(self.position.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt: float, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> None:
        """Advance the ball and bounce it off bounds or solid geometry.

        Args:
            dt: Time elapsed since the previous frame in seconds.
            bounds: Outer playfield boundary the ball must remain inside.
            solid_rects: Completed walls and claimed regions that block movement.
        """
        self.position.x += self.velocity.x * dt
        self._resolve_axis_collision(bounds, solid_rects, axis="x")
        self.position.y += self.velocity.y * dt
        self._resolve_axis_collision(bounds, solid_rects, axis="y")
        speed_ratio = self.velocity.length() / max(1.0, GameplaySettings.BASE_BALL_SPEED)
        self.spin_phase = (self.spin_phase + (GameplaySettings.BALL_SPIN_RATE * speed_ratio * dt)) % (2 * math.pi)

    def _resolve_axis_collision(
        self,
        bounds: pygame.Rect,
        solid_rects: list[pygame.Rect],
        axis: str,
    ) -> None:
        """Resolve collisions for a single movement axis.

        Args:
            bounds: Outer playfield boundary the ball must remain inside.
            solid_rects: Solid obstacles that should reflect the ball.
            axis: Axis name, either ``"x"`` or ``"y"``.
        """
        if axis == "x":
            if self.position.x - self.radius < bounds.left:
                self.position.x = bounds.left + self.radius
                self.velocity.x *= -1
            elif self.position.x + self.radius > bounds.right:
                self.position.x = bounds.right - self.radius
                self.velocity.x *= -1
        else:
            if self.position.y - self.radius < bounds.top:
                self.position.y = bounds.top + self.radius
                self.velocity.y *= -1
            elif self.position.y + self.radius > bounds.bottom:
                self.position.y = bounds.bottom - self.radius
                self.velocity.y *= -1

        ball_rect = self.rect
        for solid in solid_rects:
            if not ball_rect.colliderect(solid):
                continue

            if axis == "x":
                if self.velocity.x > 0:
                    self.position.x = solid.left - self.radius
                else:
                    self.position.x = solid.right + self.radius
                self.velocity.x *= -1
            else:
                if self.velocity.y > 0:
                    self.position.y = solid.top - self.radius
                else:
                    self.position.y = solid.bottom + self.radius
                self.velocity.y *= -1

            break

    def draw(self, surface: pygame.Surface) -> None:
        """Render the ball onto the provided surface.

        Args:
            surface: Target surface that receives the ball sprite.
        """
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, ColorSettings.BALL, center, self.radius)

        wedge_points = [center]
        segments = 18
        for step in range(segments + 1):
            angle = self.spin_phase + (math.pi * (step / segments))
            wedge_points.append(
                (
                    int(self.position.x + math.cos(angle) * self.radius),
                    int(self.position.y + math.sin(angle) * self.radius),
                )
            )
        pygame.draw.polygon(surface, ColorSettings.BALL_WHITE, wedge_points)
        pygame.draw.circle(surface, ColorSettings.BALL_OUTLINE, center, self.radius, 1)


@dataclass
class BuildingWall:
    """Wall that grows outward in both directions until it hits a boundary."""

    origin: pygame.Vector2
    orientation: Orientation
    negative_length: float = 0.0
    positive_length: float = 0.0
    negative_done: bool = False
    positive_done: bool = False

    @property
    def complete(self) -> bool:
        """Return ``True`` when both directions have finished growing."""
        return self.negative_done and self.positive_done

    def update(self, dt: float, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> None:
        """Grow the wall toward both ends until each side reaches a stopper.

        Args:
            dt: Time elapsed since the previous frame in seconds.
            bounds: Outer playfield boundary that caps wall growth.
            solid_rects: Existing walls and claimed regions that stop growth.
        """
        growth = GameplaySettings.WALL_BUILD_SPEED * dt

        if not self.negative_done:
            self.negative_length += growth
            if self._reached_stop(-1, bounds, solid_rects):
                self.negative_done = True

        if not self.positive_done:
            self.positive_length += growth
            if self._reached_stop(1, bounds, solid_rects):
                self.positive_done = True

    def _reached_stop(self, direction: int, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> bool:
        """Return whether the current wall tip has hit a boundary or solid area.

        Args:
            direction: Growth direction, ``-1`` for negative and ``1`` for positive.
            bounds: Outer playfield boundary that caps wall growth.
            solid_rects: Existing walls and claimed regions that stop growth.
        """
        tip = self._tip(direction)
        probe = pygame.Rect(
            int(tip.x - GridSettings.WALL_THICKNESS // 2),
            int(tip.y - GridSettings.WALL_THICKNESS // 2),
            GridSettings.WALL_THICKNESS,
            GridSettings.WALL_THICKNESS,
        )

        if not bounds.contains(probe):
            return True

        return any(probe.colliderect(rect) for rect in solid_rects)

    def _tip(self, direction: int) -> pygame.Vector2:
        """Return the current tip position for one end of the wall.

        Args:
            direction: Growth direction, ``-1`` for negative and ``1`` for positive.
        """
        length = self.positive_length if direction > 0 else self.negative_length
        if self.orientation is Orientation.VERTICAL:
            return pygame.Vector2(self.origin.x, self.origin.y + (direction * length))
        return pygame.Vector2(self.origin.x + (direction * length), self.origin.y)

    def get_segments(self) -> list[pygame.Rect]:
        """Return the temporary wall segments used during growth and collision checks."""
        half = GridSettings.WALL_THICKNESS // 2
        thickness = GridSettings.WALL_THICKNESS

        if self.orientation is Orientation.VERTICAL:
            up = pygame.Rect(
                int(self.origin.x - half),
                int(self.origin.y - self.negative_length),
                thickness,
                int(self.negative_length),
            )
            down = pygame.Rect(
                int(self.origin.x - half),
                int(self.origin.y),
                thickness,
                int(self.positive_length),
            )
            return [up, down]

        left = pygame.Rect(
            int(self.origin.x - self.negative_length),
            int(self.origin.y - half),
            int(self.negative_length),
            thickness,
        )
        right = pygame.Rect(
            int(self.origin.x),
            int(self.origin.y - half),
            int(self.positive_length),
            thickness,
        )
        return [left, right]

    def collides_with_ball(self, ball: Ball) -> bool:
        """Return whether any in-progress segment intersects the given ball.

        Args:
            ball: Ball to test against the active wall segments.
        """
        return any(segment.colliderect(ball.rect) for segment in self.get_segments())

    def draw(self, surface: pygame.Surface) -> None:
        """Render the currently growing wall segments.

        Args:
            surface: Target surface that receives the wall preview.
        """
        segment_colors = (ColorSettings.WALL_GROW_NEGATIVE, ColorSettings.WALL_GROW_POSITIVE)
        for rect, color in zip(self.get_segments(), segment_colors, strict=False):
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(surface, color, rect)


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
        self._start_music()

    def _load_sounds(self) -> None:
        """Load all configured one-shot sound effects into memory."""
        sound_map = {
            "wall_start": AudioSettings.SFX_WALL_START,
            "wall_complete": AudioSettings.SFX_WALL_COMPLETE,
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
            pygame.mixer.music.load(str(AudioSettings.MUSIC_PATH))
            pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        except (FileNotFoundError, pygame.error):
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
        self.audio = AudioManager()
        self.crt = CRT(self.screen, CRTSettings.OVERLAY_IMAGE)

        self.running = True
        self.score = 0
        self.current_level_index = 0
        self.level_complete = False
        self.game_over = False
        self.game_paused = False
        self.controller_axis = pygame.Vector2()
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
        self.load_level(0)

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
        self.audio.play("wall_complete")
        if self.lives_left <= 0:
            self.game_over = True

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
            return

        self.load_level(self.current_level_index + 1)

    def _restart_game(self) -> None:
        """Reset score and return the run to level one."""
        self.score = 0
        self.load_level(0)

    def _update_cursor_with_analog(self, dt: float) -> None:
        """Apply left-stick movement to the on-screen cursor.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
        if abs(self.controller_axis.x) < ControlSettings.ANALOG_DEADZONE:
            self.controller_axis.x = 0.0
        if abs(self.controller_axis.y) < ControlSettings.ANALOG_DEADZONE:
            self.controller_axis.y = 0.0

        if self.controller_axis.length_squared() == 0:
            return

        self.cursor_position.x += self.controller_axis.x * ControlSettings.CURSOR_SPEED * dt
        self.cursor_position.y += self.controller_axis.y * ControlSettings.CURSOR_SPEED * dt
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
            self.running = False
        elif event.key == pygame.K_F11:
            self._toggle_fullscreen()
        elif event.key == pygame.K_RETURN:
            if self.level_complete:
                self._advance_level()
            elif self.game_over:
                self._restart_game()
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
        elif event.button == ControlSettings.BUTTON_START:
            if self.level_complete:
                self._advance_level()
            elif self.game_over:
                self._restart_game()
            else:
                self._toggle_pause()
        elif event.button == ControlSettings.BUTTON_A:
            if self.game_over:
                self._restart_game()
            elif self.level_complete:
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self._handle_joystick_hotplug(event):
                continue

            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            elif event.type == pygame.MOUSEMOTION:
                self.cursor_position = pygame.Vector2(event.pos)
                self._snap_cursor_to_grid()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.cursor_position = pygame.Vector2(event.pos)
                self._snap_cursor_to_grid()
                self._handle_mouse_button(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_controller_button(event)
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == ControlSettings.AXIS_CURSOR_X:
                    self.controller_axis.x = event.value
                elif event.axis == ControlSettings.AXIS_CURSOR_Y:
                    self.controller_axis.y = event.value

    def _update(self, dt: float) -> None:
        """Advance the active simulation state for one frame.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
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
            f"AREA CLEARED {self.claimed_percent:.1f}% / {self.level.area_needed_percent}%",
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

    def _draw_overlay_message(self) -> None:
        """Render pause, level-clear, and game-over overlay text when needed."""
        if not (self.game_paused or self.level_complete or self.game_over):
            return

        overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)
        overlay.fill(ColorSettings.OVERLAY)
        self.screen.blit(overlay, (0, 0))

        if self.level_complete and self.current_level_index + 1 >= len(LEVELS):
            message = "YOU WIN"
            hint = "PRESS START OR A TO RESTART"
        elif self.level_complete:
            message = "LEVEL CLEAR"
            hint = "PRESS START OR A FOR NEXT LEVEL"
        elif self.game_over:
            message = "GAME OVER"
            hint = "PRESS R, START, OR A TO RESTART"
        else:
            message = "PAUSED"
            hint = "PRESS START OR ENTER TO RESUME"

        message_surface = self.large_font.render(message, False, ColorSettings.TEXT)
        hint_surface = self.small_font.render(hint, False, ColorSettings.TEXT)
        message_rect = message_surface.get_rect(center=PLAYFIELD.center)
        hint_rect = hint_surface.get_rect(center=(PLAYFIELD.centerx, PLAYFIELD.centery + 28))
        self.screen.blit(message_surface, message_rect)
        self.screen.blit(hint_surface, hint_rect)

    def _draw_frame(self) -> None:
        """Draw the full game frame and present it to the display."""
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
