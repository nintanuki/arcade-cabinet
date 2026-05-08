# Flappy Bird — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/flappy-bird
python main.py
```

## Smoke

1. Boot: window opens, no console errors.
2. Menu image renders centered.
3. Music starts and loops.
4. CRT overlay is visible.

## Gameplay

5. `Space` (or A) starts a run; the plane appears and falls under gravity.
6. Tapping `Space` (or A) flaps the plane upward.
7. Pipe pairs spawn every ~1.4 s and scroll left.
8. Passing a pipe increments the score (visible top-center).
9. Plane / pipe collision ends the run and returns to the menu.
10. Plane / ground collision ends the run and returns to the menu.

## Pause

11. `P` (or Start) toggles pause; pause-in SFX plays on entry, pause-out on exit.
12. Game state freezes while paused.

## Quit paths

13. `Esc` exits cleanly.
14. `Start + Back + L1 + R1` on any controller exits cleanly.
15. OS window-close exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + pause + quit paths all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
