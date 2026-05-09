# Puzzle League — Architecture

This document explains **how the code is put together and why**. It is meant for anyone touching the code — human or AI.

> **Heads-up:** Puzzle League is currently a **scaffold**. The structure, settings, loop, and managers are in place; gameplay is stubbed inside `Board` and `GameManager`. Sections marked _(planned)_ describe the target shape that gameplay should grow into.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                              +----------------+
                              |    main.py     |
                              |  GameManager   |   (coordinator)
                              +-------+--------+
                                      |
   +--------+----------+--------+-----+------+----------+----------+
   |        |          |        |            |          |          |
   v        v          v        v            v          v          v
 Board    Audio  ScoreMgr  SessionState   CRT        Fonts     Joysticks
 (core/  (systems/  (systems/  (systems/  (ui/                 (pygame)
  board)  audio)    managers)  managers)   crt)
```

Responsibility split:

- **`GameManager`** owns the screen, clock, joystick list, fonts, and the title/game-over copy. It pumps the event queue, dispatches by event type, runs the per-frame update, renders, and applies the CRT pass. It does **not** implement any gameplay rules.
- **`Board`** ([core/board.py](../core/board.py)) — the gameplay model: the 6×12+1 grid, the cursor, the rise/clear/chain state machine. Public surface is `tick(delta_time)` plus read-only state for the renderer. **The board never touches a Surface.**
- **`Block`** ([core/blocks.py](../core/blocks.py)) — a single grid cell's data (type, animation state).
- **`AudioManager`** ([systems/audio_manager.py](../systems/audio_manager.py)) — portable AudioManager template (data-driven music + SFX dispatcher) with the silent-on-missing-asset contract used across the cabinet.
- **`ScoreManager`** ([systems/managers.py](../systems/managers.py)) — current score, high-score persistence to `high_score.txt`, leaderboard plumbing.
- **`SessionStateManager`** ([systems/managers.py](../systems/managers.py)) — `game_active` flag, `reset_for_new_game()`, transitions between title / play / game-over.
- **`CRT`** ([ui/crt.py](../ui/crt.py)) — last-pass overlay (image + flicker + scanlines).

---

## 2. The frame loop

`GameManager.run()`:

1. Compute `delta_time` from `time.time()`.
2. Check the controller quit combo (top of frame, for held-state quits).
3. `_process_events` drains `pygame.event.get()` and dispatches by event type. Hot-plug events refresh the joystick cache.
4. `_update_world(delta_time)` — calls `board.tick(delta_time)` only when `session.game_active`.
5. `_render_frame` — fills the screen background; calls `_draw_active_gameplay` (playfield rect today, fully rendered board planned) when active, or `_draw_inactive_screen` (title + prompt) otherwise; finishes with the CRT pass.
6. `pygame.display.flip()` then `clock.tick(FPS)` cap the framerate at 60.

---

## 3. Boot sequence

1. `pygame.init()` and `pygame.joystick.init()`.
2. Display set to `ScreenSettings.RESOLUTION` with `pygame.SCALED`.
3. `_show_loading_screen()` paints a `LOADING...` card and flips the buffer **before** subsystem init so the user sees something while audio and assets load.
4. `CRT`, `Audio`, `ScoreManager`, `SessionStateManager`, and `Board` are constructed in that order.
5. `title_font` and `prompt_font` pre-load so the first frame doesn't pay the cost.

---

## 4. The board model (planned)

```
   +------------------------------+   <- top of visible playfield
   |        VISIBLE ROW 11        |
   |              ...             |
   |         VISIBLE ROW 0        |
   +------------------------------+   <- bottom of visible playfield
   |          BUFFER ROW          |   <- next rise lives here
   +------------------------------+
```

`Board` should own:

- `grid[col][row]` — a `Block` or `None` at each cell.
- `cursor_anchor` — the left half of the 1×2 cursor.
- `rise_offset_px` — how far the buffer row has scrolled into view since the last full row.
- A small state machine: `IDLE → SWAPPING → MATCHING → POPPING → FALLING → CHAIN_CHECK → IDLE`.
- A chain depth counter that increments when falling blocks land into a new match without further player input.

`tick(delta_time)`:

1. Advance any in-progress swap animation.
2. Advance any in-progress pop or fall animation.
3. If idle, integrate `rise_offset_px` against the current rise speed (or the rush speed when held).
4. When `rise_offset_px` exceeds `BLOCK_SIZE`, shift the grid up one row, generate a fresh buffer row, and check for top-out.

---

## 5. Match detection (planned)

After a swap or fall completes, `Board` runs match detection:

1. Walk the grid; for each cell, look right and downward to find runs of ≥ 3 of the same `type`.
2. Mark every cell in any matching run.
3. If any cells are marked, transition to `MATCHING` (flash for `BlockSettings.FLASH_DURATION_MS`), then to `POPPING` (sequential pops staggered by `BlockSettings.POP_INTERVAL_MS`), then to `FALLING` for any cells above pops.
4. After all falls settle, re-check for new matches. If any are found, increment chain depth and repeat. Otherwise reset chain depth to 1 and return to `IDLE`.

`ScoreSettings.POINTS_PER_BLOCK`, `COMBO_BONUS`, and `CHAIN_BONUS` are the **only** scoring knobs; do not hard-code values in match resolution.

---

## 6. Rise system (planned)

`RiseSettings` tunes the constant scroll:

- **`BASE_RISE_SPEED_PX_PER_SEC`** — the starting upward velocity of the stack.
- **`MAX_RISE_SPEED_PX_PER_SEC`** — the cap as difficulty ramps.
- **`RUSH_RISE_SPEED_PX_PER_SEC`** — applied while the rush button is held.
- **`DIFFICULTY_STEP_SCORE`** + **`SPEED_INCREMENT_PX_PER_SEC`** — every N points scored, the base rise speed steps up by the increment.
- **`TOPOUT_GRACE_MS`** — when the top row first becomes occupied, the player has this long to clear something before game-over fires.

The rise system is integrated only while `state == IDLE`. Animations halt the rise so the player isn't punished for being mid-swap when the stack scrolls.

---

## 7. Input model

Two devices, one event loop. The handlers exist; the gameplay branches are stubbed:

- **Keyboard.** `KEYDOWN` → `_handle_keydown`. Globals (`F11` fullscreen, `Esc` exit) always honored. When `session.game_active` is False, `Enter` triggers `reset_for_new_game()`. While active, gameplay routing (cursor move, swap, rush) is `# TODO`.
- **Controller.** `JOYBUTTONDOWN` → `_handle_joybuttondown`; `JOYHATMOTION` → `_handle_joyhatmotion`; `JOYAXISMOTION` → `_handle_joyaxismotion`. Globals: Back toggles fullscreen, the quit combo exits. Inactive: A or Start starts a run. Active: gameplay routing is `# TODO`. The analog axis path is intentionally edge-triggered to mirror the D-pad.

`refresh_joysticks()` and `handle_joystick_hotplug()` keep the joystick list in sync as devices are plugged in or out.

---

## 8. Settings as the only knob panel

[settings.py](../settings.py) groups every tunable into a `*Settings` class:

- `ColorSettings` — base palette and semantic aliases; `BLOCK_COLORS` keys are the canonical block-type identifiers used by match logic.
- `ScreenSettings` — `WIDTH`, `HEIGHT`, `RESOLUTION`, `FPS`, `TITLE`, CRT alpha range, scanline height.
- `BoardSettings` — grid dimensions and pixel layout; the playfield rect is fully derived from `COLS × BLOCK_SIZE` and `VISIBLE_ROWS × BLOCK_SIZE`.
- `BlockSettings` — block types, padding, flash/pop/fall timings, swap duration.
- `CursorSettings` — cursor span (1×2), outline, key-repeat timings.
- `RiseSettings` — rise speeds, difficulty ramp, top-out grace.
- `ScoreSettings` — point values, combo/chain bonus tables, high-score file path.
- `FontSettings` — pixel font path and sizes.
- `AudioSettings`, `ControllerSettings`, `UISettings` — paths/mappings/copy.

When adding a new tunable, add it to the most appropriate class with a comment explaining its **units**. **Block-type identifiers must come from `BlockSettings.TYPES`.**

---

## 9. CRT post-process

[`ui/crt.py`](../ui/crt.py) blits a TV-frame image at a per-frame random alpha (`ScreenSettings.CRT_ALPHA_RANGE`) for flicker, then draws horizontal scanlines spaced `ScreenSettings.CRT_SCANLINE_HEIGHT` pixels apart. It is the **last** thing drawn each frame.

---

## 10. Persistence

`ScoreManager.save_scores` is invoked from `close_game`, so every exit path persists scores. The high-score file is `high_score.txt` next to `settings.py`. The format and leaderboard handling will mirror Jezz Ball's defensive load (silent fallback to defaults on bad/missing JSON).

---

## 11. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two that shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner:

```python
    # -------------------------
    # SECTION NAME
    # -------------------------
```

The scaffold already places banners (`BOOT / LIFECYCLE`, `CONTROLLER PLUMBING`, `EVENT HANDLING`, `PER-FRAME UPDATE / RENDER`) inside `GameManager`. Fill those bands rather than introducing new ones.

**Function order inside a class.** Functions are grouped by role; `update` and `run` go **last** and should only call other functions on the class.

---

## 12. Source tree

```
core/
  blocks.py        Block model
  board.py         Board: grid, cursor, rise/clear/chain state machine (stubbed)
systems/
  audio_manager.py AudioManager
  managers.py      ScoreManager, SessionStateManager
ui/
  crt.py           CRT overlay
  style.py         Reusable style helpers
tools/             Developer-facing helpers
assets/
  font/, graphics/, music/, sound/
docs/              ARCHITECTURE, TODO, TESTING, CHANGELOG
main.py            GameManager + entry point
settings.py        Tunables grouped into *Settings classes
```
