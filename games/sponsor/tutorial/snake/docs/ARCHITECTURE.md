# Snake — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                          +--------------+
                          |  snake.py    |   (everything: SNAKE, FRUIT, MAIN
                          |              |    helpers, event loop)
                          +--------------+
```

This is a single-file game. `snake.py` defines:

- **`SNAKE`** — body segment list (each segment a `Vector2`), heading, growth flag, draw helpers.
- **`FRUIT`** — apple position; randomized to a free cell on respawn.
- **`MAIN`** — game-state coordinator: holds a `SNAKE` and `FRUIT`, runs `update`, `draw`, and `check_collision` each tick.
- Helpers — `refresh_joysticks`, `quit_combo_pressed`, `close_game`, `set_snake_direction`, `controller_direction`.

## 2. Movement model

Movement is grid-based: a `pygame.USEREVENT` timer fires at the configured tick rate. On each tick `MAIN.update` shifts the snake one cell in `snake.direction`, regrows if the apple was eaten, and runs collision checks.

`set_snake_direction` blocks 180-degree reversals: if the current heading is `(0, 1)` (down), pressing up is ignored. This prevents instant self-collision.

## 3. Input model

Per-frame:

1. Keyboard arrow keys produce a candidate `Vector2` heading.
2. Controller D-pad (`get_hat(0)`) overrides if any direction is held.
3. The left analog stick (`get_axis(0)` / `get_axis(1)`) acts as a fallback once it crosses `AXIS_DEADZONE = 0.6`.

The first valid signal each frame is fed through `set_snake_direction`.

Globals: `Esc` and the controller quit combo (`Start + Back + L1 + R1`) call `close_game`.

## 4. Collision

- **Wall:** the head leaves the grid → game over.
- **Self:** the head occupies any other body segment → game over.
- **Apple:** the head occupies the fruit cell → snake grows, fruit respawns on a free cell.

## 5. Source tree

```
Font/, Graphics/, Sound/   Asset folders
snake.py                   Entry point + SNAKE + FRUIT + MAIN + event loop
docs/                      ARCHITECTURE, TODO, TESTING, CHANGELOG
```

There is no `settings.py` yet — moving constants out of `snake.py` is a roadmap item.
