# Game of the Amazons — Architecture

This document explains **how the code is put together and why**. It is meant for anyone touching the code — human or AI. It deliberately skips things any Pygame project does and focuses on the parts specific to this game.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                                +----------------+
                                |   main.py      |
                                |  GameManager   |   (coordinator)
                                +-------+--------+
                                        |
   +--------+--------+----------+-------+--------+----------+----------+
   |        |        |          |                |          |          |
   v        v        v          v                v          v          v
 Board  TurnManager  BoardView  HUD       PieceAnimator   ArrowAnim  AudioManager
 (core  (core/       (ui/       (ui/      (core/          (core/    (systems/
  /board) turn_      board_      hud)      animation)      animation) audio)
          manager)   view)
                                        |
                                        v
                                       CRT (ui/crt.py)
```

Responsibility split:

- **`GameManager`** owns the screen, clock, controllers, the cursor state (`cursor_pos`, `selected_pos`, `shoot_origin`), and the main loop. It dispatches input and orchestrates phase transitions but does not implement game rules itself.
- **`Board`** owns the 10×10 tile grid (`Tile` objects with optional piece + arrow flags) and the geometric path-validation primitive `is_valid_path`.
- **`TurnManager`** owns the turn state machine: `current_player` (`"WHITE"` / `"BLACK"`), `phase` (`PHASE_MOVE` / `PHASE_SHOOT`), `game_over`, `winner`, the AI's pending arrow target, and territory totals (used in win-condition reporting).
- **`BoardView`** draws the tiles, queens, arrows, cursor highlight, selection highlight, and any in-flight animations.
- **`HUD`** draws the side panel (current player, current phase, game-over banner, win condition, territory totals).
- **`PieceAnimator`** animates a queen sliding from one tile to another at `GridSettings.ANIMATION_SPEED` pixels per frame; while animating, the queen is detached from the board so it isn't drawn twice.
- **`ArrowAnimator`** animates the in-flight arrow from queen tile to landing tile at `GridSettings.ARROW_ANIMATION_SPEED` and cycles fletching frames every `GridSettings.ARROW_FRAME_DURATION` frames.
- **`AudioManager`** plays move/shoot SFX.
- **`CRT`** is the last-pass overlay (scanlines + flicker).

---

## 2. The frame loop

`GameManager.run()`:

1. Check the controller quit combo (top of frame, for held-state quits).
2. `_process_events` drains `pygame.event.get()` and dispatches by event type — `KEYDOWN`, `JOYBUTTONDOWN`, `JOYHATMOTION`, `QUIT`.
3. `_update_game_state` advances active animations; when the queen-slide animation finishes it transitions to `PHASE_SHOOT`; when the arrow animation finishes it stamps the arrow and switches turns; if the AI is on the clock and no animation is active, it runs `TurnManager.update_ai`.
4. `_render_frame` paints background → board (tiles, queens, arrows, in-flight piece, in-flight arrow, cursor, selection) → HUD → CRT.
5. `pygame.display.flip()` then `clock.tick(FPS)` cap the framerate at 60.

---

## 3. The turn state machine

A single turn is two phases:

1. **`PHASE_MOVE`.** The active player picks one of their four queens and moves it along a valid queen-path to an empty tile.
2. **`PHASE_SHOOT`.** That same queen fires an arrow along a valid queen-path. The landing tile is permanently blocked.

`TurnManager.switch_turn()` flips `current_player` between `"WHITE"` and `"BLACK"` and resets the phase to `PHASE_MOVE`. Before the switch, it checks whether the new player has any legal move and sets `game_over` + `winner` accordingly.

The human (WHITE) drives the cursor and presses confirm on each phase. The AI (BLACK) chooses both the move and the arrow target before any animation starts; the arrow target is parked on `TurnManager` as a "pending" value, and `_finalize_move` consumes it and starts the second animation automatically.

---

## 4. The board model

[`Board`](../core/board.py) is a `cols × rows` grid of `Tile` objects. Each tile knows:

- `piece`: `None`, `"QUEEN_WHITE"`, or `"QUEEN_BLACK"`.
- `arrow`: `True` if the tile is permanently blocked.

The two interesting public methods:

- **`is_valid_path(start, end)`** — returns whether `start → end` is a queen-direction path that crosses only empty (no piece, no arrow) tiles. This is reused for both moving a queen and firing an arrow because they obey the same geometry.
- **`place_arrow(tile)`** — stamps the arrow flag.

Initial placement is fixed (the standard Amazons opening) and is set up in `Board.__init__`.

---

## 5. Animations

Both animators follow the same pattern:

1. `start(piece_type, start_pos, end_pos)` (or arrow's `start(start, end)`) fills a `moving_piece` / `flying_arrow` dict with grid positions and the current pixel position.
2. Each frame, `update()` advances the pixel position toward the destination by the animator's per-frame speed; when within one step, it snaps and returns `True`.
3. The view asks `get_render_data()` to draw the in-flight sprite at its current pixel position.
4. The board piece itself is **detached** during the slide (set to `None`) so the world doesn't render the queen twice; it's re-attached in `_finalize_move`.

This is the only reason there's a "in-flight" concept on top of a turn-based game — animation timing must not gate game rules.

---

## 6. Cursor and input

The cursor is `[col, row]` clamped to `[0, 9]`. There are two independent navigation paths:

- **Keyboard** arrows → `_handle_navigation`.
- **Controller** D-pad → `_handle_joyhatmotion`.

Both write to `self.cursor_pos` directly. Confirm is `Space` (keyboard) or A (controller); both route through `_handle_confirm_action`, which:

- Blocks input while any animation is mid-flight.
- Refuses input when it isn't WHITE's turn (the human).
- Branches by `turn.phase` to either `_handle_move_phase_space` (pick up queen, then choose destination) or `_handle_shoot_phase_space` (fire arrow at cursor tile).

After WHITE's move animation finishes, `_finalize_move` parks the cursor on the queen so the player has an obvious anchor for the SHOOT phase.

---

## 7. The HUD

`HUD` reads from `GameManager._push_hud_state` each frame — the manager mirrors `current_player`, `current_phase`, `game_over`, `winner`, `win_condition`, and `territory_totals` onto the HUD as primitive values. The HUD never reaches into `TurnManager` itself; this keeps the HUD a pure draw target.

---

## 8. The CRT post-process

[`CRT`](../ui/crt.py) blits a TV-frame image at a per-frame random alpha (`ScreenSettings.CRT_ALPHA_RANGE`) for flicker, then draws horizontal scanlines spaced `ScreenSettings.CRT_SCANLINE_HEIGHT` pixels apart. It is the **last** thing drawn each frame.

---

## 9. Settings as the only knob panel

[settings.py](../settings.py) groups every tunable into a `*Settings` class plus `ASSETS_DIR`. Notable: the entire screen layout is **derived** from `GridSettings.TILE_SIZE` and `UISettings.*` — `ScreenSettings.WIDTH` and `ScreenSettings.HEIGHT` are computed sums of margins, the board, the HUD, and the gap between them. Changing the tile size or HUD width re-flows the whole window without any other edit.

When adding a new tunable, add it to the most appropriate `*Settings` class with a comment explaining its **units**.

---

## 10. Input model

Two devices, one event loop:

- **Keyboard** events → `KEYDOWN` dispatched by `_handle_keydown`. Game-over input is gated to `Enter` only so stray keys can't edit the final board.
- **Controller** events → `JOYBUTTONDOWN` (`_handle_joybuttondown`) and `JOYHATMOTION` (`_handle_joyhatmotion`). Game-over input is gated to Start only.

Globals that intentionally fall through every other handler:
- `F11` and Back (Select) toggle fullscreen.
- `Esc` exits.
- `Start + Back + L1 + R1` quit combo on any controller exits immediately. This is checked at the top of each frame for held-state quits, **and** on each `JOYBUTTONDOWN` for instant response.

---

## 11. Restart and shutdown

`reset_game` is the canonical "start over" path. Rather than manually resetting every subsystem, it constructs a brand-new `GameManager` (preserving fullscreen state) and calls `run()` on it, then `sys.exit()`s. This guarantees the restart path uses exactly the same boot sequence the game uses on first launch.

`close_game` calls `pygame.quit()` then `sys.exit()`. Every quit path eventually funnels into it.

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
core/
  animation.py     PieceAnimator, ArrowAnimator
  board.py         Board, Tile, queen_piece_for
  turn_manager.py  TurnManager (state machine + AI hook)
systems/
  audio.py         AudioManager
ui/
  board_view.py    BoardView (tiles, queens, arrows, cursor, selection, in-flight sprites)
  crt.py           CRT
  hud.py           HUD (sidebar)
assets/
  font/, graphics/, sound/
docs/              ARCHITECTURE, TODO, TESTING, CHANGELOG
main.py            GameManager + entry point
settings.py        All tunables grouped into *Settings classes
```
