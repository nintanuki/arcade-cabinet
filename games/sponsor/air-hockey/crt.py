"""CRT overlay effect helpers for Air Hockey rendering."""

from pathlib import Path

import pygame
from settings import *
import random


ASSET_DIR = Path(__file__).resolve().parent

class CRT:
    """Draw a scanline-and-flicker effect over the game surface."""

    def __init__(self,screen):
        """Load and scale the CRT overlay texture.

        Args:
            screen (pygame.Surface): The display surface to draw onto.

        Returns:
            None.
        """
        super().__init__()
        self.screen = screen
        self.tv = pygame.image.load(str(ASSET_DIR / 'graphics' / 'tv.png')).convert_alpha()
        self.tv = pygame.transform.scale(self.tv,(SCREEN_WIDTH,SCREEN_HEIGHT))

    def create_crt_lines(self):
        """Draw horizontal scanlines into the overlay image.

        Args:
            None.

        Returns:
            None.
        """
        # TODO(bug): Re-drawing lines every frame accumulates artifacts on self.tv.
        line_height = 3
        line_amount = int(SCREEN_HEIGHT / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv,'grey',(0,y_pos),(SCREEN_WIDTH,y_pos),1)

    def draw(self):
        """Apply random alpha flicker and blit the CRT overlay.

        Args:
            None.

        Returns:
            None.
        """
        self.tv.set_alpha(random.randint(75,90))
        self.create_crt_lines()
        self.screen.blit(self.tv,(0,0))