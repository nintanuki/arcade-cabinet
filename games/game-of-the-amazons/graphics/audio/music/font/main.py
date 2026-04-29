from __future__ import annotations
import sys
import pygame
from settings import *

class GameManager:
    def __init__(self, start_fullscreen: bool = False):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)
        pygame.display.set_caption(ScreenSettings.TITLE)
        if start_fullscreen:
            pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()

        self.setup_controllers()

    # -------------------------
    # BOOT / SETUP
    # -------------------------

    def setup_controllers(self) -> None:
        """Cache currently-connected controllers so quit-combo and event polling are cheap."""
        pygame.joystick.init()
        self.connected_joysticks = [
            pygame.joystick.Joystick(index)
            for index in range(pygame.joystick.get_count())
        ]

    def reset_game(self):
        """
        Restart the game by replacing the current GameManager instance
        with a brand new one.

        This is safer than trying to manually reset every subsystem,
        because it reuses the same startup path the game already uses
        when it first launches.
        """
        current_surface = pygame.display.get_surface()
        was_fullscreen = bool(current_surface and (current_surface.get_flags() & pygame.FULLSCREEN))

        new_game_manager = GameManager(start_fullscreen=was_fullscreen)
        new_game_manager.run()
        sys.exit()

    def close_game(self) -> None:
        """Close the game process cleanly."""
        pygame.quit()
        sys.exit()

    def quit_combo_pressed(self) -> bool:
        """Return True if START + SELECT + L1 + R1 are held on any controller."""
        required_buttons = InputSettings.JOY_BUTTON_QUIT_COMBO
        for joystick in self.connected_joysticks:
            if all(joystick.get_button(button) for button in required_buttons):
                return True
        return False

        # -------------------------
    # MAIN LOOP
    # -------------------------

    def _tick_between_level_flow(self) -> None:
        """Advance level-transition, door-unlock, treasure-conversion, and game-over timers."""
        if self.ui_state == 'playing':
            self.intermission.update_level_transition()
            self.intermission.update_door_unlock_sequence()
            self.intermission.update_treasure_conversion()
        self.score_manager.update_game_over_flow()

    def _process_events(self) -> None:
        """Drain pygame's event queue and dispatch by event type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_joybuttondown(event)

    def _handle_keydown(self, event) -> None:
        """Route one keyboard press for fullscreen and exit shortcuts.

        Args:
            event: pygame KEYDOWN event.
        """
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.key == pygame.K_ESCAPE:
            # ESC always exits the game and returns to the launcher, matching
            # the L1+R1+START+SELECT controller combo.
            self.close_game()

    def _handle_joybuttondown(self, event) -> None:
        """Route one controller button press.

        Args:
            event: pygame JOYBUTTONDOWN event.
        """
        # Catch the multi-button quit chord on press for instant response;
        # the outer per-frame check covers held-state quits.
        if self.quit_combo_pressed():
            self.close_game()

        # BACK (SELECT) is the global fullscreen toggle.
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()

    def _render_frame(self) -> None:
        """Compose one frame: world, HUD panels, modal overlays, then CRT."""
        # self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        # Apply CRT pass after world/UI rendering.
        # self.crt.draw()

    def run(self):
        """Run the main game loop until the player quits."""
        while True:
            if self.quit_combo_pressed():
                self.close_game()
            self._process_events()
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
