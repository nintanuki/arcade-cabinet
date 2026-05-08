# Flappy Bird — Roadmap & TODO

The build is a fully-playable Flappy Bird tribute. Items below are ordered roughly by player-visible value.

---

## Phase 1 — Bugs

- [ ] Delay on full-screen toggle, quit combo, and pause? Sometimes the quit combo doesn't register and pause fires instead. Investigate whether `Start` / `Select` button events are racing each other.
- [ ] In fullscreen the playfield becomes "wide screen": objects pop in at the right and the CRT filter only covers the left half. Probably a scale-factor / blit-rect issue when the window flips to native resolution.

## Phase 2 — Polish

- [ ] Persist a high score to `high_score.txt` (JSON), following the jezz-ball pattern.
- [ ] Initials entry on a qualifying run; mini leaderboard on the menu.
- [ ] On-screen "controller connected" indicator.

## Phase 3 — Content

- [ ] Difficulty ramp: gap shrinks or scroll speed increases with score.
- [ ] Day / night background variants tied to score milestones.
- [ ] Multiple plane skins.

---

## Code health

- [ ] `from settings import *` in `main.py` — replace with explicit imports during the next major touch.
- [ ] Asset paths are inline string literals inside `Game.__init__`. Consolidate into an `AssetSettings` class once we add another graphics variant.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
