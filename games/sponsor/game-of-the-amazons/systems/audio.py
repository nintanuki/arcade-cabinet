import pygame
from settings import *

class AudioManager:
    """Load, route, and play game music and sound effects across fixed channels."""
    
    CHANNEL_IDS = {
        'shoot': 0,
    }

    def __init__(self):
        """
        Initialize the audio manager and load all necessary sound effects.
        Uses fixed channels for important sounds to prevent them from being cut off by other effects.
        """

        pygame.mixer.set_num_channels(len(self.CHANNEL_IDS))

        self.shoot_sound = self._load_sound(AssetPaths.SHOOT_SOUND)

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
    
    def toggle_mute(self, resume_music: bool = True) -> bool:
        """Toggle global mute and return the new mute state."""
        AudioSettings.MUTE = not AudioSettings.MUTE

        if AudioSettings.MUTE:
            # Stop all currently playing SFX/music immediately.
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            return True
        
    SOUND_BINDINGS = {
        'shoot':           ('shoot',       'shoot_sound'),
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