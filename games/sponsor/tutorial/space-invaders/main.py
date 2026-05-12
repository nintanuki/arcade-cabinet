"""Space Invaders entry point.

The ``Game`` class owns the screen, sprite groups, audio, score, and the
main loop. Sub-classes (``Player``, ``Alien``, etc.) live in
[core/sprites.py](core/sprites.py); the CRT overlay lives in
[ui/crt.py](ui/crt.py); every tuning value lives in
[settings.py](settings.py).

Running ``python main.py`` from this folder must always work standalone.
"""

import os
import sys
from pathlib import Path
from random import choice, randint

import pygame

# Resolve relative asset paths from this game's folder so standalone runs
# (python main.py) and launcher runs behave the same regardless of cwd.
os.chdir(Path(__file__).resolve().parent)

from core.sprites import Alien, Block, Extra, Laser, Player
from settings import (
    AlienSettings,
    AssetPaths,
    AudioSettings,
    ColorSettings,
    ControllerSettings,
    ExtraSettings,
    FontSettings,
    LaserSettings,
    ObstacleSettings,
    PlayerSettings,
    ScreenSettings,
)
from ui.crt import CRT


# ---------------------------------------------------------------------------
# OPTIONAL ASSET LOADERS
# ---------------------------------------------------------------------------

def load_optional_sound(sound_path):
    """Load a sound file when present, returning ``None`` for missing assets.

    Args:
        sound_path (str | os.PathLike): Filesystem location of the candidate sound.

    Returns:
        pygame.mixer.Sound | None: Loaded sound, or ``None`` when unavailable.
    """
    try:
        if Path(sound_path).exists():
            return pygame.mixer.Sound(str(sound_path))
    except pygame.error:
        return None
    return None


# ---------------------------------------------------------------------------
# GAME
# ---------------------------------------------------------------------------

class Game:
    """Owns the display, sprite groups, audio, score, and the main loop."""

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------

    def __init__(self):
        """Initialize pygame, the display, audio, sprite groups, and timers."""
        pygame.init()
        pygame.joystick.init()
        self.joysticks = []
        self.refresh_joysticks()

        # pygame.SCALED keeps the playfield centered and uniformly scaled when
        # toggle_fullscreen() flips into fullscreen mode.
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
        pygame.display.set_caption('Space Invaders')
        self.clock = pygame.time.Clock()
        self.crt = CRT(self.screen)

        self.pause_font = pygame.font.Font(AssetPaths.PIXEL_FONT, FontSettings.PAUSE_SIZE)
        # Pause SFX are optional; loaders return None if the file is missing.
        self.pause_sound = load_optional_sound(AssetPaths.PAUSE_IN_SFX)
        self.unpause_sound = load_optional_sound(AssetPaths.PAUSE_OUT_SFX)

        # Custom event that fires the alien shooting cadence.
        self.alien_laser_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.alien_laser_event, AlienSettings.LASER_INTERVAL_MS)

        # Player
        player_sprite = Player(
            (ScreenSettings.WIDTH / 2, ScreenSettings.HEIGHT),
            ScreenSettings.WIDTH,
            PlayerSettings.SPEED,
        )
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # Health, score, and HUD font
        self.lives = PlayerSettings.LIVES
        self.live_surf = pygame.image.load(AssetPaths.PLAYER).convert_alpha()
        self.live_x_start_pos = (
            ScreenSettings.WIDTH
            - (self.live_surf.get_size()[0] * 2 + FontSettings.LIVES_RIGHT_PADDING)
        )
        self.score = 0
        self.font = pygame.font.Font(AssetPaths.PIXEL_FONT, FontSettings.SCORE_SIZE)

        # Obstacles
        self.shape = ObstacleSettings.SHAPE
        self.block_size = ObstacleSettings.BLOCK_SIZE
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = ObstacleSettings.AMOUNT
        self.obstacle_x_positions = [
            num * (ScreenSettings.WIDTH / self.obstacle_amount)
            for num in range(self.obstacle_amount)
        ]
        self.create_multiple_obstacles(
            *self.obstacle_x_positions,
            x_start=ScreenSettings.WIDTH / ObstacleSettings.X_START_DIVISOR,
            y_start=ObstacleSettings.Y_START,
        )

        # Aliens
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=AlienSettings.ROWS, cols=AlienSettings.COLS)
        self.alien_direction = 1

        # Extra (UFO)
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(*ExtraSettings.SPAWN_FRAMES_INITIAL)

        # Audio
        music = pygame.mixer.Sound(AssetPaths.MUSIC)
        music.set_volume(AudioSettings.MUSIC_VOLUME)
        music.play(loops=AudioSettings.MUSIC_LOOPS)
        self.laser_sound = pygame.mixer.Sound(AssetPaths.LASER_SFX)
        self.laser_sound.set_volume(AudioSettings.LASER_VOLUME)
        self.explosion_sound = pygame.mixer.Sound(AssetPaths.EXPLOSION_SFX)
        self.explosion_sound.set_volume(AudioSettings.EXPLOSION_VOLUME)

    # ------------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------------

    def close_game(self):
        """Shut down pygame and exit the process so the launcher reopens."""
        pygame.quit()
        sys.exit()

    def refresh_joysticks(self):
        """Rebuild the active joystick list to support controller hot-plugging."""
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            if not joystick.get_init():
                joystick.init()
            self.joysticks.append(joystick)

    def quit_combo_pressed(self):
        """Return True if the L1+R1+START+SELECT quit chord is held on any controller."""
        for joystick in self.joysticks:
            try:
                if all(joystick.get_button(b) for b in ControllerSettings.QUIT_COMBO):
                    return True
            except pygame.error:
                # Device may have disconnected between frames.
                continue
        return False

    # ------------------------------------------------------------------
    # SETUP HELPERS
    # ------------------------------------------------------------------

    def create_obstacle(self, x_start, y_start, offset_x):
        """Build one bunker by stamping ``Block`` sprites for every ``'x'``."""
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = Block(self.block_size, ColorSettings.OBSTACLE, x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        """Stamp a bunker at each x-offset to spread them across the screen."""
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols,
                    x_distance=AlienSettings.X_DISTANCE,
                    y_distance=AlienSettings.Y_DISTANCE,
                    x_offset=AlienSettings.X_OFFSET,
                    y_offset=AlienSettings.Y_OFFSET):
        """Populate the alien grid with row-based colors (yellow / green / red)."""
        for row_index in range(rows):
            for col_index in range(cols):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    # ------------------------------------------------------------------
    # ALIEN MOVEMENT / FIRE
    # ------------------------------------------------------------------

    def alien_position_checker(self):
        """Flip the wave direction and step down when an alien touches an edge."""
        for alien in self.aliens.sprites():
            if alien.rect.right >= ScreenSettings.WIDTH:
                self.alien_direction = -1
                self.alien_move_down(AlienSettings.DESCEND_DISTANCE)
                return
            if alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(AlienSettings.DESCEND_DISTANCE)
                return

    def alien_move_down(self, distance):
        """Drop every alien by ``distance`` pixels in a single step."""
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        """Spawn an alien-owned laser from a random alien's center."""
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(
                random_alien.rect.center,
                LaserSettings.ALIEN_SPEED,
                ScreenSettings.HEIGHT,
            )
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        """Count down to the next UFO spawn and respawn when the timer hits zero."""
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), ScreenSettings.WIDTH))
            self.extra_spawn_time = randint(*ExtraSettings.SPAWN_FRAMES_NEXT)

    # ------------------------------------------------------------------
    # COLLISIONS
    # ------------------------------------------------------------------

    def collision_checks(self):
        """Resolve every projectile / sprite collision for this frame."""
        # Player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += ExtraSettings.POINTS
                    laser.kill()

        # Alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.close_game()

        # Alien bodies eat obstacles and end the run on contact with the player.
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    self.close_game()

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def display_lives(self):
        """Draw the remaining lives as a row of player-ship icons."""
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (
                live * (self.live_surf.get_size()[0] + FontSettings.LIVES_SPACING)
            )
            self.screen.blit(self.live_surf, (x, FontSettings.LIVES_TOP_MARGIN))

    def display_score(self):
        """Draw the running score in the top-left corner of the screen."""
        score_surf = self.font.render(f'SCORE: {self.score}', False, ColorSettings.SCORE_TEXT)
        score_rect = score_surf.get_rect(topleft=FontSettings.SCORE_TOPLEFT)
        self.screen.blit(score_surf, score_rect)

    def victory_message(self):
        """Show ``YOU WON`` centered once every alien has been destroyed."""
        if not self.aliens.sprites():
            victory_surf = self.font.render('YOU WON', False, ColorSettings.VICTORY_TEXT)
            victory_rect = victory_surf.get_rect(
                center=(ScreenSettings.WIDTH / 2, ScreenSettings.HEIGHT / 2),
            )
            self.screen.blit(victory_surf, victory_rect)

    # ------------------------------------------------------------------
    # PAUSE
    # ------------------------------------------------------------------

    def render_pause_overlay(self):
        """Paint a translucent backdrop and a centered ``PAUSED`` label."""
        # The backdrop keeps the label readable over the alien field without
        # fully obscuring the frozen run state behind it.
        overlay = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)
        overlay.fill(ColorSettings.PAUSE_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.pause_font.render('PAUSED', False, ColorSettings.PAUSE_TEXT)
        pause_rect = pause_text.get_rect(
            center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2),
        )
        self.screen.blit(pause_text, pause_rect)

    def enter_pause(self):
        """Snapshot the current frame and block until the player resumes or quits.

        Capturing the frame here means alien movement, lasers, and obstacle
        blocks all keep their pre-pause state; the inner loop redraws the
        snapshot each tick instead of stepping the simulation.
        """
        frozen_frame = self.screen.copy()
        if self.pause_sound is not None:
            self.pause_sound.play()

        while True:
            if self.quit_combo_pressed():
                self.close_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game()
                if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    self.refresh_joysticks()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        self.close_game()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.unpause_sound is not None:
                            self.unpause_sound.play()
                        return
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == ControllerSettings.BACK_BUTTON:
                        pygame.display.toggle_fullscreen()
                    elif event.button == ControllerSettings.START_BUTTON:
                        if self.unpause_sound is not None:
                            self.unpause_sound.play()
                        return

            # Repaint the frozen frame each tick so the overlay survives
            # fullscreen transitions without advancing the simulation.
            self.screen.blit(frozen_frame, (0, 0))
            self.render_pause_overlay()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self):
        """Advance every sprite group and resolve collisions for the frame."""
        self.player.update()
        self.alien_lasers.update()
        self.extra.update()

        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()

    # ------------------------------------------------------------------
    # RENDER
    # ------------------------------------------------------------------

    def render(self):
        """Draw every sprite group, the HUD, and the CRT overlay."""
        self.player.sprite.lasers.draw(self.screen)
        self.player.draw(self.screen)
        self.blocks.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_lasers.draw(self.screen)
        self.extra.draw(self.screen)
        self.display_lives()
        self.display_score()
        self.victory_message()
        self.crt.draw()

    # ------------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------------

    def _process_events(self):
        """Drain pygame's event queue and dispatch each event by type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self.refresh_joysticks()
            if event.type == self.alien_laser_event:
                self.alien_shoot()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    self.close_game()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.enter_pause()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == ControllerSettings.BACK_BUTTON:
                    pygame.display.toggle_fullscreen()
                elif event.button == ControllerSettings.START_BUTTON:
                    self.enter_pause()

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self):
        """Main game loop: pump events, advance the world, render, repeat."""
        while True:
            if self.quit_combo_pressed():
                self.close_game()

            self._process_events()

            self.screen.fill(ColorSettings.BG_FILL)
            self.update()
            self.render()

            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)


if __name__ == '__main__':
    Game().run()
