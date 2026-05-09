"""Scene for game-over state."""

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


class GameOverScene(Scene):
    """Two-step end-of-run scene before leaderboard routing.

    Step 1 displays the outcome text (loss or victory). After confirm, step 2
    displays GAME OVER. A second confirm routes to InitialsEntryScene or
    LeaderboardScene based on leaderboard qualification.
    """

    OUTCOME_EATEN_BY_BIGGER_FISH = "loss_eaten_by_bigger_fish"
    OUTCOME_ATE_ALL_FISH = "win_ate_all_fish"

    _PHASE_OUTCOME_MESSAGE = "phase_outcome_message"
    _PHASE_GAME_OVER_MESSAGE = "phase_game_over_message"

    def __init__(
        self,
        game,
        score: Score | None = None,
        outcome: str = OUTCOME_EATEN_BY_BIGGER_FISH,
    ):
        """Initialize the game-over scene.

        Args:
            game: The GameManager instance that owns this scene.
            score: Score from the run that just ended.
            outcome: Reason this run ended (loss or victory).
        """
        super().__init__(game)
        self.score = score
        self.outcome = outcome
        self._phase = self._PHASE_OUTCOME_MESSAGE
        self._overlay_font = pygame.font.Font(FontSettings.FONT, UiSettings.OVERLAY_FONT_SIZE)
        self._outcome_font = pygame.font.Font(
            FontSettings.FONT,
            UiSettings.OUTCOME_MESSAGE_FONT_SIZE,
        )

    def on_enter(self) -> None:
        """Start on the custom outcome-message phase."""
        self._phase = self._PHASE_OUTCOME_MESSAGE

    def on_exit(self) -> None:
        """Called when leaving this scene."""
        pass

    def _advance_flow_action(self) -> None:
        """Advance from outcome text to GAME OVER, then route onward."""
        if self._phase == self._PHASE_OUTCOME_MESSAGE:
            self._phase = self._PHASE_GAME_OVER_MESSAGE
            return
        self._route_to_post_game_scene()

    def _route_to_post_game_scene(self) -> None:
        """Route to initials entry when qualified, otherwise leaderboard."""
        if self.score is not None and self.game.leaderboard.qualifies(self.score.total):
            from ui.scenes.initials_entry_scene import InitialsEntryScene
            self.game.scenes.change_to(InitialsEntryScene(self.game, self.score))
        else:
            from ui.scenes.leaderboard_scene import LeaderboardScene
            self.game.scenes.change_to(LeaderboardScene(self.game, self.score))

    def _current_message_text(self) -> str:
        """Return the centered message text for the current phase."""
        if self._phase == self._PHASE_GAME_OVER_MESSAGE:
            return UiSettings.GAME_OVER_TEXT
        if self.outcome == self.OUTCOME_ATE_ALL_FISH:
            return UiSettings.ATE_ALL_FISH_TEXT
        return UiSettings.EATEN_BY_BIGGER_FISH_TEXT

    def _current_message_color(self) -> tuple[int, int, int]:
        """Return the text color for the current phase message."""
        if self._phase == self._PHASE_GAME_OVER_MESSAGE:
            return ColorSettings.WHITE
        if self.outcome == self.OUTCOME_ATE_ALL_FISH:
            return UiSettings.ATE_ALL_FISH_COLOR
        return UiSettings.EATEN_BY_BIGGER_FISH_COLOR

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle confirm input to advance the end-of-run flow.

        Args:
            event: The pygame event to process.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._advance_flow_action()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button in (InputSettings.JOY_BUTTON_A, InputSettings.JOY_BUTTON_START):
                self._advance_flow_action()

    def update(self) -> None:
        """Game-over scene has no per-frame state to advance."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Render the current game-over phase text centered on black.

        Args:
            screen: The pygame surface to draw to.
        """
        screen.fill(ColorSettings.BLACK)
        message_font = (
            self._overlay_font
            if self._phase == self._PHASE_GAME_OVER_MESSAGE
            else self._outcome_font
        )
        draw_centered_text(
            surface=screen,
            text=self._current_message_text(),
            font=message_font,
            color=self._current_message_color(),
            center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2),
        )

