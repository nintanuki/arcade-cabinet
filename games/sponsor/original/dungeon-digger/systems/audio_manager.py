"""Dungeon Digger audio dispatcher.

Built on the portable AudioManager template: data-driven via
``AudioSettings.SOUND_EFFECTS`` and ``AudioSettings.MUSIC_TRACKS``,
single ``play(name)`` entry point, standard music API. Dungeon Digger
also runs an opt-in "chase" music mode while a monster is hunting the
player, layered onto the template body as ``play_chase_music`` /
``play_normal_music``. The repellent SFX picks between the short/long
spray cue based on remaining cans (``play_repellent_sound``).
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
            if sound is None:
                continue
            volume = AudioSettings.SFX_VOLUME_OVERRIDES.get(
                name, AudioSettings.SFX_VOLUME
            )
            sound.set_volume(volume)
            self.sounds[name] = sound

        self._last_music_track: str | None = None
        self._music_is_paused = False
        # "normal" or "chase". Tracked separately so play_normal_music can
        # rotate through MUSIC_TRACKS instead of always replaying the same
        # song after a chase ends.
        self._music_mode = "normal"

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
            self._music_mode = "normal"
        except pygame.error as error:
            print(f"Could not load music track {track}: {error}")

    # Legacy alias kept for older call sites that still say play_random_bgm.
    play_random_bgm = play_random_music

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

    # ------------------------------------------------------------------
    # GAME-SPECIFIC EXTENSIONS
    # ------------------------------------------------------------------

    def play_chase_music(self) -> None:
        """Switch to battle music while a monster is chasing the player."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if self._music_mode == "chase":
            return
        track = getattr(AudioSettings, "CHASE_MUSIC", None)
        if not track:
            return
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
            pygame.mixer.music.play(loops=-1)
            self._music_is_paused = False
            self._music_mode = "chase"
        except pygame.error as error:
            print(f"Could not load chase music {track}: {error}")

    def play_normal_music(self) -> None:
        """Return to normal background music after a chase."""
        if self._music_mode == "normal":
            return
        self.play_random_music()

    def play_repellent_sound(self, cans_left: int) -> None:
        """Play the longer spray when repellent runs out, the short variant otherwise."""
        self.play("long_spray" if cans_left == 0 else "short_spray")
