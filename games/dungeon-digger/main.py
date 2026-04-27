import pygame
import sys

from settings import *
from audio import AudioManager
from windows import MessageLog, InventoryWindow, MapWindow
from dungeon import DungeonLevel
from dungeon_config import DUNGEON_CONFIG, LEVEL_DUNGEON_ORDER
from crt import CRT
from managers import ScoreLeaderboardManager, IntermissionFlow
from tutorial import TutorialManager
import coords
import loot
from level_loader import LevelLoader

class GameManager:
    """Coordinate game state, flow, rendering phases, and input orchestration."""

    def __init__(self, start_fullscreen: bool = False):
        """Initialize runtime systems, persistent state, and the first dungeon level.

        Args:
            start_fullscreen: Whether to launch directly in fullscreen mode.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)
        pygame.display.set_caption(ScreenSettings.TITLE)
        if start_fullscreen:
            pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()

        self.setup_controllers()
        self.load_assets()
        self.dungeon = DungeonLevel(self.scaled_dirt_tiles)
        self.all_sprites = pygame.sprite.Group()
        self.audio = AudioManager()
        self.score_manager = ScoreLeaderboardManager(self)
        self.intermission = IntermissionFlow(self)
        self.game_active = False
        self.game_result = None
        self.score = 0
        self.high_score = self.score_manager.load_high_score()
        self.leaderboard = self.score_manager.load_leaderboard()
        self.level_order = list(LEVEL_DUNGEON_ORDER)
        self.level_numbers = sorted(DUNGEON_CONFIG.level_difficulty_by_number.keys())
        self.current_level_index = 0
        self.pending_level_index = 0
        self.transition_label = ""
        self.transition_end_time = 0
        self.pending_level_load = False
        self.message_success_border_until = 0
        self.r2_trigger_is_pressed = False

        # Tutorial system. Constructed lazily in start_gameplay_from_title when
        # the player chooses PLAY. Stays None for SKIP TUTORIAL runs.
        self.tutorial: TutorialManager | None = None

        self.ui_state = 'title'
        self.title_menu_index = 0
        self.npcs: list = []

        # State for game over flow and leaderboard entry.
        self.game_over_message_complete_time = 0
        self.game_over_prompt_start_time = 0
        self.pending_leaderboard_score = 0
        self.initials_entry = "AAA"
        self.initials_index = 0
        self.intermission.initialize_state()

        # Pre-create the fog surface to avoid doing it every frame during rendering.
        self.fog_surface = pygame.Surface((UISettings.ACTION_WINDOW_WIDTH, UISettings.ACTION_WINDOW_HEIGHT), pygame.SRCALPHA)

        # -------- UI windows --------
        self.message_log = MessageLog(self)
        self.inventory_window = InventoryWindow(self)
        self.map_window = MapWindow(self)
        self.map_memory = None

        # -------- Post-processing --------
        self.crt = CRT(self.screen)

        # -------- Rendering facade --------
        self.render = None

        # LevelLoader needs dungeon + all_sprites alive — both built above.
        self.level_loader = LevelLoader(self)
        self.level_loader.load_level()
        self.audio.stop_music()

    # -------------------------
    # BOOT / SETUP
    # -------------------------

    def setup_controllers(self) -> None:
        """Cache currently-connected controllers so quit-combo and event polling are cheap."""
        pygame.joystick.init()
        self.connected_joysticks = [
            pygame.joystick.Joystick(index)
            for index in range(pygame.joystick.get_count())
        ]

    def load_assets(self) -> None:
        """Load and pre-scale the dirt, dug, and wall tile surfaces used by every level."""
        self.scaled_dirt_tiles = []
        for dirt_path in AssetPaths.DIRT_TILES:
            dirt_surf = pygame.image.load(dirt_path).convert_alpha()
            self.scaled_dirt_tiles.append(
                pygame.transform.scale(dirt_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE))
            )

        dug_surf = pygame.image.load(AssetPaths.DUG_TILE).convert_alpha()
        self.scaled_dug_tile = pygame.transform.scale(
            dug_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
        )

        wall_surf = pygame.image.load(AssetPaths.WALL_TILE).convert_alpha()
        self.scaled_wall_tile = pygame.transform.scale(
            wall_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
        )

    def reset_game(self):
        """
        Restart the game by replacing the current GameManager instance
        with a brand new one.

        This is safer than trying to manually reset every subsystem,
        because it reuses the same startup path the game already uses
        when it first launches.
        """
        current_surface = pygame.display.get_surface()
        was_fullscreen = bool(current_surface and (current_surface.get_flags() & pygame.FULLSCREEN))

        new_game_manager = GameManager(start_fullscreen=was_fullscreen)
        new_game_manager.run()
        sys.exit()

    def close_game(self) -> None:
        """Close the game process cleanly."""
        pygame.quit()
        sys.exit()

    def quit_combo_pressed(self) -> bool:
        """Return True if START + SELECT + L1 + R1 are held on any controller."""
        required_buttons = InputSettings.JOY_BUTTON_QUIT_COMBO
        for joystick in self.connected_joysticks:
            if all(joystick.get_button(button) for button in required_buttons):
                return True
        return False

    @property
    def current_level_number(self) -> int:
        """Return the configured level number for the current level index.

        Returns:
            Current configured level number.
        """
        if not self.level_numbers:
            return self.current_level_index
        return self.level_numbers[self.current_level_index]

    @property
    def is_transitioning(self) -> bool:
        """Report whether a level transition card is currently active.

        Returns:
            True while transition timing is in progress.
        """
        return pygame.time.get_ticks() < self.transition_end_time

    def start_gameplay_from_title(self, skip_tutorial: bool = False) -> None:
        """Leave title screen and begin active gameplay.

        Args:
            skip_tutorial: When True, advance past level 0 (The Arena) to level 1.
        """
        self.audio.play('menu_select')
        if skip_tutorial and len(self.level_order) > 1:
            self.current_level_index = 1
            self.pending_level_index = 1
            player_progress = self.level_loader.capture_player_progress()
            self.level_loader.load_level(player_progress)
        # Activate the tutorial system only when the player chose PLAY. It
        # then runs for the entire session and is level-agnostic.
        if not skip_tutorial:
            self.tutorial = TutorialManager(self)
        else:
            self.tutorial = None
        self.ui_state = 'playing'
        self.game_active = True
        self.audio.play_random_bgm()

    def handle_title_menu_move(self, direction: int) -> None:
        """Move the title screen cursor up (-1) or down (+1)."""
        options_count = 2  # PLAY, SKIP TUTORIAL
        new_index = (self.title_menu_index + direction) % options_count
        if new_index != self.title_menu_index:
            self.title_menu_index = new_index
            self.audio.play('menu_move')

    def handle_start_press(self) -> None:
        """Handle Start/Enter based on top-level UI state."""
        if self.ui_state == 'title':
            skip = self.title_menu_index == 1
            self.start_gameplay_from_title(skip_tutorial=skip)
            return

        if self.ui_state == 'game_over' and self.score_manager.can_continue_from_game_over():
            self.score_manager.continue_from_game_over()
            return

        if self.ui_state == 'enter_initials':
            self.score_manager.submit_initials_entry()
            return

        if self.ui_state == 'leaderboard':
            self.reset_game()

    def finish_game(self, result: str) -> None:
        """End the current run, freeze world updates, and persist the high score.

        Args:
            result: Either "win" (final door cleared) or "loss" (caught by a monster).
        """
        self.game_active = False
        self.game_result = result
        self.ui_state = 'game_over'
        if self.map_memory is not None:
            # Reveal the entire map so the death/victory screen is informative.
            self.map_memory.reveal_full_terrain_memory()
        self.pending_leaderboard_score = self.score
        self.game_over_message_complete_time = 0
        self.game_over_prompt_start_time = 0
        self.audio.stop_music()
        self.score_manager.save_high_score()

    # -------------------------
    # TURN RESOLUTION
    # -------------------------

    def _trigger_npc_interaction(self, npc) -> None:
        """Give the player a random loot drop from an NPC and fade the NPC out."""
        self.log_message("IT\'S DANGEROUS TO GO ALONE! TAKE THIS!")
        found_item, amount = self.dungeon.roll_random_loot()
        loot.resolve_pickup(self, found_item, amount)
        npc.fade_pending = True
        self.npcs.remove(npc)

    def advance_turn(self):
        """
        Resolve one world step after the player commits to an action.

        This is where time passes in the dungeon: temporary effects tick down,
        monsters respond, and loss conditions are checked. Keeping that logic
        together helps the game stay consistently turn-based.
        """

        if not self.game_active:
            return

        self.map_memory.remember_visible_map_info()

        # All temporary status timers (light radius, repellent, invisibility,
        # cloak cooldown) belong to the player and tick themselves.
        self.player.tick_status_effects()

        # Check NPC adjacency: trigger interaction when player moves to a tile adjacent to an NPC.
        if self.player.is_moving:
            dest_col, dest_row = coords.screen_to_grid(
                self.player.target_pos.x, self.player.target_pos.y)
            for npc in list(self.npcs):
                npc_col, npc_row = coords.screen_to_grid(npc.position.x, npc.position.y)
                if abs(dest_col - npc_col) + abs(dest_row - npc_row) == 1:
                    self._trigger_npc_interaction(npc)

        for monster in self.monsters:
            monster.resolve_turn()

        # Remove any NPC that a monster has landed on.
        for monster in self.monsters:
            dest = monster.target_pos if monster.is_moving else monster.position
            m_col, m_row = coords.screen_to_grid(dest.x, dest.y)
            for npc in list(self.npcs):
                npc_col, npc_row = coords.screen_to_grid(npc.position.x, npc.position.y)
                if m_col == npc_col and m_row == npc_row:
                    npc.kill()
                    self.npcs.remove(npc)

        self.check_player_caught_by_monster()

        # Let the tutorial decide whether to surface its next card now that
        # the world has settled for this turn.
        if self.tutorial is not None:
            self.tutorial.on_turn_end()

    def check_player_caught_by_monster(self) -> bool:
        """Return True and end the game if any monster occupies the player's tile."""
        if not self.game_active:
            return False

        if self.player.is_invisible():
            return False

        for monster in self.monsters:
            if self.player.position == monster.position:
                self.log_message("YOU WERE CAUGHT BY THE MONSTER!")
                self.audio.play('scream')
                self.finish_game("loss")
                return True

        return False

    @property
    def is_busy(self):
        """Centralized check to see if the game is currently animating."""
        return (self.player.is_moving or
                any(monster.is_moving for monster in self.monsters) or
                self.message_log.is_typing)

    # -------------------------
    # UI PASS-THROUGHS
    # -------------------------

    def log_message(self, text, type_speed=None):
        """The central hub for all game objects to send text to the UI."""
        self.message_log.add_message(text, type_speed=type_speed)

    def notify_tutorial(self, event: str, **kwargs) -> None:
        """Forward a game-side event to the tutorial system if it exists.

        No-op when the tutorial isn't active (SKIP TUTORIAL run, or already
        torn down). Game-side call sites can call this unconditionally.
        """
        if self.tutorial is not None:
            self.tutorial.notify(event, **kwargs)

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def _tick_between_level_flow(self) -> None:
        """Advance level-transition, door-unlock, treasure-conversion, and game-over timers."""
        if self.ui_state == 'playing':
            self.intermission.update_level_transition()
            self.intermission.update_door_unlock_sequence()
            self.intermission.update_treasure_conversion()
        self.score_manager.update_game_over_flow()

    def _process_events(self) -> None:
        """Drain pygame's event queue and dispatch by event type."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self._handle_joybuttondown(event)
            elif event.type == pygame.JOYHATMOTION:
                self._handle_joyhatmotion(event)
            elif event.type == pygame.JOYAXISMOTION:
                self._handle_joyaxismotion(event)

    def _handle_keydown(self, event) -> None:
        """Route one keyboard press to the appropriate UI/gameplay handler."""
        # F11 fullscreen toggle is global and intentionally falls through so
        # other handlers still see the press.
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()

        # While a tutorial card is up it consumes ALL keyboard input so the
        # player can't accidentally play through the overlay.
        if (self.tutorial is not None and self.tutorial.is_blocking):
            self.tutorial.handle_event(event)
            return

        if self.ui_state == 'title':
            if event.key in (pygame.K_UP, pygame.K_w):
                self.handle_title_menu_move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.handle_title_menu_move(1)

        if self.in_shop_phase:
            self.intermission.handle_shop_event(event)

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.handle_start_press()

        self.score_manager.handle_initials_event(event)
        # Light-source cycling lives on the player; gameplay-state gating is
        # handled inside Player.handle_event itself.
        self.player.handle_event(event)

    def _handle_joybuttondown(self, event) -> None:
        """Route one controller button press."""
        # Catch the multi-button quit chord on press for instant response;
        # the outer per-frame check covers held-state quits.
        if self.quit_combo_pressed():
            self.close_game()

        # BACK is the global fullscreen toggle and falls through.
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()

        if (self.tutorial is not None and self.tutorial.is_blocking):
            self.tutorial.handle_event(event)
            return

        if self.in_shop_phase:
            self.intermission.handle_shop_event(event)

        if event.button in (InputSettings.JOY_BUTTON_START, InputSettings.JOY_BUTTON_A):
            self.handle_start_press()

        self.player.handle_event(event)
        self.score_manager.handle_initials_event(event)

    def _handle_joyhatmotion(self, event) -> None:
        """Route a D-pad direction event for menus."""
        if self.ui_state == 'title':
            _, hat_y = event.value
            if hat_y == 1:
                self.handle_title_menu_move(-1)
            elif hat_y == -1:
                self.handle_title_menu_move(1)

        if self.in_shop_phase:
            self.intermission.handle_shop_event(event)

        self.score_manager.handle_initials_event(event)

    def _handle_joyaxismotion(self, event) -> None:
        """Edge-triggered R2 mute toggle. L2 is reserved for the cloak action."""
        if event.axis != InputSettings.JOY_AXIS_R2:
            return
        trigger_pressed = event.value > InputSettings.JOY_TRIGGER_THRESHOLD
        if trigger_pressed and not self.r2_trigger_is_pressed:
            self.audio.toggle_mute(
                resume_music=self.game_active and not self.is_transitioning
            )
        self.r2_trigger_is_pressed = trigger_pressed

    def _update_world(self) -> None:
        """Per-frame logic: message log typewriter, tutorial drain, sprite step + animate, collision."""
        self.message_log.update()
        if self.tutorial is not None:
            self.tutorial.update()

        if self.ui_state != 'playing' or not self.game_active:
            return

        # No sprite work at all while a modal overlay is up.
        if (
            self.is_transitioning
            or self.in_treasure_conversion
            or self.in_shop_phase
            or (self.tutorial is not None and self.tutorial.is_blocking)
        ):
            return

        # Sprite update reads fresh input — skip it while animations are
        # still in flight or the player would queue inputs mid-step.
        if not self.is_busy:
            self.all_sprites.update()

        # Animation completes in-flight motion regardless of is_busy so
        # sprites always finish their current step smoothly.
        for sprite in self.all_sprites:
            if hasattr(sprite, 'animate'):
                sprite.animate()
        self.check_player_caught_by_monster()

    def _render_frame(self) -> None:
        """Compose one frame: world, HUD panels, modal overlays, then CRT."""
        self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

        if self.ui_state in {'playing', 'game_over'}:
            self.render.draw_grid_background()
            self.all_sprites.draw(self.screen)
            if self.ui_state == 'playing' and not DebugSettings.NO_FOG:
                self.render.draw_fog_of_war()
            self.render.draw_ui_frames()
            self.message_log.draw(self.screen)
            self.inventory_window.draw(self.screen)
            self.map_window.draw(self.screen)
            self.render.draw_level_transition()
            self.render.draw_treasure_conversion()
            self.render.draw_shop_menu()
            if self.tutorial is not None:
                self.tutorial.draw(self.screen)

        if self.ui_state == 'title':
            self.render.draw_title_screen()
        elif self.ui_state == 'game_over':
            self.render.draw_end_game_screens()
        elif self.ui_state == 'enter_initials':
            self.render.draw_initials_entry_screen()
        elif self.ui_state == 'leaderboard':
            self.render.draw_leaderboard_screen()

        # Apply CRT pass after world/UI rendering.
        self.crt.draw()

    def run(self):
        """Run the main game loop until the player quits."""
        while True:
            if self.quit_combo_pressed():
                self.close_game()
            self._tick_between_level_flow()
            self._process_events()
            self._update_world()
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()