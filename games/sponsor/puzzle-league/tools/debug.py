"""Quick-and-dirty debug overlay.

Mirrors Star Hero's tools/debug.py so dropping a ``debug(value)`` call
into any module produces the expected on-screen readout.
"""

import pygame

from settings import ScreenSettings

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info, y: int = ScreenSettings.HEIGHT - 20, x: int = 10) -> None:
    """Render a debug string directly onto the active display surface.

    Args:
        info: Any value; converted to a string via ``str()`` before rendering.
        y: Vertical position of the debug text. Defaults to near the bottom.
        x: Horizontal position of the debug text. Defaults to 10.
    """
    display_surf = pygame.display.get_surface()
    if display_surf is None:
        return
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surf, 'Black', debug_rect)
    display_surf.blit(debug_surf, debug_rect)
