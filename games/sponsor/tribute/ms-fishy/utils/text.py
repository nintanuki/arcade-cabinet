"""Text rendering helpers for UI overlays and HUD widgets."""

import pygame


def draw_centered_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> pygame.Rect:
    """Render `text` with `font` and blit it centered at `center`.

    Returns the blitted rect (useful for stacking lines).
    """
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=center)
    return surface.blit(rendered_text, text_rect)
