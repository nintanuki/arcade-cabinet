from __future__ import annotations
import sys
import pygame
from core.board import Board
from core.turn_manager import TurnManager
from core.animation import PieceAnimator
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
        self.piece_animation = PieceAnimator()

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
            # Prevent input if an animation is already playing
            if self.piece_animation.is_animating:
                return

            col, row = self.cursor_pos
            current_tile = self.board.tile_at(col, row)

            if self.selected_pos is None:
                # Attempt to select a piece
                # only allow selecting pieces of the current player's color
                allowed_piece = "white_queen" if self.turn.current_player == "WHITE" else "black_queen"
                if current_tile.piece == allowed_piece:
                    self.selected_pos = (col, row)
            else:
                # CHECK if valid, but DON'T move it yet
                if self.board.is_valid_path(self.selected_pos, (col, row)):
                    piece_type = self.board.tile_at(*self.selected_pos).piece
                    # Start the visual slide
                    self.piece_animation.start(piece_type, self.selected_pos, (col, row))
                    # Remove from board temporarily so it doesn't draw in two places
                    self.board.tile_at(*self.selected_pos).piece = None 
                    self.selected_pos = None
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

    def _update_game_state(self):
        """Advances animations and checks AI timers."""
        # 1. Process active animations[cite: 6]
        if self.piece_animation.update():
            self._finalize_move()

        # 2. Check if AI needs to start a move
        if not self.piece_animation.is_animating and self.turn.current_player == "BLACK":
            ai_move = self.turn.update_ai() 
            if ai_move:
                self._start_move_sequence(*ai_move)

    def _start_move_sequence(self, start_pos, end_pos):
        """Initiates the transition from logic to animation[cite: 6, 7]."""
        piece_type = self.board.tile_at(*start_pos).piece
        self.piece_animation.start(piece_type, start_pos, end_pos)
        self.board.tile_at(*start_pos).piece = None # Hide from board[cite: 7]

    def _finalize_move(self):
        """Place the piece on its new tile and swap turns[cite: 7, 8]."""
        move_data = self.piece_animation.moving_piece
        target = move_data['end_grid']
        self.board.tile_at(*target).piece = move_data['type']
        self.piece_animation.moving_piece = None
        self.turn.switch_turn()

    def _render_frame(self) -> None:
        """Compose one frame: background, board, HUD, then CRT."""
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        self.hud.current_player = self.turn.current_player

        # Ask the animator if there's a piece to draw that isn't on the board yet
        anim_data = self.piece_animation.get_render_data()

        # Pass cursor states to the view
        self.board_view.draw(self.screen, self.cursor_pos, self.selected_pos, anim_data)
        self.hud.draw(self.screen)

        # Apply CRT pass after world/UI rendering.
        self.crt.draw()

    def run(self):
        """Run the main game loop until the player quits."""
        while True:
            if self.quit_combo_pressed():
                self.close_game()
            self._process_events()
            self._update_game_state()
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
