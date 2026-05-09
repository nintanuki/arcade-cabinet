# Fishy — Roadmap & TODO

Move completed items from `[ ]` to `[x]`. Do not delete entries.

---

## Completed

- [x] `GameManager` frame loop (events → update → render → flip).
- [x] Keyboard and controller input routing.
- [x] `F11` / `BACK` fullscreen toggle.
- [x] `Esc` keyboard quit.
- [x] `START + SELECT + L1 + R1` controller quit chord.
- [x] CRT overlay (scanlines + flicker, windowed only).
- [x] `Player` sprite with arrow-key and left-stick movement, screen-boundary clamping.
- [x] `Fish` sprite spawning from left/right edges, scrolling across, self-destructing off-screen.
- [x] `FishManager` spawn timer and eat-or-be-eaten collision logic.
- [x] Player grows when eating a smaller fish (`FishSettings.PLAYER_GROWTH_RATE`).
- [x] Session ends when a larger fish hits the player.

---

## In progress

*(nothing active)*

---

## Core gameplay polish

- [x] **Pixel-perfect (mask) collision** — swap `spritecollide` for `collide_mask` now that fish are polygon shapes; bounding-box overlap fires in empty transparent corners.
- [x] Game-over screen instead of abrupt `sys.exit()` when eaten — black screen, large centered `Pixeled.ttf` white text ("GAME OVER" / restart prompt). No abrupt exit.
- [ ] Title / start screen before gameplay begins.
- [ ] Scene/state machine: `title → playing → game_over → (restart or quit)`.
- [x] Pause feature — `Enter` key freezes world, stops music, shows centered pause text on black; resume restores music. Play `sfx_sounds_pause2_in.ogg` on pause and `sfx_sounds_pause2_out.ogg` on unpause.
- [ ] Score counter: track fish eaten or total pixels consumed; display in the HUD.
- [ ] High-score persistence: save the session's top score to a JSON file next to `main.py`.

---

## Feel and difficulty

- [ ] Difficulty ramp: gradually decrease `FishSettings.SPAWN_RATE` and increase fish speed as the session goes on.
- [ ] Fish variety: multiple size tiers with distinct colors so the player can read threat level at a glance.
- [ ] Player growth cap or diminishing-returns curve so the endgame stays interesting.
- [ ] Screen-wrapping option (player exits left edge → re-enters right edge) as an alternative to boundary clamping.

---

## Visuals

- [x] **Player fish shape** — give the player the same diamond-body + triangle-tail polygon treatment as enemy fish; remove the yellow square placeholder.
- [ ] **Enemy fish color variety** — randomize or tier fish colors so threat level is readable at a glance.
- [x] **Fish eyes** — small black square centered vertically, positioned one-quarter of the way from the nose toward the start of the tail.
- [ ] **Fish outlines / shadow** — add a black outline or drop-shadow to all fish (player and enemy) for legibility against the background.
- [ ] **Player distinction** — give the player a unique color, gradient, or other visual marker so it stands out from enemy fish.
- [ ] Replace fish polygon shapes with imported sprites once art is ready (multiple frames for swim cycle).
- [ ] Scrolling ocean background or parallax layers.
- [ ] Particle effect when the player eats a fish (splash, bubbles).

---

## Audio

- [ ] Initialize `pygame.mixer` in `GameManager.__init__`.
- [ ] Eat sound effect triggered in `FishManager.grow_player`.
- [ ] Death sound triggered on game-over.
- [ ] Looping background music that respects `AudioSettings.MUTE_MUSIC`.
- [ ] All audio toggle via `AudioSettings.MUTE`.

---

## Code-health items inherited from the template

- [x] `crt.py` used `from settings import *`. Now uses explicit imports.
- [x] `AudioSettings.MUTE` / `DebugSettings.MUTE` were duplicated. Kept `AudioSettings.MUTE`; removed the duplicate.
- [x] `AssetPaths.TV` was a cwd-relative path. Now `__file__`-relative, like `FontSettings.FONT`.
- [x] `GameManager.__init__` carried an unused `self.game_active`. Removed.
- [x] `pygame.display.set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)` had redundant parens. Removed.
- [x] Empty `core/`, `systems/`, `ui/`, and `utils/` folders now have `__init__.py` files so git tracks them.
- [x] `Esc` is wired in `_handle_keydown` so the game runs without a controller.
- [x] `ScreenSettings.TITLE` is still `"Pygame Template"` — update to `"Fishy"`.
- [ ] `FishManager.check_collisions` calls `pygame.quit()` / `sys.exit()` directly — should route through `GameManager.close_game()` or a scene transition instead.
- [ ] `Player.input()` re-queries `pygame.joystick.Joystick(i)` every frame — should use the cached list from `GameManager`.

---

##

- [ ] Player does not appear to be growing in size from eating smaller fish anymore! (First Priority)
- [ ] Add more realistic/challenging movement, there should be some initial inertia when first moving, and when the player lets go of the arrow key or analog stick the player should still keep moving a little before slowing down.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md).
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md).
3. Move completed items here from `[ ]` to `[x]` (do not delete).
