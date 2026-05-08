# Game of the Amazons

Game of the Amazons is a two-player abstract strategy game played on a 10×10 board. Each turn a player moves one of their four queens like a chess queen, then fires an arrow from the queen's new tile in any queen-direction. Arrows permanently block their landing tile. A player who cannot move on their turn loses.

This build is a Pygame tribute with a human (WHITE) vs AI (BLACK) match.

## Status

**Phase: Playable, polishing.** The full move/shoot turn structure, win detection, animations, audio, and a basic AI are all in place. The AI currently plays random legal moves and the in-flight arrow sprite uses placeholder facing — both tracked in [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

From this folder:

```powershell
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Game of the Amazons**.

## Rules

1. **Move.** On your turn, move one of your four queens any number of squares in a straight line (horizontal, vertical, or diagonal). The queen cannot pass through other queens or arrows.
2. **Shoot.** From the queen's new square, fire an arrow in any of the eight directions, again any number of squares. The arrow tile is permanently blocked.
3. **Win.** A player who has no legal move at the start of their turn loses. Equivalently, the last player able to move wins.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move cursor | Arrow keys | D-pad |
| Confirm (select queen / destination / arrow target) | `Space` | A button |
| Restart after game over | `Enter` | Start |
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
