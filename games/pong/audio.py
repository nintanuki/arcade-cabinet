"""Audio loading and channel management for Pong."""

from pathlib import Path

from settings import *


ASSET_DIR = Path(__file__).resolve().parent

class Audio():
    """Hold and update all Pong audio assets and mixer channels."""

    def __init__(self):
        """Load sounds and reserve channels used by the game loop.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()
        self.master_volume = MASTER_VOLUME

        self.bg_music = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'pong_bg_music.ogg'))
        self.bg_music.set_volume(self.master_volume)
        self.channel_0 = pygame.mixer.Channel(0)
        # self.play_bg_music = True # Use this later to control when bg_music is played

        self.plob_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'pong.ogg'))
        self.plob_sound.set_volume(self.master_volume)
        self.channel_1 = pygame.mixer.Channel(1)

        self.score_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'score.ogg'))
        self.score_sound.set_volume(self.master_volume)
        self.channel_2 = pygame.mixer.Channel(2)

    # Use this later for volume control
    def update(self):
        """Apply current master volume to each loaded sound.

        Args:
            None.

        Returns:
            None.
        """
        # TODO(refactor): Iterate a list/tuple of sounds to avoid repeated volume lines.
        self.bg_music.set_volume(self.master_volume)
        self.plob_sound.set_volume(self.master_volume)
        self.score_sound.set_volume(self.master_volume)