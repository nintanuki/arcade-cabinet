"""Playfield model.

Owns the 6 x (12 + 1) grid of blocks, the cursor anchor cell, the
upward scroll rate, and the match/clear/chain state machine.

Right now this is a scaffolding stub — methods are documented and
sketched out so future commits can fill them in without restructuring
the public surface area.
"""

from settings import BoardSettings, BlockSettings, CursorSettings


class Board:
    """The playfield grid plus the cursor that swaps adjacent cells."""

    def __init__(self) -> None:
        """Create an empty grid and place the cursor near the middle."""
        # Grid is indexed as grid[row][col]. Row 0 is the top of the
        # visible area; the bottom row (row TOTAL_ROWS - 1) is the
        # hidden buffer where the next rise stages.
        self.cols = BoardSettings.COLS
        self.rows = BoardSettings.TOTAL_ROWS
        self.grid: list[list[str | None]] = [
            [None for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        # Cursor anchor (left half of the 1x2 selection box). Default
        # near the middle of the visible area so a fresh run starts
        # with the cursor in a useful spot.
        self.cursor_row = BoardSettings.VISIBLE_ROWS // 2
        self.cursor_col = (self.cols // 2) - 1

        # Sub-pixel rise offset. Once non-zero, the visible stack is
        # drawn lifted by this many pixels; when it crosses BLOCK_SIZE
        # the buffer row is committed into the grid and the next buffer
        # row is generated.
        self.rise_offset_px: float = 0.0

    # -------------------------
    # CURSOR
    # -------------------------

    def move_cursor(self, drow: int, dcol: int) -> None:
        """Move the cursor anchor by the given row/col delta, clamped to bounds.

        Args:
            drow: -1 to move up, +1 to move down, 0 to leave row alone.
            dcol: -1 to move left, +1 to move right, 0 to leave col alone.
        """
        # The cursor anchor is the left cell of the selection box, so
        # the rightmost legal column is cols - WIDTH_IN_CELLS.
        max_col = self.cols - CursorSettings.WIDTH_IN_CELLS
        max_row = BoardSettings.VISIBLE_ROWS - 1
        new_row = max(0, min(max_row, self.cursor_row + drow))
        new_col = max(0, min(max_col, self.cursor_col + dcol))
        self.cursor_row = new_row
        self.cursor_col = new_col

    def swap_under_cursor(self) -> None:
        """Swap the two cells the cursor currently spans.

        Per Tetris Attack rules, swapping is always legal — empty cells
        can swap with filled ones, which is how the player drops a
        single block down a hole. Match resolution kicks in afterwards.
        """
        # TODO: animate the swap over BlockSettings.SWAP_DURATION_MS,
        # then run match detection + chain resolution. Stub for now.
        pass

    # -------------------------
    # SIMULATION TICK
    # -------------------------

    def tick(self, delta_time: float) -> None:
        """Advance the board state by ``delta_time`` seconds.

        Drives the constant upward scroll, swap animations, match
        flashes, falling-block physics after a clear, and chain
        detection. None of those subsystems exist yet — this is the
        single entry point future code can plug into.

        Args:
            delta_time: Seconds since the previous frame.
        """
        # TODO: rise the stack by RiseSettings.BASE_RISE_SPEED_PX_PER_SEC
        #       multiplied by the current difficulty multiplier.
        # TODO: tick swap, flash, pop, and fall animations.
        # TODO: resolve any matches that became valid this frame.
        _ = delta_time

    # -------------------------
    # MATCH RESOLUTION
    # -------------------------

    def find_matches(self) -> list[list[tuple[int, int]]]:
        """Return groups of (row, col) cells that form a 3+ same-color match.

        Stub returns an empty list. Real implementation will scan rows
        and columns, then merge overlapping runs into single match
        groups so a "T" shape pops as one combo rather than two.
        """
        # TODO: implement run detection + merge.
        return []

    def is_topped_out(self) -> bool:
        """Return True if any block has crossed the top of the visible area.

        Stub returns False so the run never auto-ends during scaffolding.
        """
        # TODO: check the top visible row for any non-None cell after
        # accounting for the in-flight rise offset.
        return False

    @property
    def block_size(self) -> int:
        """Convenience accessor for the configured block edge length."""
        return BoardSettings.BLOCK_SIZE
