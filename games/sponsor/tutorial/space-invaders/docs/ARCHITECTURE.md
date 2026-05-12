# Space Invaders — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                         +---------------+
                         |   main.py     |   (entry point, event loop,
                         |     Game      |    sprite groups, score, pause)
                         +-----+---------+
                               |
   +-------------+-------------+-----------+-----------------+
   |             |             |           |                 |
   v             v             v           v                 v
core/sprites   ui/crt        settings    assets/        pause helpers
(Player,       (CRT          (all       (audio/,       (in main.py:
Alien,         overlay)      constants  font/,         render_pause_overlay,
Extra,                       grouped    graphics/)     run_pause_loop)
Laser,                       into
Block)                       *Settings)
```

`Game` (in [main.py](../main.py)) owns the screen, clock, joystick list, alien wave, sprite groups, score, lives, and the per-frame update / draw cycle. The entry-point `main()` function builds the screen, the `Game`, and the `CRT` overlay before entering the run loop.

## 2. Source tree

```
main.py                Entry point + Game class + pause overlay helpers
settings.py            Every tuning value, grouped into *Settings classes
core/
    __init__.py
    sprites.py         Player, Alien, Extra, Laser, Block sprite classes
ui/
    __init__.py
    crt.py             CRT scanline + flicker overlay
assets/
    audio/             Music + sound effects
    font/              Pixeled.ttf bitmap font
    graphics/          Player ship, aliens, UFO, bunker, TV overlay
docs/                  ARCHITECTURE, TODO, TESTING, CHANGELOG
```

## 3. Sprites ([core/sprites.py](../core/sprites.py))

- **`Player`** — horizontally-constrained ship. Reads keyboard + controller input each frame; fires a `Laser` on cooldown.
- **`Alien`** — single invader; multiple rows are spawned in a grid by `Game.alien_setup`.
- **`Extra`** — UFO that occasionally streaks across the top for bonus points.
- **`Laser`** — projectile, owned by either the player or an alien.
- **`Block`** — single brick used to build destructible bunkers (the bunker shape lives in `ObstacleSettings.SHAPE`).

## 4. Alien wave

Aliens march horizontally each frame. When any alien touches a screen edge, `Game.alien_position_checker` flips `alien_direction` and steps the whole group down by `AlienSettings.DESCEND_DISTANCE`. A repeating pygame timer event (`AlienSettings.LASER_INTERVAL_MS`) drives `Game.alien_shoot`, which spawns an alien-owned `Laser` from a random alien's center.

## 5. Frame loop ([main.py](../main.py) `main()`)

Per frame: poll quit combo → drain events (keyboard, joystick, alien-laser timer) → fill background → `Game.run(screen)` → CRT draw pass → flip. `Game.run` advances every sprite group, runs `collision_checks`, then draws lasers, ships, aliens, the UFO, and the HUD in order.

## 6. Scoring ([settings.py](../settings.py) `AlienSettings.POINTS`)

`AlienSettings.POINTS` maps each color to a point value (red 100, green 200, yellow 300). The UFO (`ExtraSettings.POINTS`) is worth 500. Score is rendered at the top-left in ALL CAPS by `Game.display_score`.

## 7. Pause ([main.py](../main.py))

`render_pause_overlay` paints a translucent backdrop plus a centered `PAUSED` label. `run_pause_loop` snapshots the active frame, blits that snapshot every tick, and waits for `Enter` / `Start` to resume or any quit signal to exit. Optional `sfx_sounds_pause2_in/out.wav` play if present.

## 8. Input model ([settings.py](../settings.py) `ControllerSettings`)

- Keyboard: `Left` / `Right` move; `Space` fires; `Enter` toggles pause; `F11` fullscreen; `Esc` quits.
- Controller: D-pad / left analog move; `A` fires; `Start` toggles pause; `Back` fullscreen; `Start + Back + L1 + R1` quit combo exits.

## 9. Constants discipline

All tuning values live in [settings.py](../settings.py). Adding a new number should mean adding a class attribute (or a new `*Settings` class when the value isn't closely related to its neighbors). Sprite modules and the CRT only import the settings they need — they never hard-code dimensions, colors, or asset paths.
