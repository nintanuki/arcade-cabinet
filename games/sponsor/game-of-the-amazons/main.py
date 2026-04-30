from __future__ import annotations
import sys
import pygame
from core.board import Board, queen_piece_for
from core.turn_manager import TurnManager, PHASE_MOVE, PHASE_SHOOT
from core.animation import PieceAnimator, ArrowAnimator
from ui.board_view import BoardView
from ui.crt import CRT
from ui.hud import HUD
from systems.audio import AudioManager
from settings import *


class GameManager:
    """Top-level coordinator: input, animation, board state, and render."""

    def __init__(self, start_fullscreen: bool = False):
        """Boot pygame, create the board / view stack, and seed cursor state.

        Args:
            start_fullscreen: Whether to flip into fullscreen on startup,
                used by reset_game so a restart preserves the prior mode.

        Returns:
            None.
        """
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
        self.arrow_animation = ArrowAnimator()

        # Cursor State
        self.cursor_pos = [0, 0]  # [col, row]
        self.selected_pos = None  # None or (col, row)
        # In SHOOT phase the queen is implicitly "the tile we just moved to";
        # we cache that here so input and the AI hand-off both know the origin
        # of the upcoming arrow without re-deriving it.
        self.shoot_origin = None

        self.crt = CRT(self.screen)
        self.audio = AudioManager()
    # -------------------------
    # BOOT / SETUP
    # -------------------------

    def setup_controllers(self) -> None:
        """Cache currently-connected controllers so quit-combo and event polling are cheap.

        Returns:
            None.
        """
        pygame.joystick.init()
        self.connected_joysticks = [
            pygame.joystick.Joystick(index)
            for index in range(pygame.joystick.get_count())
        ]

    def reset_game(self):
        """Restart the game by creating a fresh GameManager instance.

        This is safer than trying to manually reset every subsystem,
        because it reuses the same startup path the game already uses
        when it first launches.

        Returns:
            None. Exits the process via sys.exit() when the new manager
            finishes its loop.
        """
        current_surface = pygame.display.get_surface()
        was_fullscreen = bool(current_surface and (current_surface.get_flags() & pygame.FULLSCREEN))

        new_game_manager = GameManager(start_fullscreen=was_fullscreen)
        new_game_manager.run()
        sys.exit()

    def close_game(self) -> None:
        """Close the game process cleanly.

        Returns:
            None.
        """
        pygame.quit()
        sys.exit()

    def quit_combo_pressed(self) -> bool:
        """Return True if START + SELECT + L1 + R1 are held on any controller.

        Returns:
            True if the quit chord is held on at least one connected joystick.
        """
        required_buttons = InputSettings.JOY_BUTTON_QUIT_COMBO
        for joystick in self.connected_joysticks:
            if all(joystick.get_button(button) for button in required_buttons):
                return True
        return False

    # -------------------------
    # INPUT
    # -------------------------

    

    def _handle_navigation(self, event) -> bool:
        """Translate arrow keys into cursor movement.

        Args:
            event: pygame KEYDOWN event.

        Returns:
            True if the event was a recognised navigation key, False otherwise.
        """
        if event.key == pygame.K_UP and self.cursor_pos[1] < 9:
            self.cursor_pos[1] += 1
            return True
        if event.key == pygame.K_DOWN and self.cursor_pos[1] > 0:
            self.cursor_pos[1] -= 1
            return True
        if event.key == pygame.K_LEFT and self.cursor_pos[0] > 0:
            self.cursor_pos[0] -= 1
            return True
        if event.key == pygame.K_RIGHT and self.cursor_pos[0] < 9:
            self.cursor_pos[0] += 1
            return True
        return False

    def _handle_confirm_action(self) -> None:
        """Route the confirm button (SPACE / A) to the appropriate phase handler.

        Returns:
            None.
        """
        # Block input while an animation is playing so the player cannot
        # queue a follow-up before the previous move has settled.
        if self.piece_animation.is_animating or self.arrow_animation.is_animating:
            return
        # Only the human (WHITE) drives selection through the confirm button.
        if self.turn.current_player != "WHITE":
            return

        if self.turn.phase == PHASE_MOVE:
            self._handle_move_phase_space()
        elif self.turn.phase == PHASE_SHOOT:
            self._handle_shoot_phase_space()

    def _handle_move_phase_space(self) -> None:
        """Pick up a queen, then choose a destination, on consecutive presses.

        Returns:
            None.
        """
        col, row = self.cursor_pos
        current_tile = self.board.tile_at(col, row)

        if self.selected_pos is None:
            # Attempt to select a piece — only the active player's color counts.
            allowed_piece = queen_piece_for(self.turn.current_player)
            if current_tile.piece == allowed_piece:
                self.selected_pos = (col, row)
            return

        if self.board.is_valid_path(self.selected_pos, (col, row)):
            piece_type = self.board.tile_at(*self.selected_pos).piece
            self.piece_animation.start(piece_type, self.selected_pos, (col, row))
            # Hide the queen from the board while it is mid-slide so it does
            # not get drawn twice.
            self.board.tile_at(*self.selected_pos).piece = None
            self.selected_pos = None
        else:
            # If move was invalid, just deselect
            self.selected_pos = None

    def _handle_shoot_phase_space(self) -> None:
        """Fire the moved queen's arrow at the cursor tile if reachable.

        Returns:
            None.
        """
        target = tuple(self.cursor_pos)
        if self.shoot_origin is None:
            return
        if not self.board.is_valid_path(self.shoot_origin, target):
            return
        self.arrow_animation.start(self.shoot_origin, target)
        self.audio.play('shoot')

    def _handle_space_press(self) -> None:
        """Treat SPACE as the per-phase confirm for the human player.

        Returns:
            None.
        """
        self._handle_confirm_action()

    def _handle_joyhatmotion(self, event) -> None:
        # event.value is (x, y) -> (-1, 0) is left, (0, 1) is up
        dx, dy = event.value
        
        # Movement logic (Clamped to board 0-9)
        if dx == -1 and self.cursor_pos[0] > 0: self.cursor_pos[0] -= 1
        elif dx == 1 and self.cursor_pos[0] < 9: self.cursor_pos[0] += 1
        
        # Pygame 'Up' is 1, but your grid logic says Y increases as it goes up
        if dy == 1 and self.cursor_pos[1] < 9: self.cursor_pos[1] += 1
        elif dy == -1 and self.cursor_pos[1] > 0: self.cursor_pos[1] -= 1

    def _handle_joybuttondown(self, event) -> None:
        """Route one controller button press.

        Args:
            event: pygame JOYBUTTONDOWN event.

        Returns:
            None.
        """
        # Catch the multi-button quit chord on press for instant response;
        # the outer per-frame check covers held-state quits.
        if self.quit_combo_pressed():
            self.close_game()

        # BACK (SELECT) is the global fullscreen toggle.
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()

        # Confirm Button (A / Button 0)
        if event.button == InputSettings.JOY_BUTTON_A:
            self._handle_confirm_action()

        if self.turn.game_over:
            if event.button == InputSettings.JOY_BUTTON_START:
                self.reset_game()

    def _handle_keydown(self, event) -> None:
        """Route one keyboard press for fullscreen, exit, navigation, and selection.

        Args:
            event: pygame KEYDOWN event.

        Returns:
            None.
        """
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return
        if event.key == pygame.K_ESCAPE:
            # ESC always exits the game and returns to the launcher, matching
            # the L1+R1+START+SELECT controller combo.
            self.close_game()
            return

        if self.turn.game_over:
            # During game over only allow the restart shortcut; ignore cursor
            # navigation and SPACE so stray input cannot edit the final board.
            if event.key == pygame.K_RETURN:
                self.reset_game()
            return

        if self._handle_navigation(event):
            return

        if event.key == pygame.K_SPACE:
            self._handle_space_press()

    def _process_events(self) -> None:
        """Drain pygame's event queue and dispatch by event type.

        Returns:
            None.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_joybuttondown(event)
            elif event.type == pygame.JOYHATMOTION:
                self._handle_joyhatmotion(event)

    # -------------------------
    # PHASE TRANSITIONS
    # -------------------------

    def _start_move_sequence(self, start_pos, end_pos):
        """Initiate the AI queen-slide animation and detach the piece from the board.

        Args:
            start_pos: (col, row) the queen is leaving.
            end_pos: (col, row) the queen will arrive at.

        Returns:
            None.
        """
        piece_type = self.board.tile_at(*start_pos).piece
        self.piece_animation.start(piece_type, start_pos, end_pos)
        self.board.tile_at(*start_pos).piece = None  # Hide from board

    def _finalize_move(self):
        """Place the moved queen on its new tile and switch into SHOOT phase.

        Returns:
            None.
        """
        move_data = self.piece_animation.moving_piece
        target = move_data['end_grid']
        self.board.tile_at(*target).piece = move_data['type']
        self.piece_animation.moving_piece = None

        # Parking the cursor on the queen makes the human's first SHOOT input
        # land on a valid tile (the queen itself blocks, so SPACE is a no-op
        # until they nudge to the target — but it gives an obvious anchor).
        self.cursor_pos = [target[0], target[1]]
        self.shoot_origin = target
        self.turn.begin_shoot_phase()

        # The AI committed to its arrow target before the slide began, so
        # kick off the second leg automatically.
        if self.turn.current_player == "BLACK":
            arrow_target = self.turn.consume_pending_arrow_target()
            if arrow_target is not None:
                self.arrow_animation.start(self.shoot_origin, arrow_target)
                self.audio.play('shoot')

    def _finalize_arrow(self):
        """Stamp the arrow on its tile, clear flight state, and end the turn.

        Returns:
            None.
        """
        landing = self.arrow_animation.landing_tile()
        self.board.place_arrow(landing)
        self.arrow_animation.clear()

        self.shoot_origin = None
        self.selected_pos = None
        self.turn.switch_turn()

    # -------------------------
    # PER-FRAME UPDATE
    # -------------------------

    def _update_game_state(self):
        """Advance any active animation and decide whether the AI should act.

        Returns:
            None.
        """
        # Process the queen slide first; an AI turn finishes inside
        # _finalize_move by kicking off the arrow leg.
        if self.piece_animation.update():
            self._finalize_move()

        if self.arrow_animation.update():
            self._finalize_arrow()

        if self.turn.game_over:
            return

        if self._animations_running():
            return

        if self.turn.current_player == "BLACK" and self.turn.phase == PHASE_MOVE:
            ai_move = self.turn.update_ai()
            if ai_move:
                self._start_move_sequence(*ai_move)

    def _animations_running(self) -> bool:
        """Return True if any animator is mid-flight.

        Returns:
            True if either the queen or arrow animator is currently animating.
        """
        return self.piece_animation.is_animating or self.arrow_animation.is_animating

    # -------------------------
    # RENDER
    # -------------------------

    def _push_hud_state(self) -> None:
        """Mirror the current turn / phase / game-over state into the HUD.

        Returns:
            None.
        """
        self.hud.current_player = self.turn.current_player
        self.hud.current_phase = self.turn.phase
        self.hud.game_over = self.turn.game_over
        self.hud.winner = self.turn.winner
        self.hud.win_condition = self.turn.win_condition
        self.hud.territory_totals = self.turn.territory_totals

    def _render_frame(self) -> None:
        """Compose one frame: background, board, HUD, then CRT.

        Returns:
            None.
        """
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        self._push_hud_state()

        # Ask the animators if there is a piece / arrow to draw that isn't
        # yet committed to the board grid.
        anim_data = self.piece_animation.get_render_data()
        arrow_data = self.arrow_animation.get_render_data()

        # Pass cursor states to the view
        self.board_view.draw(
            self.screen,
            self.cursor_pos,
            self.selected_pos,
            anim_data,
            arrow_data,
        )
        self.hud.draw(self.screen)

        # Apply CRT pass after world/UI rendering.
        self.crt.draw()

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def run(self):
        """Run the main game loop until the player quits.

        Returns:
            None. Loops forever; exits the process via close_game().
        """
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
