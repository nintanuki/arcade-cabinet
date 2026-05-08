# Space Invaders — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                          +--------------+
                          |   main.py    |   (coordinator: event loop, sprite
                          |    Game      |    groups, alien wave logic, score)
                          +-----+--------+
                                |
   +--------+----------+--------+--------+----------+
   |        |          |                 |          |
   v        v          v                 v          v
 Player    Alien     Extra            Laser      Obstacle
 (player)  (alien)   (alien)          (laser)    (obstacle)
```

`Game` (in `main.py`) owns the screen, clock, joystick list, alien wave, sprite groups, score, lives, and the per-frame update / draw cycle.

## 2. Sprites

- **`Player`** ([player.py](../player.py)) — horizontally-constrained ship. Reads keyboard + controller input each frame; fires a `Laser` on cooldown.
- **`Alien`** ([alien.py](../alien.py)) — single invader; multiple rows of these are spawned in a grid.
- **`Extra`** ([alien.py](../alien.py)) — UFO that occasionally streaks across the top for bonus points.
- **`Laser`** ([laser.py](../laser.py)) — projectile, owned by either the player or an alien.
- **`Obstacle`** ([obstacle.py](../obstacle.py)) — destructible bunker built from a brick grid; bricks `kill()` themselves on laser collision.

## 3. Alien wave

Aliens are arranged in rows. Each frame `Game` shifts the whole group horizontally; if any alien hits a screen edge, the group flips horizontal direction and drops one row. Aliens occasionally fire by selecting a random alien and spawning an alien-owned `Laser` from its position.

## 4. Frame loop

`Game.run()` (per frame): drain events → check quit combo → update player → update alien group + alien lasers → update player lasers → resolve collisions (player-laser ↔ alien / extra / obstacle ; alien-laser ↔ player / obstacle) → draw → CRT pass → flip.

## 5. Scoring

Each alien type has a different point value (front rows worth less, back rows more). `Extra` is worth a randomized bonus. Score is rendered at the top of the screen.

## 6. Pause

A pause overlay reuses the shared `Pixeled` font (loaded by `load_pause_font`, which falls back to alternative font paths if the local copy is missing). Toggling pause freezes the update loop but keeps drawing the last frame.

## 7. Input model

- Keyboard: `Left` / `Right` move; `Space` fires; `Esc` quits.
- Controller: D-pad left / right move; A button fires; `Start + Back + L1 + R1` quit combo exits.

## 8. Source tree

```
audio/, font/, graphics/   Asset folders
alien.py                   Alien + Extra sprites
laser.py                   Laser sprite
main.py                    Game + entry point + controller helpers
obstacle.py                Obstacle bunker
player.py                  Player ship
docs/                      ARCHITECTURE, TODO, TESTING, CHANGELOG
```

There is no `settings.py` yet — moving constants out of `main.py` is a roadmap item.
