# Space Invaders

A Pygame Space Invaders clone. Move the player ship horizontally, shoot lasers, dodge alien fire, hide behind destructible obstacles, occasionally watch a UFO ("extra") streak across the top.

## Status

**Phase: Tutorial / playable.** Player movement + shooting, a grid of `Alien` rows that march and descend, `Laser` projectiles, destructible `Obstacle` blocks, and an `Extra` UFO are all implemented. Pause overlay and CRT scanlines render. Open polish items (initials high-score, animations, full-screen, post-game flow) live in [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/space-invaders
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Space Invaders**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move ship | `Left` / `Right` | D-pad / left analog (horizontal) |
| Shoot | `Space` | A button |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
