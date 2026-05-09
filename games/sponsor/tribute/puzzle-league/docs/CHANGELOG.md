# Change Log

This file is an append-only record of every code change made to Puzzle League
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

Replaced `systems/audio.py` (a custom `Audio` class with a master-volume
slider and BGM playlist) with the cabinet's portable `AudioManager`
template at `systems/audio_manager.py`. `AudioSettings` was rewritten to
match the template contract.

**File:** `systems/audio_manager.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** Portable AudioManager template.
**Why:** Standardize the audio layer with the rest of the cabinet.

**File:** `systems/audio.py`
**Lines (at time of edit):** (deleted)
**Before:** Bespoke `Audio` class with master volume + BGM playlist.
**After:** (removed)
**Why:** Superseded by `systems/audio_manager.py`.

**File:** `settings.py`
**Lines (at time of edit):** AudioSettings block (modified)
**Before:** `DEFAULT_MASTER_VOLUME`, `DEBUG_MUTE`, `BGM_PLAYLIST`.
**After:** `MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`, `SFX_VOLUME`,
`SOUND_EFFECTS`, `MUSIC_TRACKS`.
**Why:** Match the AudioManager template's required keys.

**File:** `main.py`
**Lines (at time of edit):** import block + Game init (modified)
**Before:** `from systems.audio import Audio` / `Audio()`.
**After:** `from systems.audio_manager import AudioManager` / `AudioManager()`.
**Why:** Point at the new module.
**Editor:** GitHub Copilot (Claude Opus 4.7)
