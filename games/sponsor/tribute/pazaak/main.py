from __future__ import annotations

import sys
import time
import pygame

from ui.crt import CRT
from settings import *


class GameManager:
    """Manages the game loop and overall game state for Pazaak."""
    def __init__(self):
        # -------- Pygame core --------
        pygame.init()

        # Keep joystick objects alive so button events remain reliable on all backends.
        pygame.joystick.init()
        self.joysticks = []
        self.refresh_joysticks()

        # -------- Display --------
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION)
        pygame.display.set_caption("Pazaak")
        self.clock = pygame.time.Clock()

        # -------- Subsystems --------
        self.crt = CRT(self.screen)

    # -------------------------
    # BOOT / LIFECYCLE
    # -------------------------

    def close_game(self):
        """Close the game process cleanly."""
        pygame.quit()
        sys.exit()

    def refresh_joysticks(self) -> None:
        """Rebuild the active joystick list to support controller hot-plugging."""
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            if not joystick.get_init():
                joystick.init()
            self.joysticks.append(joystick)

    def quit_combo_pressed(self):
        """Return True if the START + SELECT + L1 + R1 quit chord is held on any controller."""
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
            event (pygame.event.Event): The event to inspect.

        Returns:
            bool: True if the event was a hotplug event and was handled.
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
    # GAMEPLAY ACTIONS
    # -------------------------

    # -------------------------
    # AUDIO / VOLUME ACTIONS
    # -------------------------

    # -------------------------
    # EVENT HANDLING
    # -------------------------

    def _process_events(self, delta_time: float) -> None:
        """Drain pygame's event queue and dispatch by event type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()

    # -------------------------
    # PER-FRAME UPDATE / RENDER
    # -------------------------

    def run(self) -> None:
        """Main game loop: pump events, advance world, render, repeat."""
        last_time = time.time()  # Track time for delta_time so animations are frame-rate independent.
        while True:
            delta_time = time.time() - last_time
            last_time = time.time()

            if self.quit_combo_pressed():
                self.close_game()

            self._process_events(delta_time)
            # world_speed_multiplier = self._world_speed_multiplier()
            # self._update_music()
            # self._update_world(delta_time, world_speed_multiplier)
            # self._render_frame(delta_time, world_speed_multiplier)
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)
            

# Main execution
if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()