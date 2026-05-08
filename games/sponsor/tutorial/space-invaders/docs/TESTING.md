# Space Invaders — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/space-invaders
python main.py
```

## Smoke

1. Boot: window opens, no console errors.
2. Player ship, alien grid, and obstacles render.

## Gameplay

3. `Left` / `Right` (or D-pad / analog) move the ship horizontally; the ship is clamped to the screen.
4. `Space` (or A) fires a player laser; the laser travels up.
5. Player laser destroys an alien on contact; score increments.
6. Aliens march side-to-side, drop one row at the edge, and reverse.
7. Aliens occasionally fire lasers downward.
8. Alien lasers chip the obstacle bunkers (bricks disappear on hit).
9. `Extra` UFO occasionally streaks across the top for bonus points.
10. Player getting hit by an alien laser decrements lives.

## Quit paths

11. `Esc` exits cleanly.
12. `Start + Back + L1 + R1` on any controller exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + quit paths all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
