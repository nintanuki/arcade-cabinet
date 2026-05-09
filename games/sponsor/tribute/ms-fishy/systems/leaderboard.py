"""Leaderboard persistence and ranking service."""

from __future__ import annotations

import json
import os
import re
import tempfile
from typing import TypedDict

from settings import AssetPaths


class LeaderboardEntry(TypedDict):
    """One leaderboard row persisted to disk."""

    initials: str
    score: int


class Leaderboard:
    """Top-10 scoreboard with initials persisted to JSON."""

    MAX_ENTRIES = 10

    def __init__(self) -> None:
        """Initialize an empty leaderboard model."""
        self._entries: list[LeaderboardEntry] = []

    def load(self) -> None:
        """Load leaderboard entries from disk, defaulting to empty when missing."""
        if not os.path.exists(AssetPaths.LEADERBOARD):
            self._entries = []
            return

        try:
            with open(AssetPaths.LEADERBOARD, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            self._entries = []
            return

        if not isinstance(data, list):
            self._entries = []
            return

        loaded_entries: list[LeaderboardEntry] = []
        for item in data:
            if not isinstance(item, dict):
                continue

            initials = item.get("initials")
            score = item.get("score")
            if not isinstance(initials, str) or not self._is_valid_initials(initials):
                continue
            if not isinstance(score, int):
                continue

            loaded_entries.append({"initials": initials.upper(), "score": score})

        self._entries = self._sorted_truncated(loaded_entries)

    def save(self) -> None:
        """Persist leaderboard entries to disk with an atomic replace."""
        leaderboard_dir = os.path.dirname(AssetPaths.LEADERBOARD)
        os.makedirs(leaderboard_dir, exist_ok=True)

        file_descriptor, temp_path = tempfile.mkstemp(
            prefix="leaderboard_",
            suffix=".tmp",
            dir=leaderboard_dir,
            text=True,
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as temp_file:
                json.dump(self._entries, temp_file, indent=2)
                temp_file.write("\n")
            os.replace(temp_path, AssetPaths.LEADERBOARD)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def qualifies(self, score: int) -> bool:
        """Return whether a score can enter the current top-10 table."""
        if not isinstance(score, int):
            return False

        if len(self._entries) < self.MAX_ENTRIES:
            return True

        lowest_score = self._entries[-1]["score"]
        return score > lowest_score

    def submit(self, initials: str, score: int) -> int | None:
        """Insert or update one leaderboard entry.

        Args:
            initials: Three-letter player initials.
            score: Score value for the run.

        Returns:
            0-based rank if accepted, else None.

        Raises:
            ValueError: If initials are not exactly three A-Z letters.
        """
        if not isinstance(score, int):
            raise ValueError("score must be an integer")

        normalized_initials = initials.upper().strip()
        if not self._is_valid_initials(normalized_initials):
            raise ValueError("initials must be exactly 3 letters A-Z")

        for entry in self._entries:
            if entry["initials"] == normalized_initials:
                if score > entry["score"]:
                    entry["score"] = score
                    self._entries = self._sorted_truncated(self._entries)
                    return self._index_of_initials(normalized_initials)
                return None

        if len(self._entries) < self.MAX_ENTRIES:
            self._entries.append({"initials": normalized_initials, "score": score})
            self._entries = self._sorted_truncated(self._entries)
            return self._index_of_initials(normalized_initials)

        lowest_score = self._entries[-1]["score"]
        if score <= lowest_score:
            return None

        self._entries.append({"initials": normalized_initials, "score": score})
        self._entries = self._sorted_truncated(self._entries)
        return self._index_of_initials(normalized_initials)

    def top(self) -> list[tuple[str, int]]:
        """Return high-to-low leaderboard entries as (initials, score) tuples."""
        return [(entry["initials"], entry["score"]) for entry in self._entries]

    def _index_of_initials(self, initials: str) -> int | None:
        """Return rank index for the provided initials, or None if missing."""
        for index, entry in enumerate(self._entries):
            if entry["initials"] == initials:
                return index
        return None

    def _is_valid_initials(self, initials: str) -> bool:
        """Validate three uppercase ASCII letters."""
        return bool(re.fullmatch(r"[A-Z]{3}", initials.upper()))

    def _sorted_truncated(
        self,
        entries: list[LeaderboardEntry],
    ) -> list[LeaderboardEntry]:
        """Sort entries and enforce max table length."""
        return sorted(entries, key=lambda item: item["score"], reverse=True)[: self.MAX_ENTRIES]
