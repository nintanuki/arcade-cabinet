# Breakout — Roadmap & TODO

The build is a single-stage, fully-playable Breakout clone. Items below are ordered by player-visible value.

---

## Phase 1 — Polish

- [ ] Score display (top of screen) showing current score, with simple per-brick value.
- [ ] Game-over screen when hearts reach zero, with a "press start" prompt to retry.
- [ ] Win screen when all bricks are cleared.

## Phase 2 — Persistence

- [ ] Persist a high score to `high_score.txt` (JSON) following the jezz-ball pattern.
- [ ] Initials entry on a qualifying score; mini leaderboard on the title screen.

## Phase 3 — Content

- [ ] Multiple stage layouts (rotate or progress through them).
- [ ] Increasing ball speed per stage.
- [ ] More upgrade types (multi-ball, sticky paddle, slow-motion).

## Phase 4 — UX

- [ ] `F11` / Back fullscreen toggle.
- [ ] Pause (`P` / Start) overlay.
- [ ] On-screen "controller connected" indicator.

---

## Code health

- [ ] `from settings import *` is used in `main.py` and `sprites.py`. Replace with explicit imports during the next major touch.
- [ ] Audio is loaded inline inside `Game.__init__` — refactor into a small `AudioManager` once SFX list grows beyond five files.

---

## Open questions

- Should ball speed scale linearly with bricks remaining (classic Breakout) or stay constant per stage?
- Should the paddle shrink-on-death (or grow-with-score) — neither is currently implemented.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
