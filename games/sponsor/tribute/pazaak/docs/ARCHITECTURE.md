# Pazaak — Architecture

This document explains **how the code is put together and why**. It is meant for anyone touching the code — human or AI.

> **Heads-up:** Pazaak is currently a **scaffold**. This document describes what exists today and outlines the planned structure. Sections marked _(planned)_ describe the target shape that gameplay should grow into; they are guidance for the next contributor, not promises about existing code.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program (today)

```
                +----------------+
                |    main.py     |
                |  GameManager   |   (coordinator)
                +-------+--------+
                        |
                        v
                       CRT (ui/crt.py)
```

Responsibility split as it stands:

- **`GameManager`** owns the screen, clock, and joystick list. Its loop pumps events, checks the quit combo, calls `pygame.display.flip()`, and ticks the clock. There is no gameplay logic yet.
- **`CRT`** is the post-process overlay (image + flicker + scanlines), already drawn each frame.

That's the entire program. The four placeholder section banners in `GameManager` (`GAMEPLAY ACTIONS`, `AUDIO / VOLUME ACTIONS`, `EVENT HANDLING`, `PER-FRAME UPDATE / RENDER`) are intentional landing pads for the systems below.

---

## 2. The shape of the program (planned)

```
                       +----------------+
                       |    main.py     |
                       |  GameManager   |
                       +-------+--------+
                               |
   +---------+---------+-------+--------+----------+----------+
   |         |         |                |          |          |
   v         v         v                v          v          v
  Deck    Hand     SideDeck       OpponentAI    AudioMgr     CRT
                                                              |
                                                              v
                                                          TableView
                                                          (ui/...)
```

Responsibility split that gameplay should grow into:

- **`Deck`** — the shared `+1`–`+10` main deck (and an opponent's hidden side-deck). `draw()`, `shuffle()`, `__len__`.
- **`Hand`** — a single player's table cards. Tracks total, bust state, stand state.
- **`SideDeck`** — the four cards a player brings to the table. Tracks which have been played this hand.
- **`OpponentAI`** — chooses when to play side-deck cards and when to stand.
- **`AudioManager`** — music + SFX, with the same "silent on missing assets" contract used in other tribute games.
- **`TableView`** — renders the table layout, hand totals, side-deck cards, deck back, and turn indicator.

`GameManager` should stay a coordinator: input → state machine transitions → call into systems → render → CRT. **Do not** put card logic inside `GameManager`.

---

## 3. The frame loop (today)

`GameManager.run()`:

1. Compute `delta_time` from `time.time()`.
2. Check the controller quit combo (top of frame).
3. `_process_events(delta_time)` — currently only handles `QUIT`.
4. `pygame.display.flip()`, then `clock.tick(FPS)`.

The CRT overlay class is constructed but not currently drawn each frame in the loop because the loop body is still a stub — that is one of the first items in [docs/TODO.md](TODO.md).

---

## 4. State machine (planned)

```
   TITLE  ----start match---->  DEAL  -->  PLAYER_TURN  <-->  OPPONENT_TURN
                                              |                    |
                                            stand                stand
                                              |                    |
                                              v                    v
                                              +-----> RESOLVE_HAND
                                                          |
                                                  (best of 5 hands)
                                                          |
                                                          v
                                                      MATCH_OVER --> TITLE
```

A hand is one round to 20; a match is best of five hands. Both states should live in a `GameState(Enum)` checked at the top of the input dispatch, mirroring the pattern used in `jezz-ball/main.py`.

---

## 5. Input model

The cabinet contract is:

- `Esc` exits to the launcher (planned for the keyboard handler).
- `Start + Back + L1 + R1` on any controller exits — this is **already implemented** in `GameManager.quit_combo_pressed` and checked at the top of every frame for held-state quits.
- Joystick add/remove events refresh the joystick cache via `handle_joystick_hotplug`.

Gameplay-specific input (draw, stand, play side-deck card, navigate side-deck) is undefined and tracked in [docs/TODO.md](TODO.md).

---

## 6. Settings as the only knob panel

[settings.py](../settings.py) groups every tunable into a `*Settings` class:

- `ColorSettings` — palette (currently three colors).
- `ScreenSettings` — `WIDTH`, `HEIGHT`, `RESOLUTION`, `FPS`.
- `ControllerSettings` — quit combo button indices.
- `AssetPaths` — image paths.

When adding a new tunable, add it to the most appropriate class with a comment explaining its **units**. Card values, hand limits, and match length will need new classes (`DeckSettings`, `MatchSettings`) — add them rather than overloading existing ones.

---

## 7. CRT post-process

[`ui/crt.py`](../ui/crt.py) is the standalone overlay class. It loads the TV image from `AssetPaths.TV` and applies it with a per-frame random alpha and scanlines. It must be the **last** thing drawn each frame once the render path is fleshed out.

---

## 8. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two that shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner:

```python
    # -------------------------
    # SECTION NAME
    # -------------------------
```

The scaffold already places empty banners for `GAMEPLAY ACTIONS`, `AUDIO / VOLUME ACTIONS`, `EVENT HANDLING`, and `PER-FRAME UPDATE / RENDER` inside `GameManager`. Fill those bands rather than introducing new ones.

**Function order inside a class.** Functions are grouped by role; `update` and `run` go **last** and should only call other functions on the class.

---

## 9. Source tree

```
ui/
  crt.py             CRT overlay
assets/
  graphics/, ...     Asset folders
docs/                ARCHITECTURE, TODO, TESTING, CHANGELOG
main.py              GameManager + entry point
settings.py          Tunables grouped into *Settings classes
```
