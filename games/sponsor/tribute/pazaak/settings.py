class ColorSettings:
    """Pazaak's color settings."""

    BLACK_CURRANT = (8, 12, 24)
    WHITE_SMOKE = (240, 240, 240)
    GOLDEN_YELLOW = (255, 230, 0)

    BACKGROUND_COLOR = BLACK_CURRANT
    TEXT_COLOR = WHITE_SMOKE
    ACCENT_COLOR = GOLDEN_YELLOW

class ScreenSettings:
    """Pazaak's screen settings and input handling."""

    WIDTH = 1280
    HEIGHT = 720
    RESOLUTION = (WIDTH, HEIGHT)
    FPS = 60
    

class ControllerSettings:
    """Pazaak's input handling settings."""
    # L1, R1, SELECT, START -- the cabinet-wide return-to-launcher chord.
    QUIT_COMBO = (4, 5, 6, 7)

class AssetPaths:
    """Pazaak's asset paths."""
    TV = "assets/graphics/tv.png"