# Runner — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/runner
python main.py
```

## Smoke

1. Boot: window opens, no console errors.
2. CRT overlay is visible.

## Gameplay

3. Player walk-cycle animates while running.
4. `Space` (or A) jumps; gravity returns the player to the ground.
5. `Left` / `Right` (or D-pad / analog) move the player horizontally.
6. Snails spawn on the ground line and scroll left.
7. Flies spawn higher up and scroll left.
8. Collision with any obstacle ends the run.
9. Game-over screen renders; pressing `Space` (or A) restarts.
10. Score increments while the run is active.

## Quit paths

11. `Esc` exits cleanly.
12. `Start + Back + L1 + R1` on any controller exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + quit paths all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
