# Tetris — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                          +--------------+
                          |   main.py    |
                          |    Main      |   (coordinator)
                          +-----+--------+
                                |
   +--------+----------+--------+--------+----------+----------+
   |        |          |                 |          |          |
   v        v          v                 v          v          v
  Game   Score     Preview            Timer       CRT        Music
 (game)  (score)   (preview)         (timer)    (ui/crt)    (mixer)
```

`Main` (in `main.py`) owns the screen, clock, joystick cache, music handle, fullscreen flag, and the top-level update / render orchestration. `Game` owns the playfield grid, the active tetromino, drop / lock logic, and line clears. `Score` and `Preview` are HUD components.

## 2. Frame loop

`Main.run()` (per frame): drain events → check quit combo → call `Game.run`, `Score.run`, `Preview.run` (each draws into its panel) → CRT pass on the composed frame → flip.

## 3. The active tetromino

`Game` keeps the current tetromino as a list of cell coordinates plus a color. `Timer` schedules the gravity tick and the soft-drop tick. On every gravity tick `Game.move_down()` either translates the piece or, if it would collide with the floor or a settled block, **locks** the piece into the grid, runs the line-clear pass, and asks `Main.get_next_shape` for the next shape.

## 4. Next-shape pipeline

`Main` keeps a deque of three upcoming shape names (`self.next_shapes`). `Preview` reads this list each frame to render the next-up panel. When `Game` calls `get_next_shape`, `Main` pops from the front, appends a fresh random shape, and returns the popped name to `Game`.

## 5. Scoring

`Score` tracks total points, current level, and lines cleared. Line clears award progressively more points (single < double < triple < tetris). The level rises every N lines; gravity speed scales with level via the `Timer` interval.

## 6. Audio

Music is a looping `pygame.mixer.Sound` started in `Main.__init__` (`loops=-1`, low volume). A landing SFX plays on lock (loaded inside `Game`).

## 7. Input model

`Main` caches the joystick list once at startup and re-reads it for the quit-combo check each frame. Per-frame input is forwarded into `Game`:

- Keyboard: `Left` / `Right` move; `Down` soft-drops; `Up` rotates.
- Controller: D-pad horizontal moves; D-pad down soft-drops; A rotates.

Globals: `F11` and Back toggle fullscreen via `Main`. `Esc` and the quit combo exit.

## 8. CRT

[ui/crt.py](../ui/crt.py) draws scanlines + flicker as the last pass each frame.

## 9. Settings

[settings.py](../settings.py) defines the playfield size, block size, tetromino shape definitions (`TETROMINOS` keyed by name), colors, panel dimensions, font sizes, and asset paths (`BASE_PATH`). **No magic numbers in `main.py`, `game.py`, `score.py`, `preview.py`, or `timer.py`.**

## 10. Source tree

```
graphics/, sound/          Asset folders
ui/crt.py                  CRT overlay
game.py                    Game (playfield + active tetromino + lock + clear)
main.py                    Main + entry point + controller helpers
preview.py                 Preview panel
score.py                   Score + level HUD
settings.py                All tunables (incl. TETROMINOS, BASE_PATH)
timer.py                   Tick scheduler used for gravity / soft-drop
docs/                      ARCHITECTURE, TODO, TESTING, CHANGELOG
readme.txt                 Original CC0 / asset credits (preserved for attribution)
```
