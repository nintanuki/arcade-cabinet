"""Pong entry point, event loop, and high-level runtime orchestration."""

import sys
from settings import *
from sprites import Player, Opponent, Ball
from game import GameManager
from crt import CRT
from audio import Audio


START_BUTTON = 7
SELECT_BUTTON = 6
L1_BUTTON = 4
R1_BUTTON = 5
LEFT_STICK_VERTICAL_AXIS = 1
AXIS_DEADZONE = 0.15


def refresh_joysticks() -> list[pygame.joystick.Joystick]:
    """Return all currently connected joysticks as initialized objects.

    Args:
        None.

    Returns:
        list[pygame.joystick.Joystick]: Initialized joystick instances.
    """
    connected: list[pygame.joystick.Joystick] = []
    for index in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(index)
        joystick.init()
        connected.append(joystick)
    return connected


def quit_combo_pressed(connected_joysticks: list[pygame.joystick.Joystick]) -> bool:
    """Check whether START + SELECT + L1 + R1 are held.

    Args:
        connected_joysticks (list[pygame.joystick.Joystick]): Joysticks to inspect.

    Returns:
        bool: True when the full exit combo is held on any joystick.
    """
    for joystick in connected_joysticks:
        try:
            if all(joystick.get_button(button) for button in (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)):
                return True
        except pygame.error:
            continue
    return False


def controller_vertical_direction(connected_joysticks: list[pygame.joystick.Joystick]) -> int:
    """Read left-stick vertical input and return a normalized direction.

    Args:
        connected_joysticks (list[pygame.joystick.Joystick]): Joysticks to inspect.

    Returns:
        int: -1 for up, 1 for down, or 0 for neutral.
    """
    for joystick in connected_joysticks:
        try:
            axis_value = joystick.get_axis(LEFT_STICK_VERTICAL_AXIS)
        except pygame.error:
            continue

        if axis_value <= -AXIS_DEADZONE:
            return -1
        if axis_value >= AXIS_DEADZONE:
            return 1

    return 0


# General setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()
audio = Audio()

# Joystick setup
pygame.joystick.init()
joysticks = refresh_joysticks()

# Main window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
crt = CRT(screen)
pygame.display.set_caption('Pong')

# Global runtime state
basic_font = pygame.font.Font('freesansbold.ttf', 32)
middle_strip = pygame.Rect(SCREEN_WIDTH / 2 - 2, 0, 4, SCREEN_HEIGHT)
full_screen = False
paused = False
up_pressed = False
down_pressed = False

# Game objects
player = Player('graphics/paddle.png', SCREEN_WIDTH - 20, SCREEN_HEIGHT / 2, 5)
opponent = Opponent('graphics/paddle.png', 20, SCREEN_WIDTH / 2, 5)
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)

# TODO(refactor): Move font/screen dependencies out of Ball and into a UI/controller layer.
ball = Ball('graphics/ball.png', SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 4, 4, paddle_group, audio, basic_font, screen)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite, paddle_group, basic_font, screen)

# TODO(refactor): Wrap this script-level state and loop into a GameApp class for testability.
while True:
    # TODO(bug): Holding the exit combo can quit instantly during intense gameplay moments.
    if quit_combo_pressed(joysticks):
        pygame.quit()
        sys.exit()

    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_ALT and event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                pygame.display.toggle_fullscreen()
                full_screen = not full_screen
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                full_screen = not full_screen
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                paused = not paused
            if event.key == pygame.K_UP:
                up_pressed = True
            if event.key == pygame.K_DOWN:
                down_pressed = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up_pressed = False
            if event.key == pygame.K_DOWN:
                down_pressed = False

        if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            joysticks = refresh_joysticks()

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == START_BUTTON:
                paused = not paused
            elif event.button == SELECT_BUTTON:
                pygame.display.toggle_fullscreen()
                full_screen = not full_screen

    controller_direction = controller_vertical_direction(joysticks)
    if controller_direction != 0:
        player.movement = controller_direction * player.speed
    elif up_pressed and not down_pressed:
        player.movement = -player.speed
    elif down_pressed and not up_pressed:
        player.movement = player.speed
    else:
        player.movement = 0

    # Background
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, ACCENT_COLOR, middle_strip)

    # Run/update gameplay
    if paused:
        paddle_group.draw(screen)
        ball_sprite.draw(screen)
        game_manager.draw_score()
        paused_surface = basic_font.render('PAUSED', True, ACCENT_COLOR)
        paused_rect = paused_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 90))
        screen.blit(paused_surface, paused_rect)
    else:
        game_manager.run_game()

    # Music
    # TODO(bug): Restarting sound playback whenever the channel is idle can create audible seams.
    if not audio.channel_0.get_busy():
        audio.channel_0.play(audio.bg_music)

    # Rendering
    if full_screen is False:
        crt.draw()
    pygame.display.flip()
    clock.tick(FRAMERATE)
