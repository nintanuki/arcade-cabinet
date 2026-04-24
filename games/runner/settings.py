import os
from pathlib import Path

class ScreenSettings:
    WIDTH: int = 800        # Adding ': int' tells Pylance exactly what this is
    HEIGHT: int = 400
    TITLE: str = "Runner"   # Adding ': str' clears the attribute error
    RESOLUTION: tuple[int, int] = (WIDTH, HEIGHT)
    FPS: int = 60