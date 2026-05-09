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
