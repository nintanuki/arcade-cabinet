"""Logical 10x10 board for Game of the Amazons.

Tile naming follows chess convention:
  - Columns are letters a-j (left to right).
  - Rows are numbers 1-10 (bottom to top).
  - 'a1' is the bottom-left tile, 'j10' is the top-right.

Internal grid coordinates use (col, row) zero-indexed so 'a1' is grid
(0, 0) and 'j10' is (9, 9). Pygame's screen y-axis grows downward, so
when converting to pixels we flip the row index.
"""
from __future__ import annotations
from typing import Optional
from settings import GridSettings, UISettings


COLUMN_LETTERS = "abcdefghij"

# All eight queen / arrow movement directions as (delta_col, delta_row).
# Centralised here because move scanning, AI lookup, and territory analysis all
# walk in the same eight directions; keeping one source avoids drift.
QUEEN_DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)


# Piece labels stored on Tile.piece. Centralised so callers don't sprinkle
# string literals that could silently typo (and keep working as "no piece").
PIECE_WHITE_QUEEN = "white_queen"
PIECE_BLACK_QUEEN = "black_queen"
PIECE_ARROW = "arrow"


def queen_color_of(piece: Optional[str]) -> Optional[str]:
    """Return 'WHITE' / 'BLACK' for a queen piece, else None.

    Args:
        piece: A Tile.piece string (or None).

    Returns:
        'WHITE' or 'BLACK' if piece is a queen of that color, otherwise None.
    """
    if piece == PIECE_WHITE_QUEEN:
        return "WHITE"
    if piece == PIECE_BLACK_QUEEN:
        return "BLACK"
    return None


def queen_piece_for(color: str) -> str:
    """Return the queen piece label for a player color string.

    Args:
        color: 'WHITE' or 'BLACK'.

    Returns:
        The corresponding piece label, e.g. 'white_queen'.
    """
    return PIECE_WHITE_QUEEN if color == "WHITE" else PIECE_BLACK_QUEEN


def tile_name_to_grid(name: str) -> tuple[int, int]:
    """Convert an 'a1' style tile name to (col, row) zero-indexed coords."""
    name = name.lower().strip()
    col = COLUMN_LETTERS.index(name[0])
    row = int(name[1:]) - 1
    return col, row


def grid_to_tile_name(col: int, row: int) -> str:
    """Convert (col, row) zero-indexed coords to an 'a1' style tile name."""
    return f"{COLUMN_LETTERS[col]}{row + 1}"


def grid_to_pixel_topleft(col: int, row: int) -> tuple[int, int]:
    """Top-left pixel of a tile given its (col, row) coords.

    Flips the row index because pygame's y-axis grows downward but in
    our naming row 1 is at the bottom of the screen.
    """
    pixel_row = (GridSettings.ROWS - 1) - row
    x = UISettings.BOARD_ORIGIN_X + col * GridSettings.TILE_SIZE
    y = UISettings.BOARD_ORIGIN_Y + pixel_row * GridSettings.TILE_SIZE
    return x, y


class Tile:
    """One square on the 10x10 board."""

    def __init__(self, col: int, row: int):
        self.col = col   # 0..9, columns a..j
        self.row = row   # 0..9, rows 1..10
        self.piece: Optional[str] = None  # placeholder for queens / arrows later

    @property
    def name(self) -> str:
        """Algebraic tile name like 'a1' or 'j10'."""
        return grid_to_tile_name(self.col, self.row)

    @property
    def is_light(self) -> bool:
        """Whether this tile takes the light color in the checkerboard.

        Uses chess convention: a1 (col=0, row=0) is dark. A tile is dark
        when (col + row) is even, light when odd.
        """
        return (self.col + self.row) % 2 == 1

    def __repr__(self) -> str:
        return f"Tile({self.name})"


class Board:
    """10x10 logical board with named tiles."""

    def __init__(self):
        self.cols = GridSettings.COLS
        self.rows = GridSettings.ROWS
        # tiles[col][row] so iteration mirrors the (col, row) coord order.
        self.tiles = [
            [Tile(col, row) for row in range(self.rows)]
            for col in range(self.cols)
        ]
        self.setup_amazons()

    def tile_at(self, col: int, row: int) -> Tile:
        """Look up a tile by zero-indexed (col, row) coords."""
        return self.tiles[col][row]

    def tile_by_name(self, name: str) -> Tile:
        """Look up a tile by its algebraic name like 'a1' or 'j10'."""
        col, row = tile_name_to_grid(name)
        return self.tile_at(col, row)

    def all_tiles(self):
        """Iterator over every tile on the board."""
        for col in range(self.cols):
            for row in range(self.rows):
                yield self.tiles[col][row]

    def setup_amazons(self):
        """Place the eight starting amazons in their canonical squares.

        Returns:
            None.
        """
        # White Queens
        self.tile_by_name("a4").piece = PIECE_WHITE_QUEEN
        self.tile_by_name("d1").piece = PIECE_WHITE_QUEEN
        self.tile_by_name("g1").piece = PIECE_WHITE_QUEEN
        self.tile_by_name("j4").piece = PIECE_WHITE_QUEEN

        # Black Queens
        self.tile_by_name("a7").piece = PIECE_BLACK_QUEEN
        self.tile_by_name("d10").piece = PIECE_BLACK_QUEEN
        self.tile_by_name("g10").piece = PIECE_BLACK_QUEEN
        self.tile_by_name("j7").piece = PIECE_BLACK_QUEEN

    def is_valid_path(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        """Checks if the path is a valid queen move and is unobstructed."""
        sc, sr = start_pos
        ec, er = end_pos

        if (sc, sr) == (ec, er): return False
        
        diff_c = ec - sc
        diff_r = er - sr
        
        # Must be horizontal, vertical, or diagonal
        if not (diff_c == 0 or diff_r == 0 or abs(diff_c) == abs(diff_r)):
            return False

        # Determine step direction (-1, 0, or 1)
        step_c = (diff_c // abs(diff_c)) if diff_c != 0 else 0
        step_r = (diff_r // abs(diff_r)) if diff_r != 0 else 0

        # Traverse the path to check for obstacles
        curr_c, curr_r = sc + step_c, sr + step_r
        while (curr_c, curr_r) != (ec, er):
            if self.tile_at(curr_c, curr_r).piece is not None:
                return False
            curr_c += step_c
            curr_r += step_r

        # Destination must also be empty
        return self.tile_at(ec, er).piece is None

    def move_piece(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        """Move a piece from start to end coords if the path is legal.

        Args:
            start_pos: A tuple (col, row) for the piece's current position.
            end_pos: A tuple (col, row) for the piece's new position.

        Returns:
            True if the move was applied, False if the path was illegal.
        """
        if self.is_valid_path(start_pos, end_pos):
            start_tile = self.tile_at(*start_pos)
            end_tile = self.tile_at(*end_pos)
            end_tile.piece = start_tile.piece
            start_tile.piece = None
            return True
        return False

    def place_arrow(self, pos: tuple[int, int]) -> None:
        """Stamp an arrow on the given tile, blocking it for the rest of the game.

        Args:
            pos: A (col, row) tuple identifying the tile to block.

        Returns:
            None.
        """
        # Arrows are stored as a piece value so is_valid_path's "any non-None
        # piece blocks the path" rule covers them automatically.
        self.tile_at(*pos).piece = PIECE_ARROW

    def queens_of(self, color: str) -> list[Tile]:
        """Return every tile currently holding a queen of the given color.

        Args:
            color: 'WHITE' or 'BLACK'.

        Returns:
            A list of Tile objects whose piece matches the requested color.
        """
        target = queen_piece_for(color)
        return [tile for tile in self.all_tiles() if tile.piece == target]

    def reachable_from(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        """List every tile a queen at start_pos could slide to in one move.

        Args:
            start_pos: A (col, row) tuple for the queen's current tile.

        Returns:
            A list of (col, row) destinations that are empty and reachable in
            a straight line without hitting another piece or arrow.
        """
        sc, sr = start_pos
        destinations: list[tuple[int, int]] = []
        for step_c, step_r in QUEEN_DIRECTIONS:
            curr_c, curr_r = sc + step_c, sr + step_r
            while 0 <= curr_c < self.cols and 0 <= curr_r < self.rows:
                if self.tile_at(curr_c, curr_r).piece is not None:
                    break
                destinations.append((curr_c, curr_r))
                curr_c += step_c
                curr_r += step_r
        return destinations

    def has_any_legal_move(self, color: str) -> bool:
        """Check whether the given color can play a full move-and-shoot turn.

        Args:
            color: 'WHITE' or 'BLACK'.

        Returns:
            True if at least one queen of that color has a destination from
            which it can also fire an arrow; False if the player is stuck.
        """
        for queen in self.queens_of(color):
            origin = (queen.col, queen.row)
            origin_tile = self.tile_at(*origin)
            piece_label = origin_tile.piece
            for destination in self.reachable_from(origin):
                # Simulate the queen actually moving so the shoot scan sees
                # the vacated origin square as legal arrow target / pass-through.
                origin_tile.piece = None
                dest_tile = self.tile_at(*destination)
                dest_tile.piece = piece_label
                shot_options = self.reachable_from(destination)
                dest_tile.piece = None
                origin_tile.piece = piece_label
                if shot_options:
                    return True
        return False

    def territory_counts(self) -> Optional[dict[str, int]]:
        """Score the board if every amazon is sealed off from the other color.

        Walks 8-connected components over non-arrow tiles. If any component
        contains queens of both colors, the position is still contested and
        we return None so the caller knows to keep playing. Otherwise we
        return the empty-tile count belonging to each color's territory.

        Returns:
            A dict {'WHITE': int, 'BLACK': int} of empty squares each color
            controls when fully separated, or None if any region is still
            shared by both colors.
        """
        visited = [[False] * self.rows for _ in range(self.cols)]
        components: list[tuple[set[str], int]] = []

        for start_col in range(self.cols):
            for start_row in range(self.rows):
                if visited[start_col][start_row]:
                    continue
                if self.tile_at(start_col, start_row).piece == PIECE_ARROW:
                    # Arrows act as walls; they do not belong to any component.
                    visited[start_col][start_row] = True
                    continue
                components.append(self._flood_component(start_col, start_row, visited))

        # Any component touching both colors means amazons can still interact,
        # so the territory rule has not yet kicked in.
        for colors, _ in components:
            if "WHITE" in colors and "BLACK" in colors:
                return None

        totals = {"WHITE": 0, "BLACK": 0}
        for colors, empty_squares in components:
            if len(colors) == 1:
                (only_color,) = colors
                totals[only_color] += empty_squares
        return totals

    def _flood_component(
        self,
        start_col: int,
        start_row: int,
        visited: list[list[bool]],
    ) -> tuple[set[str], int]:
        """Flood-fill one 8-connected non-arrow region starting at the given tile.

        Args:
            start_col: Column of the seed tile.
            start_row: Row of the seed tile.
            visited: 2D mutable grid of bools updated in place to mark explored
                tiles so the caller can skip them on later iterations.

        Returns:
            A tuple (colors_present, empty_count) describing which queen colors
            occupy the region and how many empty tiles it contains.
        """
        colors_present: set[str] = set()
        empty_count = 0
        stack = [(start_col, start_row)]
        while stack:
            col, row = stack.pop()
            if visited[col][row]:
                continue
            tile = self.tile_at(col, row)
            if tile.piece == PIECE_ARROW:
                # Don't cross arrow walls and don't mark them owned here.
                continue
            visited[col][row] = True
            color = queen_color_of(tile.piece)
            if color is not None:
                colors_present.add(color)
            elif tile.piece is None:
                empty_count += 1
            for step_c, step_r in QUEEN_DIRECTIONS:
                next_c, next_r = col + step_c, row + step_r
                if 0 <= next_c < self.cols and 0 <= next_r < self.rows:
                    if not visited[next_c][next_r]:
                        stack.append((next_c, next_r))
        return colors_present, empty_count