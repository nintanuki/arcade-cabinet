import os
from pathlib import Path

class ScreenSettings:
    WIDTH: int = 800        # Adding ': int' tells Pylance exactly what this is
    HEIGHT: int = 400
    TITLE: str = "Runner"   # Adding ': str' clears the attribute error
    RESOLUTION: tuple[int, int] = (800, 400)
    FPS: int = 60
    CRT_ALPHA_RANGE: tuple[int, int] = (75, 90)

class PlayerSettings:
    WALK_ANIMATION_SPEED: float = 0.1
    JUMP_VELOCITY: int = -20
    INITIAL_POSITION: tuple[int, int] = (80, 300) # Starting position on the ground
    HORIZONTAL_SPEED: int = 5
    CONTROLLER_DEADZONE: float = 0.25
    SPEED_MULTIPLIER: float = 2.0

class AssetPaths:
    BASE_DIR = Path(__file__).resolve().parent
    TV = BASE_DIR / 'graphics' / 'tv.png'