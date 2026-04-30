"""Renders the side HUD window with turn/phase information."""
import pygame
from settings import ColorSettings, FontSettings, UISettings


class HUD:
    """Draws the rounded HUD window plus turn and phase status text."""

    def __init__(self):
        """Build fonts and seed placeholder state until game logic is wired up."""
        self.title_font = pygame.font.Font(None, FontSettings.HUD_TITLE_SIZE)
        self.label_font = pygame.font.Font(None, FontSettings.HUD_LABEL_SIZE)
        self.value_font = pygame.font.Font(None, FontSettings.HUD_VALUE_SIZE)

        # Placeholder state. The real game manager will overwrite these once
        # turn tracking exists.
        self.current_player = "WHITE"
        self.current_phase = "MOVE"

    def draw(self, surface):
        """Render the HUD window border and the status text inside it.

        Args:
            surface: Target surface (typically the main screen).
        """
        self._draw_window_border(surface)
        self._draw_text(surface)

    def _draw_window_border(self, surface):
        """Draw the rounded-corner border around the HUD area."""
        rect = pygame.Rect(
            UISettings.HUD_X,
            UISettings.HUD_Y,
            UISettings.HUD_WIDTH,
            UISettings.HUD_HEIGHT,
        )
        pygame.draw.rect(
            surface,
            ColorSettings.BORDER_DEFAULT,
            rect,
            UISettings.BORDER_WIDTH,
            UISettings.BORDER_RADIUS,
        )

    def _draw_text(self, surface):
        """Stack the title, turn label/value, and phase label/value vertically."""
        x = UISettings.HUD_X + UISettings.HUD_TEXT_PADDING
        y = UISettings.HUD_Y + UISettings.HUD_TEXT_PADDING

        # Title
        title_surf = self.title_font.render("AMAZONS", True, ColorSettings.TEXT_TITLE)
        surface.blit(title_surf, (x, y))
        y += title_surf.get_height() + 22

        # TURN: <player>
        y = self._draw_label_value(
            surface, x, y, "TURN", self.current_player
        )
        y += 14

        # PHASE: <move/shoot>
        self._draw_label_value(
            surface, x, y, "PHASE", self.current_phase
        )

    def _draw_label_value(self, surface, x: int, y: int, label: str, value: str) -> int:
        """Draw a small label above a larger value and return the new y cursor.

        Args:
            surface: Target surface.
            x: Left x for both lines.
            y: Top y of the label line.
            label: Small uppercased descriptor.
            value: Larger value rendered below.

        Returns:
            The y position immediately below the value text.
        """
        label_surf = self.label_font.render(label, True, ColorSettings.TEXT_LABEL)
        surface.blit(label_surf, (x, y))
        y += label_surf.get_height() + 2

        value_surf = self.value_font.render(value, True, ColorSettings.TEXT_DEFAULT)
        surface.blit(value_surf, (x, y))
        y += value_surf.get_height()
        return y
