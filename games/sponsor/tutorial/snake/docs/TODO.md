# Snake — Roadmap & TODO

The build is a single-file, fully-playable Snake. Items below preserve the open work tracked in the original root `TODO.md`.

---

## Phase 1 — Polish (UX)

- [ ] `F11` or Back (Select) toggles fullscreen.
- [ ] Decide if the CRT effect looks good here, then either add or skip it. (No `crt.py` is currently imported.)
- [ ] Reset / quit button combo to return to launcher (`Start + Back + L1 + R1` already exits, but verify it never collides with gameplay).
- [ ] Add a pause option (`P` / Start).
- [ ] Color scheme pass: green snake on a black or monochrome background reads better with the cabinet CRT.
- [ ] More sound effects + animation feedback on apple eat, death, etc.

## Phase 2 — Audio

- [ ] Add background music (working title: "Red Sands").
- [ ] Add a mute toggle.

## Phase 3 — Persistence

- [ ] High-score persistence with initials entry, mirroring the jezz-ball pattern.

## Phase 4 — Refactor

- [ ] Extract a `settings.py` from the constants currently inside `snake.py` (cell size, grid size, FPS, colors, asset paths).
- [ ] Reorganize into a `GameManager` style with classes and constants split across files (`sprites.py`, `audio.py`, etc.) once the project grows past a few hundred lines.

---

## Code health

- [ ] Empty `controller_direction` polls every frame even with no joystick connected — early-return when `joysticks` is empty.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
