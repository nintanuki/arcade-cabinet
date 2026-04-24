import pygame
import sys
import random
from settings import *
from audio import Audio
from crt import CRT

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption('Air Hockey')
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        self.crt = CRT(self.screen)

        # Joystick support
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.joysticks.append(j)

        # Game State
        self.game_active = False
        self.paused = False
        self.muted = False
        self.full_screen = False

        # Game Rectangles and Positions
        self.player = pygame.Rect(
            (SCREEN_WIDTH / 2) - (PLAYER_WIDTH / 2),
            (SCREEN_HEIGHT * 7 / 8) - (PLAYER_HEIGHT / 2),
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        self.opponent = pygame.Rect(
            (SCREEN_WIDTH / 2) - (OPPONENT_WIDTH / 2),
            (SCREEN_HEIGHT / 8) - (OPPONENT_HEIGHT / 2),
            OPPONENT_WIDTH,
            OPPONENT_HEIGHT
        )
        self.puck = pygame.Rect(0, 0, PUCK_WIDTH, PUCK_HEIGHT)
        self.player_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), SCREEN_HEIGHT - 10, SCREEN_WIDTH / 4, 10)
        self.opponent_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), 0, SCREEN_WIDTH / 4, 10)

        # Scoring
        self.player_score = 0
        self.opponent_score = 0

        # Fonts
        self.score_font = pygame.font.Font('Pixeled.ttf', 12)
        self.countdown_font = pygame.font.Font('Pixeled.ttf', 32)
        self.title_font = pygame.font.Font('Pixeled.ttf', 28)

        # Countdown timer variables
        self.countdown = 0
        self.COUNTDOWN_EVENT = pygame.USEREVENT + 1
        self.COUNTDOWN_INTERVAL = 1000

        # Collision cooldown
        self.collision_cooldown = 0

        # Player velocity tracking
        self.player_velocity = [0, 0]
        self.prev_player_pos = self.player.center

        self.is_spiking = False
        self.spike_speed = 30

        # Joystick axis tracking
        self.joystick_x = 0.0
        self.joystick_y = 0.0
        self.using_joystick = False
        self.input_mode = "mouse"
        self.locked_input_mode = None
        self.show_title = True
        self.input_options = ["mouse", "controller"]
        self.input_selection_index = 0

        self.reset_puck()

    def puck_movement(self):
        self.puck.x += self.puck_speed_x
        self.puck.y += self.puck_speed_y

        if self.puck.top <= 0 or self.puck.bottom >= SCREEN_HEIGHT:
            self.puck_speed_y *= -1
            self.audio.channel_1.play(self.audio.plob_sound)
        if self.puck.left <= 0 or self.puck.right >= SCREEN_WIDTH:
            self.puck_speed_x *= -1
            self.audio.channel_1.play(self.audio.plob_sound)

        if self.puck.colliderect(self.player):
            relative_x = (self.puck.centerx - self.player.centerx) / (self.player.width / 2)
            relative_y = (self.puck.centery - self.player.centery) / (self.player.height / 2)
            self.puck_speed_x = relative_x * INITIAL_PUCK_SPEED
            self.puck_speed_y = relative_y * INITIAL_PUCK_SPEED
            self.puck_speed_x += self.player_velocity[0] * 0.5
            self.puck_speed_y += self.player_velocity[1] * 0.5
            self.increase_speed()
            self.audio.channel_1.play(self.audio.plob_sound)

        if self.puck.colliderect(self.opponent) and self.collision_cooldown == 0:
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            self.increase_speed()
            self.collision_cooldown = 30
            self.audio.channel_1.play(self.audio.plob_sound)

        self.puck_speed_x *= 0.995
        self.puck_speed_y *= 0.995

    def increase_speed(self):
        self.puck_speed_x *= 1.5
        self.puck_speed_y *= 1.5
        self.apply_speed_limit()

    def apply_speed_limit(self):
        speed = (self.puck_speed_x ** 2 + self.puck_speed_y ** 2) ** 0.5
        if speed > SPEED_LIMIT:
            scale = SPEED_LIMIT / speed
            self.puck_speed_x *= scale
            self.puck_speed_y *= scale
        if speed < INITIAL_PUCK_SPEED and speed > 0:
            scale = INITIAL_PUCK_SPEED / speed
            self.puck_speed_x *= scale
            self.puck_speed_y *= scale

    def opponent_movement(self):
        if self.puck.x < self.opponent.x:
            self.opponent.x -= OPPONENT_SPEED
        if self.puck.x > self.opponent.x:
            self.opponent.x += OPPONENT_SPEED
        if self.puck.y < self.opponent.y:
            self.opponent.y -= OPPONENT_SPEED
        if self.puck.y > self.opponent.y:
            self.opponent.y += OPPONENT_SPEED

    def reset_puck(self):
        if random.choice([True, False]):
            self.puck.x = (SCREEN_WIDTH / 2) - (PUCK_WIDTH / 2)
            self.puck.y = (SCREEN_HEIGHT * 3 / 4) - (PUCK_HEIGHT / 2)
        else:
            self.puck.x = (SCREEN_WIDTH / 2) - (PUCK_WIDTH / 2)
            self.puck.y = (SCREEN_HEIGHT / 4) - (PUCK_HEIGHT / 2)
        self.puck_speed_x = random.choice([-1, 1]) * INITIAL_PUCK_SPEED
        self.puck_speed_y = random.choice([-1, 1]) * INITIAL_PUCK_SPEED

    def check_goals(self):
        if self.puck.colliderect(self.player_goal):
            self.opponent_score += 1
            self.start_countdown()
            self.audio.channel_2.play(self.audio.score_sound)
        elif self.puck.colliderect(self.opponent_goal):
            self.player_score += 1
            self.start_countdown()
            self.audio.channel_2.play(self.audio.score_sound)

    def start_countdown(self):
        self.countdown = 3
        pygame.time.set_timer(self.COUNTDOWN_EVENT, self.COUNTDOWN_INTERVAL)

    def display_scores(self):
        player_score_text = self.score_font.render(f"Player: {self.player_score}", True, BLACK)
        opponent_score_text = self.score_font.render(f"Opponent: {self.opponent_score}", True, BLACK)
        self.screen.blit(player_score_text, (10, SCREEN_HEIGHT - 40))
        self.screen.blit(opponent_score_text, (10, 10))

    def draw_dotted_line(self):
        y = SCREEN_HEIGHT // 2
        x = 0
        segment_length = 10
        gap_length = 5
        while x < SCREEN_WIDTH:
            pygame.draw.line(self.screen, BLACK, (x, y), (x + segment_length, y))
            x += segment_length + gap_length

    def quit_combo_pressed(self):
        """Return True if START + SELECT + L1 + R1 are all held."""
        for joystick in self.joysticks:
            try:
                if all(joystick.get_button(b) for b in (7, 6, 4, 5)):
                    return True
            except pygame.error:
                continue
        return False

    def pause(self):
        self.paused = not self.paused
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.audio.channel_0.unpause()
                        self.audio.channel_4.play(self.audio.unpause_sound)
                        self.paused = False
            if self.quit_combo_pressed():
                pygame.quit()
                sys.exit()

            self.screen.fill(WHITE)
            self.draw_dotted_line()
            pygame.draw.rect(self.screen, BLUE, self.player_goal)
            pygame.draw.rect(self.screen, BLUE, self.opponent_goal)
            self.display_scores()
            paused_text = self.countdown_font.render("PAUSED", True, BLACK)
            text_rect = paused_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            self.screen.blit(paused_text, text_rect)
            pygame.display.flip()
            self.clock.tick(FRAMERATE)

    def _cycle_input_mode(self, direction):
        self.input_selection_index = (self.input_selection_index + direction) % len(self.input_options)

    def _confirm_input_mode(self):
        selected = self.input_options[self.input_selection_index]
        if selected == "controller" and not self.joysticks:
            selected = "mouse"
        self.locked_input_mode = "joystick" if selected == "controller" else "mouse"
        self.input_mode = self.locked_input_mode
        self.using_joystick = self.locked_input_mode == "joystick"
        self.show_title = False

    def _draw_title_screen(self):
        self.screen.fill(WHITE)
        title_text = self.title_font.render("AIR HOCKEY", True, BLACK)
        self.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 110)))

        prompt_text = self.score_font.render("SELECT INPUT", True, BLACK)
        self.screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)))

        mouse_selected = self.input_selection_index == 0
        mouse_color = RED if mouse_selected else BLACK
        mouse_text = self.score_font.render(("> " if mouse_selected else "  ") + "MOUSE", True, mouse_color)
        self.screen.blit(mouse_text, mouse_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10)))

        controller_selected = self.input_selection_index == 1
        controller_color = RED if controller_selected else BLACK
        controller_text = self.score_font.render(("> " if controller_selected else "  ") + "CONTROLLER", True, controller_color)
        self.screen.blit(controller_text, controller_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 16)))

        hint_text = self.score_font.render("ARROWS OR DPAD TO CHOOSE", True, BLACK)
        self.screen.blit(hint_text, hint_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 58)))
        start_text = self.score_font.render("ENTER OR START TO PLAY", True, BLACK)
        self.screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 78)))

        if not self.joysticks:
            no_pad_text = self.score_font.render("NO CONTROLLER DETECTED", True, RED)
            self.screen.blit(no_pad_text, no_pad_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 108)))

    def run(self):
        while True:
            dt = self.clock.tick(FRAMERATE) / 1000
            if self.quit_combo_pressed():
                pygame.quit()
                sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.JOYDEVICEADDED:
                    j = pygame.joystick.Joystick(event.device_index)
                    j.init()
                    self.joysticks.append(j)

                if self.show_title:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                            self._cycle_input_mode(-1)
                        if event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s):
                            self._cycle_input_mode(1)
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                            self._confirm_input_mode()
                        if event.key == pygame.K_F11:
                            pygame.display.toggle_fullscreen()
                            self.full_screen = not self.full_screen
                    if event.type == pygame.JOYHATMOTION:
                        hat_x, hat_y = event.value
                        if hat_x == -1 or hat_y == 1:
                            self._cycle_input_mode(-1)
                        elif hat_x == 1 or hat_y == -1:
                            self._cycle_input_mode(1)
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button in (0, 7):
                            self._confirm_input_mode()
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.locked_input_mode != "joystick":
                            self.input_mode = "mouse"
                        self.is_spiking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.locked_input_mode != "joystick":
                            self.input_mode = "mouse"
                        self.is_spiking = False
                if event.type == pygame.MOUSEMOTION:
                    if self.locked_input_mode != "joystick":
                        self.input_mode = "mouse"
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.is_spiking = True
                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        self.is_spiking = False
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        self.joystick_x = event.value
                        if abs(event.value) >= 0.15 and self.locked_input_mode != "mouse":
                            self.using_joystick = True
                            self.input_mode = "joystick"
                    elif event.axis == 1:
                        self.joystick_y = event.value
                        if abs(event.value) >= 0.15 and self.locked_input_mode != "mouse":
                            self.using_joystick = True
                            self.input_mode = "joystick"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        self.full_screen = not self.full_screen
                    if event.key == pygame.K_RETURN:
                        self.audio.channel_0.pause()
                        self.audio.channel_3.play(self.audio.pause_sound)
                        self.pause()
                    if event.key == pygame.K_m:
                        self.muted = not self.muted
                        vols = [0] * 5 if self.muted else [0.5] * 5
                        for ch, v in zip((self.audio.channel_0, self.audio.channel_1, self.audio.channel_2, self.audio.channel_3, self.audio.channel_4), vols):
                            ch.set_volume(v)
                if event.type == self.COUNTDOWN_EVENT and self.countdown > 0:
                    self.countdown -= 1
                    if self.countdown == 0:
                        pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)
                        self.reset_puck()

            if self.show_title:
                self._draw_title_screen()
                if not self.full_screen:
                    self.crt.draw()
                pygame.display.flip()
                continue

            if self.countdown > 0:
                self.screen.fill(WHITE)
                self.draw_dotted_line()
                pygame.draw.rect(self.screen, BLUE, self.player_goal, border_radius=BORDER_RADIUS)
                pygame.draw.rect(self.screen, BLUE, self.opponent_goal, border_radius=BORDER_RADIUS)
                self.display_scores()
                countdown_text = self.countdown_font.render(str(self.countdown), True, BLACK)
                text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                self.screen.blit(countdown_text, text_rect)
                if not self.full_screen:
                    self.crt.draw()
                pygame.display.flip()
                continue

            ax = self.joystick_x if abs(self.joystick_x) >= 0.15 else 0.0
            ay = self.joystick_y if abs(self.joystick_y) >= 0.15 else 0.0
            if ax == 0.0 and ay == 0.0:
                self.using_joystick = False
            if self.input_mode == "joystick":
                self.player.centerx += int(ax * 700 * dt)
                self.player.centery += int(ay * 700 * dt)
            else:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.player.centerx = mouse_x
                self.player.centery = mouse_y

            if self.is_spiking:
                self.player.y -= self.spike_speed

            if self.player.top <= SCREEN_HEIGHT / 2:
                self.player.top = SCREEN_HEIGHT / 2
            if self.player.bottom >= SCREEN_HEIGHT:
                self.player.bottom = SCREEN_HEIGHT
            if self.player.left <= 0:
                self.player.left = 0
            if self.player.right >= SCREEN_WIDTH:
                self.player.right = SCREEN_WIDTH

            if self.opponent.top <= 0:
                self.opponent.top = 0
            if self.opponent.bottom >= SCREEN_HEIGHT / 4:
                self.opponent.bottom = SCREEN_HEIGHT / 4
            if self.opponent.left <= 0:
                self.opponent.left = 0
            if self.opponent.right >= SCREEN_WIDTH:
                self.opponent.right = SCREEN_WIDTH

            if self.collision_cooldown > 0:
                self.collision_cooldown -= 1

            self.player_velocity = [
                self.player.centerx - self.prev_player_pos[0],
                self.player.centery - self.prev_player_pos[1],
            ]
            self.prev_player_pos = self.player.center

            self.puck_movement()
            self.opponent_movement()
            self.check_goals()

            self.screen.fill(WHITE)
            self.draw_dotted_line()
            pygame.draw.rect(self.screen, BLUE, self.player_goal, border_radius=BORDER_RADIUS)
            pygame.draw.rect(self.screen, BLUE, self.opponent_goal, border_radius=BORDER_RADIUS)
            pygame.draw.ellipse(self.screen, RED, self.player)
            pygame.draw.ellipse(self.screen, RED, self.opponent)
            pygame.draw.ellipse(self.screen, BLACK, self.puck)
            self.display_scores()

            if not self.audio.channel_0.get_busy():
                self.audio.channel_0.play(self.audio.bg_music)

            if not self.full_screen:
                self.crt.draw()
            pygame.display.flip()

if __name__ == '__main__':
    game_manager = Game()
    game_manager.run()
