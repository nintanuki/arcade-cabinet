# Change Log

This file is an append-only record of every code change made to Jezz Ball by a
human, AI assistant, or copilot tool. Read it before making changes so you
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
    **Editor:** name (AI model used, if any)

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

## 2026-05-09 13:55 — Refactor audio to portable AudioManager template (GitHub Copilot, Claude Opus 4.7)

Lifted the inline `AudioManager` class out of `main.py` into its own module
`audio_manager.py` next to `main.py`, conformed to the cabinet's portable
AudioManager template, and rewrote `AudioSettings` to match the template's
data-driven contract. The legacy `audio.py` (which only re-exported the
inline class) was removed. `MUSIC_HALF_VOLUME_TOGGLE` was folded into a
single numeric `MUSIC_VOLUME = 0.3` (its only consumer was the music gain).

**File:** `audio_manager.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** Portable AudioManager template (data-driven SFX dict + music
tracks list, plus a `restart_music` alias for back-compat).
**Why:** Standardize the audio layer with the rest of the cabinet.

**File:** `audio.py`
**Lines (at time of edit):** (deleted)
**Before:** Re-exported the inline `AudioManager` class from `main.py`.
**After:** (removed)
**Why:** Replaced by `audio_manager.py`.

**File:** `main.py`
**Lines (at time of edit):** import block + removed inline class
**Before:** Inline `AudioManager` class.
**After:** `from audio_manager import AudioManager`.
**Why:** Single source of truth for audio.

**File:** `settings.py`
**Lines (at time of edit):** AudioSettings block (modified)
**Before:** Bespoke layout with `MUSIC_PATH`, `MUSIC_BASE_VOLUME`,
`MUSIC_HALF_VOLUME_TOGGLE`, `SFX_*` paths, etc.
**After:** Template contract — `MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`,
`SFX_VOLUME`, `SOUND_EFFECTS` keyed by logical name (`wall_start`,
`wall_complete`, `ball_hit_cursor`, `level_clear`, `pause_in`, `pause_out`),
and `MUSIC_TRACKS`.
**Why:** Match the AudioManager template's required keys.
**Editor:** GitHub Copilot (Claude Opus 4.7)
