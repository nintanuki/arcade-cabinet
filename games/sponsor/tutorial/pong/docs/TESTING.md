# Pong — Manual Testing Checklist

Run after a non-trivial change.

```powershell
cd games/sponsor/tutorial/pong
python main.py
```

## Smoke

1. Boot: window opens, no console errors.
2. CRT overlay is visible.
3. Music starts and loops.

## Gameplay

4. `Up` / `Down` arrows move the player paddle.
5. Controller D-pad moves the player paddle.
6. Left analog stick moves the player paddle (when D-pad is centered).
7. Ball spawns moving toward one side, bounces off walls and paddles.
8. AI opponent paddle tracks the ball vertically.
9. Score increments when the ball passes a paddle into a goal.
10. Score renders top-center (or wherever `settings.py` configures).

## Globals

11. `F11` toggles fullscreen.
12. Back (Select) on a controller toggles fullscreen.
13. `Esc` exits cleanly.
14. `Start + Back + L1 + R1` on any controller exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + globals all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
