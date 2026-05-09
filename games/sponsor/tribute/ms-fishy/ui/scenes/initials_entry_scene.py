"""Scene for entering three-letter initials after a qualifying high-score run."""

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


class InitialsEntryScene(Scene):
    """Prompts the player to enter three-letter initials after a high-score run."""

    _SLOT_COUNT = 3
    _ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, game, score: Score):
        """Initialize the initials-entry scene.

        Args:
            game: The GameManager instance that owns this scene.
            score: The score from the qualifying run.
        """
        super().__init__(game)
        self.score = score
        self._slots: list[str | None] = [None, None, None]
        self._cursor = 0
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
        """Route input events to the appropriate handler.

        Args:
            event: The pygame event to process.
        """
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.JOYBUTTONDOWN:
            self._handle_joybuttondown(event)
        elif event.type == pygame.JOYHATMOTION:
            self._handle_joyhatmotion(event)

    def _handle_keydown(self, event: pygame.event.EventType) -> None:
        """Handle keyboard input for letter entry and cursor navigation.

        Args:
            event: The KEYDOWN event to process.
        """
        key = event.key
        if pygame.K_a <= key <= pygame.K_z:
            self._set_letter_action(chr(key).upper())
        elif key == pygame.K_BACKSPACE:
            self._backspace_action()
        elif key == pygame.K_UP:
            self._cycle_up_action()
        elif key == pygame.K_DOWN:
            self._cycle_down_action()
        elif key == pygame.K_LEFT:
            self._move_left_action()
        elif key == pygame.K_RIGHT:
            self._move_right_action()
        elif key == pygame.K_RETURN:
            self._commit_action()

    def _handle_joybuttondown(self, event: pygame.event.EventType) -> None:
        """Handle controller button presses.

        Args:
            event: The JOYBUTTONDOWN event to process.
        """
        if event.button == InputSettings.JOY_BUTTON_START:
            self._commit_action()

    def _handle_joyhatmotion(self, event: pygame.event.EventType) -> None:
        """Handle D-pad input for letter cycling and cursor movement.

        Args:
            event: The JOYHATMOTION event to process.
        """
        x_axis, y_axis = event.value
        if y_axis == 1:
            self._cycle_up_action()
        elif y_axis == -1:
            self._cycle_down_action()
        if x_axis == -1:
            self._move_left_action()
        elif x_axis == 1:
            self._move_right_action()

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------

    def _set_letter_action(self, letter: str) -> None:
        """Set a letter in the current slot and advance the cursor.

        After the third slot is filled the cursor stays at slot 2 so further
        key presses overwrite the last letter rather than doing nothing.

        Args:
            letter: Single uppercase A-Z letter.
        """
        self._slots[self._cursor] = letter
        if self._cursor < self._SLOT_COUNT - 1:
            self._cursor += 1

    def _backspace_action(self) -> None:
        """Clear the current slot; step back one slot if the current is already empty."""
        if self._slots[self._cursor] is not None:
            self._slots[self._cursor] = None
        elif self._cursor > 0:
            self._cursor -= 1
            self._slots[self._cursor] = None

    def _cycle_up_action(self) -> None:
        """Cycle the current slot's letter forward (A → B → … → Z → A)."""
        current = self._slots[self._cursor]
        if current is None:
            self._slots[self._cursor] = "A"
        else:
            self._slots[self._cursor] = self._ALPHABET[(self._ALPHABET.index(current) + 1) % 26]

    def _cycle_down_action(self) -> None:
        """Cycle the current slot's letter backward (A → Z → Y → …)."""
        current = self._slots[self._cursor]
        if current is None:
            self._slots[self._cursor] = "A"
        else:
            self._slots[self._cursor] = self._ALPHABET[(self._ALPHABET.index(current) - 1) % 26]

    def _move_left_action(self) -> None:
        """Move the cursor one slot to the left (clamped at 0)."""
        self._cursor = max(0, self._cursor - 1)

    def _move_right_action(self) -> None:
        """Move the cursor one slot to the right (clamped at slot 2)."""
        self._cursor = min(self._SLOT_COUNT - 1, self._cursor + 1)

    def _commit_action(self) -> None:
        """Fill empty slots with 'A', submit to the leaderboard, and transition out."""
        for i in range(self._SLOT_COUNT):
            if self._slots[i] is None:
                self._slots[i] = "A"
        initials = "".join(self._slots)  # type: ignore[arg-type]
        self.game.leaderboard.submit(initials, self.score.total)
        self.game.leaderboard.save()
        from ui.scenes.leaderboard_scene import LeaderboardScene
        self.game.scenes.change_to(
            LeaderboardScene(self.game, self.score, highlight_initials=initials)
        )

    # ------------------------------------------------------------------
    # UPDATE / RENDER
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Initials-entry scene has no per-frame state to advance."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Draw the initials-entry UI centered on screen.

        Args:
            screen: The pygame surface to draw to.
        """
        screen.fill(ColorSettings.BLACK)
        cx = ScreenSettings.WIDTH // 2
        h = ScreenSettings.HEIGHT
        block_center_y = int(h * UiSettings.INITIALS_BLOCK_CENTER_Y_RATIO)
        row_gap = UiSettings.INITIALS_BLOCK_ROW_GAP

        title_y = block_center_y - row_gap
        title_surface = self._hud_font.render("NEW HIGH SCORE:", True, ColorSettings.WHITE)
        score_surface = self._hud_font.render(f"{self.score.total:05d}", True, ColorSettings.YELLOW)
        total_width = (
            title_surface.get_width()
            + UiSettings.INITIALS_TITLE_SCORE_GAP
            + score_surface.get_width()
        )
        start_x = cx - total_width // 2
        title_rect = title_surface.get_rect(midleft=(start_x, title_y))
        score_rect = score_surface.get_rect(
            midleft=(title_rect.right + UiSettings.INITIALS_TITLE_SCORE_GAP, title_y)
        )
        screen.blit(title_surface, title_rect)
        screen.blit(score_surface, score_rect)

        draw_centered_text(
            surface=screen,
            text="ENTER YOUR INITIALS",
            font=self._hud_font,
            color=ColorSettings.LIGHT_BLUE,
            center=(cx, block_center_y),
        )
        self._draw_slots(screen, cx, block_center_y + row_gap)

    def _draw_slots(self, screen: pygame.Surface, cx: int, cy: int) -> None:
        """Draw the three letter-entry slots with the active-slot highlight.

        Args:
            screen: The pygame surface to draw on.
            cx: Horizontal center of the slot row.
            cy: Vertical center of the slot row.
        """
        slot_size = UiSettings.OVERLAY_FONT_SIZE + 16
        gap = UiSettings.INITIALS_SLOT_GAP
        total_width = self._SLOT_COUNT * slot_size + (self._SLOT_COUNT - 1) * gap
        start_x = cx - total_width // 2

        for i, letter in enumerate(self._slots):
            slot_x = start_x + i * (slot_size + gap)
            is_active = (i == self._cursor)
            display_char = letter if letter is not None else "_"
            color = ColorSettings.YELLOW if is_active else ColorSettings.GRAY
            char_surface = self._overlay_font.render(display_char, True, color)
            char_rect = char_surface.get_rect(center=(slot_x + slot_size // 2, cy))
            screen.blit(char_surface, char_rect)
