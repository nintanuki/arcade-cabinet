# Tetris

A Pygame Tetris built as a tutorial follow-along, then extended with controller support, fullscreen toggle, and a CRT overlay.

## Status

**Phase: Tutorial / playable.** The full Tetris loop runs: tetromino shapes spawn, fall on a tick timer, can be moved / rotated, lock into the playfield, complete rows clear, score tracks, a preview shows the next three shapes. CRT scanlines render as the final pass. Music loops indefinitely.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/tetris
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Tetris**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move left / right | `Left` / `Right` | D-pad / left analog (horizontal) |
| Soft drop | `Down` | D-pad down / analog down |
| Rotate | `Up` | A button |
| Toggle fullscreen | `F11` | Back (Select) |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Credits

Per the original `readme.txt` shipped with the project:

- Code and graphics are public domain (CC0).
- Background music is by [Kat](https://opengameart.org/content/title-theme-8-bit-style).
- Landing sound is from a [Little Robot Sound Factory soundpack](https://opengameart.org/content/8-bit-sound-effects-library).
- Font is [Russo One](https://www.dafont.com/russo-one.font).

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
