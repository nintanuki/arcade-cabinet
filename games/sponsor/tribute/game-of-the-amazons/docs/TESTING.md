# Game of the Amazons — Manual Testing Checklist

Run this after a non-trivial change. The mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*. The strict refactoring rules that used to live here have been consolidated into copilot-instructions.

---

## Smoke test (every change)

```powershell
cd games/sponsor/tribute/game-of-the-amazons
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Game of the Amazons**. Both entry paths must work.

1. **Boot.** Window opens at the configured resolution, titled "Game of the Amazons". No console errors.
2. **Title screen.** "GAME OF THE AMAZONS" is centered with ONE PLAYER / TWO PLAYERS options beneath it.
3. **Title input.** Arrow keys / D-pad change selection; `Space` / `Enter` / A / Start confirm.
4. **Initial board.** After selecting a mode, four WHITE queens and four BLACK queens are placed at their canonical opening positions.
5. **HUD.** Side panel shows current player ("WHITE"), current phase ("MOVE"), and mode label.
6. **CRT overlay** is visible (scanlines + flicker).

## Cursor

5. **Keyboard.** Arrow keys move the cursor highlight one tile per press. The cursor clamps to `[0, 9]` on both axes.
6. **Controller.** D-pad and (where supported) the analog hat move the cursor identically.

## Move phase (human turn)

7. **Select queen.** Position the cursor over a WHITE queen and press `Space` / A. The queen highlights as selected.
8. **Invalid select.** Pressing confirm on an empty tile or a BLACK queen does nothing.
9. **Valid move.** Move the cursor to a tile reachable in a queen-direction with no obstacles. Pressing confirm starts the slide animation; the queen detaches from its origin tile during the animation.
10. **Invalid move.** Choosing a tile blocked by a piece or an arrow, or off the queen-path, deselects the queen and does not advance the turn.
11. **Animation.** The queen arrives at the destination tile and the phase transitions to SHOOT.

## Shoot phase (human turn)

12. The cursor is parked on the moved queen for an obvious anchor.
13. **Valid arrow.** Move the cursor to a tile reachable in any queen-direction; pressing confirm fires the arrow and plays the shoot SFX.
14. **Invalid arrow.** A blocked or off-path target does nothing.
15. **Animation.** The arrow flies, lands, and the tile becomes permanently marked as blocked. The turn switches to BLACK.

## One-player mode AI turn

18. The AI's queen slides to its chosen tile and its arrow flies automatically — no further input required.
19. The phase returns to WHITE / MOVE after the arrow lands.

## Two-player mode

20. BLACK is controllable with the same keyboard/controller inputs used by WHITE.
21. No AI move/arrow animation triggers automatically when BLACK's turn begins.

## Win detection

22. Manually create a position (with cooperative play) where one player has no legal queen-move at the start of their turn. The HUD shows `GAME OVER` and announces the other player as the winner.
23. **Restart.** Pressing `Enter` (keyboard) or Start (controller) creates a fresh `GameManager` instance and the board resets to the starting position while keeping the selected mode.

## Global controls

24. `F11` and Back (Select) toggle fullscreen.
25. `Esc` quits cleanly.
26. Holding `Start + Back + L1 + R1` on a controller exits cleanly.
27. Closing the OS window quits cleanly.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- Visually confirm the changed section reflects the new values (tile size, board offset, HUD layout, animation speeds, colors, font sizes).
- Confirm no other section regressed.
- `grep` for the literal value to confirm no constants leaked back into `core/`, `systems/`, or `ui/` files.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Cursor responds to keyboard and controller.
- [ ] WHITE move + shoot phase passed end-to-end.
- [ ] One-player AI turn animates and resolves correctly.
- [ ] Two-player BLACK control works and AI is disabled.
- [ ] Win detection and restart passed.
- [ ] Global controls passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.