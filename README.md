# Mr. Navarro's Arcade

A Pygame launcher (`Coding Club Arcade`) that fronts a small library of original, tribute, and tutorial games written in Python and Pygame. It is the front end for a custom-built arcade cabinet running at John I. Leonard High School. Pick a title from the carousel and the launcher hands off to that game's `main.py`; closing the game window drops you back at the menu.

---

## About

The cabinet hosts three buckets of games:

- **Original** — Mr. Navarro's own games.
- **Tribute** — re-creations of classic games.
- **Tutorial** — small games built while following Clear Code's Pygame tutorials on YouTube.
- **Student** — student-contributed games. This bucket is discovered at runtime from `games/student/`, which is gitignored so each cabinet keeps its own students' work locally. See [games/student/README.md](games/student/README.md) for the contribution convention.

Each game is **its own standalone project** with its own `main.py` and assets. The launcher launches a game by spawning a subprocess with the game's folder as the working directory, so games are agnostic to the launcher and could be run on their own (`python main.py` from inside the game folder).

## Status

**Phase: Live.** The launcher is in active use on the cabinet. New games are added by editing [settings.py](settings.py) for sponsor games, or by dropping a folder into `games/student/` for student games. See [docs/TODO.md](docs/TODO.md) for the current roadmap and known issues, and [docs/CHANGELOG.md](docs/CHANGELOG.md) for the history of changes.

## Game Lineup

### Original
- **Adventure** — top-down dungeon crawler with text-based flavor (under construction).
- **Air Hockey** — two-paddle table game (limited controller support, physics being tuned).
- **Dungeon Digger** — turn-based dungeon RPG with shop, saves, and leaderboard.
- **Ninja Frog** — side-scrolling platformer (under construction, physics being tuned).
- **Star Hero** — vertical-scrolling space shoot'em up.

### Tribute
- **Game of the Amazons** — abstract strategy board game (queens move and shoot arrows).
- **Jezz Ball** — draw walls to trap bouncing balls (limited controller support).
- **Pazaak** — Star Wars: Knights of the Old Republic card game (under construction).
- **Puzzle League** — Tetris Attack / Panel de Pon clone (under construction).

### Tutorial
- **Breakout** — paddle, ball, blocks, with upgrades.
- **Flappy Bird** — flappy bird clone, parallax scrolling.
- **Pong** — the classic.
- **Runner** — endless side-scroller.
- **Snake** — grid-based snake.
- **Space Invaders** — Star Hero's parent project.
- **Tetris** — the falling-block classic.

For full rules and per-game controls, see each game's `README.md`.

## Requirements

- Python 3.10+
- [Pygame](https://www.pygame.org/) 2.5+

> The repo's [requirements.txt](requirements.txt) is currently empty; install Pygame manually until it is populated. Tracked in [docs/TODO.md](docs/TODO.md).

## Install & Run

From the repository root:

```powershell
git clone <repo-url> arcade-cabinet
cd arcade-cabinet
pip install pygame
python main.py
```

On Windows, `py main.py` works as well.

## Packaging a distributable build

The launcher can be packaged into a click-to-run Windows folder via PyInstaller plus a bundled embeddable Python that runs the games as subprocesses. End users do not need Python installed.

One-time setup:

```powershell
pip install -r requirements-build.txt
.\scripts\setup_runtime.ps1
```

Build:

```powershell
.\build.ps1
```

The result is `dist/ArcadeCabinet/`, a self-contained folder containing `ArcadeCabinet.exe`, the launcher's assets, the `games/` tree, and the bundled `runtime/python/` interpreter. Zip and ship that folder; users double-click the exe.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (section 7) for how `LauncherSettings.GAME_PYTHON` selects the interpreter at runtime.

## Launcher Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move selection | `Up` / `Down` / `W` / `S` | D-pad up/down, left-stick vertical |
| Confirm / launch / enter submenu | `Enter`, `Space` | `A`, `Start` |
| Back to previous menu | `Esc` (also quits at the root) | `B` |
| Toggle fullscreen | `F11` | `Select` (a.k.a. `Back`) |
| Quit launcher | Close the window | — |

### In-game controls

While in a game:

- **Toggle fullscreen:** `F11` on keyboard, `Select` on controller.
- **Return to launcher:** Close the game window, or hold `Start + Select + L1 + R1` on the controller (each game implements its own quit combo).

Per-game gameplay controls live in each game's `README.md`.

## Project Structure

```
arcade-cabinet/
├── main.py                 # Tiny entry point; constructs and runs ArcadeLauncher.
├── settings.py             # All launcher tunables and the sponsor-game registry.
├── requirements.txt        # Python package dependencies (currently empty).
├── launcher/               # Launcher implementation.
│   ├── manager.py          # ArcadeLauncher coordinator.
│   ├── renderer.py         # All UI drawing.
│   ├── discovery.py        # Student-game discovery and manifest parsing.
│   ├── models.py           # MenuNode, MenuFrame, StudentGameRecord dataclasses.
│   └── crt.py              # CRT-style scanline overlay.
├── assets/                 # Launcher fonts, graphics, previews, sounds.
├── games/
│   ├── sponsor/
│   │   ├── original/       # Mr. Navarro's original games.
│   │   ├── tribute/        # Tribute games (classics re-created).
│   │   └── tutorial/       # Games built following Clear Code tutorials.
│   └── student/            # Gitignored. Student games are discovered here at runtime.
└── docs/                   # Project documentation (read these in order below).
```

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — current phase and roadmap.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the launcher actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — most recent changes, so you know the current state.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.

Each game has its own copy of these docs inside its own folder (e.g. `games/sponsor/original/star-hero/docs/ARCHITECTURE.md`). Treat each game as a standalone project.

## Attributions

Asset credits are tracked per game inside each game's folder (typically `assets/graphics/attributions.md` and similar). Launcher-specific assets live under [assets/](assets) and use the `Pixeled` pixel font.

## Credits

- Launcher and games by Mr. Navarro.
- Tutorial games written following [Clear Code](https://www.youtube.com/@ClearCode) tutorials.
- Tribute games derive their rules from their original publishers (credited in each game's README).
