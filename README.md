# Arcade Cabinet

Arcade Cabinet is a Pygame launcher for two games:
- Star Hero (arcade space shooter)
- Dungeon Digger (turn-based dungeon crawler)

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

## Game Rules and Controls

Detailed controls/rules live in each game README:
- Star Hero: [star-hero/README.md](star-hero/README.md)
- Dungeon Digger: [dungeon-digger/README.md](dungeon-digger/README.md)

Quick summary:
- Star Hero: Survive enemy waves, collect powerups, and chase high score.
- Dungeon Digger: Find key, unlock door, survive monsters, and clear all levels.

## Attributions

Asset credits are tracked per game:
- Star Hero graphics/audio: [star-hero/graphics/attributions.md](star-hero/graphics/attributions.md), [star-hero/audio/attributions.md](star-hero/audio/attributions.md)
- Dungeon Digger graphics/sound: [dungeon-digger/graphics/attributions.md](dungeon-digger/graphics/attributions.md), [dungeon-digger/sound/attributions.md](dungeon-digger/sound/attributions.md)

## Project Notes

- Launcher roadmap: [TODO.md](TODO.md)
- Root launcher files: [main.py](main.py), [settings.py](settings.py)
