"""Scene for the title screen."""

from __future__ import annotations

import pygame

from core.scene import Scene
from settings import (
    ColorSettings,
    FontSettings,
    InputSettings,
    ScreenSettings,
    UiSettings,
)
from systems.fish_manager import FishManager
from utils.graphics import build_gradient_surface
from utils.text import draw_centered_text


class TitleScene(Scene):
    """Scene displayed when the game first launches."""

    def __init__(self, game):
        """Initialize title-screen visuals and background fish systems.

        Args:
            game: The GameManager instance that owns this scene.
        """
        super().__init__(game)
        self.bg_surface = build_gradient_surface(
            ScreenSettings.WIDTH,
            ScreenSettings.HEIGHT,
            ColorSettings.BG_COLOR_TOP,
            ColorSettings.BG_COLOR_BOTTOM,
        )
        self.title_font = pygame.font.Font(FontSettings.FONT, UiSettings.TITLE_FONT_SIZE)
        self.prompt_font = pygame.font.Font(FontSettings.FONT, UiSettings.START_PROMPT_FONT_SIZE)
        self.enemy_sprites = pygame.sprite.Group()
        self.fish_manager = FishManager(self.enemy_sprites)

    def on_enter(self) -> None:
        """Called when this scene becomes active."""
        self.game.audio.stop_music()

    def on_exit(self) -> None:
        """Called when leaving this scene."""
        pass

    def _start_game_action(self) -> None:
        """Transition from title to a fresh gameplay session."""
        from ui.scenes.play_scene import PlayScene
        self.game.scenes.change_to(PlayScene(self.game, play_intro_splash=True))

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle title-scene input for game start.

        Args:
            event: The pygame event to process.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_game_action()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == InputSettings.JOY_BUTTON_START:
                self._start_game_action()

    def update(self) -> None:
        """Advance title-scene background fish by one frame."""
        self.enemy_sprites.update()
        self.fish_manager.update(player=None)

    def render(self, screen: pygame.Surface) -> None:
        """Draw the title scene to the screen.

        Args:
            screen: The pygame surface to draw to.
        """
        screen.blit(self.bg_surface, (0, 0))
        self.enemy_sprites.draw(screen)

        draw_centered_text(
            surface=screen,
            text=UiSettings.TITLE_TEXT,
            font=self.title_font,
            color=ColorSettings.WHITE,
            center=(ScreenSettings.WIDTH // 2, int(ScreenSettings.HEIGHT * UiSettings.TITLE_CENTER_Y_RATIO)),
        )

        draw_centered_text(
            surface=screen,
            text=UiSettings.START_PROMPT_TEXT,
            font=self.prompt_font,
            color=ColorSettings.WHITE,
            center=(
                ScreenSettings.WIDTH // 2,
                int(ScreenSettings.HEIGHT * UiSettings.START_PROMPT_CENTER_Y_RATIO),
            ),
        )
