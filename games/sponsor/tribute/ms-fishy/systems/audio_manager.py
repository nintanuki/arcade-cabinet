import pygame
import random

from settings import AudioSettings


class AudioManager:
    """Data-driven music and sound-effect playback.

    All sounds are declared in ``AudioSettings.SOUND_EFFECTS`` (logical name ->
    file path). Gameplay code triggers them through a single entry point,
    ``play(name)``. Adding a new sound is one line in settings; no changes to
    this class are required.
    """

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------

    def __init__(self):
        """Load every registered sound effect and initialize music state."""
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        for name, path in AudioSettings.SOUND_EFFECTS.items():
            sound = self._load_sound(path)
            if sound is not None:
                sound.set_volume(self._get_sfx_volume(name))
                self.sounds[name] = sound

        # Track last played track so the same song never repeats back-to-back.
        self._last_music_track: str | None = None
        self._music_is_paused = False

        # Music starts when gameplay enters PlayScene.

    def _load_sound(self, path: str) -> pygame.mixer.Sound | None:
        """Load one sound from disk; return None if the asset or mixer is missing.

        Args:
            path: File path to the sound asset.

        Returns:
            pygame.mixer.Sound | None: Loaded sound, or None on failure.
        """
        try:
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError) as error:
            print(f"Could not load sound {path}: {error}")
            return None

    # ------------------------------------------------------------------
    # SOUND EFFECTS
    # ------------------------------------------------------------------

    def _clamp_volume(self, volume: float) -> float:
        """Clamp a volume scalar to pygame's supported range [0.0, 1.0]."""
        return max(0.0, min(1.0, volume))

    def _get_sfx_volume(self, name: str) -> float:
        """Compute effective SFX volume using global and per-sound toggles."""
        per_sound = AudioSettings.SOUND_EFFECT_VOLUMES.get(name, 1.0)
        return self._clamp_volume(AudioSettings.SFX_VOLUME * per_sound)

    def _get_music_volume(self) -> float:
        """Compute effective music volume using base level and toggle."""
        return self._clamp_volume(AudioSettings.MUSIC_VOLUME * AudioSettings.MUSIC_VOLUME_TOGGLE)

    def play(self, name: str) -> None:
        """Play one registered sound effect by logical name.

        Pygame auto-allocates a free channel from its default pool, so casual
        SFX never need bespoke channel bookkeeping.

        Args:
            name: Key from ``AudioSettings.SOUND_EFFECTS``.
        """
        if AudioSettings.MUTE:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.set_volume(self._get_sfx_volume(name))
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
            pygame.mixer.music.set_volume(self._get_music_volume())
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
        pygame.mixer.music.set_volume(self._get_music_volume())
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
