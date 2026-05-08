# Flappy Bird — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                          +--------------+
                          |   main.py    |
                          |    Game      |   (coordinator)
                          +-----+--------+
                                |
   +--------+----------+--------+--------+----------+----------+
   |        |          |                 |          |          |
   v        v          v                 v          v          v
  BG     Ground      Plane            Obstacle     CRT      Music/SFX
 (sprites)(sprites) (sprites)         (sprites)   (crt)    (pygame.mixer)
```

`Game` owns the screen, clock, sprite groups, score, menu surface, joystick list, pause state, music handle, and the CRT pass.

## 2. Sprite groups

- `all_sprites` — drawn each frame.
- `collision_sprites` — what the plane checks against (ground + obstacles).

## 3. Scale factor

Background art is authored at a fixed pixel height. `Game` measures the loaded background height and computes `scale_factor = ScreenSettings.HEIGHT / bg_height`, then passes that to every sprite that needs to render at the active window size. The plane uses `scale_factor / 1.7` to stay visually correct against the larger background.

## 4. Frame loop

`Game.run()` (per frame): drain events → check quit combo → if not paused, update sprite groups and check collisions → draw sprites → render score → CRT pass → flip.

## 5. Obstacle spawning

`pygame.time.set_timer(self.obstacle_timer, 1400)` fires a custom event every 1400 ms. The handler creates a top/bottom `Obstacle` pair at a randomized vertical gap. Obstacles auto-destroy when they leave the left edge.

## 6. Game state

A simple `self.active` boolean toggles between the title-menu view (with `menu_surf`) and the live gameplay view. `Game` resets the plane, clears obstacles, and zeroes `score` whenever a new run starts.

## 7. Pause

Tapping `P` (or Start) toggles `self.paused`, plays a short pause-in or pause-out SFX, and freezes the update loop. Rendering still draws the last frame plus a "PAUSED" overlay.

## 8. Audio

Background music loops indefinitely (`loops=-1`) from `assets/sounds/music.wav`. Pause SFX (`sfx_sounds_pause2_in.ogg` / `sfx_sounds_pause2_out.ogg`) play on toggle. Plane has its own SFX (loaded inside `Plane.__init__`).

## 9. CRT

`crt.py` exposes a `CRT` class that draws scanlines + flicker as the last pass each frame.

## 10. Settings

[settings.py](../settings.py) exposes `ScreenSettings` (width, height, FPS) plus other tunables. **No magic numbers in `main.py` or `sprites.py`.** Asset paths are still inline strings inside `Game.__init__`; consolidating them into an `AssetSettings` class is a roadmap item.

## 11. Source tree

```
assets/                graphics/, sounds/, etc.
crt.py                 CRT overlay
main.py                Game + entry point
settings.py            All tunables (ScreenSettings, etc.)
sprites.py             BG, Ground, Plane, Obstacle
docs/                  ARCHITECTURE, TODO, TESTING, CHANGELOG
```
