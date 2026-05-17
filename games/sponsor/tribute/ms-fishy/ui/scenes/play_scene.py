"""Scene for active gameplay."""

from __future__ import annotations

import pygame

from core.scene import Scene
from core.score import Score
from core.sprites import Player
from ui.hud import Hud
from systems.fish_manager import FishManager
from settings import (
    ColorSettings,
    FontSettings,
    InputSettings,
    PlayerSettings,
    ScreenSettings,
    TimerSettings,
    UiSettings,
)
from utils.graphics import build_gradient_surface
from utils.text import draw_centered_text


class PlayScene(Scene):
    """Scene for active gameplay and pausing."""

    DROPPING_IN = "dropping_in"
    ACTIVE = "active"
    PAUSED = "paused"

    LOSS_EATEN_BY_BIGGER_FISH = "loss_eaten_by_bigger_fish"
    LOSS_STARVED_TO_DEATH = "loss_starved_to_death"
    WIN_ATE_ALL_FISH = "win_ate_all_fish"

    def __init__(self, game, play_intro_splash: bool = False):
        """Initialize the play scene with a fresh player, score, and fish manager.
        
        Args:
            game: The GameManager instance that owns this scene.
            play_intro_splash: Whether to play splash SFX when drop-in settles.
        """
        super().__init__(game)
        self._create_gameplay_entities()
        self.bg_surface = build_gradient_surface(
            ScreenSettings.WIDTH, ScreenSettings.HEIGHT,
            ColorSettings.BG_COLOR_TOP, ColorSettings.BG_COLOR_BOTTOM,
        )
        self.hud_font = pygame.font.Font(FontSettings.FONT, UiSettings.HUD_FONT_SIZE_SMALL)
        self.hud = Hud(score=self.score, font=self.hud_font, player=self.player)
        self._state = self.DROPPING_IN
        self._play_intro_splash = play_intro_splash
        self._drop_in_splash_played = False
        self._remaining_time_seconds = float(TimerSettings.STARTING_SECONDS)

    def _create_gameplay_entities(self) -> None:
        """Build player, score, enemy container, and fish manager for one session."""
        self.player = Player(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2)
        self.score = Score()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.enemy_sprites = pygame.sprite.Group()
        self.fish_manager = FishManager(self.enemy_sprites)

    def on_enter(self) -> None:
        """Called when entering this scene from another scene."""
        self._state = self.DROPPING_IN
        self._drop_in_splash_played = False
        self._remaining_time_seconds = float(TimerSettings.STARTING_SECONDS)
        self.player.rect.center = (ScreenSettings.WIDTH // 2, -self.player.rect.height)
        self.player._pos_x = float(self.player.rect.x)
        self.player._pos_y = float(self.player.rect.y)
        self.player.velocity_x = 0.0
        self.player.velocity_y = PlayerSettings.DROP_IN_VELOCITY

    def on_exit(self) -> None:
        """Called when leaving this scene."""
        pass

    def _get_hud_detail_align(self) -> str | None:
        """Return 'left' or 'right' if the player is holding a shoulder button, else None.

        L1 or L2 held → detail HUD anchored top-left.
        R1 or R2 held → detail HUD anchored top-right.
        Neither held  → compact hunger indicator (default).
        """
        for joy in self.game.connected_joysticks:
            left_held = (
                joy.get_button(InputSettings.JOY_BUTTON_L1)
                or joy.get_axis(InputSettings.JOY_AXIS_L2) > InputSettings.JOY_TRIGGER_THRESHOLD
            )
            right_held = (
                joy.get_button(InputSettings.JOY_BUTTON_R1)
                or joy.get_axis(InputSettings.JOY_AXIS_R2) > InputSettings.JOY_TRIGGER_THRESHOLD
            )
            if left_held:
                return "left"
            if right_held:
                return "right"
        return None

    def _handle_pause_action(self) -> None:
        """Toggle pause on or off, including the audio side-effects for each transition."""
        if self._state == self.ACTIVE:
            self._state = self.PAUSED
            self.game.audio.pause_music()
            self.game.audio.play("pause_in")
            return

        if self._state == self.PAUSED:
            self._state = self.ACTIVE
            self.game.audio.play("pause_out")
            self.game.audio.resume_music()

    def _end_run(self, outcome: str, play_scream: bool) -> None:
        """Stop gameplay audio and transition to game-over messaging.

        Args:
            outcome: End-of-run outcome reason consumed by GameOverScene.
            play_scream: Whether to play the scream SFX for this ending.
        """
        # Capture final stats so Score.total includes all components.
        self.score.final_weight = self.player.size
        self.score.time_left_seconds = self._remaining_time_seconds
        self.game.audio.stop_music()
        if play_scream:
            self.game.audio.play("scream")
        from ui.scenes.game_over_scene import GameOverScene
        self.game.scenes.change_to(GameOverScene(self.game, self.score, outcome=outcome))

    def _update_drop_in_motion(self) -> None:
        """Advance the one-time player drop-in animation without reading input."""
        target_y = ScreenSettings.HEIGHT // 2
        center_tolerance = 4
        previous_bottom = self.player.rect.bottom
        delta_y = target_y - self.player.rect.centery

        if abs(delta_y) <= center_tolerance:
            input_y = 0
        elif delta_y > 0:
            input_y = 1
        else:
            input_y = -1

        if input_y != 0:
            accel = (
                PlayerSettings.COUNTER_ACCELERATION
                if input_y * self.player.velocity_y < 0
                else PlayerSettings.ACCELERATION
            )
            self.player.velocity_y = max(
                -PlayerSettings.MAX_SPEED,
                min(
                    PlayerSettings.MAX_SPEED,
                    self.player.velocity_y + input_y * accel,
                ),
            )
        else:
            self.player.velocity_y *= PlayerSettings.DRAG
            if abs(self.player.velocity_y) < PlayerSettings.STOP_THRESHOLD:
                self.player.velocity_y = 0.0

        self.player._pos_y += self.player.velocity_y
        self.player.rect.y = int(self.player._pos_y)

        # Fire splash exactly when the player first enters the visible screen.
        if (
            self._play_intro_splash
            and not self._drop_in_splash_played
            and previous_bottom < 0
            and self.player.rect.bottom >= 0
        ):
            self.game.audio.play("splash")
            self._drop_in_splash_played = True

        # Keep the drop centered horizontally and keep accumulators in sync.
        self.player.rect.centerx = ScreenSettings.WIDTH // 2
        self.player._pos_x = float(self.player.rect.x)

        if (
            abs(self.player.velocity_y) < PlayerSettings.STOP_THRESHOLD
            and self.player.rect.centery >= target_y - center_tolerance
        ):
            self.player.rect.centery = target_y
            self.player._pos_x = float(self.player.rect.x)
            self.player._pos_y = float(self.player.rect.y)
            self.player.velocity_y = 0.0
            self.game.audio.resume_music()
            self._state = self.ACTIVE

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle input events for the play scene.
        
        Args:
            event: The pygame event to process.
        """
        # Note: global events (Esc, F11, BACK, quit-combo) are handled
        # by GameManager and never reach here.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._handle_pause_action()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == InputSettings.JOY_BUTTON_START:
                self._handle_pause_action()

    def update(self) -> None:
        """Advance gameplay by one frame."""
        if self._state == self.DROPPING_IN:
            self._update_drop_in_motion()
            return

        if self._state == self.PAUSED:
            return

        self._remaining_time_seconds = max(
            0.0,
            self._remaining_time_seconds - (1 / ScreenSettings.FPS),
        )
        self.all_sprites.update(joysticks=self.game.connected_joysticks)
        self.enemy_sprites.update()
        game_over, eaten_sizes = self.fish_manager.update(self.player)
        for fish_size in eaten_sizes:
            self.score.add(fish_size)
            # Diminishing returns: eating fish much smaller than the player
            # gives proportionally less time.  The ratio is capped at 1.0 so
            # eating a peer-sized fish always gives the full SECONDS_PER_EAT
            # bonus, and floored at TIMER_MIN_RATIO so even tiny fish still
            # give some time.  Crucially, the bonus does NOT scale with
            # absolute fish size — only the ratio matters — so a huge player
            # eating a huge peer earns the same seconds as a tiny player
            # eating a tiny peer, keeping the late game challenging.
            size_ratio = min(1.0, fish_size / self.player.size)
            effective_ratio = max(TimerSettings.TIMER_MIN_RATIO, size_ratio)
            self._remaining_time_seconds += (
                effective_ratio * TimerSettings.SECONDS_PER_EAT
            )

        if eaten_sizes:
            self.game.audio.play("gulp")
        if game_over:
            self._end_run(self.LOSS_EATEN_BY_BIGGER_FISH, play_scream=True)
            return

        if self._remaining_time_seconds <= 0.0:
            self._end_run(self.LOSS_STARVED_TO_DEATH, play_scream=False)
            return

        # Win condition: once the player sprite exceeds the screen width,
        # the run ends and transitions through the custom victory flow.
        if self.player.rect.width > ScreenSettings.WIDTH:
            self._end_run(self.WIN_ATE_ALL_FISH, play_scream=False)

    def render(self, screen: pygame.Surface) -> None:
        """Draw the play scene to the screen.
        
        Args:
            screen: The pygame surface to draw to.
        """
        if self._state in (self.DROPPING_IN, self.ACTIVE):
            screen.blit(self.bg_surface, (0, 0))
            self.all_sprites.draw(screen)
            self.enemy_sprites.draw(screen)
            if self._state == self.ACTIVE:
                self.hud.draw(screen, self._remaining_time_seconds, self._get_hud_detail_align())
        elif self._state == self.PAUSED:
            screen.fill(ColorSettings.BLACK)
            draw_centered_text(
                surface=screen,
                text=UiSettings.PAUSE_TEXT,
                font=self.game.overlay_font,
                color=ColorSettings.WHITE,
                center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2),
            )
