"""CRT scanline + flicker overlay rendered on top of the game scene."""

import random

import pygame

from settings import AssetPaths, ScreenSettings


class CRT:
    """Composites a translucent TV image with scanlines onto the screen."""

    def __init__(self, screen):
        """Load and pre-scale the TV overlay to the playfield size.

        Args:
            screen (pygame.Surface): Active display surface drawn onto each frame.
        """
        self.screen = screen
        self.tv = pygame.image.load(AssetPaths.TV).convert_alpha()
        self.tv = pygame.transform.scale(self.tv, ScreenSettings.RESOLUTION)

    def create_crt_lines(self):
        """Stamp evenly-spaced horizontal scanlines onto the TV overlay."""
        line_height = ScreenSettings.CRT_SCANLINE_HEIGHT
        line_amount = int(ScreenSettings.HEIGHT / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, 'black', (0, y_pos), (ScreenSettings.WIDTH, y_pos), 1)

    def draw(self):
        """Blit the overlay with a random per-frame alpha to fake CRT flicker."""
        self.tv.set_alpha(random.randint(*ScreenSettings.CRT_ALPHA_RANGE))
        self.create_crt_lines()
        self.screen.blit(self.tv, (0, 0))
