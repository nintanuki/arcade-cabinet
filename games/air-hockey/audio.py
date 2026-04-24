"""Audio loading and channel management for Air Hockey."""

import pygame

class Audio():
    """Hold reusable sound effects, music, and mixer channels.

    This object centralizes all pygame mixer resources used by the game loop.
    """

    def __init__(self):
        """Initialize audio assets and assign dedicated playback channels.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()
        self.master_volume = 1 # default value is 1.0

        self.bg_music = pygame.mixer.Sound('audio/pong_bg_music.ogg')
        self.bg_music.set_volume(self.master_volume)
        self.channel_0 = pygame.mixer.Channel(0)
        # self.play_bg_music = True # Use this later to control when bg_music is played

        self.plob_sound = pygame.mixer.Sound('audio/pong.ogg')
        self.plob_sound.set_volume(self.master_volume)
        self.channel_1 = pygame.mixer.Channel(1)

        self.score_sound = pygame.mixer.Sound('audio/score.ogg')
        self.score_sound.set_volume(self.master_volume)
        self.channel_2 = pygame.mixer.Channel(2)
        
        self.pause_sound = pygame.mixer.Sound('audio/sfx_sounds_pause2_in.wav')
        self.pause_sound.set_volume(self.master_volume)
        self.channel_3 = pygame.mixer.Channel(3)

        self.unpause_sound = pygame.mixer.Sound('audio/sfx_sounds_pause2_out.wav')
        self.unpause_sound.set_volume(self.master_volume)
        self.channel_4 = pygame.mixer.Channel(4)

    # Use this later for volume control
    def update(self):
        """Apply the current master volume to every loaded sound.

        Args:
            None.

        Returns:
            None.
        """
        # TODO(refactor): Replace repeated set_volume calls with an iterable of sounds.
        self.bg_music.set_volume(self.master_volume)
        self.plob_sound.set_volume(self.master_volume)
        self.score_sound.set_volume(self.master_volume)
        self.pause_sound.set_volume(self.master_volume)
        self.unpause_sound.set_volume(self.master_volume)