# Ms. Fishy — Manual Testing Checklist

Run after a non-trivial change.

Docs-only exception: if a change touches documentation files only
(`README.md`, `docs/*.md`, `.github/copilot-instructions.md`) and does not
modify runtime code, gameplay smoke checks are not required.

```powershell
python main.py
```

## Smoke

1. Boot: window opens at 1280 × 720 (`ScreenSettings.RESOLUTION`), no console errors.
2. Title bar shows `ScreenSettings.TITLE`.
3. Background is a vertical gradient from aqua (`ColorSettings.BG_COLOR_TOP`) at the top to deep navy (`ColorSettings.BG_COLOR_BOTTOM`) at the bottom.
4. If `DebugSettings.ENABLE_CRT` is `True`, CRT overlay is visible (scanlines + slight flicker). If it is `False`, no CRT overlay is drawn.

## Globals

5. `F11` toggles fullscreen. When `DebugSettings.ENABLE_CRT` is `True`, the CRT overlay disappears in fullscreen and reappears in windowed.
6. `Esc` exits cleanly. When `DebugSettings.WEB_SAFE_EXIT` is `True`, the game should close by leaving the main loop without a `sys.exit()` traceback.
7. With a controller connected: `BACK` toggles fullscreen.
8. With a controller connected: holding `START + SELECT + L1 + R1` exits cleanly.
9. Closing the OS window via the title-bar `X` exits cleanly.

## Gameplay

10. Pressing `Enter` or `START` on the title scene starts gameplay with an empty ocean, then the player visibly drops in from above and settles near center.
11. On title-start drop-in, the `splash` SFX plays exactly when the player first appears from the top edge, before gameplay music begins.
12. Fish (varied retro-palette polygon shapes with black eyes and drop shadows) do not spawn until the drop-in settles.
13. Arrow keys move the player in all four directions after drop-in completes.
14. Player cannot leave the screen edges.
15. Fish appear from the left or right edge and scroll across the screen.
16. Fish that reach the opposite edge disappear without error.
18. When the player overlaps a fish smaller than itself: the fish disappears, the player grows, and the hunger timer increases. Near-peer fish add more time than tiny fish (diminishing returns).
19. The hunger timer starts at `00:30` (30 seconds) and counts down during active gameplay.
20. The top-left HUD shows four stacked rows: `TOTAL FISH EATEN`, `WEIGHT EATEN`, `CURRENT WEIGHT`, `HUNGER TIMER`, with a colour bar beneath the timer.
21. The hunger bar is green when full and drains toward red as time decreases.
22. The `HUNGER TIMER` label and text turn red when 5 or fewer seconds remain.
23. When the player overlaps a fish larger than itself: a black screen appears with centered red `YOU WERE EATEN BY A BIGGER FISH`.
24. When the timer reaches zero: a black screen appears with centered red `YOU STARVED TO DEATH`.
25. Pressing `Enter`, controller `A`, or controller `START` on either outcome screen advances to a centered white `GAME OVER` screen.
26. If the player grows so wide that `player.rect.width > ScreenSettings.WIDTH`, gameplay ends with centered white `YOU'VE EATEN ALL THE FISH!`; one confirm advances to `GAME OVER`, second confirm routes to post-run flow.
27. Pressing `Enter` during gameplay pauses updates, pauses music, and shows a black pause screen with centered white pause text.
28. Pressing `Enter` on pause resumes gameplay, resumes music, and hides the pause overlay.

## Sign-off

- [ ] Smoke + globals + gameplay all passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
