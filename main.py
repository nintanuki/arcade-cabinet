
"""Entry point for the Coding Club Arcade launcher."""

import sys
from pathlib import Path

from launcher.manager import ArcadeLauncher

def main() -> None:
    # When frozen by PyInstaller, __file__ points inside the bundle's
    # temporary extraction dir, but assets and games ship next to the exe.
    # In that case anchor the launcher to the exe's folder instead.
    if getattr(sys, "frozen", False):
        root_dir = Path(sys.executable).resolve().parent
    else:
        root_dir = Path(__file__).resolve().parent
    ArcadeLauncher(root_dir).run()

if __name__ == "__main__":
    main()