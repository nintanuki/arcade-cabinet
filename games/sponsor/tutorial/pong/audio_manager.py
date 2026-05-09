"""Pong audio dispatcher.

Built on the portable AudioManager template: data-driven via
``AudioSettings.SOUND_EFFECTS`` and ``AudioSettings.MUSIC_TRACKS``,
single ``play(name)`` entry point, standard music API. Pause / unpause
SFX are wired through ``SOUND_EFFECTS`` instead of having dedicated
methods, and the previously-bare module-level ``MASTER_VOLUME`` knob
is now ``AudioSettings.MUSIC_VOLUME`` / ``SFX_VOLUME``.
"""

import pygame
import random

from settings import AudioSettings


class AudioManager:
    """Data-driven music and sound-effect playback.

    All sounds are declared in ``AudioSettings.SOUND_EFFECTS`` (logical name
    -> file path). Gameplay code triggers them through ``play(name)``.
    """

    def __init__(self):
        """Load every registered sound effect and start background music."""
        self.sounds: dict[str, pygame.mixer.Sound] = {}
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
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError) as error:
            print(f"Could not load sound {path}: {error}")
            return None

    # ------------------------------------------------------------------
    # SOUND EFFECTS
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        """Play one registered sound effect by logical name."""
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
            pygame.mixer.music.load(track)
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
        """Flip the global mute flag and apply the side effects."""
        AudioSettings.MUTE = not AudioSettings.MUTE

        if AudioSettings.MUTE:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            self._music_is_paused = False
            return True

        if resume_music and not AudioSettings.MUTE_MUSIC:
            self.play_random_music()
        return False
