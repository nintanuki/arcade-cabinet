"""Shared HUD / menu rendering helpers.

Stub. The real implementation will own font caches, the volume bar
HUD, the pause overlay, and the title / game-over copy. Keeping it in
one place makes it easy to retheme the whole game later.
"""


class Style:
    """Front-end rendering surface shared between gameplay and menus."""

    def __init__(self, screen, audio) -> None:
        """Bind to the display surface and audio controller.

        Args:
            screen: The pygame display surface.
            audio: The Audio instance, used to read the master volume
                for the volume bar HUD.
        """
        self.screen = screen
        self.audio = audio

    def update(self, mode: str, save_data: dict, score: int, **kwargs) -> None:
        """Draw the appropriate HUD layer for the given mode.

        Args:
            mode: One of 'intro', 'game_active', 'game_over'. Future
                work will branch on this to render the right HUD layer.
            save_data: Persisted score data dict.
            score: Current run score.
            **kwargs: Mode-specific extras (e.g. initials entry state).
        """
        # TODO: branch on mode and render the appropriate HUD.
        _ = mode, save_data, score, kwargs

    def display_volume(self) -> None:
        """Render the volume bar overlay."""
        # TODO: draw a small bar showing self.audio.master_volume.
        pass
