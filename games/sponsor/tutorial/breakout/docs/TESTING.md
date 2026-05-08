# Breakout — Manual Testing Checklist

Run after a non-trivial change. Mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md).

```powershell
cd games/sponsor/tutorial/breakout
python main.py
```

Or via the cabinet launcher.

## Smoke

1. Boot: window opens, no console errors.
2. CRT overlay is visible.
3. Music loops.

## Gameplay

4. Paddle moves with `Left` / `Right` keys and with controller D-pad / analog.
5. `Space` (or A) launches the ball.
6. Ball bounces off walls and the paddle.
7. Ball destroys bricks on contact.
8. Power-ups occasionally drop from destroyed bricks; touching them with the paddle applies the effect (visible: paddle width change, projectile capability, etc.).
9. With the laser upgrade active, `Space` (or A) fires a projectile that destroys bricks.
10. Ball falling off the bottom decrements hearts.
11. With zero hearts, the game ends (currently closes — see [docs/TODO.md](TODO.md)).

## Quit paths

12. `Esc` exits cleanly.
13. `Start + Back + L1 + R1` on any controller exits cleanly.
14. OS window-close exits cleanly.

## Sign-off

- [ ] Smoke + gameplay + quit paths all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
