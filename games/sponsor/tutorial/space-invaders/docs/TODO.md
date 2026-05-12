# Space Invaders — Roadmap & TODO

The build is a fully-playable Space Invaders. Items below preserve the open work tracked in the original root `TODO.md`.

---

## Phase 1 — Bugs

- [ ] The window just closes when you die — there should be a game-over screen with restart / quit prompt instead.

## Phase 2 — Polish

- [ ] Add an initials high-score system (mirrors jezz-ball).
- [ ] Animate the alien sprites (alternate frames as the wave marches).
- [x] Add pause functionality (`Enter` / Start) with an overlay.
- [x] Add a fullscreen toggle (`F11` / Back).
- [x] Add a reset key combo to return cleanly to the launcher (`Esc` / `Start + Back + L1 + R1`).

---

## Code health

- [x] Extract a `settings.py` for window size, alien grid layout, alien speed, laser cooldown, scoring values, and asset paths.
- [x] Use explicit imports from `settings` (no `from settings import *`).
- [x] Move sprite classes under `core/`, the CRT overlay under `ui/`, and bundled media under `assets/` to mirror the star-hero reference layout.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
