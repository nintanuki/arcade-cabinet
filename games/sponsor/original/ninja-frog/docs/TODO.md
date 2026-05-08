# Ninja Frog — Roadmap & TODO

The build is a **prototype**. Items are grouped by phase so contributors know where to push next.

---

## Phase 1 — Core platforming feel

- [ ] Fix **player phasing through and flying up walls**. Likely caused by the horizontal/vertical resolution order; investigate `CollisionManager.resolve_horizontal` and the matching vertical resolver in `Player`.
- [ ] Fix **player "bounce"** at corners (also collision-resolution related).
- [ ] Fix **player starts the game by falling onto the world**. Snap to floor on spawn instead of relying on gravity.
- [ ] Replace the debug `print(f"Loaded {len(frames)} frames ...")` block in `Player.__init__` with a proper logging call (or remove it).

## Phase 2 — Enemy and player damage

- [ ] Player death on horizontal collision with enemy (currently only stomp does anything to the snail).
- [ ] Death animation / game-over screen.
- [ ] Respawn at the level start.

## Phase 3 — Level content

- [ ] Build out a full level with platforms, gaps, hazards, and a goal.
- [ ] Add an exit door / level-complete trigger.
- [ ] Support multiple maps (introduce a `LevelManager` so `GameManager` doesn't import `MAP_01` directly).
- [ ] Background art layer.

## Phase 4 — Audio

- [ ] Add an `AudioManager`.
- [ ] Sound effects: jump, land, run footsteps, stomp, death.
- [ ] Music track per level with mute toggle (`M` and `R2`).

## Phase 5 — Polish

- [ ] Decide on CRT overlay: re-enable with a softer alpha range, or remove the disabled call from `run`.
- [ ] Promote sprite drawing out of `GameManager.run` into `RenderManager` or a sprite group.
- [ ] Tune `JUMP_STRENGTH`, `GRAVITY`, and `RUN_SPEED` after Phase 1 collision fixes.

---

## Code health

- [ ] `CollisionManager` is currently defined inside `main.py`; move it to its own module (e.g. `collision.py`) once Phase 1 lands.
- [ ] `GameManager.__init__` does its own pygame setup instead of going through a small bootstrap helper. Acceptable while the codebase is this small.
- [ ] `Player.__init__` prints animation frame counts to stdout. Remove or guard with a `DebugSettings.VERBOSE` flag.
- [ ] No `docs/CHANGELOG.md` entries yet — start the history with the next code change.

---

## Open questions

- Should the camera ever scroll horizontally, or remain locked to vertical-only? Current screen size assumes vertical-only.
- Is the snail the canonical enemy, or just a placeholder? Affects how generic the enemy code should be.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
