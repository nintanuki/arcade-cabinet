# Adventure — Architecture

This document explains **how the Adventure code is put together and why**. It is meant for anyone touching the code — human or AI. It deliberately skips things any Pygame project does (open a window, fill a background, flip the buffer) and focuses on the parts that are specific to this game.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                           +-------------------+
                           |   main.py         |
                           |   GameManager     |   (thin coordinator)
                           +---------+---------+
                                     |
       +-----------------+-----------+-----------+-------------------+
       |                 |                       |                   |
       v                 v                       v                   v
     World           RenderManager           DebugPlayer            CRT
   (core/)            (ui/)                  (entities/)         (ui/crt.py)
     |                  |                       |
     |             windows.py                   |
     |             coords.py                    |
     v                                          v
  CELLS,                                  reads World via
  WORLD_LAYOUT,                           game.world.is_wall
  START_CELL_POS                          and step_to_neighbor
  (core/tilemaps.py)
```

`GameManager` is intentionally thin. Its only jobs are:

- own the Pygame display, clock, and connected controllers,
- drain the event queue and route each event to a small handler,
- own the subsystems (`world`, `render_manager`, `player`, `crt`),
- handle global concerns like fullscreen toggle, debug toggles, and the quit combo.

Anything that has its *own* state lives in its own class. `GameManager` stitches them together; it does not implement them.

---

## 2. The frame loop

Each frame, in order, inside [`GameManager.run`](../main.py):

1. **Quit-combo check.** `quit_combo_pressed()` returns True if `Start + Back + L1 + R1` are held on any controller. Checked at the top of every frame for held-state quits, and inside `_handle_joybuttondown` for instant response on press.
2. **`_process_events`** drains `pygame.event.get()` and dispatches by event type to a handler (`_handle_keydown`, `_handle_joybuttondown`).
3. **`_update`** advances per-frame simulation. Today that is just `player.update()` (gated by the debug toggle).
4. **`_render_frame`** paints the screen background, then the world tiles, then optional debug UI frames, then the cell label, then the player, then the CRT overlay on top.
5. **`pygame.display.flip()`** then **`clock.tick(FPS)`** caps the frame rate.

The render and update phases are separated so future systems (animation, input replay, screenshots) can hook in cleanly.

---

## 3. The world model

The game world is a grid of **cells**. Each cell is a 14 × 10 grid of tiles (`UISettings.COLS × UISettings.ROWS`) that fits exactly inside the action window. The whole world is a 2D map of cells, indexed by `(x, y)` cell coordinates, declared in [core/tilemaps.py](../core/tilemaps.py).

```
CELLS         : dict[name, list[list[char]]]   # tile grids keyed by cell name
WORLD_LAYOUT  : dict[(cx, cy), name]           # which cell sits at which coord
START_CELL_POS: tuple[int, int]                # cell coord the player starts in
```

[`World`](../core/world.py) holds:

- `current_pos` — the active cell coordinate.
- `current_cell_name` / `current_grid` — cached lookups, refreshed by `_refresh_active_cell` whenever `current_pos` changes.

It exposes two queries:

- `is_wall(col, row)` — does the tile at this position in the active cell block movement? Out-of-bounds is **non-wall**, which is what lets the player walk past the action window edge into a transition.
- `step_to_neighbor(dx_cells, dy_cells)` — try to swap to the neighbor cell at the offset; returns whether it succeeded. The caller (the player) clamps itself back into the cell on a False return.

This is deliberately the only place that knows the cell grid layout. The renderer reads `current_grid`; the player calls `is_wall` / `step_to_neighbor`. Adding more layers (overworld + dungeons + houses) means giving `World` a `current_layer` and an entrance-tile table; nothing else has to know.

---

## 4. The action window and UI layout

The screen is divided into four regions, all anchored by `UISettings`:

```
+--------------------------------------------------+
| HIGH SCORE                          AUDIO MUTED  |
|  +------------------------+  +-----------------+ |
|  |                        |  |                 | |
|  |     ACTION WINDOW      |  |    SIDEBAR      | |
|  |   (cell tiles render   |  |   (current      | |
|  |     here on top of     |  |    score, etc.) | |
|  |     the world grid)    |  |                 | |
|  |                        |  |                 | |
|  +------------------------+  +-----------------+ |
|  +------------------------+  +-----------------+ |
|  |        MESSAGE         |  |    MINIMAP      | |
|  |          LOG           |  |                 | |
|  +------------------------+  +-----------------+ |
| LEVEL                                            |
| DUNGEON NAME                                     |
+--------------------------------------------------+
```

`UISettings` derives every coordinate from a few anchors (`LEFT_MARGIN`, `TOP_MARGIN`, `GAP`) and a tile size (`GridSettings.TILE_SIZE`), which is itself derived from `RAW_TILE_SIZE * SCALE_FACTOR`. Changing the tile scale or the margin reflows the whole layout.

`RenderManager` ([ui/render.py](../ui/render.py)) draws each region. The action window draws the active cell's grid (walls, floors); the sidebar/minimap/log are placeholders for now (`DebugSettings.SHOW_UI_FRAMES` overlays their bounds for development).

---

## 5. The placeholder player

[`DebugPlayer`](../entities/sprites.py) is **not the real player** — it is a red square used to verify input plumbing, collision, and cell transitions before the real sprite lands. The contract is: when the real player class arrives it will replace `DebugPlayer` behind the same `GameManager.player` attribute the renderer already uses.

What it already gets right (and the real player should keep):

- **Hitbox vs. visual size.** The collision rectangle is smaller than the visual sprite (inset by `DebugPlayerSettings.HITBOX_INSET`) so the player can squeeze through 1-tile-wide openings without pixel-perfect alignment.
- **Float position.** Position is held as floats so sub-pixel velocities accumulate smoothly even though rendering rounds to integers.
- **Axis-separated AABB collision.** Horizontal and vertical movement resolve in two passes against `World.is_wall`, so sliding along walls works correctly.
- **Combined input.** Reads keyboard (`WASD` and arrow keys) and the left analog stick from every connected controller, with a deadzone applied per stick.
- **Diagonal normalization.** Diagonal motion is normalized so it does not move faster than orthogonal.
- **Edge-crossing triggers cell swap.** When the hitbox crosses the action-window edge, `World.step_to_neighbor` is called; on success the player is repositioned at the opposite edge of the new cell, on failure they are clamped.

---

## 6. Audio

[`systems/audio.py`](../systems/audio.py) is the planned home for music and SFX. It is not wired into `GameManager` yet — see [docs/TODO.md](TODO.md). When it lands it should follow the project rule that missing audio files fail silently rather than crashing.

A `MUTE` indicator is already reserved in `UISettings.MUTE_RIGHT_X` / `MUTE_Y` (top-right of the action window) for when audio is on.

---

## 7. The CRT post-process

[`ui/crt.py`](../ui/crt.py) blits a TV-frame image at a per-frame random alpha (`ScreenSettings.CRT_ALPHA_RANGE`) for a subtle flicker, then draws horizontal scanlines (`ScreenSettings.CRT_SCANLINE_HEIGHT`) on a copy of that image so the overlay does not accumulate between frames. It is the **last** thing drawn each frame, so scanlines sit on top of everything else.

---

## 8. Settings as the only knob panel

[settings.py](../settings.py) is the single place every tunable lives. Each class groups one subsystem (`ColorSettings`, `ScreenSettings`, `GridSettings`, `UISettings`, `GameSettings`, `WindowSettings`, `InputSettings`, `FontSettings`, `DebugSettings`, `DebugPlayerSettings`). The rest of the codebase imports from here and never hard-codes a number.

This matters for two reasons:

1. **No magic numbers.** A reviewer reading collision code never has to guess what `0.15` means; they look up `STICK_DEADZONE` in `settings.py` and read the comment.
2. **Designer-friendly.** Tuning feel — tile scale, hitbox inset, deadzones, font sizes — is editing one file with comments next to each value.

Adding a new tunable? Put it in `settings.py` with a comment explaining its **units** and what changing it does.

---

## 9. Input model

Two parallel input paths share the same handlers:

- **Keyboard** events come in as `KEYDOWN` and route through `_handle_keydown` (Esc to quit, F11 fullscreen, F1 / F2 debug toggles). The player also reads held keys directly via `pygame.key.get_pressed()` for movement.
- **Controller** events come in as `JOYBUTTONDOWN` and route through `_handle_joybuttondown`. Movement reads the left analog stick directly each frame in `DebugPlayer._read_left_stick`.

Two cross-cutting behaviors are global and intentionally fall through every other handler:

- **Fullscreen toggle.** `F11` on keyboard, `Back` on controller.
- **Quit combo.** `Start + Back + L1 + R1` held on any connected controller exits immediately. Checked **both** at the top of every frame (held-state) and inside `_handle_joybuttondown` (instant on press).

Connected controllers are cached once in `setup_controllers` so the per-frame quit-combo check is just `joystick.get_button(...)` calls — no enumeration overhead.

---

## 10. Restart and shutdown

`reset_game` is the canonical "start over" path. Rather than manually resetting every subsystem, it constructs a brand-new `GameManager` (preserving fullscreen state) and calls `run()` on it, then `sys.exit()`s. This guarantees the restart path uses exactly the same boot sequence the game uses on first launch.

`close_game` calls `pygame.quit()` then `sys.exit()`. It is what every quit path eventually funnels into.

---

## 11. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two are worth surfacing here because they shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner comment:

```python
    # -------------------------
    # SECTION NAME
    # -------------------------
```

This is what `main.py`, `world.py`, and `sprites.py` already use. Keep it consistent: matching length, all caps, name describes the role of the methods that follow.

**Function order inside a class.** Functions are grouped by role (boot/setup, input, collision, render). `update` and `run` go **last** and should only call other functions on the class — they are coordinators, not implementations.

---

## 12. What's *not* here yet

The following systems will get their own sections in this document as they're built. If you're implementing one of these, please add the section as part of your pass:

- **Real player sprite** (replacing `DebugPlayer`): animation, facing direction, attack frames.
- **Combat / damage / health** system.
- **Items and inventory** (torch, key, monster repellent — see the welcome message).
- **NPCs and dialogue** (the "text-based flavor" of the launcher description).
- **Dungeon layer** with entrance tiles, separate cells, and layer-aware `World`.
- **Audio system** wiring (`systems/audio.py` is empty scaffolding today).
- **Persistent save/leaderboard** (settings already declare slots and limits).
