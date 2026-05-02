"""Pazaak -- placeholder pygame window.

The full Pazaak rebuild lives on the wishlist; this scaffold exists so
the launcher can show it as a Tribute entry without crashing. Closing
the window (ESC, the launcher's quit chord, or the window's X button)
returns to the cabinet menu, matching every other game's exit contract.
"""

import sys

import pygame


SCREEN_SIZE = (1280, 720)
BACKGROUND_COLOR = (8, 12, 24)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (255, 230, 0)
FPS = 60
# L1, R1, SELECT, START -- the cabinet-wide return-to-launcher chord.
QUIT_COMBO_BUTTONS = (4, 5, 6, 7)


def _quit_combo_pressed() -> bool:
    """Return True if every button in the launcher's quit chord is held."""
    for index in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(index)
        try:
            if all(joystick.get_button(button) for button in QUIT_COMBO_BUTTONS):
                return True
        except pygame.error:
            continue
    return False


def main() -> None:
    """Show a placeholder window until ESC, the quit chord, or the close button."""
    pygame.init()
    pygame.joystick.init()

    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
    pygame.display.set_caption("Pazaak")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("Courier New", 64, bold=True)
    font_small = pygame.font.SysFont("Courier New", 24)

    title_surface = font_large.render("PAZAAK", False, ACCENT_COLOR)
    subtitle_surface = font_small.render(
        "UNDER CONSTRUCTION - PRESS ESC TO RETURN", False, TEXT_COLOR
    )

    title_rect = title_surface.get_rect(
        center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 32)
    )
    subtitle_rect = subtitle_surface.get_rect(
        center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 32)
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == pygame.JOYBUTTONDOWN and _quit_combo_pressed():
                running = False

        screen.fill(BACKGROUND_COLOR)
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
