from __future__ import annotations

import pygame
import sys

from core.sprites import Player
from systems.fish_manager import FishManager
from systems.audio_manager import AudioManager
from crt import CRT
from settings import (
    ColorSettings,
    FontSettings,
    GameStateSettings,
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

        self._create_gameplay_entities()
        self.game_state = GameStateSettings.PLAYING

        self.audio = AudioManager()

        # Post-processing: tracked separately because the CRT pass is skipped
        # when the player is already on a real CRT (i.e. fullscreen on the cabinet).
        self.full_screen = False
        self.crt = CRT(self.screen)

    def _initialize_audio_mixer(self) -> None:
        """Initialize pygame's mixer early so music and SFX are available."""
        if pygame.mixer.get_init():
            return
        try:
            pygame.mixer.init()
        except pygame.error as error:
            print(f"Audio mixer initialization failed: {error}")

    def _load_fonts(self) -> None:
        """Load UI fonts used by pause and game-over overlays."""
        self.overlay_font = pygame.font.Font(FontSettings.FONT, UiSettings.OVERLAY_FONT_SIZE)

    def _create_gameplay_entities(self) -> None:
        """Build player, enemy container, and fish manager for one session."""
        self.player = Player(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.enemy_sprites = pygame.sprite.Group()
        self.fish_manager = FishManager(self.enemy_sprites)

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
        """Restart the game by replacing the current GameManager with a fresh one.

        This is safer than resetting each subsystem by hand because it reuses
        the same startup path the game uses on first launch.
        """
        current_surface = pygame.display.get_surface()
        was_fullscreen = bool(current_surface and (current_surface.get_flags() & pygame.FULLSCREEN))

        new_game_manager = GameManager(start_fullscreen=was_fullscreen)
        new_game_manager.run()
        sys.exit()

    def restart_session(self) -> None:
        """Restart gameplay entities and return to the active playing state."""
        self._create_gameplay_entities()
        self.game_state = GameStateSettings.PLAYING
        self.audio.resume_music()

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

    def _handle_keydown(self, event) -> None:
        """Route one keyboard press to the appropriate UI/gameplay handler."""
        # Esc is the keyboard quit; useful while developing without a controller.
        if event.key == pygame.K_ESCAPE:
            self.close_game()

        if event.key == pygame.K_RETURN:
            self._handle_enter_key()

        # F11 fullscreen toggle is global and intentionally falls through so
        # other handlers still see the press.
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            self.full_screen = not self.full_screen

    def _handle_enter_key(self) -> None:
        """Handle Enter as pause/resume/restart based on the current game state."""
        if self.game_state == GameStateSettings.PLAYING:
            self.game_state = GameStateSettings.PAUSED
            self.audio.pause_music()
            self.audio.play_pause_in_sound()
            return

        if self.game_state == GameStateSettings.PAUSED:
            self.game_state = GameStateSettings.PLAYING
            self.audio.play_pause_out_sound()
            self.audio.resume_music()
            return

        if self.game_state == GameStateSettings.GAME_OVER:
            self.restart_session()

    def _handle_joybuttondown(self, event) -> None:
        """Route one controller button press."""
        # Catch the multi-button quit chord on press for instant response;
        # the outer per-frame check covers held-state quits.
        if self.quit_combo_pressed():
            self.close_game()

        # BACK is the global fullscreen toggle and falls through.
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()
            self.full_screen = not self.full_screen

    def _handle_joyhatmotion(self, event) -> None:
        """Route a D-pad direction event."""
        pass

    def _handle_joyaxismotion(self, event) -> None:
        """Route a joystick or trigger motion event."""
        pass

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
        """Advance all game systems by one frame; ignored while not playing."""
        if self.game_state != GameStateSettings.PLAYING:
            return

        self.all_sprites.update()
        self.enemy_sprites.update()
        if self.fish_manager.update(self.player):
            self.game_state = GameStateSettings.GAME_OVER
            self.audio.stop_music()

    def _render_frame(self) -> None:
        """Draw the current game state to the screen, then apply the CRT pass."""
        if self.game_state == GameStateSettings.PLAYING:
            self.screen.fill(ColorSettings.BG_COLOR)
            self.all_sprites.draw(self.screen)
            self.enemy_sprites.draw(self.screen)
        elif self.game_state == GameStateSettings.PAUSED:
            self.screen.fill(ColorSettings.BLACK)
            self._draw_centered_overlay(UiSettings.PAUSE_TEXT)
        elif self.game_state == GameStateSettings.GAME_OVER:
            self.screen.fill(ColorSettings.BLACK)
            self._draw_centered_overlay(UiSettings.GAME_OVER_TEXT)

        # Apply CRT pass after world/UI rendering.
        if not self.full_screen:
            self.crt.draw()

    def _draw_centered_overlay(self, title_text: str) -> None:
        """Draw one centered overlay title for pause and game-over screens.

        Args:
            title_text: Main large text line.
        """
        title_surface = self.overlay_font.render(title_text, True, ColorSettings.WHITE)
        title_rect = title_surface.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))

        self.screen.blit(title_surface, title_rect)

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
