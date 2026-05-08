# Air Hockey — Manual Testing Checklist

Run this after a non-trivial change. Mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*.

---

## Smoke test (every change)

```powershell
cd games/sponsor/original/air-hockey
python main.py
```

Or launch via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Original Games → Air Hockey**. Both entry paths must work.

1. **Boot.** Window opens portrait-aspect (400 × 800), titled "Air Hockey". No console errors.
2. **Title screen.** "AIR HOCKEY" displays with a `> MOUSE` / `  CONTROLLER` selector. The "NO CONTROLLER DETECTED" warning shows in red iff no controllers are plugged in.
3. **Selector cycles.** Arrow keys / WASD / D-pad / left stick all move the `>` indicator between MOUSE and CONTROLLER.
4. **CRT overlay.** Visible scanlines and a faint flicker (windowed mode only).

## Mouse mode

5. Pick **MOUSE**, press `Enter`. The match starts.
6. Paddle (red ellipse, bottom half) follows the cursor smoothly.
7. Hold left mouse button — paddle spikes upward.
8. Score a goal in either net — countdown freezes the play, then the puck respawns on the opposite side.
9. `Enter` pauses; the screen shows "PAUSED". `Enter` again resumes.
10. `M` mutes audio (no SFX/music plays); `M` again restores audio.
11. `F11` toggles fullscreen. CRT overlay disappears in fullscreen and reappears in windowed mode.
12. `Esc` quits cleanly.

## Controller mode

13. Re-launch. Pick **CONTROLLER**, press `Start` (button 7). Match starts.
14. Left analog stick moves the paddle smoothly; small stick deflections in the deadzone do not move it.
15. Holding `A` (button 0) spikes the paddle upward.
16. `Start` pauses and resumes.
17. `Back` (button 6) toggles fullscreen.
18. Holding `Start + Back + L1 + R1` exits cleanly.

## Edge cases

19. Hot-plug a controller mid-match. The new controller's stick should drive the paddle within a few seconds (the game registers `JOYDEVICEADDED`).
20. Try to walk the puck into a corner. It should never freeze in place — speed-limit floor should keep it moving.
21. Hold the player paddle pressed against a side wall while moving. It should not stick or vibrate.
22. Score, then immediately try to hit `Esc` or pause during the countdown. The game should respond.

## Failure-mode tests (when error-handling code is touched)

- Disconnect all controllers. The title screen should show "NO CONTROLLER DETECTED" in red. Choosing CONTROLLER should silently fall back to MOUSE without a crash.
- Rename one of the audio files. The game must fail with a clear error (audio is required); confirm the message is readable.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Both input modes tested.
- [ ] Edge cases passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
