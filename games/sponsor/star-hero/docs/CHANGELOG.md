# Change Log

This file is an append-only record of every code change made to Dungeon Digger
by a human, AI assistant, or copilot tool. Read it before making changes so you
know the current state of the codebase.

## Format

Each entry covers one logical change (which may touch multiple files). Use the
template below, with one `**File:** ... **Why:** ...` block per file touched.

    ## YYYY-MM-DD HH:MM — short summary

    **File:** path/to/file.py
    **Lines (at time of edit):** 38-52 (modified)
    **Before:**
        [old code]
    **After:**
        [new code]
    **Why:** explanation

## Conventions

* Line numbers reflect the file as it existed at the moment of the edit. Edits
  above shift line numbers below, so older entries will not match the current
  file. Never go back and "fix" old line numbers.
* Entries are append-only. Never delete history. If a later edit reverts an
  earlier one, write a new entry that references the original.
* For new files, write `(new file)` instead of a line range. The "Before"
  block can be omitted or marked `(file did not exist)`.
* For deletes, write `(deleted)` and put the removed code in "Before" with no
  "After" block.
* Keep "Before" / "After" blocks short. If a change is huge, summarize with a
  diff-style excerpt of the most important lines plus a sentence describing the
  rest, instead of pasting the entire file.

## 2026-04-29 23:18 — Reorganize source tree to match Dungeon Digger layout (Claude Opus 4.7)

The flat top-level layout (`animations.py`, `audio.py`, `debug.py`, `sprites.py`,
`style.py`, plus four manager classes living inside `main.py`) was reorganized
into the same `core/`, `systems/`, `ui/`, `tools/` package layout that
Dungeon Digger uses. No behavior or class/function names changed; this is a
pure structural move with import-path updates. Empty `__init__.py` files were
added in every new package, matching the Dungeon Digger pattern.

**File:** `core/__init__.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** (empty)
**Why:** Make `core` a Python package so `from core.sprites import ...` works.

**File:** `core/sprites.py`
**Lines (at time of edit):** (new file, copied from `sprites.py`)
**Before:** (file did not exist; previously `star-hero/sprites.py`)
**After:** Same content as the deleted `sprites.py` (Laser, BombProjectile,
BombBlast, Player, Alien, PowerUp).
**Why:** Group gameplay entities under `core/`, mirroring
`dungeon-digger/core/sprites.py`.

**File:** `core/animations.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist; the same code lived in `star-hero/animations.py`
alongside the `CRT` class.)
**After:** Contains only `Background` and `Explosion`.
**Why:** Sprite-style entities belong in `core/`; the unrelated `CRT` overlay
moved to `ui/` per the Dungeon Digger split.

**File:** `ui/__init__.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** (empty)
**Why:** Make `ui` a Python package.

**File:** `ui/crt.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist; `CRT` class was inside `animations.py`)
**After:** Contains only the `CRT` class, unchanged. Imports `pygame`,
`random`, and `from settings import *`.
**Why:** Match `dungeon-digger/ui/crt.py` exactly — overlay/UI code lives in
`ui/`, gameplay sprites do not.

**File:** `ui/style.py`
**Lines (at time of edit):** (new file, copied from `style.py`)
**Before:** (file did not exist; previously `star-hero/style.py`)
**After:** Same content as the deleted `style.py`.
**Why:** Move HUD/menu rendering under `ui/`, mirroring
`dungeon-digger/ui/render.py`. Class name `Style` preserved per the
"do not change names if not necessary" rule.

**File:** `systems/__init__.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** (empty)
**Why:** Make `systems` a Python package.

**File:** `systems/audio.py`
**Lines (at time of edit):** (new file, copied from `audio.py`)
**Before:** (file did not exist; previously `star-hero/audio.py`)
**After:** Same content as the deleted `audio.py`.
**Why:** Match `dungeon-digger/systems/audio.py`.

**File:** `systems/managers.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist; the four classes lived in
`main.py` lines 11–574)
**After:** Contains `CollisionManager`, `ScoreManager`,
`SessionStateManager`, and `SpawnDirector` exactly as they were in
`main.py`, plus the imports they need (`os`, `json`, `random`, `pygame`,
`from settings import *`, `from core.sprites import Laser, Alien, PowerUp`).
**Why:** Keep `GameManager` light by offloading its inline manager classes
to a dedicated module, mirroring `dungeon-digger/systems/managers.py`.

**File:** `systems/managers.py`
**Lines (at time of edit):** ScoreManager.__init__ and ScoreManager.save_scores
**Before:**
    score_file_path = os.path.join(os.path.dirname(__file__), 'high_score.txt')
**After:**
    score_file_path = os.path.join(AssetPaths.BASE_DIR, 'high_score.txt')
**Why:** Moving the manager into `systems/` would change `__file__` from the
game root to `systems/`, which would orphan the existing `high_score.txt` at
the game root and silently start a new save file. Anchoring the path to
`AssetPaths.BASE_DIR` (already defined in `settings.py`) keeps the file
exactly where players' saves already live.

**File:** `tools/__init__.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** (empty)
**Why:** Make `tools` a Python package.

**File:** `tools/debug.py`
**Lines (at time of edit):** (new file, copied from `debug.py`)
**Before:** (file did not exist; previously `star-hero/debug.py`)
**After:** Same content as the deleted `debug.py`.
**Why:** Match `dungeon-digger/tools/`, the home for dev/debug helpers
that the game does not import at runtime.

**File:** `main.py`
**Lines (at time of edit):** 1–1038 (rewritten)
**Before:** A 1038-line file containing `CollisionManager`, `ScoreManager`,
`SessionStateManager`, `SpawnDirector`, and `GameManager`, with imports
`from animations import Background, Explosion, CRT`,
`from sprites import Laser, Player, Alien, PowerUp, BombBlast`,
`from style import Style`, `from audio import Audio`.
**After:** A 481-line file with only `GameManager` and the entry-point
guard. Imports updated to:
    from core.animations import Background, Explosion
    from core.sprites import Player, BombBlast
    from ui.style import Style
    from ui.crt import CRT
    from systems.audio import Audio
    from systems.managers import (
        CollisionManager,
        ScoreManager,
        SessionStateManager,
        SpawnDirector,
    )
The previously-imported `Laser`, `Alien`, and `PowerUp` are no longer used
in `main.py` (they are referenced only inside `SpawnDirector`, which now
lives in `systems/managers.py`), so they were dropped from the import list.
The unused `import json` and `import os` at the top of the original
`main.py` were also dropped.
**Why:** Keep `GameManager` light per `TESTING.md` and avoid dead
imports. Behavior is unchanged.

**File:** `animations.py` (deleted)
**Before:** Contained `Background`, `Explosion`, and `CRT`.
**Why:** Content split into `core/animations.py` and `ui/crt.py`.

**File:** `audio.py` (deleted)
**Before:** Contained the `Audio` class.
**Why:** Moved unchanged to `systems/audio.py`.

**File:** `debug.py` (deleted)
**Before:** Contained the `debug()` helper.
**Why:** Moved unchanged to `tools/debug.py`.

**File:** `sprites.py` (deleted)
**Before:** Contained `Laser`, `BombProjectile`, `BombBlast`, `Player`,
`Alien`, `PowerUp`.
**Why:** Moved unchanged to `core/sprites.py`.

**File:** `style.py` (deleted)
**Before:** Contained the `Style` class.
**Why:** Moved unchanged to `ui/style.py`.
