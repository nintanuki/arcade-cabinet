# Breakout

A Pygame Breakout clone built as a learning exercise: paddle, ball, brick wall, falling power-ups, and a laser upgrade. Includes controller support, music, and a CRT overlay.

## Status

**Phase: Tutorial / playable.** Single-stage layout, paddle-and-ball physics, brick destruction, drop-down power-ups, projectile shoot upgrade, hearts (lives), and CRT scanlines are all implemented. No menu, score screen, or persistence — see [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/breakout
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Breakout**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move paddle | `Left` / `Right` | D-pad / left analog stick |
| Launch ball / shoot | `Space` | A button |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
