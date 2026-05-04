"""CRT-style scanline overlay for the launcher."""

import random
from pathlib import Path

import pygame

from settings import ColorSettings, CRTSettings, ScreenSettings


class LauncherCRT:
    """Render a CRT-style overlay on top of the launcher scene."""

    def __init__(self, screen: pygame.Surface, tv_image_path: Path) -> None:
        """
        Initialize the CRT overlay texture and render target.

        Args:
            screen (pygame.Surface): The display surface to draw onto.
            tv_image_path (Path): Path to the TV bezel/overlay image.
        """
        self.screen = screen
        # Fall back to a transparent surface if the CRT texture is missing.
        try:
            self.base_tv = pygame.image.load(str(tv_image_path)).convert_alpha()
            self.base_tv = pygame.transform.scale(self.base_tv, ScreenSettings.RESOLUTION)
        except (FileNotFoundError, pygame.error):
            self.base_tv = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)

    def create_crt_lines(self, surf: pygame.Surface) -> None:
        """
        Draw horizontal scan lines onto a surface.

        Args:
            surf (pygame.Surface): The surface to draw lines onto.
        """
        for y_pos in range(0, ScreenSettings.HEIGHT, CRTSettings.SCANLINE_HEIGHT):
            pygame.draw.line(
                surf,
                ColorSettings.BLACK,
                (0, y_pos),
                (ScreenSettings.WIDTH, y_pos),
                1,
            )

    def draw(self) -> None:
        """Blit a flickering CRT overlay for retro visual treatment."""
        tv = self.base_tv.copy()
        tv.set_alpha(random.randint(*CRTSettings.ALPHA_RANGE))
        self.create_crt_lines(tv)
        self.screen.blit(tv, (0, 0))
