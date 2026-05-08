# Runner — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                           +--------------+
                           |   main.py    |   (everything: event loop, sprites,
                           |              |    score, game-over, restart)
                           +-----+--------+
                                 |
                                 v
                              CRT overlay (crt.py)
```

This is a single-file game. `main.py` defines the `Player` and `Obstacle` (snail / fly) `pygame.sprite.Sprite` subclasses, the score helper, the game-over screen renderer, and the main event loop.

## 2. Player

`Player.__init__` loads two walk frames + a jump frame, sets a starting position from `PlayerSettings.INITIAL_POSITION`, and initializes the joystick list. `Player.player_input` reads keyboard + controller input each frame; jump is allowed only when the player rect is grounded (`bottom >= 300`). Gravity is integrated each `update`.

The walk frames cycle by index when the player is grounded; the jump frame is shown when airborne.

## 3. Obstacles

`Obstacle` (snail or fly) is created on a `pygame.USEREVENT` timer. Snails spawn on the ground line; flies spawn higher up. Both scroll left at the configured speed and `kill()` themselves when they leave the playfield.

## 4. Frame loop

Per frame: drain events → handle the obstacle-spawn timer → if the game is active, update sprites and check collision → draw background → draw sprites → draw score → CRT pass → flip. On collision the game falls into a "game-over" branch that renders a restart prompt; pressing `Space` (or A) starts a fresh run.

## 5. Input model

Priority order:

1. **Controller D-pad** — `joystick.get_hat(0)` x-axis.
2. **Left analog stick** — `joystick.get_axis(0)` clamped against `PlayerSettings.CONTROLLER_DEADZONE`.
3. **Keyboard** — arrow keys / `A` / `D` for horizontal motion; `Space` for jump.

Controller A button (button 0) also jumps.

## 6. Settings

[settings.py](../settings.py) groups constants:

- `ScreenSettings` — width, height, FPS, title.
- `PlayerSettings` — starting position, jump impulse, gravity, deadzone.
- `BackgroundSettings` — sky / ground rects.
- `AssetPaths` — graphics + audio paths.

**No magic numbers in `main.py`.**

## 7. CRT

[crt.py](../crt.py) draws scanlines + flicker as the last pass each frame.

## 8. Source tree

```
audio/, font/, graphics/   Asset folders
crt.py                     CRT overlay
main.py                    Entry point + Player + Obstacle + event loop
settings.py                ScreenSettings, PlayerSettings, BackgroundSettings, AssetPaths
docs/                      ARCHITECTURE, TODO, TESTING, CHANGELOG
```
