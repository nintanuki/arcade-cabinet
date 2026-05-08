# Puzzle League — Manual Testing Checklist

Run this after a non-trivial change. The mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*.

> **Note:** Puzzle League is a scaffold today. The smoke test below covers what exists. Expand sections here as gameplay is built (see [docs/TODO.md](TODO.md)).

---

## Smoke test (every change)

```powershell
cd games/sponsor/tribute/puzzle-league
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Puzzle League**. Both entry paths must work.

1. **Boot.** Window opens at `600 × 800`, titled "Puzzle League". A `LOADING...` card appears briefly during init. No console errors.
2. **Title screen.** "PUZZLE LEAGUE" title and subtitle prompt render. CRT overlay is visible (scanlines + flicker).
3. **Start input.** Pressing `Enter` (keyboard) or A / Start (controller) calls `SessionStateManager.reset_for_new_game()`; the screen transitions to the active gameplay branch (a centered playfield rectangle today).

## Active state

4. The playfield rectangle renders centered horizontally with a top margin (`BoardSettings.BOARD_X`, `BOARD_Y`).
5. The CRT overlay still applies on top of gameplay rendering.

## Global controls

6. `F11` and Back (Select) toggle fullscreen.
7. `Esc` exits cleanly.
8. Holding `Start + Back + L1 + R1` on a controller exits cleanly.
9. `close_game` calls `ScoreManager.save_scores` on every exit path (verify by running once and checking that the call does not raise — persistence will be added in Phase 7).
10. **Hot-plug.** Plugging or unplugging a controller while running does not crash; `pygame.JOYDEVICEADDED` / `JOYDEVICEREMOVED` are absorbed by `handle_joystick_hotplug`.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- For `BoardSettings` changes, confirm the playfield rectangle reflects the new dimensions.
- For `ColorSettings` changes, confirm the screen background and text colors update.
- For `RiseSettings` / `BlockSettings` / `ScoreSettings` changes, confirm the matching gameplay system reflects the new value once that phase is implemented.
- `grep` for the literal value to confirm no constants leaked into `core/`, `systems/`, or `ui/` files.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Loading card → title screen → active state transitions worked.
- [ ] Global controls passed.
- [ ] No console errors at boot or on exit.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
