import pygame
from settings import ScreenSettings, TileSettings, CameraSettings

class Camera:
    def __init__(self, map_width, map_height):
        self.zoom_enabled = CameraSettings.ZOOM_ENABLED_DEFAULT
        self.zoom_factor = CameraSettings.ZOOM_FACTOR
        self.screen_width, self.screen_height = ScreenSettings.RESOLUTION
        self.map_width = map_width * TileSettings.SIZE
        self.map_height = map_height * TileSettings.SIZE
        self.x = 0
        self.y = 0

    def toggle_zoom(self):
        self.zoom_enabled = not self.zoom_enabled

    def get_view_rect(self):
        if self.zoom_enabled:
            w = int(self.screen_width // self.zoom_factor)
            h = int(self.screen_height // self.zoom_factor)
        else:
            w = self.screen_width
            h = self.screen_height
        # Clamp width/height so we never see outside the map
        w = min(w, self.map_width)
        h = min(h, self.map_height)
        return pygame.Rect(self.x, self.y, w, h)

    def update(self, target_rect):
        # Center camera on player
        if self.zoom_enabled:
            w = int(self.screen_width // self.zoom_factor)
            h = int(self.screen_height // self.zoom_factor)
        else:
            w = self.screen_width
            h = self.screen_height
        # Clamp width/height so we never see outside the map
        w = min(w, self.map_width)
        h = min(h, self.map_height)
        # Center on player
        new_x = int(target_rect.centerx - w // 2)
        new_y = int(target_rect.centery - h // 2)
        # Clamp to map (never show outside left, right, or bottom)
        new_x = max(0, min(new_x, self.map_width - w))
        new_y = max(0, min(new_y, self.map_height - h))
        self.x = new_x
        self.y = new_y
        self.view_w = w
        self.view_h = h