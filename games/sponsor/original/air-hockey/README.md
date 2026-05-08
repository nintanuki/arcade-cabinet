# Air Hockey

A top-down air hockey game written in Python and Pygame for the Coding Club Arcade cabinet. The puck and paddles are drawn entirely as primitives — no sprite sheets — and the game supports both mouse and controller play.

---

## About

Air Hockey is one of Mr. Navarro's original games. The starting point was the loop and collision logic from [Clear Code's Pong tutorial](https://www.youtube.com/watch?v=Qf3-aDXG8q4), reworked into a vertical air-hockey rink with goals, score countdowns, a CRT post-process, and an input-mode title screen.

## Status

**Phase: Playable, polishing.** Single-player vs. a chase-AI opponent. First-to-nothing — the match runs indefinitely; ending conditions and a high-score table are still on the roadmap. See [docs/TODO.md](docs/TODO.md).

## Requirements

- Python 3.10+
- Pygame 2.5+

## Install & Run

This game is a standalone project. Run directly from its own folder:

```powershell
cd games/sponsor/original/air-hockey
python main.py
```

Or launch through the cabinet's launcher (from the repo root: `python main.py`, then **Mr. Navarro's Games → Original Games → Air Hockey**).

## Controls

| Action | Mouse / Keyboard | Controller |
| --- | --- | --- |
| Move paddle | Mouse cursor | Left analog stick |
| Spike (move forward fast) | Hold left mouse button | Hold `A` |
| Pause / resume | `Enter` | `Start` |
| Mute / unmute | `M` | — |
| Toggle fullscreen | `F11` | `Back` |
| Quit to launcher | `Esc` | `Start + Back + L1 + R1` |

A title screen at boot lets you choose between **mouse** and **controller** input. Use arrows or the D-pad to choose, `Enter` or `Start` to confirm.

## Project Structure

```
air-hockey/
├── main.py            # Entry point; the Game class is the coordinator.
├── settings.py        # All tunable constants (currently flat module-level).
├── audio.py           # Audio class: sounds, channels, mixer config.
├── crt.py             # CRT scanline / vignette overlay.
├── debug.py           # Optional debug helpers.
├── audio/             # OGG / WAV music and sound effects.
├── graphics/          # Static images (e.g. the CRT frame).
├── Pixeled.ttf        # Pixel font (lives at root for legacy reasons).
├── english.png        # Static asset.
└── docs/              # Project documentation (read in order below).
```

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap, known issues, ideas.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.

## Credits

- Design and code: Mr. Navarro.
- Loop and collision baseline: [Clear Code's Pong tutorial](https://www.youtube.com/watch?v=Qf3-aDXG8q4).
- Pixel font: `Pixeled.ttf`.
- Sound effects: see `audio/` folder; verify attribution before redistributing.
