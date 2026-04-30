from __future__ import annotations
import sys
import pygame
from core.board import Board
from core.turn_manager import TurnManager
from ui.board_view import BoardView
from ui.crt import CRT
from ui.hud import HUD
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

        # Game state and views.
        self.board = Board()
        self.turn = TurnManager(self.board)
        self.board_view = BoardView(self.board)
        self.hud = HUD()

        # Cursor State
        self.cursor_pos = [0, 0] # [col, row]
        self.selected_pos = None # None or (col, row)

        self.crt = CRT(self.screen)

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

        # --- Navigation ---
        if event.key == pygame.K_UP and self.cursor_pos[1] < 9:
            self.cursor_pos[1] += 1
        elif event.key == pygame.K_DOWN and self.cursor_pos[1] > 0:
            self.cursor_pos[1] -= 1
        elif event.key == pygame.K_LEFT and self.cursor_pos[0] > 0:
            self.cursor_pos[0] -= 1
        elif event.key == pygame.K_RIGHT and self.cursor_pos[0] < 9:
            self.cursor_pos[0] += 1

        # --- Selection Logic ---
        elif event.key == pygame.K_SPACE:
            col, row = self.cursor_pos
            current_tile = self.board.tile_at(col, row)

            if self.selected_pos is None:
                # Attempt to select a piece
                # only allow selecting pieces of the current player's color
                allowed_piece = "white_queen" if self.turn.current_player == "WHITE" else "black_queen"
                if current_tile.piece == allowed_piece:
                    self.selected_pos = (col, row)
            else:
                # Move selected piece
                if self.board.move_piece(self.selected_pos, (col, row)):
                    self.selected_pos = None
                    self.turn.switch_turn() # Trigger the turn switch
                else:
                    # If move was invalid, just deselect
                    self.selected_pos = None

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
        """Compose one frame: background, board, HUD, then CRT."""
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        # Pass cursor states to the view
        self.board_view.draw(self.screen, self.cursor_pos, self.selected_pos)
        self.hud.draw(self.screen)

        # Apply CRT pass after world/UI rendering.
        self.crt.draw()

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
