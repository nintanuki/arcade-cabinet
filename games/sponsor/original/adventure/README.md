# Adventure

A top-down, room-by-room exploration game built in Pygame. Adventure is a Zelda-style "rooms-on-a-grid" engine where the world is a 2D map of cells and each cell is its own tile grid. The current build is an **engine slice** — the world model, render pipeline, and player movement are working but the player sprite, combat, items, and dungeons are still TODO.

## Status

Engine slice / pre-alpha. You can walk around a placeholder cell and step across cell boundaries. There is no combat, no items, no audio, and no win condition yet.

## Requirements

- Python 3.10+
- `pygame` 2.5+

## Run

```powershell
cd games/sponsor/original/adventure
python main.py
```

## Controls

| Action            | Keyboard | Controller            |
| ----------------- | -------- | --------------------- |
| Move              | Arrow keys / `WASD` | D-pad / left stick |
| Toggle fullscreen | `F11`    | `BACK`                |
| Toggle debug player | `F1`   | —                     |
| Toggle debug overlay | `F2`  | —                     |
| Quit              | `Esc`    | `START+SELECT+L1+R1`  |

## Documentation

- [README.md](README.md) — this file.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the world / render / input systems fit together.
- [docs/TODO.md](docs/TODO.md) — phased roadmap (player → dungeons → combat → audio → persistence).
- [docs/TESTING.md](docs/TESTING.md) — manual smoke checks.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — append-only history.
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — rules for human or AI editors.

## Project layout

```
core/        World model, tilemaps, cell layout
entities/    Player and (eventually) enemies
systems/     Cross-cutting systems (audio, etc.)
ui/          RenderManager, windows, coords, CRT overlay
utils/       Pure helpers
assets/      Graphics, fonts, audio
docs/        Architecture, TODO, TESTING, CHANGELOG
main.py      Entry point + GameManager
settings.py  All tunables
```
