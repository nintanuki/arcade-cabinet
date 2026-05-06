
"""Entry point for the Coding Club Arcade launcher."""

from pathlib import Path

from launcher.manager import ArcadeLauncher

def main() -> None:
    ArcadeLauncher(Path(__file__).resolve().parent).run()

if __name__ == "__main__":
    main()