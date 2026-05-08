# Snake

A Pygame Snake clone in a single file. Eat the apple, grow the body, don't crash into yourself or the wall.

## Status

**Phase: Tutorial / playable.** Single-file implementation in [snake.py](snake.py): grid-based snake movement, apple spawn, growth, wall + self collision. Controller support, audio, and CRT polish items are tracked in [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/snake
python snake.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Snake**.

> **Note:** the entry point is `snake.py`, not `main.py`. The launcher's manifest knows this; standalone runs should use `python snake.py`.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Steer | Arrow keys | D-pad / left analog stick |
| Quit | `Esc` | `Start + Back + L1 + R1` |

180-degree reversals are blocked: pressing the opposite of the current heading is ignored.

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
