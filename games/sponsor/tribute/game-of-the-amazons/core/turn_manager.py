"""Turn / phase tracking and the random AI brain for the Black player.

Each player turn is two phases. MOVE is the queen slide; SHOOT is the arrow
fired from the queen's new tile. Both phases must complete before the turn
flips to the other color. After every full turn the manager re-evaluates
end-of-game conditions: a player who cannot complete a move-and-shoot loses,
and once amazons are walled off into separate territories we count squares.
"""
import random

import pygame


# Phase strings used by the manager and the HUD. Centralised to avoid drift
# between display strings and conditionals scattered across the code.
PHASE_MOVE = "MOVE"
PHASE_SHOOT = "SHOOT"

# End-of-game condition codes consumed by the HUD.
WIN_CONDITION_STALEMATE = "STALEMATE"
WIN_CONDITION_TERRITORY = "TERRITORY"
WIN_CONDITION_TERRITORY_TIE = "TERRITORY_TIE"


class TurnManager:
    """Tracks whose turn it is, what phase they are in, and end-game state."""

    def __init__(self, board):
        """Initialise turn state, AI timer, and the deferred-AI-plan slot.

        Args:
            board: The shared Board instance used for legality and AI planning.

        Returns:
            None.
        """
        self.board = board
        self.current_player = "WHITE"  # Human starts
        self.phase = PHASE_MOVE
        self.is_animating = False
        self.ai_timer = 0
        self.ai_delay = 1000  # 1 second pause before AI moves

        # End-of-game state, surfaced to HUD / main loop.
        self.game_over = False
        self.winner = None  # 'WHITE' or 'BLACK' or None on draw
        self.win_condition = None  # one of the WIN_CONDITION_* constants
        self.territory_totals = None  # populated for territory-based endings

        # The AI commits to its full move-and-shoot plan up front. The arrow
        # target is cached here so the GameManager can fire it after the
        # queen-slide animation has finished.
        self._pending_ai_arrow_target = None

    # -------------------------
    # PHASE TRANSITIONS
    # -------------------------

    def begin_shoot_phase(self):
        """Mark that the moved queen now needs to fire its arrow.

        Returns:
            None.
        """
        self.phase = PHASE_SHOOT

    def switch_turn(self):
        """Hand the turn to the other color and re-evaluate game-over rules.

        Returns:
            None.
        """
        self.phase = PHASE_MOVE
        self.current_player = "BLACK" if self.current_player == "WHITE" else "WHITE"
        self._pending_ai_arrow_target = None
        self.evaluate_game_over()
        if self.current_player == "BLACK" and not self.game_over:
            # Reset the AI thinking timer only after we know the game is still
            # live; avoids an AI move ever firing past game over.
            self.ai_timer = pygame.time.get_ticks()

    # -------------------------
    # AI PLANNING
    # -------------------------

    def trigger_ai_move(self):
        """Plan the AI's full move-and-shoot and return the queen slide.

        Picks a random queen, a random reachable destination, and a random
        legal arrow target from that destination. The arrow target is cached
        on the manager so the caller can fetch it after the queen animation.

        Returns:
            A tuple ((start_col, start_row), (end_col, end_row)) describing
            the queen's slide, or None if no legal full turn exists.
        """
        black_pieces = list(self.board.queens_of("BLACK"))
        random.shuffle(black_pieces)

        for start_tile in black_pieces:
            origin = (start_tile.col, start_tile.row)
            destinations = list(self.board.reachable_from(origin))
            random.shuffle(destinations)
            for destination in destinations:
                arrow_target = self._pick_random_arrow_target(origin, destination)
                if arrow_target is None:
                    continue
                self._pending_ai_arrow_target = arrow_target
                return origin, destination
        return None

    def consume_pending_arrow_target(self):
        """Return and clear the AI's cached arrow target.

        Returns:
            (col, row) of the planned arrow landing tile, or None if no AI
            plan is pending.
        """
        target = self._pending_ai_arrow_target
        self._pending_ai_arrow_target = None
        return target

    def _pick_random_arrow_target(self, origin, destination):
        """Find a random legal arrow target from destination after vacating origin.

        Simulates the queen actually moving (so the empty origin square counts
        as a valid pass-through / landing tile for the arrow), then restores
        the board so this stays a pure planning helper.

        Args:
            origin: (col, row) the queen is leaving.
            destination: (col, row) the queen is moving to.

        Returns:
            A random legal (col, row) the arrow can fly to, or None.
        """
        origin_tile = self.board.tile_at(*origin)
        destination_tile = self.board.tile_at(*destination)
        moving_piece = origin_tile.piece

        origin_tile.piece = None
        destination_tile.piece = moving_piece
        try:
            options = self.board.reachable_from(destination)
        finally:
            destination_tile.piece = None
            origin_tile.piece = moving_piece

        if not options:
            return None
        return random.choice(options)

    # -------------------------
    # GAME OVER EVALUATION
    # -------------------------

    def evaluate_game_over(self):
        """Apply the two end-game rules to the current board state.

        Returns:
            None. Updates self.game_over, self.winner, self.win_condition, and
            self.territory_totals on the manager when the game has ended.
        """
        if self.game_over:
            return

        # Territory rule first: if amazons are fully separated we score now,
        # without forcing the player to wiggle around in their own pocket.
        territory_totals = self.board.territory_counts()
        if territory_totals is not None:
            self._end_via_territory(territory_totals)
            return

        # Stalemate rule: if the player about to act has no legal full turn,
        # they lose immediately.
        if not self.board.has_any_legal_move(self.current_player):
            self.game_over = True
            self.winner = "BLACK" if self.current_player == "WHITE" else "WHITE"
            self.win_condition = WIN_CONDITION_STALEMATE

    def _end_via_territory(self, totals):
        """Record a territory-based ending using the supplied tile counts.

        Args:
            totals: Dict {'WHITE': int, 'BLACK': int} of empty squares each
                color controls in their now-isolated regions.

        Returns:
            None.
        """
        self.game_over = True
        self.territory_totals = totals
        if totals["WHITE"] > totals["BLACK"]:
            self.winner = "WHITE"
            self.win_condition = WIN_CONDITION_TERRITORY
        elif totals["BLACK"] > totals["WHITE"]:
            self.winner = "BLACK"
            self.win_condition = WIN_CONDITION_TERRITORY
        else:
            self.winner = None
            self.win_condition = WIN_CONDITION_TERRITORY_TIE

    # -------------------------
    # PER-FRAME UPDATE
    # -------------------------

    def update_ai(self):
        """Per-frame hook that returns an AI move once the delay has elapsed.

        Returns:
            ((start_col, start_row), (end_col, end_row)) when the AI is ready
            to begin its queen slide, else None.
        """
        if self.game_over:
            return None
        if self.current_player != "BLACK" or self.is_animating:
            return None
        if self.phase != PHASE_MOVE:
            return None
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_timer < self.ai_delay:
            return None
        return self.trigger_ai_move()
