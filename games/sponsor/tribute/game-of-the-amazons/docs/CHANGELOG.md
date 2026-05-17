# Change Log

This file is an append-only record of every code change made to Game of the
Amazons by a human, AI assistant, or copilot tool. Read it before making
changes so you know the current state of the codebase.

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

---


## 2026-05-09 — AudioManager refactor to portable template standard

**File:** systems/audio_manager.py
**Lines (at time of edit):** (new file)
**After:** Portable AudioManager: data-driven via `AudioSettings.SOUND_EFFECTS` and `MUSIC_TRACKS`, single `play(name)` entry point, music API stubs that no-op while `MUSIC_TRACKS` is empty (Amazons has no BGM yet).
**Why:** Standardize on the AudioManager template shared across the cabinet. Failure to load any individual asset is now non-fatal.
**Editor:** Bryan (Claude Opus 4.7)

**File:** systems/audio.py
**Lines (at time of edit):** (deleted)
**Before:** Per-game AudioManager that reserved fixed channels and tracked sounds via SOUND_BINDINGS / SOUND_BINDINGS dicts.
**Why:** Replaced by `systems/audio_manager.py`. Fixed-channel reservation was unnecessary for the two cues this game has.
**Editor:** Bryan (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 151-167 (modified)
**Before:** `AudioSettings` only had `MUTE`; `AssetPaths.SHOOT_SOUND`/`MOVE_SOUND` were the per-sound paths; `DebugSettings.MUTE` duplicated `AudioSettings.MUTE`.
**After:** Added `MUTE_MUSIC`, `MUSIC_VOLUME`, `SFX_VOLUME`, `SOUND_EFFECTS`, `MUSIC_TRACKS` to `AudioSettings`; moved `shoot`/`move` paths into `SOUND_EFFECTS`; removed the duplicate `DebugSettings.MUTE`.
**Why:** Match the AudioManager template contract; eliminate the duplicate mute flag.
**Editor:** Bryan (Claude Opus 4.7)

**File:** main.py
**Lines (at time of edit):** 16 (modified)
**Before:** `from systems.audio import AudioManager`
**After:** `from systems.audio_manager import AudioManager`
**Why:** Module renamed to match the template.
**Editor:** Bryan (Claude Opus 4.7)


## 2026-05-17 12:30 -04:00 — Add title mode select and hot-seat two-player

**File:** main.py
**Lines (at time of edit):** 23-607 (modified)
**Before:** Game booted straight into a one-player match; BLACK was always AI-controlled; no title/menu state existed.
**After:** Added title-screen state and render path (`in_title_screen`, option cursor, mode confirm), mode-aware input gating, mode-preserving restart, and CPU-conditional BLACK automation.
**Why:** Implement requested mode select with ONE PLAYER (current behavior) and TWO PLAYERS (human controls both colors, no CPU).
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** core/turn_manager.py
**Lines (at time of edit):** 28-222 (modified)
**Before:** `TurnManager` always ran BLACK AI when its delay elapsed.
**After:** Added `cpu_enabled` constructor flag and update guards so AI planning/timer runs only when one-player mode is active.
**Why:** Centralize AI on/off behavior for mode switching without branching AI logic across unrelated systems.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** ui/hud.py
**Lines (at time of edit):** 25-188 (modified)
**Before:** HUD assumed one-player semantics (`YOU WIN` for WHITE, `YOU LOSE` for BLACK) and had no mode display.
**After:** Added mode line (`MODE`) and two-player winner banners (`WHITE WINS` / `BLACK WINS`).
**Why:** Keep HUD messaging accurate in hot-seat mode and expose active mode clearly.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** settings.py
**Lines (at time of edit):** 117-132 (modified)
**Before:** No shared constants for match modes or title-screen typography/layout.
**After:** Added `ModeSettings` and `TitleScreenSettings` to keep menu labels and title-screen sizing/spacing out of `main.py`.
**Why:** Preserve the project rule that tunable constants live in `settings.py`.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** README.md
**Lines (at time of edit):** 5-8, 39-40 (modified)
**Before:** README described only a human-vs-AI build and omitted title menu controls.
**After:** Documented ONE PLAYER / TWO PLAYERS modes and added title-menu input controls.
**Why:** Keep top-level usage docs aligned with shipped behavior.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** docs/TODO.md
**Lines (at time of edit):** 25-26 (modified)
**Before:** Phase 4 title/two-player tasks were unchecked.
**After:** Marked both Phase 4 items `[x]`.
**Why:** Reflect completed roadmap work.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 32-34, 50-54, 66-68, 111-114 (modified)
**Before:** Architecture described one-player-only flow with no title-screen state.
**After:** Added title-screen ownership/flow notes and documented mode-dependent AI vs human turn control.
**Why:** Keep architecture accurate after behavior changes.
**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** docs/TESTING.md
**Lines (at time of edit):** 16-23, 45-51, 55-60, 77-80 (modified)
**Before:** Test checklist covered board-first boot and one-player AI flow only.
**After:** Added title-screen checks, two-player mode checks, and restart expectation that selected mode is preserved.
**Why:** Ensure manual smoke testing now covers both selectable modes and entry flow.
**Editor:** GitHub Copilot (GPT-5.3-Codex)
