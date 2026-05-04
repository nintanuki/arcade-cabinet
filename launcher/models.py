"""Data models for the arcade launcher."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StudentGameRecord:
    """
    Discovered metadata for a single student-contributed game.

    Sponsor games are curated in settings.GameSettings; student games are
    scanned from disk so a teacher can drop a folder into games/student/
    without editing any code. Records bundle every override the launcher
    might apply (label, attribution, preview, input scheme, free-form
    note, under-construction flag) so the merge step in
    ArcadeLauncher._build_games stays straightforward.
    """

    label: str
    main_path: Path
    attribution: str
    preview_path: Path | None
    input_scheme_key: str | None
    note: str | None
    under_construction: bool


@dataclass
class MenuNode:
    """
    One row in a menu frame.

    A node is either a game (selecting it launches a subprocess) or a
    submenu (selecting it pushes its children onto the menu stack). The
    game-only fields stay at their defaults on submenu nodes; the
    ``children`` list stays empty on game nodes and on category leaves
    that currently have no games (e.g. an empty Student Games folder).
    """

    kind: str  # "game" or "submenu"
    label: str
    description: str = ""
    children: list["MenuNode"] = field(default_factory=list)
    # Game-only fields below. Defaults match "no metadata available".
    main_path: Path | None = None
    preview_path: Path | None = None
    preview_label: str | None = None
    attribution: str = ""
    input_scheme_key: str | None = None
    note: str | None = None
    under_construction: bool = False
    category_key: str | None = None


@dataclass
class MenuFrame:
    """
    One level on the navigation stack.

    Tracks the items rendered for this level plus the cursor position so
    that backing out and re-entering a submenu lands on the same row.
    """

    items: list[MenuNode]
    selected_index: int = 0
