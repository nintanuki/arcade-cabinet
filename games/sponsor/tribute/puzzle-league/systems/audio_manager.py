"""Puzzle League audio dispatcher.

Drop-in of the cabinet's portable AudioManager template: data-driven via
``AudioSettings.SOUND_EFFECTS`` and ``AudioSettings.MUSIC_TRACKS``,
single ``play(name)`` entry point, standard music API.
"""

import pygame
import random

from settings import AudioSettings


class AudioManager:
    """Data-driven music and sound-effect playback for Puzzle League."""

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """Load every registered sound effect and start background music."""
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            pass

        for name, path in AudioSettings.SOUND_EFFECTS.items():
            sound = self._load_sound(path)
            if sound is not None:
                sound.set_volume(AudioSettings.SFX_VOLUME)
                self.sounds[name] = sound

        self._last_music_track: str | None = None
        self._music_is_paused = False

        self.play_random_music()

    def _load_sound(self, path: str) -> pygame.mixer.Sound | None:
        """Load one sound from disk; return None if the asset or mixer is missing."""
        try:
            return pygame.mixer.Sound(str(path))
        except (pygame.error, FileNotFoundError) as error:
            print(f"Could not load sound {path}: {error}")
            return None

    # ------------------------------------------------------------------
    # SOUND EFFECTS
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        """Play one registered sound effect by logical name.

        Args:
            name: Key from ``AudioSettings.SOUND_EFFECTS``.
        """
        if AudioSettings.MUTE:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.play()

    # ------------------------------------------------------------------
    # MUSIC
    # ------------------------------------------------------------------

    def play_random_music(self) -> None:
        """Pick a random track (avoiding the last one) and loop it indefinitely."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if not AudioSettings.MUSIC_TRACKS:
            return

        available = [t for t in AudioSettings.MUSIC_TRACKS if t != self._last_music_track]
        if not available:
            available = AudioSettings.MUSIC_TRACKS
        track = random.choice(available)
        self._last_music_track = track

        try:
            pygame.mixer.music.load(str(track))
            pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
            pygame.mixer.music.play(loops=-1)
            self._music_is_paused = False
        except pygame.error as error:
            print(f"Could not load music track {track}: {error}")

    def stop_music(self) -> None:
        """Stop the current background track."""
        pygame.mixer.music.stop()
        self._music_is_paused = False

    def pause_music(self) -> None:
        """Pause background music if anything is playing."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        pygame.mixer.music.pause()
        self._music_is_paused = True

    def resume_music(self) -> None:
        """Resume paused music, or start a new random track if nothing is queued."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if self._music_is_paused:
            pygame.mixer.music.unpause()
            self._music_is_paused = False
            return
        self.play_random_music()

    # ------------------------------------------------------------------
    # GLOBAL CONTROLS
    # ------------------------------------------------------------------

    def toggle_mute(self, resume_music: bool = True) -> bool:
        """Flip the global mute flag and apply the side effects.

        Args:
            resume_music: When unmuting, whether to restart background music.

        Returns:
            bool: The new mute state (True = muted).
        """
        AudioSettings.MUTE = not AudioSettings.MUTE

        if AudioSettings.MUTE:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            self._music_is_paused = False
            return True

        if resume_music and not AudioSettings.MUTE_MUSIC:
            self.play_random_music()
        return False
