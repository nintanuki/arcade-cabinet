"""Small on-screen debug text helper for Air Hockey."""

import pygame
from settings import *

pygame.init()
font = pygame.font.Font(None,30)

def debug(info,y = 10,x = SCREEN_WIDTH - 10):
    """Render debug text at the requested screen position.

    Args:
        info (object): Value to convert and display as debug text.
        y (int, optional): Top pixel coordinate for the label. Defaults to 10.
        x (int, optional): Right pixel coordinate for the label. Defaults to SCREEN_WIDTH - 10.

    Returns:
        None.
    """
    # TODO(refactor): Convert this module-level helper into a reusable DebugOverlay class.
    display_surf = pygame.display.get_surface()
    # TODO(bug): Guard against None when called before display initialization.
    debug_surf = font.render(str(info),True,'White')
    debug_rect = debug_surf.get_rect(topright = (x,y))
    pygame.draw.rect(display_surf,'Black',debug_rect)
    display_surf.blit(debug_surf,debug_rect)