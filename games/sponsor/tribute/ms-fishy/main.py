from __future__ import annotations

import pygame
import sys

from systems.audio_manager import AudioManager
from systems.leaderboard import Leaderboard
from systems.scene_manager import SceneManager
from crt import CRT
from settings import (
    ColorSettings,
    FontSettings,
    InputSettings,
    ScreenSettings,
    UiSettings,
)


class GameManager:
    """Coordinate game state, flow, rendering phases, and input orchestration."""

    def __init__(self, start_fullscreen: bool = False):
        """Initialize pygame, the display, the input cache, and post-processing.

        Args:
            start_fullscreen: Whether to launch directly in fullscreen mode.
        """

        pygame.init()
        self._initialize_audio_mixer()
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
        pygame.display.set_caption(ScreenSettings.TITLE)
        if start_fullscreen:
            pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()

        self.setup_controllers()
        self._load_fonts()

        self.audio = AudioManager()
        self.leaderboard = Leaderboard()
        self.leaderboard.load()

        # Post-processing: tracked separately because the CRT pass is skipped
        # when the player is already on a real CRT (i.e. fullscreen on the cabinet).
        self.full_screen = False
        self.crt = CRT(self.screen)

        # Scene management
        self.scenes = SceneManager()
        from ui.scenes.title_scene import TitleScene
        self.scenes.change_to(TitleScene(self))

    def _initialize_audio_mixer(self) -> None:
        """Initialize pygame's mixer early so music and SFX are available."""
        if pygame.mixer.get_init():
            return
        try:
            pygame.mixer.init()
        except pygame.error as error:
            print(f"Audio mixer initialization failed: {error}")

    def _load_fonts(self) -> None:
        """Load UI fonts used by overlays."""
        self.overlay_font = pygame.font.Font(FontSettings.FONT, UiSettings.OVERLAY_FONT_SIZE)

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
    # INPUT HANDLING
    # -------------------------

    def _toggle_fullscreen(self) -> None:
        """Flip fullscreen mode and keep the CRT-skip flag in sync."""
        pygame.display.toggle_fullscreen()
        self.full_screen = not self.full_screen

    def _handle_keydown(self, event) -> None:
        """Route one keyboard press to global handlers or scenes.
        
        Global handlers (Esc, F11) are processed here.
        Scene-specific events are forwarded to the current scene.
        """
        # Global: Esc quits
        if event.key == pygame.K_ESCAPE:
            self.close_game()

        # Global: F11 toggles fullscreen
        if event.key == pygame.K_F11:
            self._toggle_fullscreen()
            return  # Don't forward to scene

        # Forward to scene
        self.scenes.current.handle_event(event)

    def _handle_joybuttondown(self, event) -> None:
        """Route one controller button press to global handlers or scenes.
        
        Global handlers (quit-chord, BACK) are processed here.
        Scene-specific events are forwarded to the current scene.
        """
        # Catch the multi-button quit chord on press for instant response
        if self.quit_combo_pressed():
            self.close_game()

        # Global: BACK toggles fullscreen
        if event.button == InputSettings.JOY_BUTTON_BACK:
            self._toggle_fullscreen()
            return  # Don't forward to scene

        # Forward to scene
        self.scenes.current.handle_event(event)

    def _handle_joyhatmotion(self, event) -> None:
        """Route a D-pad direction event to the current scene."""
        self.scenes.current.handle_event(event)

    def _handle_joyaxismotion(self, event) -> None:
        """Route a joystick or trigger motion event to the current scene."""
        self.scenes.current.handle_event(event)

    def _process_events(self) -> None:
        """Drain pygame's event queue and dispatch by event type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_joybuttondown(event)
            elif event.type == pygame.JOYHATMOTION:
                self._handle_joyhatmotion(event)
            elif event.type == pygame.JOYAXISMOTION:
                self._handle_joyaxismotion(event)

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def _update_world(self) -> None:
        """Advance the current scene by one frame."""
        self.scenes.current.update()

    def _render_frame(self) -> None:
        """Render the current scene to the screen, then apply the CRT pass."""
        self.scenes.current.render(self.screen)

        # Apply CRT pass after scene rendering.
        if not self.full_screen:
            self.crt.draw()

    def run(self):
        """Run the main game loop until the player quits."""
        while True:
            if self.quit_combo_pressed():
                self.close_game()
            self._process_events()
            self._update_world()
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
