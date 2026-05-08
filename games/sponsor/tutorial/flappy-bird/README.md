# Flappy Bird

A Pygame Flappy Bird tribute: tap to flap, dodge pipes, scroll a parallax background. Built as a tutorial follow-along, then extended with controller support, pause, and a CRT overlay.

## Status

**Phase: Tutorial / playable.** Plane physics, pipe spawning, scoring, menu, music, pause, and CRT scanlines are implemented. Open polish items (full-screen artifacts, controller race conditions) are tracked in [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/flappy-bird
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Flappy Bird**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Flap / start | `Space` | A button |
| Pause | `P` | Start |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
