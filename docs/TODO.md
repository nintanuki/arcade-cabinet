# Arcade Cabinet Launcher — Roadmap

This file tracks launcher work in **phases**. Each phase has a clear goal; finish a phase before moving on. Items inside a phase can move between phases as priorities shift. Per-game roadmaps live inside each game's own `docs/TODO.md`.

---

## Phase 1 — Code health (refactor pass)

**Goal:** Bring the launcher fully in line with the rules in [.github/copilot-instructions.md](../.github/copilot-instructions.md). No new features.

- [ ] Populate the empty [requirements.txt](../requirements.txt) with `pygame>=2.5` (and pin a Python version note).
- [ ] Audit `launcher/manager.py` for any function that does both navigation *and* rendering work — those should be split.
- [ ] Confirm every constant in `launcher/` is sourced from [settings.py](../settings.py); replace any stragglers.
- [ ] Confirm every class and function has a docstring with `Args:` / `Returns:` blocks where applicable.
- [ ] Re-check that `ArcadeLauncher` only *coordinates* — any logic that fits in `LauncherRenderer`, `LauncherCRT`, or a new helper should move there.

## Phase 2 — Settings screen

**Goal:** A first-class options screen accessible from the root menu.

- [ ] New menu node "Settings" at the root.
- [ ] Toggle CRT overlay on/off (persistent across launches).
- [ ] Master volume slider with audible preview.
- [ ] Default-fullscreen toggle.
- [ ] Persistence: settings written to a JSON file next to the launcher; loaded on startup; bad/missing file falls back to defaults silently.

## Phase 3 — Attract mode

**Goal:** When the cabinet has been idle on the menu for a configurable timeout, cycle through preview screenshots and short clips until input resumes.

- [ ] Idle detection (no input for `N` seconds).
- [ ] Cycle through games' preview images full-screen.
- [ ] Bail on any input.
- [ ] Tunable timing in `settings.py`.

## Phase 4 — Hot reload of student games

**Goal:** Teachers can drop a folder into `games/student/` and see the new game appear without restarting the launcher.

- [ ] Re-scan `games/student/` on a timer or when the root menu is re-entered.
- [ ] Diff against current set; add/remove `MenuNode`s without rebuilding unrelated state.
- [ ] Reload preview images for newly added games.

## Phase 5 — Polish

**Goal:** Make it feel like a real arcade cabinet front end.

- [ ] Smooth transitions between menus (fade or slide).
- [ ] Per-game launch sound clips (drop a `launch.wav` next to `main.py` and the launcher uses it).
- [ ] Tune CRT overlay to look great on the cabinet's actual display.
- [ ] Confirm all UI text remains ALL CAPS (project rule).

---

## Open Questions / Known Challenges

- **CRT overlay at fullscreen.** The overlay tiles poorly at arbitrary resolutions. Consider whether to skip it in fullscreen, or to scale the bezel art to the active display size.
- **Audio device contention.** Each game initializes its own audio. On cabinet hardware that has a single output, a game that crashes mid-init can leave the device in a bad state. Investigate a graceful re-init in `_restore_runtime`.
- **Quit-combo standardization.** Each game implements its own `Start + Select + L1 + R1` combo today; consider a shared helper module that games can import (without breaking the agnostic-game rule — would be opt-in).
- **Multi-controller routing.** Currently the launcher reads any connected controller. For multi-player games, a future per-game manifest field could declare expected controller count.

---

## Game ideas

- [ ] Tetris Attack / Panel de Pon (in progress as **Puzzle League**).
- [ ] Pazaak (in progress).
- [ ] Fishy.
- [ ] Rodent's Revenge.

---

## Documentation maintenance

Every phase pass must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect any system that changed shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
