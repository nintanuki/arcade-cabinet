"""Puzzle League — entry point and top-level game manager.

Architecture mirrors Star Hero and Dungeon Digger so the project feels
familiar to anyone bouncing between games in the cabinet:

    puzzle-league/
        main.py            -- this file; owns GameManager + the run loop
        settings.py        -- tunable constants and asset paths
        core/              -- gameplay model (board, blocks, ...)
        systems/           -- audio, score, input managers
        ui/                -- presentation layers (CRT, HUD, style)
        tools/             -- developer-facing helpers (debug overlay, ...)
        assets/            -- font / graphics / music / sound

This module currently scaffolds the bare minimum needed to launch a
window cleanly and exit cleanly. Gameplay, rendering, and input are
left as ``pass`` placeholders or ``# TODO`` comments; future commits
will fill them in without having to reshape the surrounding plumbing.
"""

import sys
import time

import pygame

from settings import (
    AudioSettings,
    BoardSettings,
    ColorSettings,
    ControllerSettings,
    FontSettings,
    ScreenSettings,
    UISettings,
)
from core.board import Board
from systems.audio import Audio
from systems.managers import ScoreManager, SessionStateManager
from ui.crt import CRT


class GameManager:
    """Coordinates Puzzle League's display, audio, sub-managers, and main loop.

    The manager intentionally stays thin: it owns the pygame display,
    pumps the event queue, and delegates everything else to system-level
    helpers. That keeps each subsystem replaceable without surgery in
    main.py.
    """

    def __init__(self) -> None:
        """Initialize pygame, the display, audio, sub-managers, and game state."""
        # -------- Pygame core --------
        pygame.init()

        # Keep joystick objects alive so button events stay reliable on
        # all backends. Hot-plug is handled in handle_joystick_hotplug.
        pygame.joystick.init()
        self.joysticks: list[pygame.joystick.Joystick] = []
        self.refresh_joysticks()

        # -------- Display --------
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
        pygame.display.set_caption(ScreenSettings.TITLE)
        self.clock = pygame.time.Clock()
        self._show_loading_screen()

        # -------- Subsystems --------
        self.crt = CRT(self.screen)
        self.audio = Audio()

        # -------- Managers --------
        self.scores = ScoreManager(self)
        self.session = SessionStateManager(self)

        # -------- Gameplay model --------
        # The board owns the grid of blocks, the cursor position, and
        # the rise/clear/chain state machine. It does not touch pygame
        # surfaces directly; rendering is done by the manager (or a
        # future ui/render module) reading the board's public state.
        self.board = Board()

        # -------- Fonts --------
        # Pre-load the fonts we expect to use during the title screen
        # so the first frame doesn't have to pay the cost.
        self.title_font = pygame.font.Font(FontSettings.FONT, FontSettings.LARGE)
        self.prompt_font = pygame.font.Font(FontSettings.FONT, FontSettings.MEDIUM)

    # -------------------------
    # BOOT / LIFECYCLE
    # -------------------------

    def _show_loading_screen(self) -> None:
        """Paint a simple LOADING card before subsystem init blocks the UI thread."""
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)
        loading_font = pygame.font.Font(FontSettings.FONT, FontSettings.MEDIUM)
        loading_text = loading_font.render("LOADING...", False, FontSettings.DEFAULT_COLOR)
        loading_rect = loading_text.get_rect(center=ScreenSettings.CENTER)
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()

    def close_game(self) -> None:
        """Persist score state, then close the game process cleanly."""
        # Score persistence is a no-op until ScoreManager learns to save,
        # but calling it here means future work doesn't have to chase
        # down every exit path.
        self.scores.save_scores()
        pygame.quit()
        sys.exit()

    # -------------------------
    # CONTROLLER PLUMBING
    # -------------------------

    def refresh_joysticks(self) -> None:
        """Rebuild the active joystick list to support controller hot-plugging."""
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            if not joystick.get_init():
                joystick.init()
            self.joysticks.append(joystick)

    def quit_combo_pressed(self) -> bool:
        """Return True if the L1 + R1 + START + SELECT chord is held on any controller."""
        if len(self.joysticks) != pygame.joystick.get_count():
            self.refresh_joysticks()

        for joystick in self.joysticks:
            try:
                if all(joystick.get_button(button) for button in ControllerSettings.QUIT_COMBO):
                    return True
            except pygame.error:
                # Device may have disconnected between frames.
                continue
        return False

    def handle_joystick_hotplug(self, event: pygame.event.Event) -> bool:
        """Refresh the joystick cache when a controller add/remove event arrives.

        Args:
            event: The pygame event to inspect.

        Returns:
            True if the event was a hotplug event and was handled.
        """
        joystick_event_types = {
            getattr(pygame, 'JOYDEVICEADDED', None),
            getattr(pygame, 'JOYDEVICEREMOVED', None),
        }
        if event.type in joystick_event_types:
            self.refresh_joysticks()
            return True
        return False

    # -------------------------
    # EVENT HANDLING
    # -------------------------

    def _process_events(self) -> None:
        """Drain pygame's event queue and dispatch by event type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()

            if self.handle_joystick_hotplug(event):
                continue

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_joybuttondown(event)
            elif event.type == pygame.JOYHATMOTION:
                self._handle_joyhatmotion(event)
            elif event.type == pygame.JOYAXISMOTION:
                self._handle_joyaxismotion(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Route a single keyboard press to the appropriate handler."""
        # Global keys (always honored regardless of run state).
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return

        if event.key == pygame.K_ESCAPE:
            # ESC always exits the game and returns to the launcher,
            # matching the L1+R1+START+SELECT controller combo.
            self.close_game()
            return

        if self.session.game_active:
            # TODO: route gameplay keys (cursor move, swap, rush) into
            # the input manager once it exists.
            pass
        else:
            # TODO: route title/game-over keys (start, restart, etc.).
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.session.reset_for_new_game()

    def _handle_joybuttondown(self, event: pygame.event.Event) -> None:
        """Route a single controller button press."""
        # Catch the multi-button quit chord on press for instant
        # response; the outer per-frame check covers held-state quits.
        if self.quit_combo_pressed():
            self.close_game()
            return

        # BACK is the global fullscreen toggle.
        if event.button == ControllerSettings.BACK_BUTTON:
            pygame.display.toggle_fullscreen()
            return

        if self.session.game_active:
            # TODO: route gameplay buttons (A=swap, START=pause, etc.).
            pass
        else:
            # TODO: route title/game-over buttons (A or START to begin).
            if event.button in (ControllerSettings.A_BUTTON, ControllerSettings.START_BUTTON):
                self.session.reset_for_new_game()

    def _handle_joyhatmotion(self, event: pygame.event.Event) -> None:
        """Route D-pad direction events for menu nav and cursor movement."""
        # TODO: dispatch hat motion to menu nav while inactive and to
        # cursor movement while gameplay is running.
        pass

    def _handle_joyaxismotion(self, event: pygame.event.Event) -> None:
        """Route analog stick events with edge-triggered debouncing."""
        # TODO: edge-trigger threshold crossings on the left stick to
        # mirror the D-pad mapping for menu nav and cursor movement.
        pass

    # -------------------------
    # PER-FRAME UPDATE / RENDER
    # -------------------------

    def _update_world(self, delta_time: float) -> None:
        """Advance gameplay state for the frame.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        if not self.session.game_active:
            return

        # TODO: drive board.tick(delta_time) once Board exposes its
        # rise/clear/chain state machine.
        self.board.tick(delta_time)

    def _draw_active_gameplay(self) -> None:
        """Render the playfield, cursor, and HUD while a run is active."""
        # Placeholder: draw the empty playfield rectangle so the screen
        # already shows the geometry the gameplay code will fill in.
        board_rect = pygame.Rect(
            BoardSettings.BOARD_X,
            BoardSettings.BOARD_Y,
            BoardSettings.BOARD_WIDTH,
            BoardSettings.BOARD_HEIGHT,
        )
        pygame.draw.rect(self.screen, ColorSettings.BOARD_BACKGROUND, board_rect, border_radius=BoardSettings.BORDER_RADIUS)
        pygame.draw.rect(
            self.screen,
            ColorSettings.BOARD_BORDER,
            board_rect,
            BoardSettings.BORDER_WIDTH,
            border_radius=BoardSettings.BORDER_RADIUS,
        )

        # TODO: delegate to ui.render once block / cursor / HUD draw
        # routines exist.

    def _draw_inactive_screen(self) -> None:
        """Render the title or game-over screen depending on run history."""
        # Title text.
        title_surface = self.title_font.render(UISettings.TITLE_TEXT, False, FontSettings.TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)

        # Prompt under the title — flips between intro and game-over copy.
        if self.scores.score == 0:
            prompt_text = UISettings.SUBTITLE_TEXT
        else:
            prompt_text = UISettings.CONTINUE_PROMPT

        prompt_surface = self.prompt_font.render(prompt_text, False, FontSettings.PROMPT_COLOR)
        prompt_rect = prompt_surface.get_rect(center=ScreenSettings.CENTER)
        self.screen.blit(prompt_surface, prompt_rect)

    def _render_frame(self) -> None:
        """Draw one full frame: background, gameplay or menu, then CRT pass."""
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        if self.session.game_active:
            self._draw_active_gameplay()
        else:
            self._draw_inactive_screen()

        self.crt.draw()

    def run(self) -> None:
        """Main game loop: pump events, advance world, render, repeat."""
        last_time = time.time()
        while True:
            now = time.time()
            delta_time = now - last_time
            last_time = now

            if self.quit_combo_pressed():
                self.close_game()

            self._process_events()
            self._update_world(delta_time)
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)


# Main execution
if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()
