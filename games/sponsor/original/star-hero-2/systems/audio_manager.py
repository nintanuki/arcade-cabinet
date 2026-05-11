"""Star Hero audio dispatcher.

Star Hero needs more than the bare-bones AudioManager template: there's
a separate intro track, a game-over track, a low-health alarm that
must play on a reserved channel so other SFX don't cut it off, and a
runtime-tunable master volume that the volume HUD reads. The shape of
this module is deliberately aligned with the portable template:

* Data-driven SFX loading via ``AudioSettings.SOUND_EFFECTS``.
* Single ``play(name)`` entry point for one-shot effects.
* Standard music API (``play_random_music``, ``pause_music``,
  ``resume_music``, ``stop_music``, ``toggle_mute``) sitting on top of
  ``pygame.mixer.music`` for the gameplay BGM.
* Game-specific extensions (intro music, game-over music, alarm
  channel, master-volume HUD) layered on below the template body so
  they're easy to spot as additions rather than core machinery.
"""

import os
import random

import pygame

from settings import AudioSettings


# Dedicated channels that must never be stomped by an unrelated one-shot.
_ALARM_CHANNEL_INDEX = 7
_INTRO_CHANNEL_INDEX = 6


class AudioManager:
    """Data-driven music and sound-effect playback with Star Hero extensions."""

    def __init__(self) -> None:
        """Load every registered sound effect and start background music.

        A loading screen should be shown before constructing this object;
        pre-loading the BGM list freezes the UI thread briefly on slower
        hardware.
        """
        # Reserve the channels Star Hero needs for cues that can't be cut off.
        pygame.mixer.set_num_channels(max(_ALARM_CHANNEL_INDEX, _INTRO_CHANNEL_INDEX) + 1)
        self._alarm_channel = pygame.mixer.Channel(_ALARM_CHANNEL_INDEX)
        self._intro_channel = pygame.mixer.Channel(_INTRO_CHANNEL_INDEX)

        # Volume bar HUD edits this at runtime; calling update() reapplies
        # it to every loaded asset.
        self.master_volume: float = AudioSettings.DEFAULT_MASTER_VOLUME

        # SFX (one-shots) — the template-style data-driven block.
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        for name, path in AudioSettings.SOUND_EFFECTS.items():
            sound = self._load_sound(path)
            if sound is not None:
                self.sounds[name] = sound

        # Pre-loaded music tracks. They live on dedicated channels so the
        # intro track can pause/resume independently of gameplay BGM.
        self._intro_music = self._load_sound(AudioSettings.INTRO_MUSIC)
        self._game_over_music = self._load_sound(AudioSettings.GAME_OVER_MUSIC)
        self._bgm_tracks: list[pygame.mixer.Sound] = []
        for path in AudioSettings.MUSIC_TRACKS:
            sound = self._load_sound(path)
            if sound is not None:
                self._bgm_tracks.append(sound)

        # Bookkeeping.
        self._current_bgm: pygame.mixer.Sound | None = None
        self._last_bgm: pygame.mixer.Sound | None = None
        self._music_is_paused = False

        # Apply the initial master volume across every loaded asset.
        self.update()

    # ------------------------------------------------------------------
    # ASSET LOADING
    # ------------------------------------------------------------------

    def _load_sound(self, path: str | None) -> pygame.mixer.Sound | None:
        """Load one sound from disk; return None if the asset or mixer is missing."""
        if not path:
            return None
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
        """Pick a random BGM track (avoiding the last one) and play it."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if not self._bgm_tracks:
            return

        choices = self._bgm_tracks
        if self._last_bgm is not None and len(self._bgm_tracks) > 1:
            choices = [t for t in self._bgm_tracks if t is not self._last_bgm]
        track = random.choice(choices)
        self._last_bgm = track
        self._current_bgm = track

        # Sound-based playback (rather than pygame.mixer.music) so the BGM
        # channel can pause independently of intro/SFX channels.
        track.play()
        self._music_is_paused = False

    def stop_music(self) -> None:
        """Stop the current BGM track."""
        if self._current_bgm is not None:
            self._current_bgm.stop()
        self._music_is_paused = False

    def pause_music(self) -> None:
        """Pause every music channel (used when the player pauses the game)."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        # Channels 0..N each get paused; pygame.mixer.pause is global, so
        # we pause specific known channels to keep alarms playing.
        self._intro_channel.pause()
        if self._current_bgm is not None:
            for channel_index in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(channel_index)
                if channel.get_sound() is self._current_bgm:
                    channel.pause()
        self._music_is_paused = True

    def resume_music(self) -> None:
        """Resume music channels paused by ``pause_music``."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        self._intro_channel.unpause()
        if self._current_bgm is not None:
            for channel_index in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(channel_index)
                if channel.get_sound() is self._current_bgm:
                    channel.unpause()
        self._music_is_paused = False

    # ------------------------------------------------------------------
    # GLOBAL CONTROLS
    # ------------------------------------------------------------------

    def toggle_mute(self, resume_music: bool = True) -> bool:
        """Flip the global mute flag and apply the side effects."""
        AudioSettings.MUTE = not AudioSettings.MUTE

        if AudioSettings.MUTE:
            pygame.mixer.stop()
            self._music_is_paused = False
            return True

        if resume_music and not AudioSettings.MUTE_MUSIC:
            self.play_random_music()
        return False

    def update(self) -> None:
        """Reapply ``master_volume`` to every loaded asset.

        Star Hero exposes ``master_volume`` as a slider the player can
        nudge with the D-pad / volume keys. SFX mix at half the music
        volume so the score-up jingle never drowns out the music.
        """
        music_vol = 0 if AudioSettings.MUTE else self.master_volume
        sfx_vol = music_vol / 2

        if self._intro_music is not None:
            self._intro_music.set_volume(music_vol * AudioSettings.INTRO_VOL_BOOST)
        if self._game_over_music is not None:
            self._game_over_music.set_volume(music_vol)
        for track in self._bgm_tracks:
            track.set_volume(music_vol)
        for sound in self.sounds.values():
            sound.set_volume(sfx_vol)

    # ------------------------------------------------------------------
    # GAME-SPECIFIC EXTENSIONS
    # ------------------------------------------------------------------

    def play_intro_music(self) -> None:
        """Start looping intro music if it isn't already playing."""
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if self._intro_music is None or self._intro_channel.get_busy():
            return
        self._intro_channel.play(self._intro_music, loops=-1)

    def stop_intro_music(self) -> None:
        """Halt intro music immediately."""
        self._intro_channel.stop()

    def ensure_bgm_playing(self) -> None:
        """Start a randomly-picked BGM track if no BGM is currently playing.

        Replaces the standard ``play_random_music`` side-effect that always
        restarts. Used by the per-frame music driver in main.py.
        """
        if AudioSettings.MUTE or AudioSettings.MUTE_MUSIC:
            return
        if self._current_bgm is not None:
            for channel_index in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(channel_index)
                if channel.get_sound() is self._current_bgm and channel.get_busy():
                    return
        self.play_random_music()

    def stop_bgm(self) -> None:
        """Halt the gameplay BGM channel; alias of stop_music."""
        self.stop_music()

    def play_game_over_music(self) -> None:
        """Swap the gameplay-music channel to the game-over track."""
        if self._game_over_music is None:
            return
        self.stop_bgm()
        self._game_over_music.play()
        self._current_bgm = self._game_over_music

    @property
    def player_down(self) -> pygame.mixer.Sound | None:
        """Compatibility shim for ``self.audio.player_down.play()`` call sites."""
        return self._game_over_music

    def play_alarm(self, name: str) -> None:
        """Play an alarm SFX on the reserved alarm channel so it can't be cut off."""
        if AudioSettings.MUTE:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        self._alarm_channel.play(sound)

    def stop_alarms(self) -> None:
        """Stop the low-health alarm channel; safe to call when not playing."""
        self._alarm_channel.stop()
