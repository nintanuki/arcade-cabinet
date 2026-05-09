"""Global configuration constants for Pong rendering, timing, and audio."""

import os

import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FRAMERATE = 120
MASTER_VOLUME = 0.5

# Colors
BG_COLOR = pygame.Color('#222222')
# ACCENT_COLOR = (27,35,43)
ACCENT_COLOR = (200,200,200)


class AudioSettings:
    """Global audio toggles, volumes, and the sound/music registry consumed by AudioManager."""

    BASE_DIR = os.path.dirname(__file__)
    AUDIO_DIR = os.path.join(BASE_DIR, 'audio')

    # Standard template contract.
    MUTE = False
    MUTE_MUSIC = True  # Pong's bg music is disabled by default; flip to False to enable.
    MUSIC_VOLUME = MASTER_VOLUME  # Background music volume in the range [0.0, 1.0].
    SFX_VOLUME = MASTER_VOLUME  # Sound effect volume in the range [0.0, 1.0].

    # Logical name -> filesystem path.
    SOUND_EFFECTS = {
        "plob": os.path.join(AUDIO_DIR, 'pong.ogg'),
        "score": os.path.join(AUDIO_DIR, 'score.ogg'),
        "pause": os.path.join(AUDIO_DIR, 'sfx_sounds_pause2_in.wav'),
        "unpause": os.path.join(AUDIO_DIR, 'sfx_sounds_pause2_out.wav'),
    }

    # Background tracks; one is chosen at random each time music starts.
    MUSIC_TRACKS = [
        os.path.join(AUDIO_DIR, 'pong_bg_music.ogg'),
    ]

# TODO(refactor): Group related constants into settings classes/dataclasses for structure.