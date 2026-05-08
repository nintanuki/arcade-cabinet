# Jezz Ball — Roadmap & TODO

The build is **playable end-to-end**: title screen, ten levels, game-over, initials entry, leaderboard. Items are grouped by phase so contributors know where to push next.

---

## Phase 1 — Bugs to fix

- [ ] Get the controller analog stick to work. The mapping exists in `ControlSettings.AXIS_CURSOR_X` / `AXIS_CURSOR_Y` and `CURSOR_SPEED`, but the per-frame analog→cursor integration is incomplete. D-pad navigation is functional.
- [ ] When a ball hits the blue or red half of a still-growing wall, only that half should disappear. Today the entire wall (both segments) is destroyed regardless of which segment was hit.

## Phase 2 — Polish

- [ ] Re-enable SFX. `AudioSettings.SFX_VOLUME` is currently `0.0`; once raised, audit each cue (`wall_start`, `wall_complete`, `ball_hit_cursor`, `level_clear`, `pause_in`, `pause_out`) so volumes are balanced against music.
- [ ] Visual feedback when a wall is destroyed by a ball (flash, particle, screen shake) so the cause-and-effect is unmistakable.
- [ ] Pause overlay says `PAUSED` and lists controls; today it dims the screen but reads thinly.

## Phase 3 — Content

- [ ] More than 10 levels. The `LEVELS` tuple is the single source of truth; add stages with rising `area_needed_percent`, `ball_count`, `speed_multiplier`, and tighter `time_limit_seconds`.
- [ ] Optional: per-level palette tweaks for variety.

## Phase 4 — Asset / housekeeping

- [ ] Consolidate audio. The legacy standalone `audio.py` is not imported by `main.py` (which has its own embedded `AudioManager`). Either remove the legacy file or refactor to import it.
- [ ] Consolidate CRT. Same situation as audio — `crt.py` is legacy; the live one is embedded in `main.py`.

---

## Code health

- [ ] `main.py` is over 1500 lines and contains four classes (`CRT`, `AudioManager`, `GameManager`, plus `GameState`). Splitting `CRT` and `AudioManager` into their own files (replacing the legacy `crt.py` / `audio.py`) would make the file easier to navigate and align with the per-class-per-file convention used elsewhere in the cabinet.
- [ ] `from settings import *` style is avoided here in favor of `importlib.util` loading — that's defensive, but the resulting `JEZZ_SETTINGS` indirection is harder to read than a direct `from settings import ...`. Reconsider during the next major main.py touch.

---

## Open questions

- Should pausing also pause the timer? Today this is implicit but it's worth confirming behavior on a code review.
- Should claimed regions visually differ from solid walls (e.g. a hatched fill)? Today both render as solid black against the gray field.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
