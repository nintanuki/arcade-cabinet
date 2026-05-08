# Air Hockey — Architecture

This document explains **how the Air Hockey code is put together and why**. It is meant for anyone touching the code — human or AI. It deliberately skips things any Pygame project does and focuses on the parts that are specific to this game.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                +-------------------+
                |   main.py         |
                |   class Game      |   (coordinator + input + render)
                +---------+---------+
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
      Audio              CRT          (pygame.Rect entities)
    (audio.py)        (crt.py)       player / opponent / puck /
                                     player_goal / opponent_goal
```

Today there is no entity class hierarchy — `player`, `opponent`, and `puck` are all `pygame.Rect` instances owned directly by `Game`. That is fine for the current scope; it is also explicitly listed in [docs/TODO.md](TODO.md) as a candidate for future extraction into sprite classes.

---

## 2. The frame loop

`Game.run()` is the single per-frame loop. Each iteration:

1. Compute `dt` from `clock.tick(FRAMERATE)`.
2. Check the controller quit combo (top of loop, for held-state quits).
3. Drain the event queue. The handler routes by event type and **also** by current screen state — there is a `show_title` branch and a normal-gameplay branch.
4. If `show_title` is True, draw the title screen and continue.
5. If `countdown > 0` (post-goal pause), draw a frozen field with the countdown number and continue.
6. Otherwise, run gameplay update: read input → move player paddle → clamp to rink halves → update velocity tracking → run `puck_movement` → run `opponent_movement` → `check_goals`.
7. Render: white field, dotted divider, goals, paddles (red ellipses), puck (black ellipse), scores, CRT overlay (windowed only), `display.flip()`.

`pause()` runs its own nested loop with its own event handling and render. Resuming returns control to `run()`.

The loop is intentionally documented "as-is" rather than aspirationally — the pending refactor in [docs/TODO.md](TODO.md) is to extract the input / update / render phases into helper methods.

---

## 3. The rink

The play field is portrait-oriented (`SCREEN_WIDTH = 50 * BLOCK_SIZE = 400`, `SCREEN_HEIGHT = 100 * BLOCK_SIZE = 800`). The rink is divided in half by a horizontal dotted line (`draw_dotted_line`).

- **Player half:** the bottom half. The paddle is clamped to `top >= SCREEN_HEIGHT/2` and `bottom <= SCREEN_HEIGHT`.
- **Opponent half:** the top quarter. The opponent paddle is clamped to `top >= 0` and `bottom <= SCREEN_HEIGHT/4`.
- **Goals:** thin horizontal `pygame.Rect`s spanning the middle quarter of the screen at the top (`opponent_goal`) and bottom (`player_goal`). Drawn with rounded corners (`BORDER_RADIUS`).

The asymmetry — opponent has only the top quarter to move in — is deliberate to keep the AI from running away from the puck.

---

## 4. Puck physics

`puck_movement()` is the heart of the game.

- **Wall bounces:** when the puck's bounding edges cross the rink edges, the corresponding velocity component flips and the bounce SFX plays.
- **Player paddle bounce:** uses a Pong-style relative-position formula — the bounce direction is `(relative_x, relative_y) * INITIAL_PUCK_SPEED`, where `relative_x` and `relative_y` are how far off-center the puck struck the paddle. The player's recent velocity is then added in at half-weight, so a moving paddle imparts spin/speed.
- **Opponent paddle bounce:** simpler — both velocity components flip — and a `collision_cooldown = 30` frames is applied so the puck cannot get re-hit while still inside the opponent rect. This is a **known band-aid** documented in `TODO.md`; a future pass should replace it with proper collision resolution that pushes the puck outside the rect.
- **Speed scaling:** every paddle hit calls `increase_speed()` which multiplies both components by 1.5, then `apply_speed_limit` clamps the magnitude to `[INITIAL_PUCK_SPEED, SPEED_LIMIT]`. This guarantees the puck never freezes (no zero-speed lock) and never tunnels (no insane-speed escape).
- **Friction:** every frame both velocity components are multiplied by 0.995. This is also flagged in `TODO.md` as creating a slow-drift state that can make the puck unreachable; the current `apply_speed_limit` minimum partially counters it but not perfectly.

---

## 5. Opponent AI

`opponent_movement()` is a 4-line greedy chaser: move toward the puck on each axis at `OPPONENT_SPEED` if the puck is on that side. There is no anticipation, no "get above the puck and hit it down" logic, and no difficulty scaling. This is intentional for the current phase; smarter AI is in `TODO.md`.

The clamping to the top quarter (see §3) effectively turns the opponent into a competent goalie even with this trivial AI — to the point that the game is currently flagged as *too hard*.

---

## 6. Input model

Three input devices are routed through one event loop:

- **Mouse:** the paddle's center snaps to the mouse cursor each frame. Left mouse button press/release toggles `is_spiking`.
- **Keyboard:** global keys only (`Enter` pause, `M` mute, `F11` fullscreen, `Esc` quit, plus `Return / Space` to confirm input on title screen).
- **Controller:** left stick drives paddle motion via `pygame.JOYAXISMOTION` events, with a 0.15 deadzone. `A` button (button 0) toggles `is_spiking`. `Start` (button 7) pauses. `Back` (button 6) toggles fullscreen. `Start + Back + L1 + R1` exits.

`input_mode` ("mouse" / "joystick") tracks which is currently active. Once the player picks a mode on the title screen, `locked_input_mode` pins it for the match and the per-event handlers refuse to switch modes mid-match. This prevents the paddle from "fighting" between mouse drift and stick input.

`JOYDEVICEADDED` events register hot-plugged controllers mid-match.

---

## 7. The title screen

`show_title` flips off only after `_confirm_input_mode()` runs. Until then, the gameplay branch of the event loop and the gameplay render are skipped entirely. The title screen has its own draw routine (`_draw_title_screen`) that paints the title, the two input options with a `>` selector, hint lines, and a red "NO CONTROLLER DETECTED" warning when no joysticks are connected.

If the player picks **CONTROLLER** but no joystick is connected, `_confirm_input_mode` silently downgrades to **MOUSE**. This avoids a soft-lock.

---

## 8. The countdown

After a goal, `start_countdown()` sets `countdown = 3` and arms a one-second `pygame.time.set_timer` (`COUNTDOWN_EVENT`). Each tick decrements the value and renders a frozen field with the number on screen. When it reaches zero, the timer is disarmed and `reset_puck()` repositions the puck on the side opposite the scoring goal with a randomized initial velocity.

During countdown the gameplay update is skipped — paddles don't move, AI doesn't move, the puck is invisible (its position has been moved to the reset coordinate but rendering doesn't draw it during countdown).

---

## 9. Audio

[`Audio`](../audio.py) preloads five sounds onto five dedicated `pygame.mixer.Channel` instances:

| Channel | Sound | Trigger |
| --- | --- | --- |
| 0 | `pong_bg_music.ogg` | Background loop (currently disabled by default — `MUTE_MUSIC = True` in settings) |
| 1 | `pong.ogg` | Wall and paddle bounce |
| 2 | `score.ogg` | Goal |
| 3 | `sfx_sounds_pause2_in.wav` | Pause |
| 4 | `sfx_sounds_pause2_out.wav` | Unpause |

Each sound has its own channel so they never preempt each other. Mute (`M`) iterates the channels and sets volume to zero or back. **Known bug:** unmuting forces all channels to 0.5, ignoring per-channel configured levels — see [docs/TODO.md](TODO.md).

---

## 10. CRT post-process

[`CRT`](../crt.py) renders the TV-frame overlay and scanlines. It is drawn last each frame, but **only** in windowed mode — `if not self.full_screen: self.crt.draw()`. In fullscreen the overlay is skipped, on the assumption the cabinet's physical CRT is doing the work. This is intentional and worth preserving when refactoring the render phase.

---

## 11. Settings

[settings.py](../settings.py) is currently a flat module of `UPPER_CASE` constants. Every other module imports them with `from settings import *`. This is a *transitional* state — the plan in [docs/TODO.md](TODO.md) is to group them into `*Settings` classes (matching the rest of the arcade) but the migration has not happened yet.

When adding a new constant, add it here with a comment explaining its **units** and what changing it does. Do not introduce new magic numbers in any other file.

`MUTE_MUSIC = True` is the global music toggle. Today the gameplay loop checks it directly (`if not MUTE_MUSIC:`) before starting the BG channel.

---

## 12. What's *not* here yet

These will get their own sections as they are built:

- **Score-to-win condition** and post-match results screen.
- **High-score table** persisted to disk.
- **Sprite classes** for player / opponent / puck (currently bare `Rect`s).
- **Refactored `run()`** split into input / update / render helpers.
- **Better opponent AI** that anticipates puck trajectory.
- **Delta-time-based puck motion** that doesn't slow the puck to a crawl.
