
"""Entry point for the Coding Club Arcade launcher."""

from pathlib import Path

from launcher.manager import ArcadeLauncher

if __name__ == "__main__":
    ArcadeLauncher(Path(__file__).resolve().parent).run()

