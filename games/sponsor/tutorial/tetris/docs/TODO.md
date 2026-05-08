# Tetris — Roadmap & TODO

The build is a fully-playable Tetris. Items below are ordered by player-visible value.

---

## Phase 1 — Polish

- [ ] Game-over screen with final score and a "press start" prompt.
- [ ] Pause (`P` / Start) overlay.
- [ ] Hold piece (classic modern-Tetris feature).
- [ ] Hard-drop (`Space` slams the piece to the floor and locks instantly).
- [ ] Ghost piece preview at the floor.

## Phase 2 — Persistence

- [ ] Persist a high score to `high_score.txt` (JSON), following the jezz-ball pattern.
- [ ] Initials entry on a qualifying run.

## Phase 3 — Audio

- [ ] Mute toggle.
- [ ] Per-line-clear SFX (single / double / triple / tetris).
- [ ] Level-up jingle.

## Phase 4 — Refinement

- [ ] SRS-style wall kicks for rotation against the playfield walls.
- [ ] T-spin detection + bonus scoring.

---

## Code health

- [ ] `from settings import *` in `main.py` — replace with explicit imports during the next major touch.
- [ ] Consider extracting a `Sprites` / palette helper rather than repeating color lookups inline in `game.py`.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
