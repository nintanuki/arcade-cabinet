# Pazaak — Manual Testing Checklist

Run this after a non-trivial change. The mental rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md); this file lists what to *do*.

> **Note:** Pazaak is a scaffold. The smoke test below covers what exists today. Add new sections here as gameplay is built (see [docs/TODO.md](TODO.md)).

---

## Smoke test (every change)

```powershell
cd games/sponsor/tribute/pazaak
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Pazaak**. Both entry paths must work.

1. **Boot.** Window opens at `1280 × 720`. No console errors.
2. **Quit chord.** Holding `Start + Back + L1 + R1` on a connected controller exits cleanly.
3. **OS close.** Closing the window via the OS quits cleanly.
4. **Hot-plug.** Plugging or unplugging a controller while running does not crash; `pygame.JOYDEVICEADDED` / `JOYDEVICEREMOVED` are handled by `handle_joystick_hotplug`.
5. **CRT overlay.** Once Phase 0 of [TODO](TODO.md) is complete, the CRT scanlines + flicker render every frame.

---

## Settings-change tests

When [settings.py](../settings.py) is edited:

- Visually confirm the changed section reflects the new values (window size, palette, controller mapping).
- `grep` for the literal value to confirm no constants leaked into other files.

---

## Sign-off

- [ ] Smoke test passed.
- [ ] Quit paths exit cleanly.
- [ ] No console errors at boot.
- [ ] [docs/CHANGELOG.md](CHANGELOG.md) updated.
- [ ] [docs/ARCHITECTURE.md](ARCHITECTURE.md) updated if structure changed.
- [ ] [docs/TODO.md](TODO.md) updated if a roadmap item was completed.
