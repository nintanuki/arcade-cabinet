# Mr. Navarro's Arcade

A Pygame launcher (`Mr. Navarro's Arcade`) that fronts a small library of original and tribute games. Pick a title from the carousel and the launcher hands off to that game's `main.py`; closing the game window drops you back at the menu.

Current lineup:
- Adventure (action dungeon crawler)
- Air Hockey (two-paddle table game)
- Breakout (block-busting paddle game)
- Dungeon Digger (turn-based dungeon crawler)
- Game of the Amazons (abstract strategy board game)
- Jezz Ball (build walls to trap bouncing balls)
- Ninja Frog (side-scrolling platformer)
- Pong (the classic)
- Runner (endless-runner side-scroller)
- Snake (grid-based snake)
- Space Invaders (alien-wave shooter)
- Star Hero (vertical-scrolling space shooter)
- Tetris (falling-block puzzle)

Sponsor games are committed to the repo under `games/sponsor/`. Student-contributed games live under `games/student/` (gitignored, discovered at runtime); see [games/student/README.md](games/student/README.md) for the convention.

## Requirements

- Python 3.10+
- pygame

Install dependency:

```bash
pip install pygame
```

## Run the Launcher

From the repository root:

```bash
python main.py
```

If your system uses `py` on Windows:

```bash
py main.py
```

## Launcher Controls

### Keyboard
- Up/Down or W/S: Move selection
- Enter/Space: Enter submenu / launch selected game
- Esc: Back to previous menu (exits the launcher when already at the root)
- F11: Toggle fullscreen

### Controller
- D-pad/left stick vertical: Move selection
- A or Start: Enter submenu / launch selected game
- B: Back to previous menu
- Select: Toggle fullscreen

While in a game, press F11 (or Select on a controller) to toggle fullscreen, and press Start + Select + L1 + R1 (or close the game window) to return to the launcher.

## Games

Each sponsor game lives under `games/sponsor/<name>/` with its own `main.py` and a per-game README. Categories, input-scheme tags, free-form notes, and the under-construction flag all come from `settings.py` (`GAME_CATEGORIES`, `GAME_INPUT_SCHEMES`, `GAME_NOTES`, `UNDER_CONSTRUCTION_GAMES`).

### Adventure
Action-style dungeon crawler companion piece to Dungeon Digger. README: [games/sponsor/adventure/README.md](games/sponsor/adventure/README.md).
- Status: Under construction.

### Air Hockey
A two-paddle air hockey / pong-style table game. Everything is drawn directly in Pygame with no sprite assets. README: [games/sponsor/air-hockey/README.md](games/sponsor/air-hockey/README.md).
- Status: Playable. Physics are still being tuned, expect wonkiness.
- Input: Mouse and limited controller support.

### Breakout
Bounce a ball off a paddle to clear rows of colored blocks; collect upgrades for extra hearts, lasers, paddle size, and ball speed. README: [games/sponsor/breakout/README.md](games/sponsor/breakout/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Dungeon Digger
Turn-based dungeon crawler. Dig for treasure, find the key, unlock the door, and descend through every level. Includes a 10-slot save system, shop, and leaderboard. README: [games/sponsor/dungeon-digger/README.md](games/sponsor/dungeon-digger/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Game of the Amazons
Implementation of the abstract strategy board game (queens that move and shoot arrows to reduce the playable territory). README: [games/sponsor/game-of-the-amazons/README.md](games/sponsor/game-of-the-amazons/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Jezz Ball
Trap bouncing balls behind walls you draw on a shrinking play field. README: [games/sponsor/jezz-ball/README.md](games/sponsor/jezz-ball/README.md).
- Status: Playable.
- Input: Mouse and limited controller support.

### Ninja Frog
Side-scrolling platformer starring a ninja frog, with tilemap levels and a tile viewer dev tool. README: [games/sponsor/ninja-frog/README.md](games/sponsor/ninja-frog/README.md).
- Status: Under construction. Physics are still being tuned, expect wonkiness.

### Pong
Classic two-paddle Pong, built following Clear Code's Pong tutorial. README: [games/sponsor/pong/README.md](games/sponsor/pong/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Runner
Endless-runner side-scroller. README: [games/sponsor/runner/README.md](games/sponsor/runner/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Snake
Grid-based Snake. Eat, grow, do not crash into yourself. README: [games/sponsor/snake/README.md](games/sponsor/snake/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Space Invaders
Tribute take on Space Invaders with player ship, laser-pocked obstacles, and waves of aliens. README: [games/sponsor/space-invaders/README.md](games/sponsor/space-invaders/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Star Hero
Vertically scrolling space shoot'em up: dodge enemies, collect powerups, chase a high score. Difficulty ramps with score; supports laser/rapid-fire/rainbow upgrades and bombs. README: [games/sponsor/star-hero/README.md](games/sponsor/star-hero/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Tetris
The falling-block classic with preview, score, and timer. README: [games/sponsor/tetris/README.md](games/sponsor/tetris/README.md).
- Status: Playable.
- Input: Keyboard and controller.

## Game Rules and Controls

For full rules and the complete control scheme of each game, see the per-game README linked above. Quick reference:
- Star Hero: Survive enemy waves, collect powerups, chase the high score.
- Dungeon Digger: Find the key, unlock the door, survive monsters, clear all levels.
- Pong / Air Hockey: Outscore your opponent.
- Breakout / Jezz Ball: Clear the play field.
- Snake / Runner / Space Invaders / Tetris: Last as long as possible while score climbs.
- Adventure, Ninja Frog: Under construction — playable extent varies.

## Attributions

Asset credits are tracked per game:
- Star Hero: [games/sponsor/star-hero/assets/graphics/attributions.md](games/sponsor/star-hero/assets/graphics/attributions.md), [games/sponsor/star-hero/assets/audio/attributions.md](games/sponsor/star-hero/assets/audio/attributions.md), [games/sponsor/star-hero/assets/music/attributions.md](games/sponsor/star-hero/assets/music/attributions.md)
- Dungeon Digger: [games/sponsor/dungeon-digger/assets/graphics/attributions.md](games/sponsor/dungeon-digger/assets/graphics/attributions.md), [games/sponsor/dungeon-digger/assets/sound/attributions.md](games/sponsor/dungeon-digger/assets/sound/attributions.md), [games/sponsor/dungeon-digger/assets/music/attributions.md](games/sponsor/dungeon-digger/assets/music/attributions.md)
- Adventure: [games/sponsor/adventure/graphics/attributions.md](games/sponsor/adventure/graphics/attributions.md), [games/sponsor/adventure/sound/attributions.md](games/sponsor/adventure/sound/attributions.md), [games/sponsor/adventure/music/attributions.md](games/sponsor/adventure/music/attributions.md)

Other games either use no third-party assets or have not yet published an attributions file.

## Project Notes

- Launcher roadmap: [docs/TODO.md](docs/TODO.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Testing notes: [docs/TESTING.md](docs/TESTING.md)
- Root launcher files: [main.py](main.py), [settings.py](settings.py)
- Game registry, preview images, and status flags (under-construction, no-controller-support) are all configured in [settings.py](settings.py) under `GameSettings`.
