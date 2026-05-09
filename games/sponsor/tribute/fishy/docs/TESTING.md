# Fishy — Manual Testing Checklist

Run after a non-trivial change.

```powershell
python main.py
```

## Smoke

1. Boot: window opens at 1280 × 720 (`ScreenSettings.RESOLUTION`), no console errors.
2. Title bar shows `ScreenSettings.TITLE`.
3. Background is `ColorSettings.BG_COLOR` (blue).
4. CRT overlay is visible (scanlines + slight flicker).

## Globals

5. `F11` toggles fullscreen. CRT overlay disappears in fullscreen, reappears in windowed.
6. `Esc` exits cleanly.
7. With a controller connected: `BACK` toggles fullscreen.
8. With a controller connected: holding `START + SELECT + L1 + R1` exits cleanly.
9. Closing the OS window via the title-bar `X` exits cleanly.

## Gameplay

10. The player (yellow fish polygon with a black eye) is centered on screen at startup.
11. Arrow keys move the player in all four directions.
12. Player cannot leave the screen edges.
13. Fish (red fish polygons with black eyes) appear from the left or right edge and scroll across the screen.
14. Fish that reach the opposite edge disappear without error.
15. When the player overlaps a fish smaller than itself: the fish disappears and the player grows visibly.
16. When the player overlaps a fish larger than itself: a black game-over screen appears with centered white `GAME OVER` + restart prompt text (no abrupt process exit).
17. Pressing `Enter` during gameplay pauses updates, pauses music, and shows a black pause screen with centered white pause text.
18. Pressing `Enter` on pause resumes gameplay, resumes music, and hides the pause overlay.
19. Pressing `Enter` on game-over restarts the session.

## Sign-off

- [ ] Smoke + globals + gameplay all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
