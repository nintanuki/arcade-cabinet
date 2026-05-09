# Pong — Architecture

> **Maintenance rule:** every pass that meaningfully changes a system must update this document.

## 1. The shape of the program

```
                          +--------------+
                          |   main.py    |   (event loop, input routing, fullscreen)
                          +-----+--------+
                                |
                                v
                          +--------------+
                          | GameManager  |   (gameplay coordinator)
                          | (game.py)    |
                          +-----+--------+
                                |
   +--------+----------+--------+--------+
   |        |          |                 |
   v        v          v                 v
 Player  Opponent     Ball          AudioManager + CRT
 (sprites)(sprites)  (sprites)      (audio_manager.py / crt.py)
```

`main.py` owns the screen, clock, joystick list, and global controls (fullscreen, quit). `GameManager` owns sprite groups, score, AI logic, and the per-frame update / draw cycle. Sprites are simple `pygame.sprite.Sprite` subclasses.

## 2. Frame loop

`main.run()` (per frame): drain events → check quit combo → read paddle direction (D-pad → analog fallback → keyboard) → `GameManager.run(direction)` (updates sprites, handles collision, draws) → CRT pass → flip.

## 3. Input model

[main.py](../main.py) resolves paddle direction in priority order:

1. **D-pad** — `joystick.get_hat(0)` y-axis. Pygame reports y=1 up / y=-1 down; the paddle uses inverse so the helper flips it.
2. **Left analog stick** — `joystick.get_axis(LEFT_STICK_VERTICAL_AXIS)` clamped against `AXIS_DEADZONE = 0.15`.
3. **Keyboard** — `Up` / `Down` arrow keys.

The first non-zero source wins.

Globals: `F11` and the Back button toggle fullscreen. `Esc` or `Start + Back + L1 + R1` exits.

## 4. AI opponent

`Opponent` reads the ball position each frame and moves toward it, capped at the opponent paddle speed in [settings.py](../settings.py). There is no perceptual lag or imperfect tracking yet — at fast ball speeds the AI is essentially unbeatable; that's tracked as a roadmap item.

## 5. Audio

[audio_manager.py](../audio_manager.py) is a drop-in of the cabinet's portable AudioManager template. It is data-driven by `AudioSettings.SOUND_EFFECTS` and `AudioSettings.MUSIC_TRACKS` in [settings.py](../settings.py); call sites use `audio.play(name)` for SFX and the standard `play_random_music` / `pause_music` / `resume_music` / `stop_music` / `toggle_mute` API for music. Background music is muted by default (`MUTE_MUSIC = True`); flip the flag in `AudioSettings` to enable it.

## 6. CRT

[crt.py](../crt.py) draws scanlines + flicker as the last pass each frame.

## 7. Settings

[settings.py](../settings.py) defines the window size, paddle dimensions and speed, ball speed, score font, and asset paths. **No magic numbers in `main.py`, `game.py`, or `sprites.py`.**

## 8. Source tree

```
audio/, font/, graphics/   Asset folders
audio_manager.py           Portable AudioManager template
crt.py                     CRT overlay
game.py                    GameManager
main.py                    Entry point + event loop
settings.py                All tunables
sprites.py                 Player, Opponent, Ball
docs/                      ARCHITECTURE, TODO, TESTING, CHANGELOG
```
