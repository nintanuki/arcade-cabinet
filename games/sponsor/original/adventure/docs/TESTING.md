# Adventure — Manual Testing Checklist

This is the run-through to perform after a non-trivial change. The mental checklist in [.github/copilot-instructions.md](../.github/copilot-instructions.md) covers what to *think* about during a change; this file covers what to *do* before considering a change shippable.

---

## Smoke test (every change)

Run from this game's folder:

```powershell
cd games/sponsor/original/adventure
python main.py
```

Or launch through the cabinet's launcher: `python main.py` from the repo root → **Mr. Navarro's Games → Original Games → Adventure**. Both entry paths must work.

1. **Boot.** The window opens at 800 × 600 with the title "Adventure". No console errors.
2. **Layout.** The action window, sidebar, message log area, and minimap area all render in their expected positions.
3. **Placeholder player.** A red square renders inside the action window, roughly centered.
4. **F1 toggle.** Pressing `F1` shows/hides the debug UI frame outlines around all four regions.
5. **F2 toggle.** Pressing `F2` shows/hides the placeholder player.
6. **CRT overlay.** Visible scanlines and a faint flicker over the whole screen. The effect persists in fullscreen.

---

## Movement and collision

7. **Keyboard movement.** WASD and arrow keys move the player smoothly. Diagonals are not faster than orthogonal.
8. **Controller movement.** Left analog stick moves the player. Inside the deadzone, the player does not drift.
9. **Wall collision.** The player cannot pass through wall tiles in the active cell. Sliding along a wall (pressing into it diagonally) still allows movement along the unblocked axis.
10. **Hitbox vs. visual size.** The player can slip through a 1-tile-wide opening even when not perfectly aligned.
11. **Cell transition (defined neighbor).** Walking past the action-window edge into a defined neighbor cell swaps the active cell and repositions the player at the opposite edge.
12. **Cell transition (undefined neighbor).** Walking past the action-window edge into an undefined direction clamps the player back inside the action window without crashing.

---

## Global controls

13. **`Esc`.** Quits the game cleanly and returns to the launcher (or terminates if launched standalone).
14. **`F11` / `Back`.** Toggles fullscreen. The CRT overlay still renders in both modes.
15. **Quit combo.** Holding `Start + Back + L1 + R1` on a controller exits the game cleanly.
16. **Window-close button.** Closing the window via the OS chrome quits cleanly.

---

## Failure-mode tests (when error-handling code is touched)

- Rename `assets/font/Pixeled.ttf`. Boot. The game should fail explicitly (font is required); confirm the error message is clear.
- Rename a CRT-overlay asset (if one exists in `assets/`). The game should still boot with no overlay rather than crashing.
- Disconnect any controllers and boot. Keyboard play must still work.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- Visually confirm the changed section reflects the new values (e.g. tile scale, action-window position, font size).
- Confirm no other section regressed.
- Confirm no constants leaked back into `core/`, `entities/`, `ui/`, or `systems/` files (`grep` for the literal value if uncertain).

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Movement and collision tests passed.
- [ ] Global controls tests passed.
- [ ] Failure-mode behavior still graceful (if touched).
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
