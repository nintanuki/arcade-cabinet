# Puzzle League

A Pygame tribute to *Tetris Attack* / *Panel de Pon* / *Pokémon Puzzle League*. The stack rises continuously from the bottom; the player swaps adjacent blocks with a 1×2 cursor to form matches of three or more like-colored blocks; matches clear and falling blocks chain into more matches.

## Status

**Phase: Scaffold.** The project structure, settings, controller plumbing, loading screen, title/game-over screen, CRT overlay, and main loop are all in place. Gameplay (block rendering, cursor, swap, matching, chaining, rise, top-out) is stubbed with `# TODO` comments inside `GameManager` and `Board`. See [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

From this folder:

```powershell
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Puzzle League**.

## Rules (target gameplay)

1. The stack continuously rises from the bottom of the 6 × 12 visible playfield. New blocks emerge from the hidden buffer row.
2. The player controls a **1×2 cursor** that highlights two horizontally-adjacent cells. The confirm button **swaps** those two cells (whether or not either is empty).
3. Three or more like-colored blocks in a horizontal or vertical line **match**, flash, then pop.
4. Blocks above a popped match **fall**. If a fall results in another match without further player input, that's a **chain** — chain points scale steeply by depth.
5. Holding the rush button raises the stack faster; running the stack into the ceiling causes a top-out (with a short grace period before game-over fires).
6. Game over when the stack tops out and the grace timer elapses.

## Controls (target)

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move cursor | Arrow keys | D-pad / left analog |
| Swap | `Space` | A button |
| Rush (raise stack) | `Shift` | R1 |
| Pause | `P` | Start |
| Toggle fullscreen | `F11` | Select (Back) |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Project structure

```
core/
  blocks.py        Block model
  board.py         Board: grid, cursor, rise/clear/chain state machine (stubbed)
systems/
  audio_manager.py Audio manager
  managers.py      ScoreManager, SessionStateManager
ui/
  crt.py           CRT overlay
  style.py         Reusable style helpers
tools/             Developer-facing helpers
assets/
  font/, graphics/, music/, sound/
docs/              ARCHITECTURE, TODO, TESTING, CHANGELOG
main.py            GameManager + entry point
settings.py        Tunables grouped into *Settings classes
```

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
