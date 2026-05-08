# Pong

A Pygame Pong tribute, originally built following ClearCode's [Learning Pygame by making Pong](https://youtu.be/Qf3-aDXG8q4) tutorial and then extended with a CRT overlay, controller support, custom audio, and a `GameManager` separation.

## Status

**Phase: Tutorial / playable.** Player paddle, AI opponent, ball with collision, and score tracking are all implemented. Music plays on loop and SFX trigger on hits. CRT scanlines + flicker render as the final pass each frame. Open polish items (delta-time movement, mute, pause, high-score file, intro/menu, level scaling) live in [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

```powershell
cd games/sponsor/tutorial/pong
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tutorial Games → Pong**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move paddle | `Up` / `Down` | D-pad / left analog (vertical) |
| Toggle fullscreen | `F11` | Back (Select) |
| Quit | `Esc` | `Start + Back + L1 + R1` |

## Documentation

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.

## Credits

Tutorial source: [Clear Code — Learning Pygame by making Pong](https://youtu.be/Qf3-aDXG8q4). LMMS for the initial beat used in the music track.