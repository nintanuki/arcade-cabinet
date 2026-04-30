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
from settings import GridSettings, UISettings


COLUMN_LETTERS = "abcdefghij"


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
        self.piece = None  # placeholder for queens / arrows later

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

    def move_piece(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        """
        Moves a piece from start (col, row) to end (col, row).
        
        Args:
            start_pos: A tuple (col, row) for the piece's current position.
            end_pos: A tuple (col, row) for the piece's new position.
        """
        start_tile = self.tile_at(*start_pos)
        end_tile = self.tile_at(*end_pos)
        
        end_tile.piece = start_tile.piece
        start_tile.piece = None