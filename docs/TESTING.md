# Arcade Cabinet Launcher — Manual Testing Checklist

This is the run-through to perform after a non-trivial change to the launcher. The mental checklist in [.github/copilot-instructions.md](../.github/copilot-instructions.md) covers what to *think* about during a change; this file covers what to *do* before considering a change shippable.

> Per-game testing checklists live in each game's own `docs/TESTING.md`.

---

## Smoke test (every change)

Run from the repo root.

```powershell
python main.py
```

1. **Boot.** The launcher window opens at 1280 × 720 with the title "Coding Club Arcade". No console errors.
2. **Header.** The JIL logo and title sit centered as one unit; the subtitle is below them.
3. **Root menu.** Two entries are visible: **Student Games** and **Mr. Navarro's Games**.
4. **Move SFX.** Pressing `Down` (or D-pad down) moves the cursor and plays a short click. Holding the direction does not spam clicks faster than the move rate.
5. **Carousel vs list.** Mr. Navarro's Games → Original Games shows a **carousel** (more than 5 items). Mr. Navarro's Games shows a **static list** (3 items). Visually confirm both renderers are working.
6. **Submenu push/pop.** Enter a submenu with `Enter` / `A` / `Start`. Back out with `Esc` / `B`. Selection state persists when re-entering the same submenu.
7. **Quit at root.** Pressing `Esc` at the root closes the launcher.
8. **Fullscreen toggle.** `F11` (keyboard) or `Select` (controller) toggles fullscreen. The CRT overlay still draws in both modes.
9. **Mouse navigation.** Hovering an option highlights it; clicking enters/launches.

---

## Game-launch test

For at least **one game per category** (original / tribute / tutorial), and any newly added game:

1. Highlight the game; the right-side preview shows its screenshot (or "PREVIEW NOT AVAILABLE" with a clear visual fallback).
2. Confirm the caption above the preview matches `GameSettings.GAME_DESCRIPTIONS[label]`.
3. If the game has an `input_scheme` set, the red warning line is visible.
4. If the game is in `UNDER_CONSTRUCTION_GAMES`, the "UNDER CONSTRUCTION" stamp is rendered over the preview.
5. Confirm. The "LOADING..." screen plays for ~2.2 seconds with animated dots.
6. The game launches in its own window; the launcher window is gone.
7. Closing the game window (or pressing the in-game quit combo) returns control to the launcher with the same menu state and selection.
8. Repeat once more with a different game to confirm `_restore_runtime` is stable across launches.

---

## Student-game test (when student-discovery code is touched)

1. With `games/student/` empty, **Student Games** is shown but its submenu has no items. Confirm SFX still plays on enter.
2. Add a folder containing only `main.py` (no manifest). Restart the launcher. The folder appears under Student Games with a title-cased name and `CREATED BY UNKNOWN STUDENT` attribution.
3. Add `game.json` next to `main.py` with all six fields (`label`, `attribution`, `preview`, `input_scheme`, `note`, `under_construction`). Restart. Each field shows up correctly in the UI.
4. Break the JSON (intentionally). Restart. The launcher still boots, the broken game falls back to defaults, no console crash.
5. Set `input_scheme` to something not in `InputSchemeSettings.LABELS`. Restart. The warning line is silently absent.

---

## Failure-mode tests (when error-handling code is touched)

- Rename a sponsor game's folder. Try to launch it. The status message shows `Cannot launch <name>: folder not found.` and the launcher does not tear down.
- Rename `assets/font/Pixeled.ttf`. The launcher should crash explicitly at startup (font is required; we don't fake it).
- Rename `assets/graphics/jil_logo.webp`. The launcher should boot anyway, with a red placeholder rectangle in the logo position.
- Rename `assets/graphics/tv.png`. The launcher should boot anyway, with no CRT overlay.
- Rename `assets/sound/sfx_menu_move2.wav`. The launcher should boot anyway, silent on cursor moves.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- Visually confirm the changed section reflects the new values (e.g. preview box position, font size).
- Confirm no other section regressed.
- Confirm no constants leaked back into `launcher/*.py` files (`grep` for the literal value if uncertain).

---

## Sign-off

- [ ] Smoke test passed.
- [ ] At least one game per category launched and exited cleanly.
- [ ] Student-game discovery still works (if touched).
- [ ] Failure-mode behavior still graceful (if touched).
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
