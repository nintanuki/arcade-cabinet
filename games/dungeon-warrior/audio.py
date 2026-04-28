import pygame
import random
from settings import *

class AudioManager:
    """Load, route, and play game music and sound effects across fixed channels."""

    CHANNEL_IDS = {
        'movement': 0,
        'boundary': 1,
        'coin': 2,
        'menu_move': 3,
        'menu_select': 4,
    }

    def __init__(self):
        """
        Initialize the audio manager and load all necessary sound effects.
        Uses fixed channels for important sounds to prevent them from being cut off by other effects.
        """
        pygame.mixer.set_num_channels(len(self.CHANNEL_IDS))

        # Track last played song to avoid back-to-back repeats.
        self._last_bgm_track = None
        self._music_mode = "normal"

        self.play_random_bgm()

        self.move_sound = self._load_sound(AssetPaths.MOVE_SOUND)
        self.boundary_sound = self._load_sound(AssetPaths.BOUNDARY_SOUND)
        self.coin_sound = self._load_sound(AssetPaths.COIN_SOUND)
        self.coin_sound.set_volume(0.5)
        self.menu_move_sound = self._load_sound(AssetPaths.MENU_MOVE_SOUND)
        self.menu_select_sound = self._load_sound(AssetPaths.MENU_SELECT_SOUND)

        self.channels = {
            name: pygame.mixer.Channel(channel_id)
            for name, channel_id in self.CHANNEL_IDS.items()
        }

    def _load_sound(self, path: str) -> pygame.mixer.Sound:
        """Load one sound effect from disk.

        Args:
            path: File path to the sound asset.

        Returns:
            pygame.mixer.Sound: Loaded sound object.
        """
        return pygame.mixer.Sound(path)

    def play_random_bgm(self):
        """Selects a random track (avoiding the last played) and starts looping it."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return

        if not AssetPaths.MUSIC_TRACKS:
            print("Warning: No music tracks found in AssetPaths.MUSIC_TRACKS")
            return

        # Exclude the last played track so the same song never repeats back-to-back.
        available = [t for t in AssetPaths.NORMAL_MUSIC_TRACKS if t != self._last_bgm_track]
        if not available:
            available = AssetPaths.MUSIC_TRACKS
        track = random.choice(available)
        self._last_bgm_track = track

        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
            # Use loops=-1 for indefinite looping.
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            # Gracefully handle unsupported or missing audio assets.
            print(f"Could not load music track {track}: {e}")

    def play_chase_music(self) -> None:
        """Switch to battle music while a monster is chasing."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return

        if self._music_mode == "chase":
            return

        self._music_mode = "chase"
        pygame.mixer.music.load(AssetPaths.CHASE_MUSIC)
        pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1)


    def play_normal_music(self) -> None:
        """Return to normal background music."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return

        if self._music_mode == "normal":
            return

        self._music_mode = "normal"
        self.play_random_bgm()

    def stop_music(self) -> None:
        """Stop the currently playing background track."""
        pygame.mixer.music.stop()

    def toggle_mute(self, resume_music: bool = True) -> bool:
        """Toggle global mute and return the new mute state."""
        AudioSettings.MUTE = not AudioSettings.MUTE

        if AudioSettings.MUTE:
            # Stop all currently playing SFX/music immediately.
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            return True

        if resume_music and not AudioSettings.MUTE_MUSIC:
            self.play_random_bgm()

        return False
    
    # Logical SFX name -> (channel, attribute holding the loaded Sound).
    SOUND_BINDINGS = {
        'move':           ('movement',       'move_sound'),
        'boundary':       ('boundary',       'boundary_sound'),
        'coin':           ('coin',           'coin_sound'),
        'menu_move':      ('menu_move',      'menu_move_sound'),
        'menu_select':    ('menu_select',    'menu_select_sound'),
    }

    def play(self, name: str) -> None:
        """Play one named sound effect on its reserved channel.

        Args:
            name: A key in SOUND_BINDINGS (e.g. 'dig', 'coin', 'menu_move').
        """
        if AudioSettings.MUTE or DebugSettings.MUTE:
            return
        channel_name, sound_attr = self.SOUND_BINDINGS[name]
        self.channels[channel_name].play(getattr(self, sound_attr))