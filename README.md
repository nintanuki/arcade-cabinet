# Mr. Navarro's Arcade

A Pygame launcher (`Mr. Navarro's Arcade`) that fronts a small library of original and tribute games. Pick a title from the carousel and the launcher hands off to that game's `main.py`; closing the game window drops you back at the menu.

Current lineup:
- Air Hockey (two-paddle table game)
- Breakout (block-busting paddle game)
- Dungeon Digger (turn-based dungeon crawler)
- Dungeon Warrior (action dungeon crawler)
- Game of the Amazons (abstract strategy board game)
- Jezz Ball (build walls to trap bouncing balls)
- Ninja Frog (side-scrolling platformer)
- Pong (the classic)
- Runner (endless-runner side-scroller)
- Snake (grid-based snake)
- Space Invaders (alien-wave shooter)
- Star Hero (vertical-scrolling space shooter)
- Tetris (falling-block puzzle)

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
- Enter/Space: Launch selected game
- F11: Toggle fullscreen
- Esc: Exit launcher

### Controller
- D-pad/left stick vertical: Move selection
- A or Start: Launch selected game
- Select/Back: Toggle fullscreen

While in a game, press F11 (or Select on a controller) to toggle fullscreen, and press Start + Select + L1 + R1 (or close the game window) to return to the launcher.

## Games

Each game lives under `games/<name>/` with its own `main.py` and (where present) a per-game README. Status flags below come from `settings.py` (`UNDER_CONSTRUCTION_GAMES` and `NO_CONTROLLER_SUPPORT_GAMES`).

### Air Hockey
A two-paddle air hockey / pong-style table game. Everything is drawn directly in Pygame with no sprite assets. README: [games/air-hockey/README.md](games/air-hockey/README.md).
- Status: Playable. Physics are still being tuned, expect quirks.
- Input: Keyboard/mouse only (no controller support).

### Breakout
Bounce a ball off a paddle to clear rows of colored blocks; collect upgrades for extra hearts, lasers, paddle size, and ball speed. README: [games/breakout/README.md](games/breakout/README.md).
- Status: Playable.
- Input: Keyboard/mouse only (no controller support).

### Dungeon Digger
Turn-based dungeon crawler. Dig for treasure, find the key, unlock the door, and descend through every level. Includes a 10-slot save system, shop, and leaderboard. README: [games/dungeon-digger/README.md](games/dungeon-digger/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Dungeon Warrior
Action-style dungeon crawler companion piece to Dungeon Digger. README: [games/dungeon-warrior/README.md](games/dungeon-warrior/README.md).
- Status: Under construction.

### Game of the Amazons
Implementation of the abstract strategy board game (queens that move and shoot arrows to reduce the playable territory). README: [games/game-of-the-amazons/README.md](games/game-of-the-amazons/README.md).
- Status: Under construction.

### Jezz Ball
Trap bouncing balls behind walls you draw on a shrinking play field. README: [games/jezz-ball/README.md](games/jezz-ball/README.md).
- Status: Playable.
- Input: Keyboard/mouse only (no controller support).

### Ninja Frog
Side-scrolling platformer starring a ninja frog, with tilemap levels and a tile viewer dev tool. README: [games/ninja-frog/README.md](games/ninja-frog/README.md).
- Status: Under construction.

### Pong
Classic two-paddle Pong, built following Clear Code's Pong tutorial. README: [games/pong/README.md](games/pong/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Runner
Endless-runner side-scroller. README: [games/runner/README.md](games/runner/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Snake
Grid-based Snake. Eat, grow, do not crash into yourself. README: [games/snake/README.md](games/snake/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Space Invaders
Tribute take on Space Invaders with player ship, laser-pocked obstacles, and waves of aliens. README: [games/space-invaders/README.md](games/space-invaders/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Star Hero
Vertically scrolling space shoot'em up: dodge enemies, collect powerups, chase a high score. Difficulty ramps with score; supports laser/rapid-fire/rainbow upgrades and bombs. README: [games/star-hero/README.md](games/star-hero/README.md).
- Status: Playable.
- Input: Keyboard and controller.

### Tetris
The falling-block classic with preview, score, and timer. README: [games/tetris/README.md](games/tetris/README.md).
- Status: Playable.
- Input: Keyboard/mouse only (no controller support).

## Game Rules and Controls

For full rules and the complete control scheme of each game, see the per-game README linked above. Quick reference:
- Star Hero: Survive enemy waves, collect powerups, chase the high score.
- Dungeon Digger: Find the key, unlock the door, survive monsters, clear all levels.
- Pong / Air Hockey: Outscore your opponent.
- Breakout / Jezz Ball: Clear the play field.
- Snake / Runner / Space Invaders / Tetris: Last as long as possible while score climbs.
- Dungeon Warrior, Game of the Amazons, Ninja Frog: Under construction — playable extent varies.

## Attributions

Asset credits are tracked per game:
- Star Hero: [games/star-hero/graphics/attributions.md](games/star-hero/graphics/attributions.md), [games/star-hero/audio/attributions.md](games/star-hero/audio/attributions.md), [games/star-hero/music/attributions.md](games/star-hero/music/attributions.md)
- Dungeon Digger: [games/dungeon-digger/assets/graphics/attributions.md](games/dungeon-digger/assets/graphics/attributions.md), [games/dungeon-digger/assets/sound/attributions.md](games/dungeon-digger/assets/sound/attributions.md), [games/dungeon-digger/assets/music/attributions.md](games/dungeon-digger/assets/music/attributions.md)
- Dungeon Warrior: [games/dungeon-warrior/graphics/attributions.md](games/dungeon-warrior/graphics/attributions.md)

Other games either use no third-party assets or have not yet published an attributions file.

## Project Notes

- Launcher roadmap: [docs/TODO.md](docs/TODO.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Testing notes: [docs/TESTING.md](docs/TESTING.md)
- Root launcher files: [main.py](main.py), [settings.py](settings.py)
- Game registry, preview images, and status flags (under-construction, no-controller-support) are all configured in [settings.py](settings.py) under `GameSettings`.
