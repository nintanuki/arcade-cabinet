# Adventure — Roadmap

This file tracks work in **phases**. Each phase has a clear goal; finish a phase before moving on. Items inside a phase can move between phases as priorities shift, but Phase 1 is intentionally minimal — *get to a real, playable slice first, then expand.*

The original priority order from the previous TODO ("refactor → docs → bug fixes → balance → features, in strict order") is preserved as a **per-pass discipline** rather than a project-wide phase ordering: inside any single pass, do refactor work before adding new features.

---

## Phase 1 — Real Player and First Cell

**Goal:** Replace the placeholder red square with a real animated player sprite and have one fully playable cell. Ugly is fine; the rest of the world can wait.

### Player
- [ ] Real player sprite with idle / walk animations in 4 directions.
- [ ] Facing direction tracked in player state.
- [ ] Player class lives in `entities/` and exposes the same attributes `GameManager.player` already needs (so the renderer does not change).
- [ ] Move the float-position / hitbox-inset / axis-separated collision logic from `DebugPlayer` into the real player class verbatim — those are the parts that work.
- [ ] `DebugPlayer` and the `DebugSettings.SHOW_DEBUG_PLAYER` toggle stay in tree until the real sprite is committed, then get removed.

### Welcome message and torch
- [ ] Wire up the welcome message ("IT'S PITCH BLACK", etc.) so it actually displays in the message log on launch.
- [ ] Implement the torch: pressing `B` (controller) / `F` (keyboard) toggles a vision radius around the player, hiding tiles outside it.
- [ ] Vision radius and dimming color in `settings.py`.

### One real cell
- [ ] Replace the placeholder cell layout in `core/tilemaps.py` with a hand-designed first cell that demonstrates walls, openings, and at least one transition into a neighbor cell.
- [ ] Confirm the cell name renders in the bottom-left ("LEVEL" / "DUNGEON NAME" labels).

---

## Phase 2 — Dungeons and Layers

**Goal:** Two-layer world: overworld + at least one dungeon, with entrance tiles connecting them.

- [ ] Add a `current_layer` field to `World`.
- [ ] Build an entrance-tile table: stepping on an entrance swaps the active layer and repositions the player.
- [ ] One dungeon with at least three connected cells.
- [ ] Make the dungeon-name UI label react to the active layer.

## Phase 3 — Combat and Items

**Goal:** Make the world dangerous and rewarding.

- [ ] Health and damage model (settings-driven values in a new `CombatSettings`).
- [ ] At least one enemy type with a simple AI (chase player when in line of sight).
- [ ] Sword attack animation + collision frames.
- [ ] Pickups: key, monster repellent (already referenced in the welcome message), gold/score items.
- [ ] HUD: hearts in the sidebar, current score updating from pickups.

## Phase 4 — Audio

**Goal:** The game has voice.

- [ ] Wire `systems/audio.py` into `GameManager`.
- [ ] Background music per layer.
- [ ] SFX: footstep, sword swing, enemy hit, item pickup, door unlock.
- [ ] All audio loads optional — missing files must fail silently per the project rule.
- [ ] Mute indicator (`UISettings.MUTE_RIGHT_X` is already reserved) reflects audio state.

## Phase 5 — Persistence

**Goal:** Saves and a leaderboard.

- [ ] Implement save/load against the slot system already declared in `GameSettings.SAVES_DIR` / `MAX_SAVE_SLOTS` / `SAVE_VERSION`.
- [ ] Save format is JSON; `SAVE_VERSION` mismatch falls back to "incompatible save" rather than crashing.
- [ ] Leaderboard reads/writes `GameSettings.LEADERBOARD_FILE` with `LEADERBOARD_LIMIT` enforced.
- [ ] Player-name input screen with `MAX_PLAYER_NAME_LENGTH`.

## Phase 6 — Polish

**Goal:** Make it feel like a real arcade cabinet game.

- [ ] Title screen and attract mode.
- [ ] Smooth transitions between cells (not just a hard cut).
- [ ] Tune CRT overlay to look great on the cabinet's actual display.
- [ ] Confirm all UI text remains ALL CAPS (project rule).

---

## Code health

Issues spotted during the documentation pass that should be addressed before adding new features:

- [ ] `_handle_joybuttondown` has a commented-out hat/axis handler block — either implement them or remove the dead comments.
- [ ] `load_assets` is currently empty. Either populate it with the real preload list or remove it until it has a job.
- [ ] Confirm every class and function has a docstring with `Args:` / `Returns:` blocks where applicable.
- [ ] Double-check that no constants leaked into `core/`, `entities/`, or `ui/` files outside `settings.py`.

---

## Open Questions / Known Challenges

- **Cell-transition animation.** The current model swaps cells instantly. A slide animation (Zelda-style) is nicer but requires the renderer to draw two grids during the transition.
- **Overworld vs. dungeons in one save.** A save needs to encode active layer and per-cell state (defeated enemies, opened chests). Decide the schema before Phase 5.
- **Action window aspect ratio.** 14 × 10 cells is anchored by `UISettings`. Changing it later is invasive; lock it in before sprite art is commissioned.
- **Companion-piece interaction with Dungeon Digger.** Adventure and Dungeon Digger share a fantasy theme but are fully independent codebases. Decide whether they share any save/leaderboard data (probably no — keeps them truly standalone).

---

## Documentation maintenance

Every phase pass must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect any system that changed shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
