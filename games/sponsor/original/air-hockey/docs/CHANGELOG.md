# Change Log

This file is an append-only record of every code change made to Air Hockey
by a human, AI assistant, or copilot tool. Read it before making changes so you
know the current state of the codebase.

## Format

Each entry covers one logical change (which may touch multiple files). Use the
template below, with one `**File:** ... **Why:** ...` block per file touched.

    ## YYYY-MM-DDTHH:MM:SS±HH:MM — short summary

    **Editor:** GitHub Copilot (Model Name)

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
* New entries go BELOW the `---` separator, newest first. These instructions
  must stay on top.

---

## 2026-05-09 — AudioManager refactor to portable template standard

**File:** audio_manager.py
**Lines (at time of edit):** (new file)
**After:** Portable AudioManager: data-driven via `AudioSettings.SOUND_EFFECTS` and `MUSIC_TRACKS`, single `play(name)` entry point, standard `play_random_music` / `pause_music` / `resume_music` / `stop_music` / `toggle_mute` API. Failure to load any individual asset is now non-fatal.
**Why:** Standardize on the AudioManager template shared across the cabinet. The previous `Audio` class hard-coded numbered channels and exposed raw `Sound` objects to call sites.
**Editor:** Bryan (Claude Opus 4.7)

**File:** audio.py
**Lines (at time of edit):** (deleted)
**Why:** Replaced by `audio_manager.py`.
**Editor:** Bryan (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 1-32 (modified)
**Before:** Flat module-level constants only. Audio paths were resolved inside the `Audio` class.
**After:** Added an `AudioSettings` class implementing the AudioManager template contract (`MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`, `SFX_VOLUME`, `SOUND_EFFECTS`, `MUSIC_TRACKS`). The legacy module-level `MUTE_MUSIC` is mirrored on the class.
**Why:** Match the AudioManager template contract without breaking existing wildcard imports.
**Editor:** Bryan (Claude Opus 4.7)

**File:** main.py
**Lines (at time of edit):** 15, 38, ~125-145, ~231-235, ~314-315, ~481-482, ~511-516, ~599-601 (modified)
**Before:** `from audio import Audio`, `Audio()` instance, `audio.channel_N.play(audio.X_sound)` for every cue, manual mute logic, ad-hoc BGM start in the main loop.
**After:** `from audio_manager import AudioManager`, `AudioManager()` instance, `play(name)` for every SFX, `pause_music` / `resume_music` for music control, `toggle_mute(resume_music=False)` for the mute key. BGM starts inside `AudioManager.__init__`.
**Why:** Mirror the new manager's API.
**Editor:** Bryan (Claude Opus 4.7)
