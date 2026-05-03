import pygame
from settings import AssetPaths, TileSettings
from tile_maps import TILE_LEGEND

SHEET_COLS = 22
SHEET_TILE = 16   # native size of each tile in the sheet


def load_tiles(path: str) -> list[pygame.Surface]:
    """
    Slice every 16×16 cell from the terrain sheet and return a flat list,
    indexed left→right then top→bottom. Tiles are scaled up to TileSettings.SIZE
    so they match the rest of the game grid.
    """
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rows = sheet.get_height() // SHEET_TILE
    tiles = []
    for row in range(sheet_rows):
        for col in range(SHEET_COLS):
            raw = sheet.subsurface((col * SHEET_TILE, row * SHEET_TILE, SHEET_TILE, SHEET_TILE))
            scaled = pygame.transform.scale(raw, (TileSettings.SIZE, TileSettings.SIZE))
            tiles.append(scaled)
    return tiles


class RenderManager:
    def __init__(self, screen):
        self.screen = screen

        # Load every tile from the sheet once at startup
        all_tiles = load_tiles(AssetPaths.TILE_WALL)

        # Build a surface lookup keyed by map symbol using the legend.
        # Both solid and passable tiles get drawn — solid is only a collision concern.
        self.tile_surfaces = {
            symbol: all_tiles[data['index']]
            for symbol, data in TILE_LEGEND.items()
        }

    def draw_map(self, current_map, camera, surface):
        """Draw the tile map using the camera view. Draws to the given surface (camera or screen)."""
        view = camera.get_view_rect()
        for row_index, row in enumerate(current_map):
            for col_index, symbol in enumerate(row):
                tile = self.tile_surfaces.get(symbol)
                if tile:
                    x = col_index * TileSettings.SIZE - view.x
                    y = row_index * TileSettings.SIZE - view.y
                    if 0 <= x < view.width and 0 <= y < view.height:
                        surface.blit(tile, (x, y))