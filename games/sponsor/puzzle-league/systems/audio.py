"""Audio subsystem.

Owns the pygame mixer setup, the master-volume knob, and the SFX/BGM
playback API. Right now this is a no-op stub so the rest of the game
can call ``audio.play(name)`` and ``audio.update()`` without crashing.
"""

import pygame

from settings import AudioSettings


class Audio:
    """Minimal audio controller.

    Future work will load every SFX in ``AssetPaths`` once at boot,
    cache them in ``self._sfx``, and expose ``play(name)`` to play
    them by short string id (e.g. ``'swap'``, ``'pop'``, ``'chain'``).
    """

    def __init__(self) -> None:
        """Initialize the mixer if available and record the default volume."""
        # mixer.init() can fail on systems with no audio device. Catch
        # that here so the game still launches in silent mode.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            pass

        self.master_volume = AudioSettings.DEFAULT_MASTER_VOLUME
        self._sfx: dict[str, pygame.mixer.Sound] = {}

    # -------------------------
    # PUBLIC API
    # -------------------------

    def play(self, name: str) -> None:
        """Play a previously-loaded SFX by name. No-op if missing."""
        # TODO: look up self._sfx[name] and call .play() once SFX are
        # loaded during __init__.
        _ = name

    def update(self) -> None:
        """Reapply the current master volume to every loaded sound."""
        # TODO: walk self._sfx and the music channel, multiplying each
        # by self.master_volume * (0 if AudioSettings.DEBUG_MUTE else 1).
        pass

    def pause_music(self) -> None:
        """Pause whatever BGM track is currently playing."""
        # TODO: pygame.mixer.music.pause() once a playlist is wired up.
        pass

    def ensure_bgm_playing(self) -> None:
        """Start the next BGM track if nothing is currently playing."""
        # TODO: drive a simple round-robin over AudioSettings.BGM_PLAYLIST.
        pass

    def stop_bgm(self) -> None:
        """Stop the BGM channel entirely."""
        # TODO: pygame.mixer.music.stop() once a playlist is wired up.
        pass
