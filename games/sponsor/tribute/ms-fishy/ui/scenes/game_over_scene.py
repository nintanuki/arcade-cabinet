"""Scene for game-over state."""

from __future__ import annotations

import pygame

from core.scene import Scene
from core.score import Score
from settings import (
    ColorSettings,
    FontSettings,
    InputSettings,
    ScoreSettings,
    ScreenSettings,
    UiSettings,
)
class GameOverScene(Scene):
    """Outcome message then timed stat tally before leaderboard routing."""

    OUTCOME_EATEN_BY_BIGGER_FISH = "loss_eaten_by_bigger_fish"
    OUTCOME_STARVED_TO_DEATH = "loss_starved_to_death"
    OUTCOME_ATE_ALL_FISH = "win_ate_all_fish"

    _PHASE_OUTCOME_MESSAGE = "phase_outcome_message"
    _PHASE_TALLY = "phase_tally"

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
        self._tally_elapsed_ms = 0
        self._overlay_font = pygame.font.Font(FontSettings.FONT, UiSettings.OVERLAY_FONT_SIZE)
        self._outcome_font = pygame.font.Font(
            FontSettings.FONT,
            UiSettings.OUTCOME_MESSAGE_FONT_SIZE,
        )
        self._tally_font = pygame.font.Font(FontSettings.FONT, UiSettings.HUD_FONT_SIZE)
        self._tally_total_font = pygame.font.Font(
            FontSettings.FONT,
            UiSettings.TALLY_TOTAL_FONT_SIZE,
        )

    def on_enter(self) -> None:
        """Start on the custom outcome-message phase."""
        self._phase = self._PHASE_OUTCOME_MESSAGE
        self._tally_elapsed_ms = 0

    def on_exit(self) -> None:
        """Called when leaving this scene."""
        pass

    def _advance_flow_action(self) -> None:
        """Advance from outcome text to tally, then route onward."""
        if self._phase == self._PHASE_OUTCOME_MESSAGE:
            self._phase = self._PHASE_TALLY
            self._tally_elapsed_ms = 0
            return
        if self._phase == self._PHASE_TALLY and self._all_tally_lines_visible():
            self._route_to_post_game_scene()

    def _route_to_post_game_scene(self) -> None:
        """Route directly to the leaderboard scene."""
        from ui.scenes.leaderboard_scene import LeaderboardScene
        self.game.scenes.change_to(LeaderboardScene(self.game, self.score))

    def _tally_lines(self) -> list[str]:
        """Build tally rows shown after the outcome message.

        Returns:
            List of rows with leading + for component stats and = for total.
        """
        if self.score is None:
            return ["TOTAL SCORE = 0!"]

        fish_points = self.score.fish_eaten * ScoreSettings.FISH_EATEN_BONUS
        weight_points = self.score.size_eaten * ScoreSettings.WEIGHT_EATEN_FACTOR
        final_weight = int(self.score.final_weight)
        final_weight_points = final_weight * ScoreSettings.FINAL_WEIGHT_FACTOR
        seconds_left = int(self.score.time_left_seconds)
        time_points = seconds_left * ScoreSettings.TIME_LEFT_BONUS

        return [
            f"+ NUMBER OF FISH EATEN: {self.score.fish_eaten} ({fish_points})",
            f"+ TOTAL WEIGHT OF FISH EATEN: {self.score.size_eaten} ({weight_points})",
            f"+ MS. FISHY'S FINAL WEIGHT: {final_weight} ({final_weight_points})",
            f"+ SECONDS LEFT ON THE TIMER: {seconds_left} ({time_points})",
            f"TOTAL SCORE = {self.score.total}!",
        ]

    def _visible_tally_line_count(self) -> int:
        """Return how many tally rows should currently be visible."""
        lines = self._tally_lines()
        delay_ms = max(1, UiSettings.TALLY_LINE_REVEAL_DELAY_MS)
        visible = 1 + (self._tally_elapsed_ms // delay_ms)
        return min(len(lines), visible)

    def _all_tally_lines_visible(self) -> bool:
        """Return True once every tally row is visible."""
        return self._visible_tally_line_count() >= len(self._tally_lines())

    def _current_message_text(self) -> str:
        """Return the centered message text for the current phase."""
        if self.outcome == self.OUTCOME_ATE_ALL_FISH:
            return UiSettings.ATE_ALL_FISH_TEXT
        if self.outcome == self.OUTCOME_STARVED_TO_DEATH:
            return UiSettings.STARVED_TO_DEATH_TEXT
        return UiSettings.EATEN_BY_BIGGER_FISH_TEXT

    def _current_message_color(self) -> tuple[int, int, int]:
        """Return the text color for the current phase message."""
        if self.outcome == self.OUTCOME_ATE_ALL_FISH:
            return UiSettings.ATE_ALL_FISH_COLOR
        if self.outcome == self.OUTCOME_STARVED_TO_DEATH:
            return UiSettings.STARVED_TO_DEATH_COLOR
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
        """Advance timed reveal of tally lines."""
        if self._phase == self._PHASE_TALLY:
            self._tally_elapsed_ms += int(1000 / ScreenSettings.FPS)

    def render(self, screen: pygame.Surface) -> None:
        """Render the current game-over phase.

        Args:
            screen: The pygame surface to draw to.
        """
        screen.fill(ColorSettings.BLACK)
        if self._phase == self._PHASE_OUTCOME_MESSAGE:
            outcome_surface = self._outcome_font.render(
                self._current_message_text(),
                True,
                self._current_message_color(),
            )
            outcome_rect = outcome_surface.get_rect(
                center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2)
            )
            screen.blit(outcome_surface, outcome_rect)
            return

        lines = self._tally_lines()
        visible_count = self._visible_tally_line_count()
        start_y = int(ScreenSettings.HEIGHT * UiSettings.TALLY_LINE_START_Y_RATIO)

        # Keep the block anchor stable across reveal steps by measuring all
        # tally rows (including rows not visible yet) before drawing.
        all_row_widths: list[int] = []
        for i, line in enumerate(lines):
            is_total_row = i == len(lines) - 1
            text_font = self._tally_total_font if is_total_row else self._tally_font
            all_row_widths.append(text_font.size(line)[0])
        block_width = max(all_row_widths)
        block_left_x = (ScreenSettings.WIDTH - block_width) // 2

        visible_surfaces: list[tuple[pygame.Surface, bool]] = []
        for i in range(visible_count):
            is_total_row = i == len(lines) - 1
            text_color = ColorSettings.YELLOW if is_total_row else ColorSettings.WHITE
            text_font = self._tally_total_font if is_total_row else self._tally_font
            line_surface = text_font.render(lines[i], True, text_color)
            visible_surfaces.append((line_surface, is_total_row))

        y = start_y
        for surface, is_total_row in visible_surfaces:
            if is_total_row:
                y += UiSettings.TALLY_TOTAL_TOP_GAP
            screen.blit(surface, (block_left_x, y))
            y += UiSettings.TALLY_LINE_ROW_GAP

