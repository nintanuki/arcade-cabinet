"""Gameplay HUD widget for run score, fish count, and timer display."""

from __future__ import annotations

import pygame

from core.score import Score
from settings import ColorSettings, UiSettings


class Hud:
    """Draw fish count, run score, and elapsed-time indicators for the active play scene."""

    def __init__(
        self,
        score: Score,
        font: pygame.font.Font,
    ):
        """Initialize HUD dependencies.

        Args:
            score: The run-scoped score model for the current session.
            font: Font used for all HUD text.
        """
        self.score = score
        self.font = font

    def draw(self, screen: pygame.Surface, seconds: int = 0) -> None:
        """Draw fish count, run score, and elapsed time labels.

        Args:
            screen: The pygame surface to draw on.
            seconds: Elapsed active gameplay time in whole seconds.
        """
        padding = UiSettings.HUD_PADDING
        fish_text = f"FISH: {self.score.fish_eaten:02d}"
        score_text = f"SCORE: {self.score.total:05d}"
        minutes, secs = divmod(seconds, 60)
        time_text = f"TIME: {minutes:02d}:{secs:02d}"

        fish_surface = self.font.render(fish_text, True, ColorSettings.WHITE)
        fish_rect = fish_surface.get_rect(topleft=(padding, padding))
        screen.blit(fish_surface, fish_rect)

        score_surface = self.font.render(score_text, True, ColorSettings.WHITE)
        score_rect = score_surface.get_rect(midtop=(screen.get_width() // 2, padding))
        screen.blit(score_surface, score_rect)

        time_surface = self.font.render(time_text, True, ColorSettings.WHITE)
        time_rect = time_surface.get_rect(
            topright=(screen.get_width() - padding, padding)
        )
        screen.blit(time_surface, time_rect)
