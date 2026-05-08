# Tetris — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/tetris
python main.py
```

## Smoke

1. Boot: window opens, no console errors.
2. CRT overlay is visible.
3. Music starts and loops.

## Gameplay

4. A tetromino spawns at the top of the playfield.
5. The piece falls on the gravity tick.
6. `Left` / `Right` (or D-pad / analog) translate the piece horizontally; the piece is clamped to the playfield walls.
7. `Down` (or D-pad down) soft-drops while held.
8. `Up` (or A) rotates the piece.
9. Reaching the floor or a settled block locks the piece; landing SFX plays.
10. After lock, the next piece in the preview becomes active and a new shape appears at the back of the preview list.
11. A complete row clears; score and level update; the rows above shift down.

## Globals

12. `F11` and Back (Select) toggle fullscreen.
13. `Esc` and `Start + Back + L1 + R1` exit cleanly.

## Sign-off

- [ ] Smoke + gameplay + globals all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
