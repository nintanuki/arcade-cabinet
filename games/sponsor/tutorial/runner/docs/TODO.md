# Runner — Roadmap & TODO

The build is a fully-playable side-scrolling runner. Items below are ordered roughly by player-visible value.

---

## Phase 1 — Polish

- [ ] Title screen with a proper "press start" prompt instead of cold-booting into gameplay.
- [ ] Game-over UI: show final score and high score side-by-side.
- [ ] Pause (`P` / Start) overlay.

## Phase 2 — Persistence

- [ ] Persist a high score to `high_score.txt` (JSON) following the jezz-ball pattern.
- [ ] Initials entry on a qualifying run.

## Phase 3 — Difficulty

- [ ] Increase scroll speed with score.
- [ ] Add additional obstacle types.
- [ ] Spawn-rate ramp tied to score milestones.

## Phase 4 — Refactor

- [ ] Split `Player` and `Obstacle` out of `main.py` into `sprites.py`.
- [ ] Introduce a `GameManager` once the game has multiple states (title / play / pause / game-over).
- [ ] Replace `print` statements (e.g. "Controller connected") with optional debug logging gated by a flag in [settings.py](../settings.py).

---

## Code health

- [ ] `Player.player_input` polls the joystick list directly each frame; cache the active joysticks once like `pong/main.py` does.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
