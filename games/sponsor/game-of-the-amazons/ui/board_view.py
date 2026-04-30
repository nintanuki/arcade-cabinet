"""Renders the rounded board window and the 10x10 checkerboard tiles."""
import pygame
from settings import ColorSettings, GridSettings, UISettings, AssetPaths
from core.board import grid_to_pixel_topleft


class BoardView:
    """Draws the board window and the alternating-color tiles inside it."""

    def __init__(self, board):
        """Cache the logical board so draw() can read each tile's color.

        Args:
            board: A core.board.Board instance.
        """
        self.board = board

        self.pieces = {
            "white_queen": pygame.image.load(AssetPaths.WHITE_QUEEN).convert_alpha(),
            "black_queen": pygame.image.load(AssetPaths.BLACK_QUEEN).convert_alpha(),
        }

        # Scale both
        for key in self.pieces:
            self.pieces[key] = pygame.transform.scale(
                self.pieces[key], (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
            )

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

    def _draw_pieces(self, surface):
        for tile in self.board.all_tiles():
            if tile.piece in self.pieces:
                x, y = grid_to_pixel_topleft(tile.col, tile.row)
                surface.blit(self.pieces[tile.piece], (x, y))

    def _draw_cursor(self, surface, cursor_pos, selected_pos):
        # Draw moving cursor (white outline)
        cx, cy = grid_to_pixel_topleft(*cursor_pos)
        pygame.draw.rect(surface, ColorSettings.COLOR_WORDS["WHITE"], 
                         (cx, cy, GridSettings.TILE_SIZE, GridSettings.TILE_SIZE), 3)
        
        # Draw selection highlight (yellow outline) if something is picked up
        if selected_pos:
            sx, sy = grid_to_pixel_topleft(*selected_pos)
            pygame.draw.rect(surface, ColorSettings.COLOR_WORDS["YELLOW"], 
                             (sx, sy, GridSettings.TILE_SIZE, GridSettings.TILE_SIZE), 3)

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

    def draw(self, surface, cursor_pos, selected_pos):
        """Render the board window border and every tile.

        Tiles are drawn before the border so the rounded corners cleanly
        mask the tile rectangles at the four corners of the board.

        Args:
            surface: Target surface (typically the main screen).
            cursor_pos: (col, row) of the current cursor position.
            selected_pos: (col, row) of the currently selected tile, or None if no selection.
        """
        self._draw_tiles(surface)
        self._draw_pieces(surface)
        self._draw_cursor(surface, cursor_pos, selected_pos)
        self._draw_window_border(surface)