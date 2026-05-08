# Jezz Ball

A Pygame tribute to the classic *Jezzball*: build walls inside a playfield filled with bouncing balls, claim 70%+ of the field per level, and survive the climb in ball count and speed across ten stages.

## Status

**Phase: Playable, polishing.** Title screen → ten levels → game-over → initials entry → leaderboard, with mouse, keyboard, and controller input. Two known issues are tracked in [docs/TODO.md](docs/TODO.md): the analog stick input path is unfinished, and partial-wall destruction (red vs. blue half) is not implemented.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

From this folder:

```powershell
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Jezz Ball**.

## Rules

1. Each level seeds the playfield with bouncing balls.
2. The cursor builds **walls** (vertical or horizontal) starting at the cursor's position. The wall grows out from the build point in both directions until each end hits a wall or the edge.
3. While a wall is growing, the segment **before** the cursor is one color and the segment **after** is the other. If a ball hits *any* part of a still-growing wall, the wall is destroyed and you lose a life.
4. Once a wall fully completes, the playfield is split. Any region with no ball in it is **claimed** and locked in.
5. Clear the level by claiming the level's `area_needed_percent` (70 → 80 across the 10 stages).
6. Run out of lives or time and the game is over.

## Controls

| Action | Mouse / Keyboard | Controller |
| --- | --- | --- |
| Move cursor | Mouse motion / arrow keys | D-pad or left analog |
| Build wall | Left-click / `Space` | A button |
| Toggle wall orientation | Right-click / `R` | X button |
| Pause | `P` | Start |
| Toggle fullscreen | `F11` | Select (Back) |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap, known bugs, and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
