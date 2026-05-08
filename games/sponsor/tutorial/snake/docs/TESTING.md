# Snake — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/snake
python snake.py
```

## Smoke

1. Boot: window opens, no console errors.

## Gameplay

2. Snake moves left-to-right (or whatever the initial heading is) on the grid tick.
3. Arrow keys steer the snake.
4. Controller D-pad steers the snake.
5. Left analog stick steers the snake when the D-pad is centered (and the stick is past the deadzone).
6. Pressing the opposite of the current heading is ignored (no instant self-collision).
7. Apple spawns on a free cell.
8. Eating an apple grows the snake by one segment and respawns the apple.
9. Hitting a wall ends the game.
10. Hitting yourself ends the game.

## Quit paths

11. `Esc` exits cleanly.
12. `Start + Back + L1 + R1` on any controller exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + quit paths all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
