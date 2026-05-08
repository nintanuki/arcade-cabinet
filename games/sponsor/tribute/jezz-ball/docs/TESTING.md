# Jezz Ball — Manual Testing Checklist

Run this after a non-trivial change. The mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*.

---

## Smoke test (every change)

```powershell
cd games/sponsor/tribute/jezz-ball
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Jezz Ball**. Both entry paths must work.

1. **Boot.** Window opens at `800 × 600`. Title screen renders with the bouncing demo ball and the `MOUSE / CONTROLLER` selector. No console errors.
2. **CRT overlay** is visible (scanlines + flicker).

## Title screen

3. Cycle the input mode selector with arrows / D-pad; the highlight follows.
4. Selecting `MOUSE` and pressing confirm starts level 1 with the cursor following the OS mouse.
5. Selecting `CONTROLLER` and pressing confirm starts level 1 with the cursor driven by the D-pad. (Analog support is a known gap — see [docs/TODO.md](TODO.md).)

## In-game (level 1)

6. Cursor is visible inside the playfield rect (not the full screen).
7. Pressing the orientation button (`R` / X) flips the build axis between horizontal and vertical.
8. Pressing the build button (`Space` / left-click / A) starts a wall; both grow segments are visible in the negative/positive colors.
9. A ball touching a still-growing wall destroys the wall, plays the `ball_hit_cursor` SFX (when SFX volume > 0), and decrements lives by 1.
10. When both grow segments anchor (edge or another wall), the wall converts to solid black cells.
11. Any region of the playfield that contains **no** ball after a wall completion is claimed (locked-in fill).
12. The HUD updates score, lives, level, and (level 3+) the time remaining.
13. Reaching the level's `area_needed_percent` plays the level-clear SFX, awards the time bonus and clear bonus, and advances to the next stage.

## Pause

14. `P` / Start pauses the game: balls and the build wall halt; pause SFX plays.
15. Pressing pause again resumes from the same state.

## Game over

16. Run lives to zero (or fail the timer). Game transitions to `GAME_OVER` and displays the final score.
17. If the score qualifies, the `INITIALS` state appears: cycle three letters with directional input and confirm to submit.
18. After initials are submitted, the leaderboard renders the top entries with the new entry inserted in rank order.
19. Pressing the dismiss button returns to `TITLE` and high-score persistence is preserved (verify by reopening `high_score.txt`).

## Persistence

20. After a leaderboard entry is added, close and relaunch the game. The leaderboard and high score must still be present.
21. Manually corrupt `high_score.txt` (e.g. write `not json`). Relaunch — the game must start with a fresh leaderboard, not crash.

## Global controls

22. `F11` and Back (Select) toggle fullscreen.
23. `Esc` exits cleanly.
24. Holding `Start + Back + L1 + R1` on a controller exits cleanly.

## Settings-change tests

When [settings.py](../settings.py) is edited:

- For `LEVELS` changes, run a full level cycle and confirm the new values (claim percentage, ball count, time limit) take effect.
- For `GameplaySettings` changes, visually confirm the changed value (build speed, ball speed, scoring) reflects in-game.
- `grep` for the literal value to confirm no constants leaked into other files.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Wall build / destroy / capture passed.
- [ ] Score and HUD update correctly.
- [ ] Game-over → initials → leaderboard flow passed.
- [ ] Persistence verified.
- [ ] Global controls passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
