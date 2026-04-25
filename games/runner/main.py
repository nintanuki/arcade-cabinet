from __future__ import annotations
import pygame
import sys
from pathlib import Path
from sys import exit
from random import randint, choice

from settings import ScreenSettings, PlayerSettings, AssetPaths
from crt import CRT

ASSET_DIR = Path(__file__).resolve().parent

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load graphics
        player_walk_1 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Player' / 'player_walk_1.png')).convert_alpha()
        player_walk_2 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Player' / 'player_walk_2.png')).convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Player' / 'jump.png')).convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=PlayerSettings.INITIAL_POSITION) # Starting position on the ground
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'jump.mp3'))
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'fly':
            fly_1 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Fly' / 'fly1.png')).convert_alpha()
            fly_2 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Fly' / 'fly2.png')).convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'snail' / 'snail1.png')).convert_alpha()
            snail_2 = pygame.image.load(str(ASSET_DIR / 'graphics' / 'snail' / 'snail2.png')).convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        if self.rect.x <= -100:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ScreenSettings.WIDTH, ScreenSettings.HEIGHT))
        pygame.display.set_caption(ScreenSettings.TITLE)
        self.clock = pygame.time.Clock()
        self.crt = CRT(self.screen) # Now self.screen exists!
        
        # Game State
        self.game_active = False
        self.start_time = 0
        self.score = 0
        self.font = pygame.font.Font(str(ASSET_DIR / 'font' / 'Pixeltype.ttf'), 50)

        # Music
        self.bg_music = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'music.wav'))
        self.bg_music.play(loops=-1)

        # Groups
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player())
        self.obstacle_group = pygame.sprite.Group()

        # Backgrounds
        self.sky_surf = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Sky.png')).convert()
        self.ground_surf = pygame.image.load(str(ASSET_DIR / 'graphics' / 'ground.png')).convert()

        # Intro Screen
        self.player_stand = pygame.image.load(str(ASSET_DIR / 'graphics' / 'Player' / 'player_stand.png')).convert_alpha()
        self.player_stand = pygame.transform.rotozoom(self.player_stand, 0, 2)
        self.player_stand_rect = self.player_stand.get_rect(center=(400, 200))

        # Timer
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1500)

    def display_score(self):
        current_time = int(pygame.time.get_ticks() / 1000) - self.start_time
        score_surf = self.font.render(f'Score: {current_time}', False, (64, 64, 64))
        score_rect = score_surf.get_rect(center=(400, 50))
        self.screen.blit(score_surf, score_rect)
        return current_time

    def collision_sprite(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.obstacle_group, False):
            self.obstacle_group.empty()
            return False
        return True

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if self.game_active:
                    if event.type == self.obstacle_timer:
                        self.obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_active = True
                        self.start_time = int(pygame.time.get_ticks() / 1000)

            if self.game_active:
                self.screen.blit(self.sky_surf, (0, 0))
                self.screen.blit(self.ground_surf, (0, 300))
                self.score = self.display_score()
                
                self.player.draw(self.screen)
                self.player.update()

                self.obstacle_group.draw(self.screen)
                self.obstacle_group.update()

                self.game_active = self.collision_sprite()
            else:
                self.screen.fill((94, 129, 162))
                self.screen.blit(self.player_stand, self.player_stand_rect)
                
                # Show score logic here...
                score_message = self.font.render(f'Your score: {self.score}', False, (111, 196, 169))
                score_rect = score_message.get_rect(center=(300, 330))
                if self.score == 0:
                    msg = self.font.render('Press space to run', False, (111, 196, 169))
                    self.screen.blit(msg, (250, 330))
                else:
                    self.screen.blit(score_message, score_rect)

            # Apply CRT effect at the very end of the draw cycle
            self.crt.draw() 

            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()