"""Pixel-stepping animators that drive piece slides and arrow flights.

Each animator owns its own frame state so the renderer can ask 'where is the
mid-flight piece right now?' without the game logic having to know about
pixels. The game logic only deals with grid coords; pixel math lives here.
"""
from settings import GridSettings
from core.board import grid_to_pixel_topleft


# Counter-clockwise rotation, in degrees, that turns a south-facing sprite into
# the requested direction. Keys are the sign-normalised (delta_col, delta_row)
# direction the projectile is travelling. Row deltas are stored in board-space
# where +row points UP (north) on screen, matching grid_to_pixel_topleft's flip.
DIRECTION_ROTATION_DEGREES = {
    (0, -1): 0,    # south
    (-1, -1): 45,  # south-west
    (-1, 0): 90,   # west
    (-1, 1): 135,  # north-west
    (0, 1): 180,   # north
    (1, 1): 225,   # north-east
    (1, 0): 270,   # east
    (1, -1): 315,  # south-east
}


def _sign(value: int) -> int:
    """Return -1, 0, or +1 matching the sign of value.

    Args:
        value: Any integer.

    Returns:
        -1 if value is negative, 0 if zero, +1 if positive.
    """
    return (value > 0) - (value < 0)


class PieceAnimator:
    """Slides a single queen sprite from its old tile to its new tile."""

    def __init__(self):
        """Set up an idle animator with no piece in flight.

        Returns:
            None.
        """
        self.moving_piece = None  # Stores the current animation data
        self.is_animating = False

    def start(self, piece_type, start_grid, end_grid):
        """Begin sliding a piece from start_grid to end_grid.

        Args:
            piece_type: Piece label string (e.g. 'white_queen').
            start_grid: (col, row) the slide starts from.
            end_grid: (col, row) the slide ends at.

        Returns:
            None.
        """
        self.is_animating = True
        start_px = list(grid_to_pixel_topleft(*start_grid))
        end_px = grid_to_pixel_topleft(*end_grid)

        self.moving_piece = {
            'type': piece_type,
            'current_px': start_px,
            'target_px': end_px,
            'end_grid': end_grid
        }

    def get_render_data(self):
        """Expose mid-flight piece data so BoardView can draw a ghost sprite.

        Returns:
            (piece_type, [pixel_x, pixel_y]) when a piece is in flight,
            otherwise None.
        """
        if self.moving_piece:
            return self.moving_piece['type'], self.moving_piece['current_px']
        return None

    def update(self):
        """Advance the slide one frame and report whether it just finished.

        Returns:
            True on the frame the slide reached its target tile, else False.
        """
        if not self.moving_piece:
            return False  # Animation finished or not started

        curr = self.moving_piece['current_px']
        target = self.moving_piece['target_px']
        speed = GridSettings.ANIMATION_SPEED

        # Move X and Y incrementally toward target
        for i in range(2):
            if curr[i] < target[i]:
                curr[i] = min(curr[i] + speed, target[i])
            elif curr[i] > target[i]:
                curr[i] = max(curr[i] - speed, target[i])

        # Check if we arrived at the destination tile
        if curr[0] == target[0] and curr[1] == target[1]:
            self.is_animating = False
            return True  # Signal that we just finished

        return False


class ArrowAnimator:
    """Flies a rotated arrow sprite from the shooter to its landing tile."""

    def __init__(self):
        """Set up an idle arrow animator.

        Returns:
            None.
        """
        # flight is None when nothing is in the air, otherwise a dict with
        # current pixel position, target pixel position, the rotation angle
        # already chosen for the flight, and the landing tile in grid coords.
        self.flight = None
        self.is_animating = False
        self._frame_tick = 0
        self._frame_index = 0

    def start(self, start_grid, end_grid):
        """Launch an arrow from start_grid toward end_grid.

        Args:
            start_grid: (col, row) the arrow is fired from.
            end_grid: (col, row) the arrow will land on.

        Returns:
            None.
        """
        start_px = self._tile_center_pixel(start_grid)
        end_px = self._tile_center_pixel(end_grid)
        self.flight = {
            'current_px': list(start_px),
            'target_px': end_px,
            'end_grid': end_grid,
            'rotation': self._rotation_for_direction(start_grid, end_grid),
        }
        self.is_animating = True
        self._frame_tick = 0
        self._frame_index = 0

    def get_render_data(self):
        """Expose mid-flight arrow data so BoardView can draw the sprite.

        Returns:
            A dict with 'center_px', 'rotation', and 'frame_index' when an
            arrow is in flight, otherwise None.
        """
        if not self.flight:
            return None
        return {
            'center_px': tuple(self.flight['current_px']),
            'rotation': self.flight['rotation'],
            'frame_index': self._frame_index,
        }

    def landing_tile(self) -> tuple[int, int]:
        """Return the grid coords where the arrow is heading or has landed.

        Returns:
            (col, row) of the landing tile.
        """
        return self.flight['end_grid']

    def update(self):
        """Step the arrow toward its target one frame and cycle fletching.

        Returns:
            True on the frame the arrow reaches its destination, else False.
        """
        if not self.flight:
            return False

        self._advance_frame_index()

        curr = self.flight['current_px']
        target = self.flight['target_px']
        speed = GridSettings.ARROW_ANIMATION_SPEED
        for i in range(2):
            if curr[i] < target[i]:
                curr[i] = min(curr[i] + speed, target[i])
            elif curr[i] > target[i]:
                curr[i] = max(curr[i] - speed, target[i])

        if curr[0] == target[0] and curr[1] == target[1]:
            self.is_animating = False
            return True
        return False

    def clear(self) -> None:
        """Reset the animator after the renderer has consumed the landing.

        Returns:
            None.
        """
        self.flight = None
        self._frame_tick = 0
        self._frame_index = 0

    def _advance_frame_index(self) -> None:
        """Cycle to the next fletching frame after the configured hold time.

        Returns:
            None.
        """
        self._frame_tick += 1
        if self._frame_tick >= GridSettings.ARROW_FRAME_DURATION:
            self._frame_tick = 0
            self._frame_index = (self._frame_index + 1) % 4

    @staticmethod
    def _tile_center_pixel(grid_pos: tuple[int, int]) -> tuple[int, int]:
        """Return the pixel coords at the centre of the given tile.

        Args:
            grid_pos: (col, row) of the target tile.

        Returns:
            (x, y) pixel coords for the tile's centre point.
        """
        x, y = grid_to_pixel_topleft(*grid_pos)
        half = GridSettings.TILE_SIZE // 2
        return x + half, y + half

    @staticmethod
    def _rotation_for_direction(
        start_grid: tuple[int, int],
        end_grid: tuple[int, int],
    ) -> int:
        """Pick a rotation that aims the south-facing sprite at the target.

        Args:
            start_grid: (col, row) the arrow leaves from.
            end_grid: (col, row) the arrow flies to.

        Returns:
            Counter-clockwise rotation in degrees, suitable for
            pygame.transform.rotate.
        """
        delta_col = _sign(end_grid[0] - start_grid[0])
        delta_row = _sign(end_grid[1] - start_grid[1])
        # Same-tile shots should not happen, but fall back to "no rotation"
        # so we never KeyError mid-flight if the caller mis-routes input.
        return DIRECTION_ROTATION_DEGREES.get((delta_col, delta_row), 0)
