# Star Hero <img src="https://raw.githubusercontent.com/frankiebry/star-hero/refs/heads/main/graphics/player_ship.png" height="32">

Star Hero is a vertically scrolling, space-themed shoot'em up built with Python and Pygame.

This project started as a learning game and continues to grow with new polish, mechanics, and balance updates.

## Requirements

- [Python](https://www.python.org/) 3.10+
- [Pygame](https://www.pygame.org/)

Install Pygame:

```bash
pip install pygame
```

## Run the Game

From the repository root, run through the launcher:

```bash
python main.py
```

Or run Star Hero directly:

```bash
python star-hero/main.py
```

If your Windows environment uses `py`:

```bash
py star-hero/main.py
```

## Core Gameplay Rules

- You start with 3 hearts.
- Getting hit by enemy lasers or colliding with enemies costs hearts.
- Lose all hearts and the run ends.
- Your score increases as you destroy enemies.
- Difficulty ramps up over time.

## Controls

### Keyboard

- `WASD` or Arrow Keys: Move
- `Space`: Fire
- Hold `F`: Move faster
- `Alt + Enter`: Toggle fullscreen
- `Esc`: Pause/unpause
- `+` / `-`: Increase or decrease volume

### Controller (Logitech-style mapping)

- Left analog stick: Move
- `A`: Fire
- `X`: Move faster
- Select/Back: Toggle fullscreen
- `L1` / `R1`: Volume down/up

## Enemy Drops and Powerups

- Hearts: Dropped by red aliens; restores health.
- Laser Upgrades: Dropped by green aliens.
	- Twin Laser: Hits two side-by-side targets.
	- Hyper Laser: Pierces through enemies.
- Rapid Fire: Temporary fire-rate boost dropped by yellow aliens.
- Rainbow Beam: Temporary screen-wide beam attack dropped by blue aliens.

## Enemy Types and Score Values

Each alien behaves differently and awards different points:

- <img src="https://raw.githubusercontent.com/frankiebry/star-hero/refs/heads/main/graphics/red1.png" width="20" height="16"> Red Alien: Slow, drops hearts. **100 points**
- <img src="https://raw.githubusercontent.com/frankiebry/star-hero/refs/heads/main/graphics/green1.png" width="20" height="16"> Green Alien: Medium speed, drops laser upgrades. **200 points**
- <img src="https://raw.githubusercontent.com/frankiebry/star-hero/refs/heads/main/graphics/yellow1.png" width="20" height="16"> Yellow Alien: Fast zigzag movement, drops rapid fire. **300 points**
- <img src="https://raw.githubusercontent.com/frankiebry/star-hero/refs/heads/main/graphics/blue1.png" width="20" height="10"> Blue Alien: Very fast and rare, may use confusion beam, drops rainbow beam. **500 points**

## Attributions

- Graphics attributions: [graphics/attributions.md](graphics/attributions.md)
- Audio attributions: [audio/attributions.md](audio/attributions.md)

## Learning Resources

This project was heavily inspired by [Clear Code's tutorials](https://www.youtube.com/@ClearCode), especially [The ultimate introduction to Pygame](https://www.youtube.com/watch?v=AY9MnQ4x3zk).
