# Pong — Roadmap & TODO

The build is a fully-playable Pong tribute. Items below preserve the open and closed work tracked in the original root `TODO.md`.

---

## Phase 1 — Bugs / known issues

- [ ] VS Code complains about inconsistent tabs and spaces, but pressing tab inserts spaces. Sweep the source for hidden tabs.

## Phase 2 — Frame-rate independence

- [ ] Stop relying on `clock.tick(FRAMERATE)` for movement; multiply velocities by delta time so behavior is consistent at any framerate (re-watch ClearCode's video).

## Phase 3 — Audio polish

- [ ] Add a mute option for music.
- [ ] Loop music seamlessly after the intro section.
- [ ] Add a volume bar / volume control.

## Phase 4 — UX

- [ ] Pause function (`P` / Start).
- [ ] Toggle to disable the CRT effect.
- [ ] Game-over menu after a score limit.
- [ ] Intro menu (loop the first part of the music, then seamlessly enter the rest).
- [ ] Make the controller list survive hot-plug (re-init joysticks while a game is running).

## Phase 5 — Persistence

- [ ] Add high score to a `.txt` file (JSON-shaped, mirroring jezz-ball).

## Phase 6 — Content / feel

- [ ] Speed scaling: increase opponent and ball speed with every score.
- [ ] Power-ups (optional).
- [ ] Color customization for paddles.
- [ ] Move score location to the top of the screen (matches classic Pong layouts).
- [ ] Make the centerline dotted.

---

## Done

- [x] CRT effect.
- [x] `settings.py` extracted.
- [x] Maximize-window option.
- [x] Sprite classes split into `sprites.py`.
- [x] `GameManager` extracted into `game.py`.
- [x] LMMS-based beat + melody music; credit LMMS tutorial for the initial beat.
- [x] Controller D-pad input.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
