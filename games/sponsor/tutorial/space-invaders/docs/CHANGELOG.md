# Change Log

Append-only record of every code change made to Space Invaders.

## Format

    ## YYYY-MM-DD HH:MM — short summary

    **File:** path/to/file.py
    **Lines (at time of edit):** 38-52 (modified)
    **Before:**
        [old code]
    **After:**
        [new code]
    **Why:** explanation
    **Editor:** name (AI model used, if any)

## Conventions

* Line numbers reflect the file at the moment of the edit; never go back to "fix" old line numbers.
* Append-only. Never delete history.
* For new files write `(new file)` instead of a line range.
* For deletes write `(deleted)` and put the removed code in "Before".

---

## 2026-05-12 — Refactor: star-hero-style folder layout + centralized settings

**Files:**
- `main.py` (rewritten; previously held controller helpers, `Game`, `CRT`, and pause helpers in one file)
- `settings.py` (new file)
- `core/__init__.py` (new file)
- `core/sprites.py` (new file; consolidates the old `alien.py`, `player.py`, `laser.py`, `obstacle.py`)
- `ui/__init__.py` (new file)
- `ui/crt.py` (new file; was the `CRT` class in `main.py`)
- `alien.py`, `player.py`, `laser.py`, `obstacle.py` (deleted; contents moved into `core/sprites.py`)
- `audio/`, `font/`, `graphics/` → `assets/audio/`, `assets/font/`, `assets/graphics/` (moved)

**Why:** The TODO roadmap called for a centralized `settings.py` and the project layout was diverging from the star-hero reference (which keeps sprites under `core/`, UI under `ui/`, and bundled media under `assets/`). This pass:

1. Created `settings.py` with `ColorSettings`, `ScreenSettings`, `ControllerSettings`, `PlayerSettings`, `AlienSettings`, `ExtraSettings`, `LaserSettings`, `ObstacleSettings`, `AudioSettings`, `FontSettings`, and `AssetPaths` so every magic number now has a named home.
2. Moved every sprite class into `core/sprites.py` and updated their constructors to import settings instead of hard-coding values or string-joining asset paths.
3. Moved the `CRT` class into `ui/crt.py` so the overlay subsystem stops sharing space with `Game`.
4. Refactored `main.py` into a thin entry-point: an unchanged `Game` class (now driving `screen` through parameters instead of closing over a module global), pause helpers, and a top-level `main()` function. Every input button index, color, sound volume, and pixel dimension now comes from `settings.py`.
5. Moved `audio/`, `font/`, and `graphics/` under `assets/` and pointed `AssetPaths` at the new locations so the project root only carries code + docs.

**Editor:** Bryan Navarro (GitHub Copilot — Claude Opus 4.7)
