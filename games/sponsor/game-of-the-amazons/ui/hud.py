"""Renders the side HUD window with turn / phase / game-over information."""
import pygame
from settings import ColorSettings, FontSettings, UISettings


# HUD lines specific to game-over banners. Centralised so the GameManager and
# the HUD can't disagree on the labels we render.
WIN_BANNER = "YOU WIN"
LOSE_BANNER = "YOU LOSE"
DRAW_BANNER = "DRAW"


class HUD:
    """Draws the rounded HUD window plus turn, phase, and game-over text."""

    def __init__(self):
        """Build fonts and seed placeholder state until game logic is wired up.

        Returns:
            None.
        """
        self.title_font = pygame.font.Font(None, FontSettings.HUD_TITLE_SIZE)
        self.label_font = pygame.font.Font(None, FontSettings.HUD_LABEL_SIZE)
        self.value_font = pygame.font.Font(None, FontSettings.HUD_VALUE_SIZE)

        # Placeholder state. The real game manager will overwrite these once
        # turn tracking exists.
        self.current_player = "WHITE"
        self.current_phase = "MOVE"

        # Game-over state pushed by GameManager each frame. None when the
        # game is still in progress.
        self.game_over = False
        self.winner = None
        self.win_condition = None
        self.territory_totals = None

    # -------------------------
    # WINDOW + STATIC LAYOUT
    # -------------------------

    def _draw_window_border(self, surface):
        """Draw the rounded-corner border around the HUD area.

        Args:
            surface: Target pygame surface.

        Returns:
            None.
        """
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

    # -------------------------
    # TEXT BLOCKS
    # -------------------------

    def _draw_text(self, surface):
        """Stack the title, turn, phase, and any game-over text vertically.

        Args:
            surface: Target pygame surface.

        Returns:
            None.
        """
        x = UISettings.HUD_X + UISettings.HUD_TEXT_PADDING
        y = UISettings.HUD_Y + UISettings.HUD_TEXT_PADDING

        # Title
        title_surf = self.title_font.render("AMAZONS", True, ColorSettings.TEXT_TITLE)
        surface.blit(title_surf, (x, y))
        y += title_surf.get_height() + 22

        if self.game_over:
            self._draw_game_over_block(surface, x, y)
            return

        # TURN: <player>
        y = self._draw_label_value(
            surface, x, y, "TURN", self.current_player
        )
        y += 14

        # PHASE: <move/shoot>
        self._draw_label_value(
            surface, x, y, "PHASE", self.current_phase
        )

    def _draw_game_over_block(self, surface, x, y):
        """Draw the WIN / LOSE / DRAW banner and any territory totals.

        Args:
            surface: Target pygame surface.
            x: Left x for the block.
            y: Top y for the block.

        Returns:
            None.
        """
        banner = self._game_over_banner()
        banner_surf = self.title_font.render(banner, True, ColorSettings.TEXT_TITLE)
        surface.blit(banner_surf, (x, y))
        y += banner_surf.get_height() + 12

        condition_label = "CONDITION"
        condition_value = self._condition_label()
        y = self._draw_label_value(surface, x, y, condition_label, condition_value)
        y += 12

        if self.territory_totals is not None:
            y = self._draw_label_value(
                surface, x, y, "WHITE TILES", str(self.territory_totals["WHITE"])
            )
            y += 8
            y = self._draw_label_value(
                surface, x, y, "BLACK TILES", str(self.territory_totals["BLACK"])
            )
            y += 12

        restart_surf = self.label_font.render(
            "PRESS START TO PLAY AGAIN", True, ColorSettings.TEXT_LABEL
        )
        surface.blit(restart_surf, (x, y))

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

    def _game_over_banner(self):
        """Return the headline for the game-over block based on the winner.

        The human is always WHITE in the current build, so winner == 'WHITE'
        is a player victory and 'BLACK' is a player loss. A None winner means
        a territory tie.

        Returns:
            One of the WIN_BANNER / LOSE_BANNER / DRAW_BANNER constants.
        """
        if self.winner == "WHITE":
            return WIN_BANNER
        if self.winner == "BLACK":
            return LOSE_BANNER
        return DRAW_BANNER

    def _condition_label(self):
        """Map the win-condition code into HUD-friendly text.

        Returns:
            A short human-readable description of the ending.
        """
        if self.win_condition == "STALEMATE":
            return "NO MOVES"
        if self.win_condition == "TERRITORY":
            return "TERRITORY"
        if self.win_condition == "TERRITORY_TIE":
            return "TIE"
        return ""

    # -------------------------
    # PUBLIC ENTRY
    # -------------------------

    def draw(self, surface):
        """Render the HUD window border and the status text inside it.

        Args:
            surface: Target surface (typically the main screen).

        Returns:
            None.
        """
        self._draw_window_border(surface)
        self._draw_text(surface)
