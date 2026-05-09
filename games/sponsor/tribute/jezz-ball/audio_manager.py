"""Jezz Ball audio dispatcher.

Built on the portable AudioManager template: data-driven via
``AudioSettings.SOUND_EFFECTS`` and ``AudioSettings.MUSIC_TRACKS``,
single ``play(name)`` entry point, standard music API.

Jezz Ball-specific extensions:
- ``restart_music`` — alias for ``play_random_music`` kept for the
  existing call sites that expect "stop and restart from the top".
- ``shutdown`` — torn-down at process exit so the mixer device is
  released cleanly even when running standalone.
- The previous ``MUSIC_HALF_VOLUME_TOGGLE`` flag is folded into
  ``AudioSettings.MUSIC_VOLUME``; tweak that one number instead.
"""

import pygame
import random

from settings import AudioSettings


class AudioManager:
    """Data-driven music and sound-effect playback for Jezz Ball."""

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """Load every registered sound effect; music starts on first gameplay."""
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.enabled = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            return

        for name, path in AudioSettings.SOUND_EFFECTS.items():
            sound = self._load_sound(path)
            if sound is not None:
                sound.set_volume(AudioSettings.SFX_VOLUME)
                self.sounds[name] = sound

        self._last_music_track: str | None = None
        self._music_is_paused = False

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
        if not self.enabled or AudioSettings.MUTE:
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
        if not self.enabled or AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
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

    def restart_music(self) -> None:
        """Stop and restart background music; alias for ``play_random_music``."""
        self.stop_music()
        self.play_random_music()

    def stop_music(self) -> None:
        """Stop the current background track."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self._music_is_paused = False

    def pause_music(self) -> None:
        """Pause background music if anything is playing."""
        if not self.enabled or AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        pygame.mixer.music.pause()
        self._music_is_paused = True

    def resume_music(self) -> None:
        """Resume paused music, or start a new random track if nothing is queued."""
        if not self.enabled or AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
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

    def shutdown(self) -> None:
        """Stop all playback and close the mixer device for clean exit."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
