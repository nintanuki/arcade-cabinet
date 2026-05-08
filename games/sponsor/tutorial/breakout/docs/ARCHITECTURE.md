# Breakout — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                           +--------------+
                           |   main.py    |
                           |    Game      |   (coordinator)
                           +-----+--------+
                                 |
   +--------+----------+---------+---------+----------+
   |        |          |                   |          |
   v        v          v                   v          v
 Player   Ball     Block / Upgrade     SurfaceMaker  CRT
 (sprites)(sprites) Projectile         (surfacemaker)(legacy)
```

`Game` owns the screen, clock, joysticks, sprite groups, music, sound effects, and the CRT pass. Sprite classes live in [sprites.py](../sprites.py); brick face and paddle gradient surfaces are generated procedurally by [`SurfaceMaker`](../surfacemaker.py).

## 2. Sprite groups

- `all_sprites` — everything that needs to be drawn each frame.
- `block_sprites` — bricks; ball collision targets.
- `upgrade_sprites` — falling power-up tiles released when bricks die.
- `projectile_sprites` — laser shots fired by the paddle when the laser power-up is active.

`Player` is constructed with the joystick list so analog-stick polling survives controller hot-plug.

## 3. Frame loop

`Game.run()` (per frame): drain events → check quit combo → update sprite groups → handle ball/brick/upgrade collisions → handle projectile/brick collisions → draw sprites → CRT pass → flip.

## 4. Power-ups

When a brick dies, `Block.create_upgrade` may spawn an `Upgrade` sprite that falls. If it overlaps the paddle, an effect is applied:

- Paddle-grow.
- Paddle-shrink (negative).
- Speed change.
- Laser (paddle gains the ability to shoot `Projectile`s).
- Extra heart.

The exact effect tags and probabilities live in [settings.py](../settings.py).

## 5. Settings

[settings.py](../settings.py) holds the window dimensions, brick layout grid, paddle speed, ball speed, upgrade pool, and asset paths. Do not hard-code any of these in `main.py`, `sprites.py`, or `surfacemaker.py`.

## 6. Audio

Sounds are loaded directly inside `Game.__init__` (`laser`, `powerup`, `laser_hit`, looping `music`). Volumes are set per-sound. There is no shared `AudioManager` — keep audio loads local and fail loudly if a file is missing (this is a tutorial-grade game).

## 7. CRT

A `CRT` class draws scanlines + flicker as the last pass each frame.

## 8. Input model

- Keyboard arrows / `A` / `D` move the paddle. `Space` launches the ball and shoots laser projectiles when the laser upgrade is active.
- Controller D-pad and left analog stick move the paddle (D-pad takes priority). The A button launches / shoots.
- `Start + Back + L1 + R1` quit combo on any controller exits.

## 9. Source tree

```
graphics/, sounds/    Asset folders
main.py               Game + entry point
settings.py           All tunables
sprites.py            Player, Ball, Block, Upgrade, Projectile
surfacemaker.py       Procedurally-generated brick & paddle surfaces
docs/                 ARCHITECTURE, TODO, TESTING, CHANGELOG
```
