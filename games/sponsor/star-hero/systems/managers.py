import os
import json
import random
import pygame

from settings import *
from core.sprites import Laser, Alien, PowerUp


class CollisionManager:
    """Handles all collision logic in one place"""
    def __init__(self, game):
        """
        Initializes the CollisionManager with a reference to the main game object.

        Args:
            game (GameManager): The main game manager instance.
        """
        self.game = game

    def _player_lasers(self):
        """Checks for collisions between player lasers and aliens"""
        if not self.game.player.sprite.lasers: return
        for laser in self.game.player.sprite.lasers:
            aliens_hit = pygame.sprite.spritecollide(laser, self.game.aliens, True)
            if aliens_hit:
                # Laser only dies if it is NOT piercing
                if not laser.is_piercing:
                    laser.kill()

                for alien in aliens_hit:
                    self.game.handle_alien_destroyed(alien)

    def _player_bombs(self):
        """Checks collisions for active bomb projectiles and starts bomb blasts on impact."""
        player = self.game.player.sprite
        for bomb in player.bomb_projectiles.sprites():
            aliens_hit = pygame.sprite.spritecollide(bomb, self.game.aliens, True)
            if not aliens_hit:
                continue

            for alien in aliens_hit:
                self.game.handle_alien_destroyed(alien)

            blast_center = bomb.rect.center
            bomb.kill()
            self.game.trigger_bomb_blast(blast_center)

    def _bomb_blasts(self):
        """Applies bomb blast damage to aliens in the expanding area."""
        for blast in self.game.bomb_blasts:
            nearby_aliens = pygame.sprite.spritecollide(blast, self.game.aliens, False)
            for alien in nearby_aliens:
                if id(alien) in blast.hit_aliens:
                    continue

                dx = alien.rect.centerx - blast.center[0]
                dy = alien.rect.centery - blast.center[1]
                # Compare squared distances to avoid a costly sqrt call.
                # Equivalent to: distance(alien, blast_center) <= blast.radius
                if (dx * dx) + (dy * dy) <= (blast.radius * blast.radius):
                    blast.hit_aliens.add(id(alien))
                    alien.kill()
                    self.game.handle_alien_destroyed(alien)

    def _alien_lasers(self):
        """Checks for collisions between alien lasers and the player"""
        player = self.game.player.sprite
        for laser in self.game.alien_lasers:
            if pygame.sprite.spritecollide(laser, self.game.player, False):
                laser.kill() # Lasers always stop on player contact.
                if not player.is_invulnerable():
                    self.game.session.player_damage()

    def _ship_collisions(self):
        """Checks for collisions between the player's ship and aliens"""
        # Damage player if their ship collides with an alien
        aliens_crash = pygame.sprite.spritecollide(self.game.player.sprite, self.game.aliens, True)
        for alien in aliens_crash:
            self.game.scores.score += alien.value
            if self.game.hearts > 1:
                self.game.explode(alien.rect.centerx, alien.rect.centery)
        if aliens_crash and not self.game.player.sprite.is_invulnerable():
            self.game.session.player_damage()

    def _powerups(self):
        """Checks for collisions between player and powerups, applying effects and playing sounds as necessary"""
        powerups_collected = pygame.sprite.spritecollide(self.game.player.sprite, self.game.powerups, True)
        for powerup in powerups_collected:
            if powerup.powerup_type == 'heal' and self.game.hearts < PlayerSettings.MAX_HEALTH: # Only heal if player isn't at full health
                self.game.audio.channel_8.play(self.game.audio.powerup_heart)
                self.game.hearts += 1
            else:
                # Only play sound if it's a new powerup activation, not if player already has it active
                if powerup.powerup_type == 'laser_upgrade':
                    if self.game.player.sprite.laser_level < 4:
                        self.game.audio.channel_8.play(self.game.audio.powerup_twin)
                elif powerup.powerup_type in ['rapid_fire', 'rainbow_beam', 'shield', 'bomb']:
                    self.game.audio.channel_8.play(self.game.audio.powerup_weapon)

                self.game.player.sprite.activate_powerup(powerup)

    def update(self):
        """Checks all collisions"""
        self._player_lasers()
        self._player_bombs()
        self._bomb_blasts()
        self._alien_lasers()
        self._ship_collisions()
        self._powerups()


class ScoreManager:
    """
    Manages score, high score, leaderboard I/O, and initials entry state.

    Args:
        game (GameManager): The main game manager instance, used for accessing score and saving data.
    """
    def __init__(self, game):
        self.game = game
        self.score = 0
        self.save_data = {
            'high_score': 0,
            'leaderboard': []
        }

        # Leaderboard / initials entry state
        self.entering_initials = False
        self.initials = FontSettings.DEFAULT_INITIALS
        self.initials_index = 0
        self.pending_score = None
        self.score_processed = False

        # Load saved high score and leaderboard data if available.
        # AssetPaths.BASE_DIR keeps the save anchored to the game root rather
        # than this module's folder, so the file does not move when this code
        # is relocated under systems/.
        try:
            score_file_path = os.path.join(AssetPaths.BASE_DIR, 'high_score.txt')
            with open(score_file_path) as high_score_file:
                self.save_data = json.load(high_score_file)
        except (OSError, json.JSONDecodeError):
            print('No file created yet')

    def reset(self) -> None:
        """Resets score and initials entry state for a new game."""
        self.score = 0
        self.entering_initials = False
        self.initials = FontSettings.DEFAULT_INITIALS
        self.initials_index = 0
        self.pending_score = None
        self.score_processed = False

    def _sort_and_trim_leaderboard(self) -> None:
        """Sorts the leaderboard and keeps only the top 10 scores, also updates high score."""
        # Sort descending by score and keep only the top 10 entries.
        self.save_data['leaderboard'] = sorted(
            self.save_data.get('leaderboard', []),
            key=lambda entry: entry['score'],
            reverse=True
        )[:10]

        if self.save_data['leaderboard']:
            self.save_data['high_score'] = self.save_data['leaderboard'][0]['score']
        else:
            self.save_data['high_score'] = 0

    def save_scores(self) -> None:
        """Saves the current leaderboard and high score to a file."""
        self._sort_and_trim_leaderboard()
        score_file_path = os.path.join(AssetPaths.BASE_DIR, 'high_score.txt')
        with open(score_file_path, 'w') as high_score_file:
            json.dump(self.save_data, high_score_file)

    def qualifies_for_leaderboard(self, score: int) -> bool:
        """
        Checks if the given score qualifies for the leaderboard.

        Args:
            score (int): The player's final score to check.

        Returns:
            bool: True if the score earns a leaderboard spot, False otherwise.
        """
        leaderboard = self.save_data.get('leaderboard', [])
        if len(leaderboard) < 10:
            return score > 0
        return score > leaderboard[-1]['score']

    def start_initial_entry(self) -> None:
        """Initiates the process of entering initials for a new high score."""
        self.entering_initials = True
        self.initials = FontSettings.DEFAULT_INITIALS
        self.initials_index = 0
        self.pending_score = self.score

    def submit_initials(self) -> None:
        """Submits the entered initials and score to the leaderboard."""
        leaderboard = self.save_data.get('leaderboard', [])
        # If this name already exists on the board, update it only if the new score is higher.
        # Otherwise add a fresh entry so duplicate names don't bloat the leaderboard.
        existing_entry = next((item for item in leaderboard if item["name"] == self.initials), None)

        if existing_entry:
            if self.pending_score > existing_entry['score']:
                existing_entry['score'] = self.pending_score
        else:
            leaderboard.append({'name': self.initials, 'score': self.pending_score})

        self.save_data['leaderboard'] = leaderboard
        self._sort_and_trim_leaderboard()
        self.save_scores()

        self.entering_initials = False
        self.pending_score = None
        self.score_processed = True

    def finalize_game_over_score(self) -> None:
        """Checks if the score qualifies for the leaderboard and starts initials entry or saves directly."""
        if self.score_processed:
            return
        if self.qualifies_for_leaderboard(self.score):
            self.start_initial_entry()
        else:
            self._sort_and_trim_leaderboard()
            self.save_scores()
            self.score_processed = True

    def _move_initials_cursor(self, step: int) -> None:
        """
        Move initials cursor left/right and clamp to valid range.

        Args:
            step (int): Direction to move (-1 for left, 1 for right).
        """
        self.initials_index = max(0, min(2, self.initials_index + step))

    def _cycle_initials_char(self, step: int) -> None:
        """
        Rotate the selected initials character by one alphabet step.

        Args:
            step (int): Direction to cycle (1 for forward, -1 for backward).
        """
        chars = list(self.initials)
        current = chars[self.initials_index]
        # Use ord/chr arithmetic to step through ASCII letters, wrapping Z→A and A→Z.
        if step > 0:
            chars[self.initials_index] = 'A' if current == 'Z' else chr(ord(current) + 1)
        else:
            chars[self.initials_index] = 'Z' if current == 'A' else chr(ord(current) - 1)
        self.initials = ''.join(chars)


class SessionStateManager:
    """Manages game session state: active/paused/player-alive flags, run resets, pause, and player damage."""
    def __init__(self, game):
        self.game = game
        self.game_active = False
        self.paused = False
        self.player_alive = True
        self.play_intro_music = True

    def reset_for_new_game(self) -> None:
        """Resets all necessary game state to start a new game."""
        game = self.game
        game.scores.reset()
        game.hearts = PlayerSettings.MAX_HEALTH
        self.player_alive = True
        self.game_active = True

        # Reset player position
        game.player.sprite.rect.center = ScreenSettings.CENTER

        # Clear all sprite groups from previous run
        game.aliens.empty()
        game.alien_lasers.empty()
        game.powerups.empty()
        game.exploding_sprites.empty()
        game.bomb_blasts.empty()
        game.player.sprite.lasers.empty()
        game.player.sprite.bomb_projectiles.empty()

        # Reset player state
        player = game.player.sprite
        player.ready = True
        player.laser_time = 0
        player.laser_cooldown = PlayerSettings.DEFAULT_LASER_COOLDOWN
        player.laser_level = 1
        player.rapid_fire_level = 0
        player.rainbow_beam_active = False
        player.rainbow_beam_start_time = 0
        player.shield_active = False
        player.shield_start_time = 0
        player.bombs = BombSettings.START_COUNT

        player.boost_meter = 1.0
        player.boost_active = False
        player.brake_active = False
        player.boost_locked_until_full = False
        player.world_speed_multiplier = 1.0

        player.confused = False
        player.confusion_timer = 0

        player.is_flashing = False
        player.flash_timer = 0
        player.last_flash_time = 0
        player.is_red = False
        player.image = player.original_image.copy()

        # Reset background speed
        for bg in game.background.sprites():
            bg.scroll_speed = ScreenSettings.DEFAULT_BG_SCROLL_SPEED

        # Stop any lingering audio/effects from previous game
        game.audio.channel_4.stop()  # low health alarms
        game.audio.channel_9.stop()  # tractor beam if active

        # Make sure death timer isn't still hanging around
        pygame.time.set_timer(game.spawner.player_death_timer, 0)

    def pause(self) -> None:
        """Pauses game when ESC or START is pressed."""
        game = self.game
        self.paused = not self.paused
        # Stop confusion-beam loop while paused to prevent lingering audio.
        game.audio.channel_9.stop()
        while self.paused:
            if game.quit_combo_pressed():
                game.close_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.close_game()

                if game._handle_joystick_hotplug(event):
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    if event.key == pygame.K_ESCAPE:
                        # ESC always exits the game and returns to the launcher,
                        # matching the L1+R1+START+SELECT controller combo.
                        game.close_game()
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.unpause_game()
                    if event.key == pygame.K_m:
                        game.toggle_debug_mute()

                if event.type == pygame.JOYBUTTONDOWN:
                    if game.quit_combo_pressed():
                        game.close_game()
                    if event.button == 7:
                        self.unpause_game()
                    if event.button == 6:
                        pygame.display.toggle_fullscreen()
                    # if event.button == 4:
                    #     game.adjust_master_volume(-0.1, show_overlay=True)
                    # if event.button == 5:
                    #     game.adjust_master_volume(0.1, show_overlay=True)

            game.screen.fill((0, 0, 0))
            game.style.update('pause', game.scores.save_data, game.scores.score)
            pygame.display.update()

    def unpause_game(self) -> None:
        """Handles unpausing logic."""
        game = self.game
        game.audio.channel_0.unpause()
        game.audio.channel_1.unpause()
        game.audio.channel_7.play(game.audio.unpause_sound)
        self.paused = False

    def player_damage(self) -> None:
        """
        Handles logic for when the player takes damage.
        If the player has any active upgrade or powerup, that is stripped instead of losing a heart.
        """
        game = self.game
        player = game.player.sprite
        if player and player.shield_active:
            return

        # If the player has any active upgrade, strip it instead of removing a heart.
        # This gives the player a second chance before actually taking damage.
        has_upgrade = player and (
            player.laser_level > 1 or
            player.rapid_fire_level > 0 or
            player.rainbow_beam_active
        )

        if has_upgrade:
            # Play the same alarm as losing the first heart
            game.audio.channel_4.play(game.audio.low_health_alarm1)
            player.trigger_damage_effect()
            return

        game.hearts -= 1

        if player:
            player.trigger_damage_effect()

        if game.hearts == 2:
            game.audio.channel_4.play(game.audio.low_health_alarm1)
        elif game.hearts == 1:
            game.audio.channel_4.play(game.audio.low_health_alarm2)

        if game.hearts <= 0:
            game.explode(player.rect.centerx, player.rect.centery)
            game.audio.channel_1.pause()
            self.player_alive = False
            player.ready = False
            player.shoot_button_held = True
            pygame.time.set_timer(game.spawner.player_death_timer, PlayerSettings.DEATH_DELAY)


class SpawnDirector:
    """Manages spawn timers, alien/powerup spawning, alien shooting, and adaptive difficulty."""
    def __init__(self, game):
        self.game = game

        self.alien_spawn_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.alien_spawn_timer, AlienSettings.SPAWN_RATE)

        self.alien_laser_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.alien_laser_timer, AlienSettings.LASER_RATE)

        # Custom timer for player death delay before showing game over screen
        self.player_death_timer = pygame.event.custom_type()
        self.volume_display_timer = pygame.event.custom_type()

    def spawn_aliens(self, alien_color: str) -> None:
        """
        Spawns a new alien of the given color.

        Args:
            alien_color (str): The color of the alien, which determines its behavior and point value.
        """
        self.game.aliens.add(Alien(alien_color, *ScreenSettings.RESOLUTION))
        if alien_color == 'blue':
            self.game.audio.channel_5.play(self.game.audio.ufo_sound)

    def spawn_powerup(self, pos: tuple[int, int], color: str) -> None:
        """
        Spawns a new powerup at the given position.

        Args:
            pos (tuple[int, int]): The (x, y) position to spawn the powerup.
            color (str): The color of the powerup, which determines its type and effect.
        """
        self.game.powerups.add(PowerUp(pos, color))

    def alien_shoot(self) -> None:
        """Spawns a new alien laser from a random alien."""
        game = self.game
        if game.aliens.sprites():
            attacking_aliens = [alien for alien in game.aliens.sprites() if alien.color != 'blue']
            if attacking_aliens:
                random_alien = random.choice(attacking_aliens)

                if random_alien.color == 'green':
                    # Green aliens fire a double shot — two lasers spread either side of center.
                    offset = 10
                    game.alien_lasers.add(
                        Laser(
                            pos=(random_alien.rect.centerx - offset, random_alien.rect.centery),
                            speed=LaserSettings.ALIEN_LASER_SPEED,
                            colors=LaserSettings.COLORS['alien'],
                            width=LaserSettings.DEFAULT_WIDTH
                        )
                    )
                    game.alien_lasers.add(
                        Laser(
                            pos=(random_alien.rect.centerx + offset, random_alien.rect.centery),
                            speed=LaserSettings.ALIEN_LASER_SPEED,
                            colors=LaserSettings.COLORS['alien'],
                            width=LaserSettings.DEFAULT_WIDTH
                        )
                    )
                else:
                    game.alien_lasers.add(
                        Laser(
                            random_alien.rect.center,
                            LaserSettings.ALIEN_LASER_SPEED,
                            LaserSettings.COLORS['alien'],
                            LaserSettings.DEFAULT_WIDTH
                        )
                    )

    def adjust_difficulty(self) -> None:
        """Gradually decreases timers as score increases."""
        game = self.game
        # Each full DIFFICULTY_STEP points earned unlocks one more level of difficulty.
        steps = game.scores.score // AlienSettings.DIFFICULTY_STEP

        # Reduce alien spawn interval by 25 ms per step, capped at the minimum.
        new_spawn_rate = max(
            AlienSettings.MIN_SPAWN_RATE,
            AlienSettings.SPAWN_RATE - (steps * 25)
        )
        pygame.time.set_timer(self.alien_spawn_timer, new_spawn_rate)

        # Reduce alien laser interval by 15 ms per step, capped at the minimum.
        new_laser_rate = max(
            AlienSettings.MIN_LASER_RATE,
            AlienSettings.LASER_RATE - (steps * 15)
        )
        pygame.time.set_timer(self.alien_laser_timer, new_laser_rate)

        # Speed up background scroll to reinforce the sense of increasing pace.
        new_bg_speed = min(
            ScreenSettings.BG_SCROLL_MAX,
            ScreenSettings.DEFAULT_BG_SCROLL_SPEED + (steps * ScreenSettings.BG_SCROLL_STEP)
        )
        for bg in game.background.sprites():
            bg.scroll_speed = new_bg_speed

    def get_bomb_drop_chance(self, alien_value: int) -> float:
        """
        Returns a rare bomb-drop chance weighted by alien point value.

        Args:
            alien_value (int): The point value of the defeated alien.

        Returns:
            float: Drop chance between BOMB_DROP_BASE and BOMB_DROP_BASE + BOMB_DROP_BONUS.
        """
        all_values = AlienSettings.POINTS.values()
        min_value = min(all_values)
        max_value = max(all_values)
        if max_value == min_value:
            # All alien types are worth the same — use the flat base chance.
            return AlienSettings.BOMB_DROP_BASE
        # Linear interpolation: rarer (higher-value) aliens drop bombs more often.
        # value_ratio == 0.0 for the weakest alien, 1.0 for the strongest.
        value_ratio = (alien_value - min_value) / (max_value - min_value)
        return AlienSettings.BOMB_DROP_BASE + (AlienSettings.BOMB_DROP_BONUS * value_ratio)

    def try_spawn_alien_drop(self, alien: Alien) -> None:
        """
        Evaluates whether a destroyed alien should drop a powerup and spawns it if so.

        Args:
            alien (Alien): The alien that was destroyed, used to determine drop chances and type.
        """
        game = self.game
        player = game.player.sprite

        if alien.color == 'red':
            if random.random() < AlienSettings.DROP_CHANCE['red']:
                eligible_drops = []
                weights = []
                # Heart drop
                if game.hearts < PlayerSettings.MAX_HEALTH: # Only drop hearts if player isn't at full health
                    eligible_drops.append('red')
                    weights.append(1.0)
                # Bomb drop
                eligible_drops.append('bomb')
                weights.append(1.0)
                # Shield drop
                if not player.shield_active: # Only drop shield if player doesn't already have one active
                    eligible_drops.append('red_shield')
                    weights.append(0.5)  # Shields are half as likely as hearts or bombs

                if eligible_drops:
                    chosen = random.choices(eligible_drops, weights=weights, k=1)[0]
                    self.spawn_powerup(alien.rect.center, chosen)
        else:
            can_drop_color_powerup = True
            if alien.color == 'green':
                can_drop_color_powerup = player.laser_level < 4
            elif alien.color == 'yellow':
                can_drop_color_powerup = player.rapid_fire_level < 3

            if can_drop_color_powerup and random.random() < AlienSettings.DROP_CHANCE[alien.color]:
                self.spawn_powerup(alien.rect.center, alien.color)
