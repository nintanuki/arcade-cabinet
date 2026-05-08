# Ninja Frog — Manual Testing Checklist

Run this after a non-trivial change. The mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*.

---

## Smoke test (every change)

```powershell
cd games/sponsor/original/ninja-frog
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Original Games → Ninja Frog**. Both entry paths must work.

1. **Boot.** Window opens at the configured resolution, titled "Platformer". No console errors aside from the known animation-frame-count debug prints.
2. **Player spawn.** Player appears in the bottom-left of the visible map.
3. **Camera.** Player is centered horizontally; the entire row is visible because the screen is 1.5× the map width.

---

## Movement

4. **Walk.** `A` / `D` / arrows / D-pad / left stick all move the player horizontally.
5. **Run.** Holding `Shift` / `X` button increases horizontal speed.
6. **Jump.** `Space` / `W` / `Up` / `A` button on a controller all trigger a jump.
7. **Air control.** Player can change horizontal direction mid-air.
8. **Gravity.** Player falls and lands on the floor without phasing through it.

## Animation

9. **Idle.** Standing still plays the idle animation cycle.
10. **Run.** Moving plays the run cycle.
11. **Jump → Fall.** Rising shows the jump frame; falling shows the fall frame.
12. **Facing.** The sprite flips to match the direction of travel.

## Collision

13. **Wall block.** Player cannot move through the side walls (`x` tiles).
14. **Floor block.** Player cannot fall through the bottom row.
15. **Platform landing.** Player lands cleanly on the floating `g` platforms.
16. **Known issue checks.** Confirm the bouncing/phasing/start-fall TODO items are still reproducible (or fixed).

## Enemy

17. **Snail patrol.** The snail walks back and forth on its platform.
18. **Stomp kill.** Landing on the snail from above bounces the player and kills the snail.
19. **Side collision.** *(Known gap)* Walking into the snail from the side currently does nothing — confirm any new behavior matches the change.

## Camera

20. **Follow.** Moving up/down causes the camera to scroll vertically; the camera does not scroll horizontally.
21. **Clamping.** The camera does not show outside the left, right, or bottom map edges.
22. **Zoom toggle.** `Z` switches between the zoomed-in gameplay view and the zoomed-out debug view; both render correctly.

## Global controls

23. `F11` and Select toggle fullscreen.
24. `Esc` quits cleanly.
25. Holding `Start + Select + L1 + R1` on a controller exits cleanly.
26. Closing the OS window quits cleanly.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- Visually confirm the changed section reflects the new values (gravity, jump strength, speeds, screen size, zoom factor, animation speed).
- Confirm no other section regressed.
- `grep` for the literal value to confirm no constants leaked back into `main.py`, `sprites.py`, `camera.py`, `render.py`, or `tile_maps.py`.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Movement and animation passed.
- [ ] Collision passed.
- [ ] Enemy interactions passed.
- [ ] Camera passed.
- [ ] Global controls passed.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
