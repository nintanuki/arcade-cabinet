"""Renders the rounded board window, the 10x10 checkerboard, and projectiles."""
import pygame
from settings import ColorSettings, GridSettings, UISettings, AssetPaths
from core.board import grid_to_pixel_topleft, PIECE_ARROW


# Arrow.png is a 2x2 grid of 32x32 frames. Frame indices map row-major so
# index 0 is the top-left pose and index 3 is the bottom-right pose.
ARROW_SHEET_COLS = 2
ARROW_SHEET_ROWS = 2
ARROW_FRAME_COUNT = ARROW_SHEET_COLS * ARROW_SHEET_ROWS


class BoardView:
    """Draws the board window, the alternating-color tiles, and game pieces."""

    def __init__(self, board):
        """Cache board state and pre-load every sprite this view will draw.

        Args:
            board: A core.board.Board instance.

        Returns:
            None.
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

        self.arrow_frames = self._load_arrow_frames()

    # -------------------------
    # SPRITE LOADING
    # -------------------------

    def _load_arrow_frames(self):
        """Slice the Arrow.png sheet into per-frame surfaces.

        Returns:
            A list of pygame.Surface frames in row-major order, with the
            sprite's south-pointing pose preserved (rotation happens later
            per shot in _draw_flying_arrow).
        """
        sheet = pygame.image.load(AssetPaths.ARROW_SHEET).convert_alpha()
        frame_size = sheet.get_width() // ARROW_SHEET_COLS
        frames = []
        for row in range(ARROW_SHEET_ROWS):
            for col in range(ARROW_SHEET_COLS):
                rect = pygame.Rect(
                    col * frame_size,
                    row * frame_size,
                    frame_size,
                    frame_size,
                )
                frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                if frame_size != GridSettings.TILE_SIZE:
                    frame = pygame.transform.scale(
                        frame,
                        (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE),
                    )
                frames.append(frame)
        return frames

    # -------------------------
    # DRAW HELPERS
    # -------------------------

    def _draw_tiles(self, surface):
        """Fill each of the 100 tiles with its light or dark color.

        Args:
            surface: Target pygame surface (typically the main screen).

        Returns:
            None.
        """
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
        """Blit queens and arrow markers for every occupied tile.

        Args:
            surface: Target pygame surface.

        Returns:
            None.
        """
        for tile in self.board.all_tiles():
            if tile.piece in self.pieces:
                x, y = grid_to_pixel_topleft(tile.col, tile.row)
                surface.blit(self.pieces[tile.piece], (x, y))
            elif tile.piece == PIECE_ARROW:
                self._draw_blocked_marker(surface, tile.col, tile.row)

    def _draw_blocked_marker(self, surface, col, row):
        """Draw the black "blocked" disc for a tile with a stuck arrow.

        Args:
            surface: Target pygame surface.
            col: Column of the blocked tile.
            row: Row of the blocked tile.

        Returns:
            None.
        """
        x, y = grid_to_pixel_topleft(col, row)
        center = (x + GridSettings.TILE_SIZE // 2, y + GridSettings.TILE_SIZE // 2)
        pygame.draw.circle(
            surface,
            ColorSettings.COLOR_WORDS["BLACK"],
            center,
            GridSettings.BLOCKED_RADIUS,
        )

    def _draw_cursor(self, surface, cursor_pos, selected_pos):
        """Outline the cursor tile and any selected origin tile.

        Args:
            surface: Target pygame surface.
            cursor_pos: (col, row) the player's cursor is currently on.
            selected_pos: (col, row) of the picked-up queen, or None.

        Returns:
            None.
        """
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
        """Draw the rounded-corner border around the board.

        Args:
            surface: Target pygame surface.

        Returns:
            None.
        """
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

    def _draw_flying_arrow(self, surface, arrow_data):
        """Draw the rotated arrow sprite at its current pixel position.

        Args:
            surface: Target pygame surface.
            arrow_data: Dict from ArrowAnimator.get_render_data() with
                'center_px', 'rotation', and 'frame_index'.

        Returns:
            None.
        """
        frame_index = arrow_data['frame_index'] % ARROW_FRAME_COUNT
        sprite = self.arrow_frames[frame_index]
        rotated = pygame.transform.rotate(sprite, arrow_data['rotation'])
        rect = rotated.get_rect(center=arrow_data['center_px'])
        surface.blit(rotated, rect.topleft)

    # -------------------------
    # PUBLIC ENTRY
    # -------------------------

    def draw(self, surface, cursor_pos, selected_pos, anim_data=None,
             arrow_data=None):
        """Render one full frame of the board onto the supplied surface.

        Args:
            surface: Target pygame surface.
            cursor_pos: (col, row) of the player's cursor.
            selected_pos: (col, row) of the picked-up queen, or None.
            anim_data: Optional (piece_type, [px, py]) tuple for a queen
                that is currently sliding.
            arrow_data: Optional dict for an in-flight arrow (see
                ArrowAnimator.get_render_data).

        Returns:
            None.
        """
        self._draw_tiles(surface)
        self._draw_pieces(surface)  # Draws pieces still on the board

        # Draw the 'ghost' piece mid-animation
        if anim_data:
            piece_type, pos_px = anim_data
            surface.blit(self.pieces[piece_type], pos_px)

        if arrow_data:
            self._draw_flying_arrow(surface, arrow_data)

        self._draw_cursor(surface, cursor_pos, selected_pos)
        self._draw_window_border(surface)
