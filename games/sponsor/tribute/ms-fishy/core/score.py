"""Run score model for gameplay sessions."""

from settings import ScoreSettings


class Score:
    """Tracks a single run's score. Owned by PlayScene."""

    def __init__(self):
        """Initialize counters for one gameplay run."""
        self.fish_eaten = 0
        self.size_eaten = 0
        # Set by PlayScene._end_run before transitioning to GameOverScene.
        self.final_weight: float = 0.0
        self.time_left_seconds: float = 0.0

    def add(self, fish_size: int) -> None:
        """Accumulate score from an eaten fish.

        Args:
            fish_size: Width of the eaten fish in pixels.
        """
        self.fish_eaten += 1
        self.size_eaten += fish_size

    @property
    def total(self) -> int:
        """Compound end-of-run score combining all tracked stats.

        Returns:
            Integer score computed from weight eaten, fish count, final
            player weight, and seconds remaining on the hunger timer.
        """
        return (
            self.size_eaten * ScoreSettings.WEIGHT_EATEN_FACTOR
            + self.fish_eaten * ScoreSettings.FISH_EATEN_BONUS
            + int(self.final_weight) * ScoreSettings.FINAL_WEIGHT_FACTOR
            + int(self.time_left_seconds) * ScoreSettings.TIME_LEFT_BONUS
        )