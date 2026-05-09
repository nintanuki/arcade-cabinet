"""Scene for displaying the leaderboard after a game-over event."""

from __future__ import annotations

import pygame

from core.scene import Scene
from core.score import Score
from settings import (
    ColorSettings,
    FontSettings,
    InputSettings,
    ScreenSettings,
    UiSettings,
)
from utils.text import draw_centered_text


class LeaderboardScene(Scene):
    """Displays the top-10 leaderboard after a game ends.

    Reached either from InitialsEntryScene (after a qualifying run) or
    directly from GameOverScene (after a non-qualifying run).
    """

    def __init__(
        self,
        game,
        score: Score | None = None,
        highlight_initials: str | None = None,
    ):
        """Initialize the leaderboard display.

        Args:
            game: The GameManager instance that owns this scene.
            score: Score from the run that just ended, or None.
            highlight_initials: If the player just submitted, their initials
                are used to highlight that row.
        """
        super().__init__(game)
        self.score = score
        self.highlight_initials = highlight_initials
        self._overlay_font = pygame.font.Font(FontSettings.FONT, UiSettings.OVERLAY_FONT_SIZE)
        self._hud_font = pygame.font.Font(FontSettings.FONT, UiSettings.HUD_FONT_SIZE)

    def on_enter(self) -> None:
        """Called when this scene becomes active."""
        pass

    def on_exit(self) -> None:
        """Called when leaving this scene."""
        pass

    # ------------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle input to return to the title screen.

        Args:
            event: The pygame event to process.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._return_to_title_action()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == InputSettings.JOY_BUTTON_START:
                self._return_to_title_action()

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------

    def _return_to_title_action(self) -> None:
        """Transition back to the title screen."""
        from ui.scenes.title_scene import TitleScene
        self.game.scenes.change_to(TitleScene(self.game))

    # ------------------------------------------------------------------
    # UPDATE / RENDER
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Leaderboard scene has no per-frame state to advance."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Draw the game-over header, run score, and leaderboard table.

        Args:
            screen: The pygame surface to draw to.
        """
        screen.fill(ColorSettings.BLACK)
        cx = ScreenSettings.WIDTH // 2

        draw_centered_text(
            surface=screen,
            text=UiSettings.GAME_OVER_TEXT,
            font=self._overlay_font,
            color=ColorSettings.WHITE,
            center=(cx, 60),
        )

        self._draw_entries(screen, cx)

        draw_centered_text(
            surface=screen,
            text="PRESS START TO RETURN TO TITLE",
            font=self._hud_font,
            color=ColorSettings.WHITE,
            center=(cx, ScreenSettings.HEIGHT - 40),
        )

    def _draw_entries(self, screen: pygame.Surface, cx: int) -> None:
        """Render the ranked leaderboard rows, highlighting the player's entry.

        Args:
            screen: The pygame surface to draw on.
            cx: Horizontal center for all rows.
        """
        entries = self.game.leaderboard.top()
        row_height = UiSettings.HUD_FONT_SIZE + 8
        start_y = UiSettings.LEADERBOARD_ENTRIES_START_Y
        run_score = self.score.total if self.score is not None else -1

        for rank, (initials, entry_score) in enumerate(entries):
            y = start_y + rank * row_height
            row_text = f"{rank + 1:2d}.  {initials}    {entry_score:05d}"
            is_highlight = (
                self.highlight_initials is not None
                and initials == self.highlight_initials
                and entry_score == run_score
            )
            text_color = ColorSettings.YELLOW if is_highlight else ColorSettings.WHITE
            text_surface = self._hud_font.render(row_text, True, text_color)
            text_rect = text_surface.get_rect(center=(cx, y))
            screen.blit(text_surface, text_rect)
