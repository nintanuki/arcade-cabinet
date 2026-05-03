"""CRT scan-line + flicker overlay.

Same approach as the other games in the cabinet: blit a TV-screen
texture on top of the frame, randomize its alpha each tick for a
flicker effect, and stripe horizontal scan lines across it. Falls back
to a transparent surface if the texture is missing so a brand-new
checkout still launches.
"""

import random

import pygame

from settings import AssetPaths, ColorSettings, ScreenSettings


class CRT:
    """Render a flickering CRT-style overlay on top of the active frame."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Pre-load and scale the CRT texture.

        Args:
            screen: The display surface the overlay will be drawn onto.
        """
        self.screen = screen
        try:
            self.tv = pygame.image.load(AssetPaths.TV).convert_alpha()
            self.tv = pygame.transform.scale(self.tv, ScreenSettings.RESOLUTION)
        except (FileNotFoundError, pygame.error):
            # Missing texture is non-fatal. Use a fully-transparent
            # placeholder so subsequent draws are no-ops.
            self.tv = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)

    def _draw_scanlines(self, surf: pygame.Surface) -> None:
        """Stripe horizontal scan lines across the supplied surface."""
        for y_pos in range(0, ScreenSettings.HEIGHT, ScreenSettings.CRT_SCANLINE_HEIGHT):
            pygame.draw.line(
                surf,
                ColorSettings.BLACK,
                (0, y_pos),
                (ScreenSettings.WIDTH, y_pos),
                1,
            )

    def draw(self) -> None:
        """Blit the flickering CRT overlay over the current frame."""
        tv = self.tv.copy()
        tv.set_alpha(random.randint(*ScreenSettings.CRT_ALPHA_RANGE))
        self._draw_scanlines(tv)
        self.screen.blit(tv, (0, 0))
