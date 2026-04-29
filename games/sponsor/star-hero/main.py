import pygame
import sys
import time
import random

from settings import *
from core.animations import Background, Explosion
from core.sprites import Player, BombBlast
from ui.style import Style
from ui.crt import CRT
from systems.audio import Audio
from systems.managers import (
    CollisionManager,
    ScoreManager,
    SessionStateManager,
    SpawnDirector,
)


class GameManager:
    """Main game manager class"""
    def __init__(self):
        """Initializes the game, setting up display, audio, sprites, managers, and game state."""
        # Game setup
        pygame.init()

        # Controller setup
        pygame.joystick.init()
        # Keep joystick objects alive so button events remain reliable on all backends.
        self.joysticks = []
        self.refresh_joysticks()

        # Display setup
        self.screen = pygame.display.set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)
        pygame.display.set_caption('Star Hero')
        self.clock = pygame.time.Clock()

        # Show a temporary loading screen while audio files are being loaded in to prevent lag during gameplay
        # This part can't be handled in the style class since we need to load audio before we can use that
        self.screen.fill(ColorSettings.COLORS['BLACK'])
        loading_font = pygame.font.Font(FontSettings.FONT, FontSettings.MEDIUM)
        loading_text = loading_font.render("LOADING...", False, FontSettings.COLOR)
        loading_rect = loading_text.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()

        self.crt = CRT(self.screen)
        self.audio = Audio()
        self.style = Style(self.screen, self.audio)

        self.show_volume = False

        # Managers
        self.collisions = CollisionManager(self)
        self.scores = ScoreManager(self)
        self.session = SessionStateManager(self)
        self.spawner = SpawnDirector(self)

        # Player Health
        self.hearts = PlayerSettings.MAX_HEALTH
        self.heart_surf = pygame.image.load(AssetPaths.HEART).convert_alpha()
        self.heart_x_start_pos = ScreenSettings.WIDTH - (self.heart_surf.get_size()[0] * PlayerSettings.MAX_HEALTH + 30)

        # Background Setup
        self.background = pygame.sprite.Group()
        Background(self.background)

        # Player setup
        player_sprite = Player((ScreenSettings.CENTER), self.audio)
        self.player = pygame.sprite.GroupSingle(player_sprite)  # type: ignore[arg-type]
        self.player.sprite.bombs = BombSettings.START_COUNT

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()

        # Powerup setup
        self.powerups = pygame.sprite.Group()

        # Explosion setup
        self.exploding_sprites = pygame.sprite.Group()
        self.bomb_blasts = pygame.sprite.Group()

    def close_game(self):
        """Close the game process cleanly."""
        self.scores.save_scores()
        pygame.quit()
        sys.exit()

    def refresh_joysticks(self) -> None:
        """Rebuild the active joystick list to support controller hot-plugging."""
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            if not joystick.get_init():
                joystick.init()
            self.joysticks.append(joystick)

    def quit_combo_pressed(self):
        """
        Checks whether the quit combo (START + SELECT + L1 + R1) is held on any controller.

        Returns:
            bool: True if the combo is held, False otherwise.
        """
        if len(self.joysticks) != pygame.joystick.get_count():
            self.refresh_joysticks()

        required_buttons = (7, 6, 4, 5)
        for joystick in self.joysticks:
            try:
                if all(joystick.get_button(button) for button in required_buttons):
                    return True
            except pygame.error:
                # Device may have disconnected between frames.
                continue
        return False

    def _is_joystick_device_event(self, event_type: int) -> bool:
        """
        Checks whether the event type indicates a joystick connect or disconnect.

        Args:
            event_type (int): The pygame event type integer.

        Returns:
            bool: True if the event is a joystick add/remove event.
        """
        joystick_events = {
            getattr(pygame, 'JOYDEVICEADDED', None),
            getattr(pygame, 'JOYDEVICEREMOVED', None),
        }
        return event_type in joystick_events

    def _handle_joystick_hotplug(self, event: pygame.event.Event) -> bool:
        """
        Refreshes the joystick cache when a controller connect/disconnect event arrives.

        Args:
            event (pygame.event.Event): The event to inspect.

        Returns:
            bool: True if the event was a hotplug event and was handled.
        """
        if self._is_joystick_device_event(event.type):
            self.refresh_joysticks()
            return True
        return False

    def handle_alien_destroyed(self, alien) -> None:
        """
        Awards score, triggers explosion, and evaluates drops after an alien is destroyed.

        Args:
            alien (Alien): The alien that was destroyed.
        """
        self.scores.score += alien.value
        self.spawner.adjust_difficulty()
        self.explode(alien.rect.centerx, alien.rect.centery)
        self.spawner.try_spawn_alien_drop(alien)

    def trigger_bomb_blast(self, center: tuple[int, int]) -> None:
        """
        Spawns an expanding bomb blast orb at the given center position.

        Args:
            center (tuple[int, int]): The (x, y) origin of the blast.
        """
        self.bomb_blasts.add(BombBlast(center))

    def handle_bomb_input(self) -> None:
        """Launches a bomb on first press or detonates the active bomb on second press."""
        detonation_center = self.player.sprite.detonate_air_bomb()
        if detonation_center:
            self.trigger_bomb_blast(detonation_center)
            return

        self.player.sprite.launch_bomb()

    def explode(self, x_pos: int, y_pos: int) -> None:
        """
        Triggers an explosion animation at the given position and plays the sound effect.

        Args:
            x_pos (int): The x-coordinate of the explosion's center.
            y_pos (int): The y-coordinate of the explosion's center.
        """
        self.audio.channel_2.play(self.audio.explosion_sound)
        explosion = Explosion(x_pos, y_pos)
        self.exploding_sprites.add(explosion)
        explosion.explode()

    def display_hearts(self) -> None:
        """displays the heart icons on the top right"""
        for heart in range(self.hearts):
            # Step right by (icon width + spacing) for each successive heart.
            x = self.heart_x_start_pos + (heart * (self.heart_surf.get_size()[0] + UISettings.HEART_SPACING))
            self.screen.blit(self.heart_surf,(x,UISettings.HEART_TOP_MARGIN))

    def toggle_debug_mute(self) -> None:
        """Flips debug mute and immediately reapplies all audio volumes."""
        AudioSettings.DEBUG_MUTE = not AudioSettings.DEBUG_MUTE
        self.audio.update()

    def adjust_master_volume(self, delta: float, show_overlay: bool = False) -> None:
        """
        Adjusts master volume with clamping and optionally shows the HUD volume bar.

        Args:
            delta (float): Amount to add to the current volume (can be negative).
            show_overlay (bool): If True, displays the volume bar HUD.
        """
        self.audio.master_volume = max(0.0, min(1.0, self.audio.master_volume + delta))
        self.audio.update()

        if show_overlay:
            pygame.time.set_timer(self.spawner.volume_display_timer, UISettings.VOLUME_DISPLAY_TIME)
            self.show_volume = True

    def run(self) -> None:
        """Main game loop"""
        last_time = time.time() # Track time for delta_time calculations for smooth movement and animations regardless of frame rate
        while True:
            delta_time = time.time() - last_time
            last_time = time.time()

            if self.quit_combo_pressed():
                self.close_game()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game()

                if self._handle_joystick_hotplug(event):
                    continue

                # Controller input
                if event.type == pygame.JOYHATMOTION and not self.scores.entering_initials:
                    # event.value is (x, y). y=1 is Up, y=-1 is Down
                    if event.value[1] == 1:
                        self.adjust_master_volume(0.1, show_overlay=True)
                    elif event.value[1] == -1:
                        self.adjust_master_volume(-0.1, show_overlay=True)

                if event.type == pygame.JOYBUTTONDOWN:
                    if self.quit_combo_pressed():
                        self.close_game()

                    if event.button == 7:  # Button 7 is usually 'Start'
                        if self.session.game_active:
                            # Pause the game
                            self.audio.channel_0.pause()
                            self.audio.channel_1.pause()
                            self.audio.channel_6.play(self.audio.pause_sound)
                            self.session.pause()
                        else:
                            if not self.scores.entering_initials:
                                self.session.reset_for_new_game()

                    # Select Button (Toggle Fullscreen)
                    if event.button == 6:
                        pygame.display.toggle_fullscreen()

                    # B Button (Launch bomb / detonate active bomb)
                    if event.button == 1 and self.session.game_active:
                        self.handle_bomb_input()

                # Keyboard input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    if event.key == pygame.K_ESCAPE:
                        # ESC always exits the game and returns to the launcher,
                        # matching the L1+R1+START+SELECT controller combo.
                        self.close_game()
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.session.game_active:
                        # ENTER pauses an active run. The game-over branch below
                        # still maps RETURN to "play again" / submit-initials.
                        self.audio.channel_0.pause()
                        self.audio.channel_1.pause()
                        self.audio.channel_6.play(self.audio.pause_sound)
                        self.session.pause()
                    if event.key == pygame.K_m:
                        self.toggle_debug_mute()
                    if event.key == pygame.K_b and self.session.game_active:
                        self.handle_bomb_input()
                    if event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                        self.adjust_master_volume(0.1, show_overlay=True)
                    elif event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:
                        self.adjust_master_volume(-0.1, show_overlay=True)
                if event.type == self.spawner.volume_display_timer:
                    self.show_volume = False
                    pygame.time.set_timer(self.spawner.volume_display_timer, 0)

                # Game timers (alien spawn, alien shoot, player death delay)
                if self.session.game_active:
                    if event.type == self.spawner.alien_spawn_timer:
                        alien_color = random.choices(AlienSettings.COLOR, weights=AlienSettings.SPAWN_CHANCE)[0]
                        self.spawner.spawn_aliens(alien_color)
                    if event.type == self.spawner.alien_laser_timer:
                        self.spawner.alien_shoot()
                    if event.type == self.spawner.player_death_timer:
                        self.audio.player_down.play()
                        self.aliens.empty()
                        self.powerups.empty()

                        for bg in self.background.sprites():
                            bg.scroll_speed = ScreenSettings.DEFAULT_BG_SCROLL_SPEED

                        self.session.game_active = False
                        pygame.time.set_timer(self.spawner.player_death_timer, 0)
                        self.scores.finalize_game_over_score()
                else:
                    # --- KEYBOARD INPUTS FOR INITIALS ---
                    if event.type == pygame.KEYDOWN:
                        if self.scores.entering_initials:
                            if event.key == pygame.K_LEFT:
                                self.scores._move_initials_cursor(-1)
                            elif event.key == pygame.K_RIGHT:
                                self.scores._move_initials_cursor(1)
                            elif event.key == pygame.K_UP:
                                self.scores._cycle_initials_char(1)
                            elif event.key == pygame.K_DOWN:
                                self.scores._cycle_initials_char(-1)
                            elif event.key == pygame.K_RETURN:
                                self.scores.submit_initials()
                        else:
                            if event.key == pygame.K_RETURN:
                                self.session.reset_for_new_game()

                    # --- CONTROLLER INPUTS FOR INTIIALS ---
                    if self.scores.entering_initials:
                        # Handle D-Pad (Hat) movement
                        if event.type == pygame.JOYHATMOTION:
                            hat_x, hat_y = event.value

                            # Left/Right to change character index
                            if hat_x == -1: # D-pad Left
                                self.scores._move_initials_cursor(-1)
                            elif hat_x == 1: # D-pad Right
                                self.scores._move_initials_cursor(1)

                            # Up/Down to cycle through letters
                            if hat_y == 1: # D-pad Up
                                self.scores._cycle_initials_char(1)
                            elif hat_y == -1: # D-pad Down
                                self.scores._cycle_initials_char(-1)

                        # Handle Button Press (A button or Start)
                        if event.type == pygame.JOYBUTTONDOWN:
                            # Button 0 is usually 'A' (Xbox) or 'Cross' (PS), Button 7 is 'Start'
                            if event.button == 0 or event.button == 7:
                                self.scores.submit_initials()
                    else:
                        # If not entering initials, press Start (7) or A (0) to restart
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 0 or event.button == 7:
                                self.session.reset_for_new_game()

            # Drawing
            self.screen.fill(ScreenSettings.BG_COLOR)

            world_speed_multiplier = 1.0
            if self.session.game_active and self.player.sprite:
                world_speed_multiplier = self.player.sprite.get_world_speed_multiplier()

            self.background.update(delta_time, world_speed_multiplier)
            self.background.draw(self.screen)
            if self.show_volume:
                self.style.display_volume()

            # Game logic and drawing only happens if game is active, otherwise show intro or game over screen
            if self.session.game_active:
                self.audio.channel_0.stop()
                self.session.play_intro_music = False
                if not self.audio.channel_1.get_busy():
                    self.audio.load_random_bgm()
                    self.audio.channel_1.play(self.audio.bg_music)
                self.player.sprite.world_speed_multiplier = world_speed_multiplier
                if self.session.player_alive:
                    self.player.update()
                self.alien_lasers.update(world_speed_multiplier)
                self.aliens.update(world_speed_multiplier)
                self.powerups.update()
                self.bomb_blasts.update()
                self.collisions.update()
                self.display_hearts()

                self.player.sprite.lasers.draw(self.screen)
                self.player.sprite.bomb_projectiles.draw(self.screen)
                if self.session.player_alive:
                    self.player.draw(self.screen)
                    self.player.sprite.draw_shield_orb(self.screen)
                self.exploding_sprites.draw(self.screen)

                self.exploding_sprites.update(ExplosionSettings.ANIMATION_SPEED)

                # Draw blue alien confusion attack
                # 1. Track if ANY alien is currently confusing
                any_alien_confusing = False

                # 2. Draw blue alien confusion attack
                for alien in self.aliens:
                    if getattr(alien, 'is_confusing', False):
                        any_alien_confusing = True # Mark that at least one is attacking

                        if alien.confusion_growth < ScreenSettings.HEIGHT:
                            alien.confusion_growth += 15

                        # Draw a downward-expanding trapezoid for the confusion beam.
                        # The beam starts narrow at the alien's belly and fans out as it grows.
                        top_width = 10
                        bottom_width = top_width + (alien.confusion_growth * 0.2)  # widens by 20% of growth length

                        top_left  = (alien.rect.centerx - top_width // 2, alien.rect.bottom)
                        top_right = (alien.rect.centerx + top_width // 2, alien.rect.bottom)
                        bottom_right = (alien.rect.centerx + bottom_width // 2, alien.rect.bottom + alien.confusion_growth)
                        bottom_left  = (alien.rect.centerx - bottom_width // 2, alien.rect.bottom + alien.confusion_growth)
                        shape_points = [top_left, top_right, bottom_right, bottom_left]

                        field_surf = pygame.Surface((ScreenSettings.WIDTH, ScreenSettings.HEIGHT), pygame.SRCALPHA)
                        pygame.draw.polygon(field_surf, (200, 0, 255, 80), shape_points)
                        self.screen.blit(field_surf, (0, 0))

                        # Pixel-perfect overlap test: check if any non-transparent pixel
                        # of the beam overlaps the player's sprite mask.
                        beam_mask = pygame.mask.from_surface(field_surf, threshold=1)
                        offset = (self.player.sprite.rect.x, self.player.sprite.rect.y)

                        if beam_mask.overlap(self.player.sprite.mask, offset):
                            self.player.sprite.shield_active = False
                            if not self.player.sprite.confused:
                                self.player.sprite.confused = True
                                self.player.sprite.confusion_timer = pygame.time.get_ticks()

                # 3. Handle Audio outside the loop based on the collective state
                if any_alien_confusing:
                    # Tractor beam sound disabled (file deleted)
                    pass
                else:
                    # Only stop if the channel is actually busy and NO aliens are attacking
                    if self.audio.channel_9.get_busy():
                        self.audio.channel_9.stop()

                self.aliens.draw(self.screen)
                self.alien_lasers.draw(self.screen)
                self.powerups.draw(self.screen)
                self.bomb_blasts.draw(self.screen)

                self.style.update('game_active', self.scores.save_data, self.scores.score) # Display score and high score
                self.style.display_player_status(self.player.sprite) # Display player status info under hearts
            else:
                self.audio.channel_1.stop()
                self.audio.channel_9.stop()
                if self.session.play_intro_music:
                    if not self.audio.channel_0.get_busy():
                        self.audio.channel_0.play(self.audio.intro_music)

                # Show intro screen if score is 0, otherwise show game over screen
                if self.scores.score == 0:
                    self.style.update('intro', self.scores.save_data, self.scores.score)
                else:
                    self.style.update(
                        'game_over',
                        self.scores.save_data,
                        self.scores.score,
                        entering_initials=self.scores.entering_initials,
                        initials=self.scores.initials,
                        initials_index=self.scores.initials_index
                    )

            # Apply CRT filter and update display
            self.crt.draw()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

# Main execution
if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()
