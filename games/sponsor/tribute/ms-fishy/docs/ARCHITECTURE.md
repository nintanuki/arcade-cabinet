# Ms. Fishy — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                    +---------------------+
                    |     main.py       |
                    |   GameManager     |   (coordinator)
                    +-----+---------+---+
                          |         |
          +----------------+       +---------------+
          v                        v               v
      events / input          SceneManager       render
   (keyboard, joystick)      (scene dispatch)   (to screen)
                                   |
                                   v
                            +-----------+
                            |   Scene   |
                            +-----------+
                                   A
                      +------------+----------+
                      |            |          |
                      v            v          v
                   PlayScene   TitleScene   GameOverScene
                   (gameplay)   (title)     (game-over)
```

`GameManager` owns the screen, the clock, the cached joystick list, the fullscreen flag, the main-loop `running` flag, a process-wide `Leaderboard` instance, and a `SceneManager` instance. Global input (Esc quit, F11 fullscreen, controller quit-chord, BACK) is handled by `GameManager`. Everything else — gameplay, scenes, UI, audio, persistence — is coordinated through scenes and the `SceneManager`.

## 2. Frame loop

`GameManager.run()` per frame:

1. `quit_combo_pressed()` — early-exit on the held quit chord.
2. `_process_events()` — drain pygame's event queue; handle global input in `GameManager`, forward scene-specific input to `scenes.current.handle_event(event)`.
3. `_update_world()` — calls `scenes.current.update()` to advance the active scene.
4. `_render_frame()` — calls `scenes.current.render(screen)` to draw the active scene, then applies CRT overlay (windowed only).
5. `pygame.display.flip()` and `clock.tick(FPS)`.
6. On shutdown, `pygame.quit()` runs after the loop exits. When `DebugSettings.WEB_SAFE_EXIT` is false, shutdown still raises `SystemExit`; when true, quit requests only clear the loop flag so web builds can exit cleanly.

## 3. Scenes (`core/scene.py`, `systems/scene_manager.py`, `ui/scenes/`)

A `Scene` is a discrete game state that handles its own events, updates, and rendering. The `SceneManager` ensures only one scene is active at a time and calls transition hooks.

### Scene lifecycle

- `on_enter()` — called once when this scene becomes active.
- `handle_event(event)` — called for each pygame event (after globals are handled by `GameManager`).
- `update()` — called once per frame to advance the scene.
- `render(screen)` — called once per frame to draw to the screen.
- `on_exit()` — called once when leaving this scene.

### Scenes in the game

#### `TitleScene` (`ui/scenes/title_scene.py`)

Launch scene shown on boot.

- **On Enter:** Stop music.
- **Update:** Spawns and advances background fish via `FishManager.update(player=None)`.
- **Render:** Draws the ocean gradient, background fish, centered `MS. FISHY` title text, and `PRESS START TO PLAY` prompt.
- **Handle Events:** Enter/START transitions to a fresh `PlayScene` and enables the title-intro splash cue.

#### `PlayScene` (`ui/scenes/play_scene.py`)

Handles active gameplay and pausing. Owns the player, run `Score`, all sprites, enemy sprites, and fish manager.

- **On Enter:** Set local substate to `DROPPING_IN`, place the player above the screen, and seed downward velocity from `PlayerSettings.DROP_IN_VELOCITY`. Music is intentionally deferred until drop-in completes.
- **Handle Events:** Enter/START toggles pause only when active (pause/resume SFX, music pause/resume); global input is not forwarded here.
- **Update:**
  - `DROPPING_IN`: advances one-time auto-pilot motion using the same acceleration/counter-acceleration/drag model as player movement, without reading input and without spawning fish.
  - During drop-in: if title-started, play one-shot `splash` SFX exactly when the player first crosses into the visible screen from the top.
  - On drop-in settle: start/resume gameplay music and switch to `ACTIVE`.
  - `ACTIVE`: runs a countdown from `TimerSettings.STARTING_SECONDS`; subtracts `1 / ScreenSettings.FPS` each frame, adds a time bonus when the player eats a fish, advances sprites and fish manager, records fish sizes from collision results into `Score`, and checks for game-over.
  - **Time bonus with diminishing returns:** `max(TIMER_MIN_RATIO, fish.size / player.size) × SECONDS_PER_EAT`. The bonus depends only on the *relative* size of the eaten fish, not its absolute pixel width, so eating a peer-sized fish always adds `SECONDS_PER_EAT` seconds regardless of player scale. When the eaten fish is much smaller the ratio approaches `TIMER_MIN_RATIO` (default 0.05), guaranteeing a small but non-zero reward.
  - `ACTIVE` transitions to `GameOverScene(score=..., outcome=...)` when a larger fish hits the player or when the countdown reaches zero.
  - `ACTIVE` additionally treats `player.rect.width > ScreenSettings.WIDTH` as a win condition (`WIN_ATE_ALL_FISH`) and transitions to `GameOverScene` with a victory outcome.
  - `PAUSED`: no world updates.
- **Render:** `DROPPING_IN` and `ACTIVE` draw ocean gradient + world sprites. During `ACTIVE`, `Hud.draw(screen, remaining_seconds)` is called after world sprites so score labels sit on top of gameplay. The HUD shows a countdown timer in the top-right. `PAUSED` draws black background + centered pause text.

#### `GameOverScene` (`ui/scenes/game_over_scene.py`)

Displays a two-step end-of-run flow before leaderboard routing.

- **Phase 1 render:** Black background + centered outcome text.
  - Loss path: `YOU WERE EATEN BY A BIGGER FISH`
  - Starvation path: `YOU STARVED TO DEATH`
  - Win path: `YOU'VE EATEN ALL THE FISH!`
  - Font size: `UiSettings.OUTCOME_MESSAGE_FONT_SIZE`.
  - Loss and starvation use red text.
- **Phase 2 render:** Black background + delayed stat tally reveal.
  - Reveals one line every `UiSettings.TALLY_LINE_REVEAL_DELAY_MS`:
    - `+ NUMBER OF FISH EATEN`
    - `+ TOTAL WEIGHT EATEN`
    - `+ MS. FISHY'S FINAL WEIGHT`
    - `+ SECONDS LEFT ON THE TIMER`
    - `= TOTAL SCORE!`
  - Final total line is highlighted in yellow.
- **Input:** Enter / controller A / controller START advances from phase 1 to phase 2. In phase 2, confirm routes onward only after all tally lines are visible.
- **Routing:** Always routes to `LeaderboardScene` after tally confirmation.
- **Data:** Receives both run `Score` and a run-ending `outcome` from `PlayScene`.

### `Score` (`core/score.py`)

Run-scoped model for points.

- Tracks `fish_eaten` (count), `size_eaten` (cumulative fish width in px), `final_weight` (player width at run end), and `time_left_seconds` (hunger timer at run end).
- `add(fish_size)` increments `fish_eaten` and `size_eaten`.
- `final_weight` and `time_left_seconds` are set by `PlayScene._end_run` just before transitioning to `GameOverScene`.
- `total` property computes the compound leaderboard score:
  `size_eaten × WEIGHT_EATEN_FACTOR + fish_eaten × FISH_EATEN_BONUS + final_weight × FINAL_WEIGHT_FACTOR + time_left_seconds × TIME_LEFT_BONUS`
  All factors live in `ScoreSettings`.

### `Hud` (`ui/hud.py`)

Lightweight gameplay overlay widget owned by `PlayScene`.

- Inputs: run `Score`, HUD font, player sprite (for live weight display).
- Layout: top-left stacked column:
  - `TOTAL FISH EATEN: NN`
  - `WEIGHT EATEN: NNNNN`
  - `CURRENT WEIGHT: NNNNN` (reads `player.size` live)
  - `HUNGER TIMER: MM:SS` — text turns red at or below `UiSettings.HUNGER_WARNING_SECONDS`
  - Hunger bar below the timer: full-width = green, empty = red (smooth RGB lerp), filled fraction = `remaining / STARTING_SECONDS`.
- Score is no longer shown in the HUD; it is computed from all stats at run end.

### `Leaderboard` (`systems/leaderboard.py`)

Process-scoped high-score service owned by `GameManager`.

- Persistence: loads and saves JSON at `AssetPaths.LEADERBOARD`.
- Table shape: top-10 entries sorted high-to-low.
- Initials rule: `submit` accepts only 3-letter A-Z initials, updates existing initials only on strictly better scores, and otherwise inserts/replaces by score cutoff.
- Consumers: currently read by `Hud`; game-over flow uses `qualifies` to prepare the initials-entry path in later pass items.



### `Player`

A `pygame.sprite.Sprite` representing the player fish.

- **Appearance:** Gradient polygon fish (yellow dorsal → orange belly, diamond body + triangle tail) with a small black square eye, a soft drop shadow, and a pink bow (two mirrored triangles meeting at a central apex) floating above the body's top point — Ms. Fishy's signature accessory. Built once at init and rebuilt only on `grow()`. Initial size `PlayerSettings.SIZE`.
- **Movement:** Arrow keys and left analog stick. Uses a velocity model: each frame of held input adds `PlayerSettings.ACCELERATION` to the velocity on that axis (capped at `PlayerSettings.MAX_SPEED`). When input is released, `PlayerSettings.DRAG` is multiplied into the velocity each frame until it falls below `PlayerSettings.STOP_THRESHOLD`, giving an underwater coast-and-stop feel. Direction flip waits until velocity exceeds `PlayerSettings.FLIP_THRESHOLD` so the sprite doesn't flicker while drifting to a stop. Sub-pixel accumulators (`_pos_x`, `_pos_y`) prevent fractional velocities from being silently discarded by `int()` truncation each frame.
- **Boundary:** `enforce_boundaries` clamps the rect to the screen edges, zeroes velocity on any clamped axis (so the player doesn't fight the wall), and resyncs the float accumulators to the clamped position.
- **Growth:** `FishManager.grow_player` calls `Player.grow(...)`, which rebuilds the fish polygon/mask at a larger size while preserving center position. `self.size` is stored as `float` so fractional growth (from `PLAYER_GROWTH_COEFFICIENT = 0.10`) accumulates across multiple fish eaten; the surface is always built from `int(self.size)`. Storing it as `int` would silently discard sub-pixel growth on every call.

### `Fish`

A `pygame.sprite.Sprite` representing an enemy fish.

- **Appearance:** Solid-color polygon fish (random color from `ColorSettings.FISH_PALETTE`, chosen at spawn) with a small black square eye of size `FishSettings.EYE_SIZE_RATIO * size` and a soft drop shadow. The palette is a curated set of retro hues chosen to contrast against the ocean gradient background.
- **Spawn:** From off the left or right edge at a random vertical position. Direction is set to match the side it spawned from (left→right, right→left).
- **Movement:** Constant horizontal speed in `[FishSettings.MIN_SPEED, FishSettings.MAX_SPEED]`, integrated through a float x-position accumulator and then written to `rect.x` each frame so sub-pixel speeds move smoothly in both directions. Self-destructs (`kill()`) once it clears the opposite edge by 50 px.

## 4. Fish manager (`systems/fish_manager.py`)

`FishManager` holds the `enemy_sprites` group and drives the fish lifecycle each frame:

1. **Spawn timer:** increments each frame; fires `spawn_fish()` every `FishSettings.SPAWN_RATE` frames (≈1 s at 60 FPS) and resets.
2. **Collision:** if `player is None`, collision is skipped and update returns `(False, [])`.
3. **Player collision path:** with a player, `check_collisions` calls `pygame.sprite.spritecollide` against the player.
  - Player size > fish size → `grow_player`, fish is killed, fish size is appended to the `eaten_fish_sizes` result.
  - Player size ≤ fish size → returns `True` to signal game-over.

When game-over is detected, the scene transitions automatically to `GameOverScene`.

## 5. Input

**Parity rule:** every action available on the keyboard must also be reachable on the controller. Keep this invariant when adding new input actions.

**Handler design rule:** input handlers (e.g. methods in scenes) must never call each other. When two input sources share a behaviour, extract that behaviour into a dedicated action method (e.g. `_handle_pause_action`) and have each handler call the action method directly. This keeps every handler self-contained and prevents one input path from silently inheriting unrelated side-effects of another.

**Global input routing:** `GameManager` handles global input (Esc quit, F11 fullscreen, controller quit-chord, BACK fullscreen). After global handlers, scene-specific input is forwarded to `scenes.current.handle_event(event)`.

Events are routed by type in `GameManager`:

- `KEYDOWN` → `_handle_keydown`. `Esc` is handled globally; `F11` is handled globally; other keys are forwarded to the scene.
- `JOYBUTTONDOWN` → `_handle_joybuttondown`. Quit-chord check is handled globally; `BACK` is handled globally; other buttons are forwarded to the scene.
- `JOYHATMOTION` → forwarded to scene.
- `JOYAXISMOTION` → forwarded to scene.

Player movement from the analog stick is polled directly in `Player.input()` each frame rather than being event-driven, so it is continuous. `PlayScene.update()` passes its cached `game.connected_joysticks` list to `all_sprites.update(joysticks=...)`, which forwards it to `Player.input()` — no per-frame `pygame.joystick.Joystick(i)` re-queries.


The joystick list is cached once at startup via `setup_controllers()`. Hot-plug requires re-running that method or re-init.

The quit chord is `InputSettings.JOY_BUTTON_QUIT_COMBO` (START + SELECT + L1 + R1). When all buttons are held on any connected controller, the game closes.

## 6. CRT overlay (`crt.py`)

`CRT` loads `AssetPaths.TV`, scales it to the screen, and on each `draw()` blits a fresh copy with a randomized alpha (flicker) and per-row scanlines. `GameManager` only constructs the CRT pass when `DebugSettings.ENABLE_CRT` is true, and `_render_frame` only calls it in windowed mode so it doesn't double-up on a real CRT cabinet.

## 7. Settings (`settings.py`)

Single source of truth for all tunables.

| Class            | Purpose                                                               |
| ---------------- | --------------------------------------------------------------------- |
| `ColorSettings`  | Named colors + semantic aliases (`BG_COLOR`, `OVERLAY_BACKGROUND`).  |
| `ScreenSettings` | Resolution, FPS, title, CRT alpha range, scanline height.             |
| `InputSettings`  | Controller button/axis indices + quit combo + analog threshold.       |
| `PlayerSettings` | Player movement speed and initial sprite size.                        |
| `FishSettings`   | Fish spawn rate, size range, speed range, player growth amount.       |
| `TimerSettings`  | Countdown starting time, seconds-per-pixel bonus, min ratio, and warning threshold. |
| `ScoreSettings`  | Weighting factors for the compound end-of-run score formula.         |
| `UiSettings`     | Overlay/HUD text labels, font sizes, and HUD padding.                 |
| `GameStateSettings` | Canonical state names (`playing`, `paused`, `game_over`).           |
| `FontSettings`   | Font file path.                                                       |
| `AudioSettings`  | Mute toggles + music volume + per-sound volume toggles.              |
| `AssetPaths`     | `__file__`-relative paths for non-font assets.                        |
| `DebugSettings`  | Debug-only toggles (including CRT enable/disable, web-safe loop exit, and optional large-player start for end-game testing). |

**No magic numbers anywhere outside this file.**

## 8. Source tree

```
assets/
  font/Pixeled.ttf              Pixel font for retro UI text.
  graphics/effects/tv.png       CRT overlay texture.
core/
  scene.py                      Base Scene class for game states.
  score.py                      Run-scoped score model (fish count + size total).
  sprites.py                    Player and Fish sprite classes.
systems/
  scene_manager.py              Scene manager for state transitions.
  fish_manager.py               Fish spawning, collision, and player growth.
  audio_manager.py              Data-driven sound and music system.
  leaderboard.py                Top-10 leaderboard model + JSON persistence.
ui/
  hud.py                         Gameplay HUD widget (fish count, score, high score).
  scenes/
    __init__.py
    title_scene.py              Boot title scene with background fish.
    play_scene.py               Active gameplay + pause overlay.
    game_over_scene.py          Game-over screen.
utils/
  graphics.py                  Shared gradient background helper.
  text.py                       Centered text drawing helper.
crt.py                          CRT post-processing overlay.
main.py                         Entry point + GameManager.
settings.py                     All tunables.
docs/                           ARCHITECTURE, TODO, TESTING, CHANGELOG.
.github/copilot-instructions.md Editor rules.
```

## 9. Current state-machine scope

- Active scenes: `TitleScene`, `PlayScene` (DROPPING_IN/ACTIVE/PAUSED substates), `GameOverScene`.
- Not yet implemented: `InitialsEntryScene`, `LeaderboardScene` (planned for Pass 2).

## 10. Audio (`systems/audio_manager.py`)

`AudioManager` is **data-driven**: every sound effect is declared in
`AudioSettings.SOUND_EFFECTS` (logical name → file path), and every gameplay
call site triggers one through a single entry point:

```python
self.audio.play("gulp")
self.audio.play("pause_in")
self.audio.play("scream")
```

Adding a new sound is one line in `settings.py`; the manager never changes.

**Why this shape:**

- **DRY.** No bespoke `play_X_sound` wrappers. One `play(name)` method covers every cue.
- **No middlemen.** Earlier drafts mapped each sound to a reserved
  `pygame.mixer.Channel`. For casual SFX that's overkill — pygame's default
  8-channel pool, used implicitly via `Sound.play()`, is sufficient and never
  drops audible cues in practice. If a future sound *must* never be cut off,
  the template documents a one-line opt-in for a dedicated channel.
- **Portable.** The class has zero game-specific identifiers; only the
  `AudioSettings` registry differs per project.

**Music API:** `play_random_music`, `pause_music`, `resume_music`,
`stop_music`, `toggle_mute`. `play_random_music` avoids back-to-back repeats
of the same track.

**Volume toggles:** `AudioSettings` now exposes `MUSIC_VOLUME_TOGGLE` plus
per-sound entries in `SOUND_EFFECT_VOLUMES` so music and individual cues can
be silenced by setting their multipliers to `0.0` without changing playback
call sites.

**Failure mode:** a missing asset or uninitialised mixer logs a warning and is
skipped; the game keeps running silently rather than crashing.

**Template:** `systems/audio_manager_template.py` is a self-documenting copy
intended to be lifted into other pygame projects. The header docstring
describes the `AudioSettings` contract the manager expects.

## 11. Extension points

- **More scenes:** add `InitialsEntryScene`, `LeaderboardScene` (planned for Pass 2).
- **Leaderboard scenes:** finish `InitialsEntryScene` and `LeaderboardScene` transitions and persistence writes during game-over flow.
- **Sprite art:** replace the `pygame.Surface` placeholders in `Player.__init__` and `Fish.__init__` with loaded images.

## 12. Project rules

- **No imported visual assets.** All sprites, backgrounds, particles, and
  visual effects must be drawn at runtime with `pygame.draw`,
  `pygame.Surface` operations, or per-pixel manipulation. Audio files and
  font files are allowed. The CRT overlay PNG
  (`assets/graphics/effects/tv.png`) is grandfathered as the only exception;
  do not add new image files.
- **Title-screen lock.** Keep `TitleScene` to exactly two centered text lines
  (`MS. FISHY` and `PRESS START TO PLAY`) over the ocean background and
  background fish. Do not add score/high-score/extra prompt text unless the
  user explicitly requests it.
