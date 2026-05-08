# Runner

A Pygame side-scrolling runner: jump over flies, dodge snails, score points by surviving. Originally a tutorial follow-along, extended with controller support and a CRT overlay.

## Status

**Phase: Tutorial / playable.** Ground-bounded player with gravity-based jumps, animated player sprite, parallax background, alternating snail / fly enemies, score, and game-over restart. CRT scanlines render as the final pass.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/runner
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Runner**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move left / right | `Left` / `Right` (or `A` / `D`) | D-pad / left analog (horizontal) |
| Jump / start | `Space` | A button |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
