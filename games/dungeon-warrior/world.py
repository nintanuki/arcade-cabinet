"""Active world state.

Owns which cell is currently loaded, exposes per-tile wall queries against
that cell, and handles cell-to-cell transitions when the player crosses
the action window edge. Doing this in one place keeps the renderer
(reads `current_grid`) and the player (calls `is_wall` and
`step_to_neighbor`) decoupled from how the cell layout is stored.

When more than one layer exists (overworld + dungeons + houses), this is
the natural place to grow a `current_layer` field plus an entrance-tile
table. For now we only have the overworld layer, so it stays implicit.
"""

from settings import UISettings
from tilemaps import CELLS, START_CELL_POS, WORLD_LAYOUT


class World:
    """Tracks the active cell and answers wall/transition questions about it."""

    WALL_CHAR = 'x'

    def __init__(self) -> None:
        """Initialize with the configured starting cell."""
        self.cells = CELLS
        self.layout = WORLD_LAYOUT
        self.current_pos = START_CELL_POS
        self._refresh_active_cell()

    # -------------------------
    # ACTIVE CELL
    # -------------------------

    def _refresh_active_cell(self) -> None:
        """Re-bind current_cell_name and current_grid from current_pos."""
        cell_name = self.layout[self.current_pos]
        self.current_cell_name = cell_name
        self.current_grid = self.cells[cell_name]

    # -------------------------
    # COLLISION QUERIES
    # -------------------------

    def is_wall(self, col: int, row: int) -> bool:
        """Return whether the given grid cell in the active cell is a wall.

        Out-of-bounds positions are treated as NOT walls so the player can
        keep moving past the action window edge; the cell-transition logic
        in DebugPlayer is what catches the crossing afterwards.
        """
        if not (0 <= row < UISettings.ROWS and 0 <= col < UISettings.COLS):
            return False
        return self.current_grid[row][col] == self.WALL_CHAR

    # -------------------------
    # CELL TRANSITIONS
    # -------------------------

    def step_to_neighbor(self, dx_cells: int, dy_cells: int) -> bool:
        """Try to swap to the neighbor cell at the given offset.

        Args:
            dx_cells: -1 west, +1 east, 0 no horizontal step.
            dy_cells: -1 north, +1 south, 0 no vertical step.

        Returns:
            True if a neighbor cell exists and the swap happened. False
            when the offset points off the world (caller should clamp the
            player back into the current cell in that case).
        """
        cx, cy = self.current_pos
        new_pos = (cx + dx_cells, cy + dy_cells)
        if new_pos in self.layout:
            self.current_pos = new_pos
            self._refresh_active_cell()
            return True
        return False
