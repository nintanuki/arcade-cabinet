"""High-level coordination managers.

Each manager owns one slice of cross-cutting state so GameManager
itself can stay thin. The subdivision mirrors Star Hero so a developer
already familiar with that codebase will find the same names here.
"""

from settings import ScoreSettings


class ScoreManager:
    """Tracks the current run's score, the persistent high score, and initials entry.

    Persistence is unimplemented while the game is being scaffolded. The
    public ``save_scores`` / ``load_scores`` methods are no-ops so the
    rest of the engine can call them without crashing.
    """

    def __init__(self, game_manager) -> None:
        """Bind back to the game manager and initialize score state.

        Args:
            game_manager: The owning GameManager instance.
        """
        self.game = game_manager
        self.score = 0
        self.high_score = 0
        self.entering_initials = False
        self.initials = ScoreSettings.DEFAULT_INITIALS
        self.initials_index = 0

        # Save data dict is the structure the leaderboard renderer will
        # ultimately read from. Empty for now.
        self.save_data: dict = {}

    # -------------------------
    # SCORING
    # -------------------------

    def add_match_score(self, blocks_cleared: int, chain_depth: int) -> None:
        """Award points for a single match resolution.

        Args:
            blocks_cleared: Number of blocks popped by this match.
            chain_depth: Depth of the chain this match belongs to. 1 is
                the player-initiated match; 2+ are cascading chains.
        """
        # TODO: pull POINTS_PER_BLOCK, COMBO_BONUS, and CHAIN_BONUS
        # from ScoreSettings and combine them into the score delta.
        _ = blocks_cleared
        _ = chain_depth

    # -------------------------
    # PERSISTENCE
    # -------------------------

    def save_scores(self) -> None:
        """Write the current high score and leaderboard out to disk."""
        # TODO: serialize self.high_score (and any leaderboard rows) to
        # ScoreSettings.HIGH_SCORE_FILE.
        pass

    def load_scores(self) -> None:
        """Load any persisted high score and leaderboard from disk."""
        # TODO: deserialize ScoreSettings.HIGH_SCORE_FILE if it exists.
        pass

    def finalize_game_over_score(self) -> None:
        """Decide whether the just-finished run earned a leaderboard slot."""
        # TODO: compare self.score against the leaderboard threshold and
        # flip self.entering_initials accordingly.
        pass


class SessionStateManager:
    """Tracks whether a run is currently active and resets between runs."""

    def __init__(self, game_manager) -> None:
        """Bind back to the game manager and initialize session flags.

        Args:
            game_manager: The owning GameManager instance.
        """
        self.game = game_manager
        self.game_active = False
        self.player_alive = True
        self.play_intro_music = True

    def reset_for_new_game(self) -> None:
        """Clear per-run state and put the world back into "active" mode."""
        # TODO: reset the board, score, and any animation timers. For
        # now flipping the flag is enough to exercise the title-screen
        # event paths during scaffolding.
        self.game_active = True
        self.player_alive = True
        self.game.scores.score = 0

    def pause(self) -> None:
        """Enter the pause loop. Future work will spin a sub-loop here."""
        # TODO: implement pause loop. Star Hero's pattern is a good
        # reference: spin in a small while loop drawing a "PAUSED"
        # overlay until START is pressed again.
        pass
