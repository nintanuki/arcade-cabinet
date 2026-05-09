# Change Log

Append-only record of every code change made to Pong.

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

## 2026-05-09 13:55 — Refactor audio to portable AudioManager template (GitHub Copilot, Claude Opus 4.7)

Replaced the bespoke `AudioManager` class in `audio.py` with the cabinet's
portable `AudioManager` template under `systems/audio_manager.py`. The new
manager loads SFX from a data-driven `AudioSettings.SOUND_EFFECTS` dict and
music from `AudioSettings.MUSIC_TRACKS`, and exposes the standard API
(`play(name)`, `play_random_music`, `pause_music`, `resume_music`,
`stop_music`, `toggle_mute`).

**File:** `systems/audio_manager.py`
**Lines (at time of edit):** (new file)
**Before:** (file did not exist)
**After:** Portable AudioManager template (see arcade-cabinet `audio_manager_template.py`).
**Why:** Standardize the audio layer across every cabinet game.

**File:** `audio.py`
**Lines (at time of edit):** (deleted)
**Before:** Bespoke `AudioManager` class with a hard-coded SFX dict.
**After:** (removed)
**Why:** Superseded by `systems/audio_manager.py`.

**File:** `settings.py`
**Lines (at time of edit):** AudioSettings block (modified)
**Before:** Volume constants only.
**After:** Full template contract — `MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`,
`SFX_VOLUME`, `SOUND_EFFECTS`, `MUSIC_TRACKS`. `MUTE_MUSIC` defaults to `True`
because Pong shipped without bundled music.
**Why:** Match the AudioManager template's required keys.

**File:** `main.py`
**Lines (at time of edit):** import block + `Game.__init__` (modified)
**Before:** `from audio import AudioManager`
**After:** `from systems.audio_manager import AudioManager`
**Why:** Point at the new module location.

**File:** `docs/ARCHITECTURE.md`, `.github/copilot-instructions.md`
**Lines (at time of edit):** all references to `audio.py` (modified)
**Before:** `audio.py` referenced as the audio module.
**After:** `systems/audio_manager.py` referenced instead.
**Why:** Reflect the new file layout.
**Editor:** GitHub Copilot (Claude Opus 4.7)
