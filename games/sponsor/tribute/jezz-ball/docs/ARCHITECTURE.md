# Jezz Ball — Architecture

This document explains **how the code is put together and why**. It is meant for anyone touching the code — human or AI. It deliberately skips things any Pygame project does and focuses on the parts specific to this game.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                          +------------------+
                          |    main.py       |
                          |   GameManager    |   (coordinator)
                          +--------+---------+
                                   |
        +---------+---------+------+-------+-----------+----------+
        |         |         |              |           |          |
        v         v         v              v           v          v
      Ball   BuildingWall  AudioManager   CRT       GameState   LevelConfig
     (ball.py) (wall.py)   (main.py)   (main.py)   (Enum)     (settings.py)
```

Responsibility split:

- **`GameManager`** owns the screen, clock, controllers, audio, fonts, and the game state machine. It owns the cursor, the active wall (if any), the ball list, the wall/claim grids, and the leaderboard. It dispatches input and orchestrates level flow but does not implement physics or wall geometry itself.
- **`Ball`** owns its own position, velocity, and visual spin. Each ball updates itself against the playfield and the current wall set.
- **`BuildingWall`** is the in-flight wall: a position, an orientation (`HORIZONTAL` / `VERTICAL`), and two grow-direction segments. While building, the wall reports its rectangles for both rendering and ball-collision so a ball that touches it can destroy it.
- **`AudioManager`** ([audio_manager.py](../audio_manager.py)) loads music and one-shots from a data-driven registry in `AudioSettings`, and survives a missing mixer device by going silent rather than crashing.
- **`CRT`** is a last-pass overlay (image + flickering alpha + scanlines).
- **`GameState`** (`Enum`) gates which input handler and renderer are active each frame: `TITLE`, `PLAYING`, `GAME_OVER`, `INITIALS`, `LEADERBOARD`.
- **`LevelConfig`** in [settings.py](../settings.py) is a frozen dataclass; the `LEVELS` tuple is the **only** place the per-level numbers live.

---

## 2. The frame loop

`GameManager.run()`:

1. Check the controller quit combo (top of frame, for held-state quits).
2. Drain `pygame.event.get()` and dispatch by current `GameState`.
3. Update the active state:
   - `TITLE` — bounce the demo ball, pulse menu prompts.
   - `PLAYING` — advance balls, advance the active wall, run capture flood-fill on completion, update score and timer.
   - `GAME_OVER` / `INITIALS` / `LEADERBOARD` — animate prompts and accept input.
4. Render the active state's view, then composite the CRT pass.
5. `pygame.display.flip()` then `clock.tick(FPS)` cap the framerate at 60.

---

## 3. The grid model

The playfield is a fixed `PLAYFIELD_LEFT/TOP/WIDTH/HEIGHT` rect in `ScreenSettings`. `GridSettings.CELL_SIZE` (16 px) tiles the playfield into `GRID_COLUMNS × GRID_ROWS` cells. Two grids are tracked alongside the rect lists for rendering:

- **`wall_cells[col][row]`** — which cells are permanently solid wall.
- **`claimed_cells[col][row]`** — which cells have been claimed (locked-in territory).

The rect lists (`wall_rects`, `claimed_rects`, `solid_rects`) are derived from the cell grids so the renderer can blit big rectangles instead of per-cell quads. Whenever a wall completes or a flood-fill claims a region, both the cell grid **and** the rect lists are updated together.

---

## 4. Wall building

`BuildingWall` ([wall.py](../wall.py)) holds an orientation and a build point. When the player triggers a build:

1. The cursor cell becomes the seed.
2. Two grow-segments extend out from the seed at `GameplaySettings.WALL_BUILD_SPEED` until each tip hits an edge or another wall.
3. Until both tips have stopped, the wall is **vulnerable**. A ball touching either segment destroys the wall and costs a life.
4. When both tips are anchored, the wall converts to permanent cells (`wall_cells`) and the playfield re-evaluates which regions are now ball-free.

The two segments render in different colors (`WALL_GROW_NEGATIVE` / `WALL_GROW_POSITIVE`) so the player can see which side will close first.

---

## 5. Capture (flood-fill)

When a wall completes, `GameManager` flood-fills from each open cell:

1. Walk the cell grid, ignoring already-claimed and wall cells.
2. For each connected region, mark whether it contains a ball.
3. Regions with **no ball** are claimed: their cells are flipped in `claimed_cells`, their rects are appended, and `claimed_percent` is recomputed.
4. If `claimed_percent >= level.area_needed_percent`, the level is complete: stop time, play the clear SFX, score the time bonus, and advance.

`POINTS_PER_CLAIMED_CELL`, `LEVEL_CLEAR_BONUS`, and `TIME_BONUS_PER_SECOND` in `GameplaySettings` are the only knobs for scoring.

---

## 6. Game state machine

```
   TITLE  --- start game --->  PLAYING
     ^                            |
     |                       (lives==0 or
     |                        time==0 or
     |                        finish stage 10)
     |                            v
     |                        GAME_OVER
     |        no qualify    /         \   qualifies for leaderboard
     |    +-----------------          ---------------+
     |    |                                          v
     +----+                                       INITIALS
                                                     |
                                              submit initials
                                                     v
                                                LEADERBOARD ---> TITLE
```

`GameState` is checked at the top of input dispatch and update; each branch only runs the handler relevant to its state. This keeps gameplay code from leaking into menu screens.

---

## 7. Input model

Two devices, one event loop:

- **Mouse + keyboard.** Mouse motion drives the cursor in `mouse` mode. `Space` (or left-click) is the build button. `R` (or right-click) toggles wall orientation. `P` pauses. `F11` toggles fullscreen. `Esc` exits.
- **Controller.** D-pad and the analog stick drive the cursor in `controller` mode (the analog path is incomplete — see [docs/TODO.md](TODO.md)). `A` builds. `X` rotates orientation. Start pauses. Back (Select) toggles fullscreen. The combo `Start + Back + L1 + R1` exits immediately and is checked **at the top of every frame** for held-state quits.

The selected input mode (`mouse` / `controller`) is chosen on the title screen and stored in `selected_input_mode`. `using_joystick` flips on each detected controller event so the cursor can switch sources mid-game.

---

## 8. Audio

`AudioManager` ([audio_manager.py](../audio_manager.py)) loads:

- One looping music track from `AudioSettings.MUSIC_TRACKS` at `AudioSettings.MUSIC_VOLUME`.
- Six one-shot SFX keyed by logical name in `AudioSettings.SOUND_EFFECTS` (`wall_start`, `wall_complete`, `ball_hit_cursor`, `level_clear`, `pause_in`, `pause_out`).

If the mixer can't initialize or any file is missing, `AudioManager.enabled` is `False` and every method becomes a no-op. **Do not** raise from missing-audio paths — silent degradation is the contract.

`SFX_VOLUME` is currently `0.0` in [settings.py](../settings.py); raising it will re-enable SFX.

---

## 9. CRT post-process

`CRT` blits a TV-frame image at a per-frame random alpha (`CRTSettings.ALPHA_RANGE`) for flicker, then draws horizontal scanlines spaced `CRTSettings.SCANLINE_HEIGHT` pixels apart. It is the **last** thing drawn each frame.

If the overlay image is missing, `CRT` falls back to a transparent surface so the game still runs.

---

## 10. Persistence and scoring

`high_score.txt` is a JSON file (despite the `.txt` extension):

```json
{
  "high_score": 12345,
  "leaderboard": [
    {"name": "AAA", "score": 5000},
    ...
  ]
}
```

`_load_scores` is defensive — bad/missing JSON falls back to defaults. `_qualifies_for_leaderboard` decides whether the game-over flow routes through the `INITIALS` state. `_sort_and_trim_leaderboard` keeps only the top entries.

---

## 11. Settings as the only knob panel

[settings.py](../settings.py) groups every tunable into a `*Settings` class:

- `ScreenSettings` — window and playfield rect.
- `ColorSettings` — full palette pulled from `COLOR_PALETTE`.
- `GridSettings` — cell size, wall thickness, derived column/row counts.
- `ControlSettings` — controller button indices and analog stick axes.
- `FontSettings` — pixel-font sizes for HUD/overlay/title text.
- `CRTSettings` — overlay image, scanline thickness, flicker alpha range.
- `GameplaySettings` — global gameplay constants (ball radius, build speed, scoring).
- `AudioSettings` — portable AudioManager template contract: `MUTE`, `MUTE_MUSIC`, `MUSIC_VOLUME`, `SFX_VOLUME`, `SOUND_EFFECTS` (logical-name dict), `MUSIC_TRACKS`.
- `LEVELS` — the 10 stage configs as `LevelConfig` entries.

When adding a new tunable, add it to the most appropriate class with a comment explaining its **units**. Per-stage values must go into `LEVELS`, not into branching code.

---

## 12. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two that shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner:

```python
    # -------------------------
    # SECTION NAME
    # -------------------------
```

**Function order inside a class.** Functions are grouped by role; `update` and `run` go **last** and should only call other functions on the class.

---

## 13. Source tree

```
ball.py             Ball: position, velocity, render, collision response
wall.py             BuildingWall, Orientation
audio_manager.py    AudioManager (data-driven music + SFX dispatcher)
crt.py              (legacy / standalone CRT)
main.py             GameManager, embedded CRT, entry point
settings.py         All tunables grouped into *Settings classes; LEVELS tuple
high_score.txt      JSON: { high_score, leaderboard[] }
font/, graphics/, music/, sound/   Asset folders
docs/               ARCHITECTURE, TODO, TESTING, CHANGELOG
```

> The standalone `crt.py` predates the embedded `CRT` class inside `main.py`; it is not imported in the main entry path and should be treated as legacy until consolidated. See [docs/TODO.md](TODO.md).
