"""Renders the rounded board window and the 10x10 checkerboard tiles."""
import pygame
from settings import ColorSettings, GridSettings, UISettings
from core.board import grid_to_pixel_topleft


class BoardView:
    """Draws the board window and the alternating-color tiles inside it."""

    def __init__(self, board):
        """Cache the logical board so draw() can read each tile's color.

        Args:
            board: A core.board.Board instance.
        """
        self.board = board

    def draw(self, surface):
        """Render the board window border and every tile.

        Tiles are drawn before the border so the rounded corners cleanly
        mask the tile rectangles at the four corners of the board.

        Args:
            surface: Target surface (typically the main screen).
        """
        self._draw_tiles(surface)
        self._draw_window_border(surface)

    def _draw_tiles(self, surface):
        """Fill each of the 100 tiles with its light or dark color."""
        for tile in self.board.all_tiles():
            x, y = grid_to_pixel_topleft(tile.col, tile.row)
            color = (
                ColorSettings.BOARD_LIGHT_TILE
                if tile.is_light
                else ColorSettings.BOARD_DARK_TILE
            )
            pygame.draw.rect(
                surface,
                color,
                (x, y, GridSettings.TILE_SIZE, GridSettings.TILE_SIZE),
            )

    def _draw_window_border(self, surface):
        """Draw the rounded-corner border around the board."""
        rect = pygame.Rect(
            UISettings.BOARD_WINDOW_X,
            UISettings.BOARD_WINDOW_Y,
            UISettings.BOARD_WINDOW_SIZE,
            UISettings.BOARD_WINDOW_SIZE,
        )
        pygame.draw.rect(
            surface,
            ColorSettings.BORDER_DEFAULT,
            rect,
            UISettings.BORDER_WIDTH,
            UISettings.BORDER_RADIUS,
        )
