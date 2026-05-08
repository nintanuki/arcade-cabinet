# Ninja Frog — Architecture

This document explains **how the Ninja Frog code is put together and why**. It is meant for anyone touching the code — human or AI. The build is currently a prototype, so several systems described here are intentionally minimal and called out as such.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                           +----------------+
                           |   main.py      |
                           |  GameManager   |   (coordinator)
                           +-------+--------+
                                   |
   +---------+---------+-----------+-----------+----------+----------+
   |         |         |           |           |          |          |
   v         v         v           v           v          v          v
RenderManager Camera CollisionManager Player   Enemy     CRT      tile_maps
 (render.py)  (camera.py) (main.py)  (sprites.py)      (crt.py)  (tile_maps.py)
```

Responsibility split:

- **`GameManager`** owns the screen, clock, controllers, the active map, the camera, the player, the enemy group, and the CRT. It dispatches input and runs the render loop.
- **`CollisionManager`** turns a tile-symbol grid into solid rects and resolves horizontal/vertical collisions against them.
- **`RenderManager`** draws the tile map by indexing into the terrain spritesheet.
- **`Camera`** computes a view rect that follows the player, clamped to map bounds, with a debug zoom-out toggle.
- **`Player` / `Enemy`** are `pygame.sprite.Sprite`s with their own animation, physics, and (for the enemy) AI.
- **`CRT`** is the optional post-process scanline overlay (currently disabled in `run`).
- **`tile_maps`** is data only: `TILE_LEGEND` (symbol → spritesheet index + solid flag) and `MAP_01` (the current map grid).

---

## 2. The frame loop

`GameManager.run()`:

1. Check the controller quit combo (top of frame, for held-state quits).
2. Drain `pygame.event.get()` and dispatch by event type — quit, fullscreen toggle, escape, zoom toggle.
3. Update the camera against the player rect.
4. Pick a render surface — a smaller surface when zoomed (so pixel-art scaling is cheap), or the screen directly when zoomed out.
5. Fill the background, draw the map, update and draw the player, update and draw enemies.
6. If zoomed, scale the render surface up to the screen.
7. `pygame.display.flip()` then `clock.tick(FPS)` cap the framerate at 60.

The CRT overlay call (`self.crt.draw()`) is currently commented out because the look did not suit the bright pixel art; it remains in the codebase so it can be re-enabled per-game later.

---

## 3. The world model

### Tile grid
A map is a list of rows of single-character symbols. The map is currently 20 columns × 30 rows at 16 × 16 px per tile, which is 320 × 480 in world space. The screen is 1.5× the map width (480 × 480) so the entire row of tiles is always visible — the camera is intentionally vertical-only. This is encoded in `ScreenSettings.WIDTH = TileSettings.SIZE * TileSettings.COLUMNS * 3 // 2`.

### Tile legend
[`TILE_LEGEND`](../tile_maps.py) maps each symbol to a `{'index': int, 'solid': bool}`. Adding a new tile type means adding one entry here — `RenderManager` looks up `index` to pick the sprite, `CollisionManager` looks up `solid` to decide whether to add the tile to the solid-rects list.

### Tile viewer
[tile_viewer.py](../tile_viewer.py) and [tile_viewer.html](../tile_viewer.html) are dev tools for finding tile indices in the spritesheet visually. They are not used at runtime.

---

## 4. Collision

`CollisionManager` is rebuilt once per map load. It walks the grid and produces a flat list of `pygame.Rect`s for every solid tile. Per-frame collision queries iterate this list — fine at this map size; would be a candidate for a spatial grid if maps grow.

`resolve_horizontal` and (its vertical counterpart on `Player`) snap the player rect against the colliding tile. The horizontal resolver guards against accidentally treating floor tiles as walls by requiring the player's `centery` to fall inside the tile's vertical span.

**Known issue (TODO):** the player can occasionally phase up walls or "bounce" off corners. Both are tracked in [docs/TODO.md](TODO.md).

---

## 5. The player

[`Player`](../sprites.py) tracks position with float accumulators (`pos_x`, `pos_y`) so fractional speeds aren't lost to integer truncation when written back to `rect`.

### Animation states
Four spritesheets are loaded into the `animations` dict: `idle`, `run`, `jump`, `fall`. Each is a horizontal strip of 32 × 32 frames sliced by `load_frames`. The current animation is selected each frame from physics state:
- On ground + horizontal velocity → `run`
- On ground + no horizontal velocity → `idle`
- Airborne + rising → `jump`
- Airborne + falling → `fall`

The frame index is a float advanced by `PlayerSettings.ANIMATION_SPEED` per frame; converting to int picks the displayed frame.

### Physics
Standard platformer integration: gravity adds to `velocity_y` each frame, `velocity_y` is clamped to a terminal value, then position is updated and resolved against collisions. Jump is impulsive: pressing jump while `on_ground` sets `velocity_y = JUMP_STRENGTH` (negative).

### Input
`get_input(joysticks)` reads keyboard + controller in the same call and returns `(moving_left, moving_right, running)`. Jump is read as an edge in the same scan because there's only one jump key — multiple presses per held button aren't a concern at this scope. Run multiplies the move speed.

---

## 6. The enemy

`Enemy` (the snail) walks horizontally at `EnemySettings.SPEED`, flips direction on wall collision, and falls under gravity. Stomping it (player landing on top while falling) kills it and bounces the player by `PlayerSettings.STOMP_BOUNCE`. Side collision with the player is currently a no-op — proper hit/death is on the TODO list.

---

## 7. The camera

[`Camera`](../camera.py) computes a view rect each frame:

- **Zoomed in** (default): the view is `screen_size / ZOOM_FACTOR` in world space, then scaled back up to fit the screen.
- **Zoomed out** (debug, toggle with `Z`): the view is the full screen size in world space, no scaling.

The view is clamped so it never shows past the left, right, or bottom of the map. There is no top clamp by design — the level scrolls upward indefinitely as more rooms are added.

`Camera.x` / `Camera.y` are subtracted from world rects when blitting, so each draw site does `rect.move(-self.camera.x, -self.camera.y)`.

---

## 8. Rendering

`RenderManager.draw_map(map, camera, surface)` walks the visible tile range (derived from the camera view rect) and blits the matching subsurface from the terrain spritesheet for each tile. Empty tiles are skipped. The terrain sheet is loaded once at construction.

Sprite drawing is done directly in `GameManager.run` rather than through `RenderManager` to keep the prototype straightforward. Promoting sprite draws into a sprite group inside `RenderManager` is on the TODO list.

---

## 9. The CRT post-process

[`CRT`](../crt.py) is the same scanline + flicker overlay used elsewhere in the cabinet. It is currently disabled in `run` because the look did not match the bright pixel art. The setup remains in place so it can be re-enabled per-game later without touching boot code.

---

## 10. Settings as the only knob panel

[settings.py](../settings.py) groups every tunable into a `*Settings` class, plus `AssetPaths`. Subsystems import the classes they need.

When adding a new tunable, add it to the most appropriate `*Settings` class with a comment explaining its **units**.

---

## 11. Input model

Two devices, one event loop:

- **Keyboard** events → `KEYDOWN` / `KEYUP` for global controls (fullscreen, escape, zoom). Movement is read via polled `pygame.key.get_pressed()`.
- **Controller** events → `JOYBUTTONDOWN` for `Select` (fullscreen toggle). Movement is read each frame via `joy.get_axis`, `joy.get_hat`, and `joy.get_button`.

Globals that intentionally fall through every other handler:
- `F11` and Select both toggle fullscreen.
- `Esc` exits.
- `Start + Select + L1 + R1` quit combo on any controller exits immediately (top-of-frame held-state check).

---

## 12. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two that shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner:

```python
    # ------------------------------------------------------------------
    # SECTION NAME
    # ------------------------------------------------------------------
```

**Function order inside a class.** Functions are grouped by role; `update` and `run` go **last** and should only call other functions on the class.
