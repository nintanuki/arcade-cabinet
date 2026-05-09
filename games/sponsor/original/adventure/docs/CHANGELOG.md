# Change Log

This file is an append-only record of every code change made to Adventure
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

---

#
## 2026-05-09 — AudioManager refactor to portable template standard

**File:** systems/audio_manager.py
**Lines (at time of edit):** (new file)
**After:** Portable AudioManager: data-driven via `AudioSettings.SOUND_EFFECTS` / `MUSIC_TRACKS`, single `play(name)` entry point, standard `play_random_music`/`pause_music`/`resume_music`/`stop_music`/`toggle_mute` API. Adventure's chase-music swap is preserved as `play_chase_music` / `play_normal_music` extensions below the standard body.
**Why:** Standardize on the AudioManager template shared across the cabinet. The previous implementation reserved fixed channels for SFX that don't actually need that protection, and used `from settings import *` which obscured its dependencies.
**Editor:** Bryan (Claude Opus 4.7)

**File:** systems/audio.py
**Lines (at time of edit):** (deleted)
**Why:** Replaced by `systems/audio_manager.py`.
**Editor:** Bryan (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 202-238 (modified)
**Before:** `AudioSettings` was a 3-field stub; per-sound paths and music paths lived under `AssetPaths`.
**After:** `AudioSettings` now owns `MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`, `SFX_VOLUME`, `SOUND_EFFECTS`, `MUSIC_TRACKS`, plus the `CHASE_MUSIC` extension. `AssetPaths` keeps only `SOUND_DIR` / `MUSIC_DIR` plumbing.
**Why:** Match the AudioManager template contract.
**Editor:** Bryan (Claude Opus 4.7)
