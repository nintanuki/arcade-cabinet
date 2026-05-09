"""Graphics helpers shared across scenes."""

from __future__ import annotations

import pygame


def build_gradient_surface(
    width: int,
    height: int,
    color_top: tuple[int, int, int],
    color_bottom: tuple[int, int, int],
) -> pygame.Surface:
    """Pre-render a vertical gradient surface for scene backgrounds.

    Args:
        width: Surface width in pixels.
        height: Surface height in pixels.
        color_top: RGB color at y=0 (top of screen).
        color_bottom: RGB color at y=height-1 (bottom of screen).

    Returns:
        pygame.Surface: The rendered gradient surface.
    """
    surface = pygame.Surface((width, height))
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width - 1, y))
    return surface
