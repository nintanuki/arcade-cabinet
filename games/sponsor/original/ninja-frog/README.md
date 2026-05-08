# Ninja Frog

Ninja Frog is an in-progress 2D platformer built in Pygame using the public-domain "Pixel Adventure" sprite pack. The current build is a prototype: one looping room, one snail enemy, basic run/jump physics, and a vertically-scrolling camera.

## Status

**Phase: Prototype.** The core movement, animation, collision, and camera systems are working. Full level design, sound, enemy variety, and a goal/exit are not yet implemented. See [docs/TODO.md](docs/TODO.md) for the live backlog.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

From this folder:

```powershell
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Original Games → Ninja Frog**.

## Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move left / right | `A` `D` / arrows | D-pad or left stick |
| Jump | `Space` / `W` / `Up` | A button |
| Run | `Shift` | X button |
| Toggle zoom (debug) | `Z` | — |
| Toggle fullscreen | `F11` | Select |
| Quit | `Esc` | `Start + Select + L1 + R1` |

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap, known bugs, and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.

## Credits

Sprite art is from the [Pixel Adventure 1](https://pixelfrog-assets.itch.io/pixel-adventure-1) pack by Pixel Frog (free / CC0).
