# Air Hockey — Roadmap

This file tracks work in **phases**. Each phase has a clear goal; finish a phase before moving on. Items inside a phase can move between phases as priorities shift.

---

## Phase 1 — Critical bug fixes

**Goal:** Eliminate states that make the game unplayable or visibly wrong.

- [ ] **Puck gets stuck "inside" the opponent paddle.** The current `collision_cooldown = 30` frames is a band-aid. Replace with proper collision resolution that pushes the puck outside the opponent rect along the shortest separation axis.
- [ ] **Player paddle can stick to the side of the rink.** Reproduce by holding the cursor or stick against the wall. Investigate clamping interaction with `is_spiking`.
- [ ] **Puck can stick to a wall or in a corner.** Likely an interaction between the wall flip, the friction multiply, and `apply_speed_limit`. Verify the puck always escapes a corner within ~0.5s.
- [ ] **Mute toggle ignores per-channel volume.** `M` while unmuting forces all channels to 0.5 (see code note in `main.py` event handler). Save and restore each channel's prior volume instead.
- [ ] **`self.game_active` is unused.** It's set but never read. Either implement game-over gating around it or remove it.

## Phase 2 — Code health refactor

**Goal:** Make `main.py` and `settings.py` match the rest of the arcade in structure.

- [ ] Group constants in `settings.py` into `*Settings` classes (`ScreenSettings`, `RinkSettings`, `PuckSettings`, `PaddleSettings`, `ColorSettings`, `InputSettings`, `AudioSettings`). Replace `from settings import *` with explicit imports.
- [ ] Split the giant `Game.run()` method into `_process_events`, `_update`, `_render_frame` helpers. `run` should only call them.
- [ ] Extract `Player`, `Opponent`, and `Puck` into entity classes (probably as `pygame.sprite.Sprite` subclasses). Keep the same outward API `Game` already uses.
- [ ] Add a section-banner pass to `main.py` (init, input, gameplay update, render, lifecycle) using the project banner style.
- [ ] Implement delta-time-based motion for the puck without making it slow to a crawl. Probably means dropping the per-frame 0.995 friction multiply and using a velocity decay rate per *second*, with a minimum-speed floor enforced inside the integration step.
- [ ] Use `pygame.math.Vector2` for puck and player velocity instead of paired floats.

## Phase 3 — Game balance

**Goal:** The game should feel winnable.

- [ ] **Opponent is too good.** Loosen the AI: cap reaction speed, add a small reaction delay, or reduce the paddle clamp area in proportion to puck speed.
- [ ] **Puck slows down too much.** Tune `apply_speed_limit` minimum or remove the friction term entirely (see Phase 2 delta-time refactor).
- [ ] Add a difficulty selector on the title screen (Easy / Normal / Hard) that picks an AI profile.
- [ ] Smarter AI: instead of chasing the puck, the opponent should try to position above the puck and strike toward the player goal.

## Phase 4 — Match flow and persistence

**Goal:** Real matches with real outcomes.

- [ ] Score-to-win: first to N goals wins. Configurable in settings.
- [ ] Post-match results screen with a "play again" prompt.
- [ ] High-score table written to disk (similar to `high_score.txt` used in other arcade games).
- [ ] Track and display match time / best time per win.

## Phase 5 — Polish

- [ ] **Add the mute icon** to the HUD when muted. (Carried over from the original TODO.)
- [ ] Hide the OS mouse cursor while in joystick mode.
- [ ] Pre-match player-name input (4-letter classic-arcade style) for high scores.
- [ ] Funny score-based commentary text (e.g. messages that change as one side falls behind). (Carried over from the original TODO.)
- [ ] Animated puck trail or paddle hit-flash for game feel.
- [ ] Verify CRT overlay looks right on the cabinet's physical display.

---

## Code health audit (spotted during the documentation pass)

- [ ] `Audio.update()` repeats `set_volume` calls per sound — replace with an iterable of `(sound, base_volume)` pairs.
- [ ] `Game.__init__` sets `self.game_active = False` but it is never read.
- [ ] `INITIAL_PUCK_SPEED = 10` is also used as a "minimum speed" by `apply_speed_limit` — extract a separate `MIN_PUCK_SPEED` constant when the settings are grouped.
- [ ] Stray asset files at the project root (`Pixeled.ttf`, `english.png`) should move into `assets/font/` and `graphics/` respectively. Keep paths in sync when moving.

---

## Open Questions / Known Challenges

- **Delta-time vs. fixed-step physics.** Air hockey at 60 FPS with simple AABB collision is fine fixed-step, but supporting variable framerates (Steam Deck, weaker hardware) needs a sub-step integrator so the puck never tunnels through a paddle at high speed.
- **Mute persistence.** Should the mute state survive between sessions? Currently it resets every launch.
- **Two-player mode.** A second player on a second controller would require splitting input and giving the opponent a player-driven movement path. Possible but invasive — defer until match flow is solid.

---

## Documentation maintenance

Every phase pass must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect any system that changed shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
