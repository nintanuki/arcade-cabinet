"""Run score model for gameplay sessions."""


class Score:
    """Tracks a single run's score. Owned by PlayScene."""

    def __init__(self):
        """Initialize counters for one gameplay run."""
        self.fish_eaten = 0
        self.size_eaten = 0

    def add(self, fish_size: int) -> None:
        """Accumulate score from an eaten fish.

        Args:
            fish_size: Width of the eaten fish in pixels.
        """
        self.fish_eaten += 1
        self.size_eaten += fish_size

    @property
    def total(self) -> int:
        """The number persisted on the leaderboard. Equals size_eaten."""
        return self.size_eaten