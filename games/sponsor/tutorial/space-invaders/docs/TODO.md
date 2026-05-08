# Space Invaders — Roadmap & TODO

The build is a fully-playable Space Invaders. Items below preserve the open work tracked in the original root `TODO.md`.

---

## Phase 1 — Bugs

- [ ] The window just closes when you die — there should be a game-over screen with restart / quit prompt instead.

## Phase 2 — Polish

- [ ] Add an initials high-score system (mirrors jezz-ball).
- [ ] Animate the alien sprites (alternate frames as the wave marches).
- [ ] Add pause functionality (`P` / Start) with an overlay.
- [ ] Add a fullscreen toggle (`F11` / Back).
- [ ] Add a reset key combo to return cleanly to the launcher.

---

## Code health

- [ ] Extract a `settings.py` for window size, alien grid layout, alien speed, laser cooldown, scoring values, and asset paths. (No central settings file exists today.)
- [ ] `from settings import *` should be replaced with explicit imports once `settings.py` is added.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
