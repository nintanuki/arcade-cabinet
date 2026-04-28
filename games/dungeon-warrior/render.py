import pygame
import random
import colorsys
from settings import *
from render_utils import color_with_alpha
import coords

class RenderManager:
    """Draw gameplay, overlays, and menu/state-specific UI screens."""

    def __init__(self, game) -> None:
        """Capture render dependencies from the active game manager.

        Args:
            game: Active game manager containing sprites, state, and surfaces.
        """
        self.game = game
        self.screen = game.screen

        # World tile surfaces. Loaded once and cached at TILE_SIZE so
        # draw_world is a hot loop of plain blits.
        wall_surf = pygame.image.load(AssetPaths.WALL_TILE).convert_alpha()
        floor_surf = pygame.image.load(AssetPaths.FLOOR_TILE).convert_alpha()
        self.scaled_wall_tile = pygame.transform.scale(
            wall_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
        )
        self.scaled_floor_tile = pygame.transform.scale(
            floor_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
        )

        title_sprite_size = GridSettings.TILE_SIZE * 2

    # -------------------------
    # BORDER COLOR HELPERS
    # -------------------------

    def _rainbow_color(self) -> tuple[int, int, int]:
        """Return a slow-cycling rainbow RGB color."""
        hue = (pygame.time.get_ticks() * 0.00008) % 1.0
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
        return int(red * 255), int(green * 255), int(blue * 255)
    
    def _get_map_border_color(self) -> tuple[int, int, int]:
        """Return the minimap border color based on map ownership state.

        Returns:
            RGB color used for map window border.
        """
        # if self.game.map_memory.player_has_magic_map():
        #     return self._rainbow_color()
        # if self.game.map_memory.player_has_regular_map():
        #     return ColorSettings.BORDER_MAP_ACTIVE
        return ColorSettings.BORDER_DEFAULT

    def _get_inventory_border_color(self) -> tuple[int, int, int]:
        """Return the inventory border color based on key ownership.

        Returns:
            RGB color for inventory window border.
        """
        # if self.game.player.inventory.get("KEY", 0) > 0:
        #     return ColorSettings.BORDER_KEY_ACTIVE
        return ColorSettings.BORDER_DEFAULT

    def _get_message_border_color(self) -> tuple[int, int, int]:
        """Return the message-log border color from current game outcome/state.

        Returns:
            RGB color for message window border.
        """
        # if not self.game.game_active and self.game.game_result == "loss":
        #     return ColorSettings.BORDER_MESSAGE_FAILURE

        # if pygame.time.get_ticks() < self.game.message_success_border_until:
        #     return ColorSettings.BORDER_MESSAGE_SUCCESS

        return ColorSettings.BORDER_DEFAULT

    
    # -------------------------
    # WORLD RENDERING
    # -------------------------

    def draw_grid_background(self):
        pass

    def draw_world(self):
        """Blit the active cell's tile grid into the action window.

        Reads the active cell straight off game.world so the renderer has
        no opinion about which cell is loaded — it just paints whatever
        World currently exposes as current_grid.
        """
        grid = self.game.world.current_grid
        for row in range(UISettings.ROWS):
            row_cells = grid[row]
            for col in range(UISettings.COLS):
                x, y = coords.grid_to_screen(col, row)
                if row_cells[col] == 'x':
                    self.screen.blit(self.scaled_wall_tile, (x, y))
                else:
                    self.screen.blit(self.scaled_floor_tile, (x, y))

    def draw_cell_label(self):
        """Render the active cell's name at the top of the map window.

        Useful while testing cell transitions — flashes obvious feedback
        when the world swaps under your feet. The minimap itself will
        eventually live in this same window and replace this placeholder.
        """
        font = pygame.font.Font(FontSettings.FONT, FontSettings.HUD_SIZE)
        label = f"CELL: {self.game.world.current_cell_name}"
        surf = font.render(label, False, ColorSettings.TEXT_TITLE)
        rect = surf.get_rect(center=(
            UISettings.MAP_X + (UISettings.MAP_WIDTH // 2),
            UISettings.MAP_Y + 18,
        ))
        self.screen.blit(surf, rect)

    # -------------------------
    # HUD
    # -------------------------

    def draw_debug_ui_frames(self):
        """Draw plain borders + labels for the four UI windows.

        Lightweight stand-in for draw_ui_frames() while gameplay state
        (player, dungeon, score, in_shop_phase, ...) is still being wired up.
        Intentionally has zero dependencies on game state so it can run on a
        bare GameManager.
        """
        frames = (
            ("ACTION", pygame.Rect(
                UISettings.ACTION_WINDOW_X,
                UISettings.ACTION_WINDOW_Y,
                UISettings.ACTION_WINDOW_WIDTH,
                UISettings.ACTION_WINDOW_HEIGHT,
            )),
            ("INVENTORY", pygame.Rect(
                UISettings.SIDEBAR_X,
                UISettings.SIDEBAR_Y,
                UISettings.SIDEBAR_WIDTH,
                UISettings.SIDEBAR_HEIGHT,
            )),
            ("MESSAGE LOG", pygame.Rect(
                UISettings.LOG_X,
                UISettings.LOG_Y,
                UISettings.LOG_WIDTH,
                UISettings.LOG_HEIGHT,
            )),
            ("MAP", pygame.Rect(
                UISettings.MAP_X,
                UISettings.MAP_Y,
                UISettings.MAP_WIDTH,
                UISettings.MAP_HEIGHT,
            )),
        )

        label_font = pygame.font.Font(FontSettings.FONT, FontSettings.HUD_SIZE)

        for label, rect in frames:
            pygame.draw.rect(
                self.screen,
                ColorSettings.BORDER_DEFAULT,
                rect,
                2,
                UISettings.BORDER_RADIUS,
            )
            label_surf = label_font.render(label, False, ColorSettings.TEXT_DEFAULT)
            self.screen.blit(label_surf, (rect.x + 8, rect.y + 6))

    def draw_ui_frames(self):
        """Draw borders around all UI sections."""
        action_window_rect = pygame.Rect(
            UISettings.ACTION_WINDOW_X,
            UISettings.ACTION_WINDOW_Y,
            UISettings.ACTION_WINDOW_WIDTH,
            UISettings.ACTION_WINDOW_HEIGHT
        )
        sidebar_rect = pygame.Rect(
            UISettings.SIDEBAR_X,
            UISettings.SIDEBAR_Y,
            UISettings.SIDEBAR_WIDTH,
            UISettings.SIDEBAR_HEIGHT,
        )
        log_rect = pygame.Rect(
            UISettings.LOG_X,
            UISettings.LOG_Y,
            UISettings.LOG_WIDTH,
            UISettings.LOG_HEIGHT,
        )
        map_rect = pygame.Rect(
            UISettings.MAP_X,
            UISettings.MAP_Y,
            UISettings.MAP_WIDTH,
            UISettings.MAP_HEIGHT,
        )

        pygame.draw.rect(
            self.screen,
            self._get_inventory_border_color(),
            sidebar_rect,
            2,
            UISettings.BORDER_RADIUS,
        )
        pygame.draw.rect(
            self.screen,
            self._get_message_border_color(),
            log_rect,
            2,
            UISettings.BORDER_RADIUS,
        )
        pygame.draw.rect(
            self.screen,
            self._get_map_border_color(),
            map_rect,
            2,
            UISettings.BORDER_RADIUS,
        )

        border_color, border_alpha = self.game.player.get_action_window_border_style()
        if border_alpha >= 255:
            pygame.draw.rect(
                self.screen,
                border_color,
                action_window_rect,
                2,
                UISettings.BORDER_RADIUS
            )
        else:
            border_surface = pygame.Surface(
                (action_window_rect.width, action_window_rect.height),
                pygame.SRCALPHA
            )
            alpha_color = color_with_alpha(border_color, border_alpha)
            pygame.draw.rect(border_surface, alpha_color, border_surface.get_rect(), 2, UISettings.BORDER_RADIUS)
            self.screen.blit(border_surface, action_window_rect.topleft)

        score_font = pygame.font.Font(FontSettings.FONT, FontSettings.SCORE_SIZE)
        hud_font = pygame.font.Font(FontSettings.FONT, FontSettings.HUD_SIZE)

        score_surf = score_font.render(f"SCORE: {self.game.score}", False, ColorSettings.TEXT_DEFAULT)
        high_score_surf = hud_font.render(f"HIGH SCORE: {self.game.high_score}", False, ColorSettings.TEXT_DEFAULT)
        level_surf = hud_font.render(f"LEVEL {self.game.current_level_number}", False, ColorSettings.TEXT_DEFAULT)
        dungeon_name_surf = hud_font.render(self.game.dungeon.dungeon_name.upper(), False, ColorSettings.TEXT_DEFAULT)

        dungeon_name_rect = dungeon_name_surf.get_rect(center=(UISettings.MAP_X + (UISettings.MAP_WIDTH / 2), UISettings.DUNGEON_NAME_Y))

        self.screen.blit(high_score_surf, (UISettings.SCORE_X, UISettings.SCORE_Y))
        self.screen.blit(score_surf, (UISettings.CURRENT_SCORE_X, UISettings.CURRENT_SCORE_Y))
        self.screen.blit(level_surf, (UISettings.LEVEL_X, UISettings.LEVEL_Y))
        if not self.game.in_shop_phase:
            self.screen.blit(dungeon_name_surf, dungeon_name_rect)

        # Persistent green AUDIO MUTED indicator at the top-right of the
        # action window, opposite the HIGH SCORE label.
        if AudioSettings.MUTE:
            mute_surf = hud_font.render("AUDIO MUTED", False, ColorSettings.GREEN)
            mute_rect = mute_surf.get_rect(topright=(UISettings.MUTE_RIGHT_X, UISettings.MUTE_Y))
            self.screen.blit(mute_surf, mute_rect)
