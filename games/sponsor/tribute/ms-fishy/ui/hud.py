"""Gameplay HUD widget showing run stats and hunger timer."""

from __future__ import annotations

import math

import pygame

from core.score import Score
from core.sprites import Player
from settings import ColorSettings, TimerSettings, UiSettings


class Hud:
    """Draw either a compact hunger indicator or a full stats overlay.

    Compact mode (always shown): 'HUNGER' label with a colour-coded bar to its
    right, centred at the top of the screen.

    Detail mode: four stacked stat rows anchored to the top-left or top-right
    corner, drawn in addition to the compact bar while a shoulder button is held.
    The bar is not repeated in the detail panel.
    """

    def __init__(
        self,
        score: Score,
        font: pygame.font.Font,
        player: Player,
    ):
        """Initialize HUD dependencies.

        Args:
            score: The run-scoped score model for the current session.
            font: Font used for all HUD text.
            player: The player sprite; provides current weight for display.
        """
        self.score = score
        self.font = font
        self.player = player

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def draw(
        self,
        screen: pygame.Surface,
        remaining_seconds: float = 0.0,
        detail_align: str | None = None,
    ) -> None:
        """Draw the HUD in compact or detail mode.

        Args:
            screen: The pygame surface to draw on.
            remaining_seconds: Countdown time left in seconds.
            detail_align: None to show compact only, 'left' or 'right' to also
                show the full detail panel anchored to that corner.
        """
        # Compact bar is always visible.
        self._draw_compact(screen, remaining_seconds)
        # Detail overlay is drawn on top while a shoulder button is held.
        if detail_align is not None:
            self._draw_detail(screen, remaining_seconds, detail_align)

    # ------------------------------------------------------------------
    # COMPACT MODE
    # ------------------------------------------------------------------

    def _draw_compact(self, screen: pygame.Surface, remaining_seconds: float) -> None:
        """Draw the minimal hunger indicator centred at the top.

        Layout: [HUNGER] [========bar========]
        """
        padding = UiSettings.HUD_PADDING
        bar_w = UiSettings.HUD_BAR_WIDTH
        bar_h = UiSettings.HUD_BAR_HEIGHT
        gap = UiSettings.HUD_COMPACT_BAR_GAP

        label_surf = self.font.render(
            UiSettings.HUD_COMPACT_LABEL,
            True,
            self._timer_color(remaining_seconds),
        )
        total_w = label_surf.get_width() + gap + bar_w
        label_x = (screen.get_width() - total_w) // 2
        label_y = padding
        # Vertically centre bar within the label text height.
        bar_x = label_x + label_surf.get_width() + gap
        bar_y = label_y + (label_surf.get_height() - bar_h) // 2

        screen.blit(label_surf, (label_x, label_y))
        self._draw_bar(screen, bar_x, bar_y, bar_w, bar_h, remaining_seconds)

    # ------------------------------------------------------------------
    # DETAIL MODE
    # ------------------------------------------------------------------

    def _draw_detail(
        self, screen: pygame.Surface, remaining_seconds: float, align: str
    ) -> None:
        """Draw the full stats overlay anchored to the left or right corner.

        Args:
            screen: The pygame surface to draw on.
            remaining_seconds: Countdown time left in seconds.
            align: 'left' or 'right'.
        """
        padding = UiSettings.HUD_PADDING
        line_h = UiSettings.HUD_LINE_SPACING
        right_edge = screen.get_width() - padding

        stat_rows = [
            f"TOTAL FISH EATEN: {self.score.fish_eaten}",
            f"WEIGHT EATEN: {self.score.size_eaten}",
            f"CURRENT WEIGHT: {int(self.player.size)}",
        ]

        # ------------------------------------------------------------------
        # STAT ROWS
        # ------------------------------------------------------------------
        for i, text in enumerate(stat_rows):
            surf = self.font.render(text, True, ColorSettings.IN_GAME_HUD_TEXT)
            x = padding if align == "left" else right_edge - surf.get_width()
            screen.blit(surf, (x, padding + i * line_h))

        # ------------------------------------------------------------------
        # HUNGER TIMER
        # ------------------------------------------------------------------
        timer_y = padding + 3 * line_h
        display_seconds = max(0, math.ceil(remaining_seconds))
        minutes, secs = divmod(display_seconds, 60)
        timer_text = f"TIME LEFT: {minutes:02d}:{secs:02d}"
        # TODO: add a warning audio cue here when sound system supports it.
        timer_surf = self.font.render(timer_text, True, self._timer_color(remaining_seconds))
        x = padding if align == "left" else right_edge - timer_surf.get_width()
        screen.blit(timer_surf, (x, timer_y))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _timer_color(self, remaining_seconds: float) -> tuple[int, int, int]:
        """Return red at or below the warning threshold, otherwise the HUD text colour."""
        if remaining_seconds <= UiSettings.HUNGER_WARNING_SECONDS:
            return ColorSettings.RED
        return ColorSettings.IN_GAME_HUD_TEXT

    def _draw_bar(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        remaining_seconds: float,
    ) -> None:
        """Draw the hunger bar background and green-to-red fill.

        Args:
            screen: Surface to draw on.
            x: Left edge of the bar.
            y: Top edge of the bar.
            w: Total bar width in pixels.
            h: Bar height in pixels.
            remaining_seconds: Used to compute the fill fraction.
        """
        fraction = max(0.0, min(1.0, remaining_seconds / TimerSettings.STARTING_SECONDS))
        # Background track.
        pygame.draw.rect(screen, ColorSettings.NERO, (x, y, w, h))
        # Filled portion: green when full, red when empty, smooth lerp.
        fill_w = int(w * fraction)
        if fill_w > 0:
            r = int(255 * (1.0 - fraction))
            g = int(255 * fraction)
            pygame.draw.rect(screen, (r, g, 0), (x, y, fill_w, h))
