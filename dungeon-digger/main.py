import pygame
import sys

from settings import *
from audio import AudioManager
from sprites import Player, Monster, Door, NPC
from windows import MessageLog, InventoryWindow, MapWindow
from dungeon import DungeonMaster
from mapmemory import MapMemory
from render import RenderManager
from crt import CRT
from tilemaps import DUNGEON_ORDER
from managers import ScoreLeaderboardManager, BetweenLevelManager

class GameManager:
    """Coordinate game state, flow, rendering phases, and input orchestration."""

    def __init__(self, start_fullscreen: bool = False):
        """Initialize runtime systems, persistent state, and the first dungeon level.

        Args:
            start_fullscreen (bool): Whether to launch directly in fullscreen mode.
        """
        # Initialize Pygame and set up the display
        pygame.init()
        self.screen = pygame.display.set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)
        pygame.display.set_caption('Dungeon Digger')
        if start_fullscreen:
            pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        
        # -------- Core subsystem initialization --------
        self.setup_controllers()
        self.load_assets()
        self.dungeon = DungeonMaster(self.scaled_dirt_tiles)
        self.all_sprites = pygame.sprite.Group()
        self.audio = AudioManager()
        self.score_manager = ScoreLeaderboardManager(self)
        self.between_level_manager = BetweenLevelManager(self)
        self.game_active = False
        self.game_result = None
        self.score = 0
        self.high_score = self.score_manager.load_high_score()
        self.leaderboard = self.score_manager.load_leaderboard()
        self.level_order = list(DUNGEON_ORDER)
        self.current_level_index = 0
        self.pending_level_index = 0
        self.transition_label = ""
        self.transition_end_time = 0
        self.pending_level_load = False
        self.message_success_border_until = 0
        self.l2_trigger_is_pressed = False
        self.ui_state = 'title'
        self.npcs: list = []

        self.game_over_message_complete_time = 0
        self.game_over_prompt_start_time = 0
        self.pending_leaderboard_score = 0
        self.initials_entry = "AAA"
        self.initials_index = 0
        self.between_level_manager.initialize_state()
        
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

        self.load_level()
        self.audio.stop_music()

        # TODO: Continue splitting run() into process_events(), update_state(), and render_frame().

    def reset_game(self):
        """
        Restart the game by replacing the current GameManager instance
        with a brand new one.

        This is safer than trying to manually reset every subsystem,
        because it reuses the same startup path the game already uses
        when it first launches.

        We will implement a more elegant reset in the future,
        but this is a good quick solution for now to speed up testing.
        """
        current_surface = pygame.display.get_surface()
        was_fullscreen = bool(current_surface and (current_surface.get_flags() & pygame.FULLSCREEN))

        new_game_manager = GameManager(start_fullscreen=was_fullscreen)
        new_game_manager.run()
        sys.exit()

        # TODO: Preserve fullscreen state through reset/restart flow.

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
        """Return the current 1-based dungeon level number.

        Returns:
            int: Current level index expressed as a human-facing number.
        """
        return self.current_level_index + 1

    @property
    def is_transitioning(self) -> bool:
        """Report whether a level transition card is currently active.

        Returns:
            bool: True while transition timing is in progress.
        """
        return pygame.time.get_ticks() < self.transition_end_time

    @property
    def is_in_treasure_conversion_phase(self) -> bool:
        """Report whether the treasure conversion UI phase is active.

        Returns:
            bool: True when conversion UI/input handling should run.
        """
        return self.in_treasure_conversion

    @property
    def is_in_shop_phase(self) -> bool:
        """Report whether the between-level shop phase is active.

        Returns:
            bool: True when shop UI/input handling should run.
        """
        return self.in_shop_phase

    def get_high_score_path(self) -> str:
        """Return the absolute path to the high-score data file.

        Returns:
            str: Filesystem path for the high-score file.
        """
        return self.score_manager.get_high_score_path()

    def get_leaderboard_path(self) -> str:
        """Return the absolute path to the leaderboard data file.

        Returns:
            str: Filesystem path for the leaderboard file.
        """
        return self.score_manager.get_leaderboard_path()

    def load_high_score(self) -> int:
        """Load the saved high score from disk if it exists."""
        return self.score_manager.load_high_score()

    def save_high_score(self) -> None:
        """Persist the best score reached so far to disk."""
        self.score_manager.save_high_score()

    def _sanitize_initials(self, initials: str) -> str:
        """Normalize initials to exactly three uppercase alphabetic characters.

        Args:
            initials (str): Raw initials input.

        Returns:
            str: Sanitized three-character initials string.
        """
        return self.score_manager.sanitize_initials(initials)

    def load_leaderboard(self) -> list[tuple[str, int]]:
        """Load top scores from disk in descending order."""
        return self.score_manager.load_leaderboard()

    def save_leaderboard(self) -> None:
        """Persist leaderboard entries to disk."""
        self.score_manager.save_leaderboard()

    def is_top_ten_score(self, score: int) -> bool:
        """Return True when score qualifies for leaderboard entry."""
        return self.score_manager.is_top_ten_score(score)

    def add_leaderboard_entry(self, initials: str, score: int) -> None:
        """Insert and persist one top-score entry."""
        self.score_manager.add_leaderboard_entry(initials, score)

    def start_gameplay_from_title(self) -> None:
        """Leave title screen and begin active gameplay."""
        self.ui_state = 'playing'
        self.game_active = True
        self.audio.play_random_bgm()

    def can_continue_from_game_over(self) -> bool:
        """Return True when the post-loss continue prompt is currently visible."""
        return self.score_manager.can_continue_from_game_over()

    def update_game_over_flow(self) -> None:
        """Wait until death text is done, then reveal the continue prompt."""
        self.score_manager.update_game_over_flow()

    def continue_from_game_over(self) -> None:
        """Advance to initials entry or directly to the leaderboard."""
        self.score_manager.continue_from_game_over()

    def submit_initials_entry(self) -> None:
        """Commit initials for this run, then show leaderboard."""
        self.score_manager.submit_initials_entry()

    def handle_initials_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard/controller input while entering leaderboard initials."""
        self.score_manager.handle_initials_event(event)

    def handle_start_press(self) -> None:
        """Handle Start/Enter based on top-level UI state."""
        if self.ui_state == 'title':
            self.start_gameplay_from_title()
            return

        if self.ui_state == 'game_over' and self.can_continue_from_game_over():
            self.continue_from_game_over()
            return

        if self.ui_state == 'enter_initials':
            self.submit_initials_entry()
            return

        if self.ui_state == 'leaderboard':
            self.reset_game()

    def capture_player_progress(self) -> dict[str, object] | None:
        """Snapshot persistent player state before rebuilding the level."""
        if not hasattr(self, 'player'):
            return None

        return {
            'inventory': self.player.inventory.copy(),
            'discovered_items': set(self.player.discovered_items),
        }

    def restore_player_progress(self, progress: dict[str, object] | None) -> None:
        """Restore inventory and discovery state after spawning a fresh player."""
        if not progress:
            return

        self.player.inventory = progress['inventory'].copy()
        self.player.discovered_items = set(progress['discovered_items'])

    def load_level(self, player_progress: dict[str, object] | None = None) -> None:
        """Build the currently selected dungeon level and spawn fresh entities."""
        self.all_sprites.empty()

        dungeon_name = self.level_order[self.current_level_index]
        self.dungeon.load_dungeon(dungeon_name)
        self.dungeon.setup_tile_map()
        self.spawn_door()
        self.spawn_monster()
        self.spawn_npcs()
        self.spawn_player()
        self.restore_player_progress(player_progress)

        self.map_memory = MapMemory(self)
        self.render = RenderManager(self)

    def start_level_transition(self) -> None:
        """Pause on a title card before loading the next dungeon."""
        self.between_level_manager.start_level_transition()

    def update_level_transition(self) -> None:
        """Load the pending dungeon once the transition card has finished."""
        self.between_level_manager.update_level_transition()

    def finish_game(self, result: str) -> None:
        """End the current run and persist the high score."""
        self.game_active = False
        self.game_result = result
        self.ui_state = 'game_over'
        self.pending_leaderboard_score = self.score
        self.game_over_message_complete_time = 0
        self.game_over_prompt_start_time = 0
        self.audio.stop_music()
        self.save_high_score()

    def handle_door_unlock(self) -> None:
        """Advance to the next dungeon, or finish the run on the last door."""
        self.between_level_manager.handle_door_unlock()

    def update_door_unlock_sequence(self) -> None:
        """Delay treasure exchange until after unlock message has finished typing."""
        self.between_level_manager.update_door_unlock_sequence()

    def remove_between_level_items(self) -> None:
        """Remove inventory items that should never carry across dungeon boundaries."""
        self.between_level_manager.remove_between_level_items()

    def start_treasure_conversion(self) -> None:
        """Collect treasures from inventory and prepare for conversion display."""
        self.between_level_manager.start_treasure_conversion()

    def update_treasure_conversion(self) -> None:
        """Handle input and state updates during treasure conversion phase."""
        self.between_level_manager.update_treasure_conversion()

    def complete_treasure_conversion(self) -> None:
        """Convert collected treasures to gold coins and proceed to the shop."""
        self.between_level_manager.complete_treasure_conversion()

    def start_shop_phase(self) -> None:
        """Open the between-level shop with refreshed stock."""
        self.between_level_manager.start_shop_phase()

    def get_shop_menu_options(self) -> list[str]:
        """Return shop items plus a continue option."""
        return self.between_level_manager.get_shop_menu_options()

    def move_shop_selection(self, delta: int) -> None:
        """Move the highlighted shop row up or down."""
        self.between_level_manager.move_shop_selection(delta)

    def _format_purchase_message(self, item_name: str, quantity: int) -> str:
        """Build purchase confirmation text with simple plural rules."""
        return self.between_level_manager.format_purchase_message(item_name, quantity)

    def buy_shop_item(self, item_name: str, quantity: int = 1) -> None:
        """Try to buy one shop item and immediately update inventory and gold."""
        self.between_level_manager.buy_shop_item(item_name, quantity)

    def complete_shop_phase(self) -> None:
        """Close the shop and begin loading the next level."""
        self.between_level_manager.complete_shop_phase()

    def handle_shop_event(self, event: pygame.event.Event) -> None:
        """Process keyboard/controller input for the between-level shop."""
        self.between_level_manager.handle_shop_event(event)

    # -------------------------
    # BOOT / SETUP
    # -------------------------

    def setup_controllers(self):
        """Initializes connected gamepads or joysticks."""
        pygame.joystick.init()
        # Cache all currently connected controllers.
        self.connected_joysticks = [pygame.joystick.Joystick(index) for index in range(pygame.joystick.get_count())]

    def load_assets(self):
        """Handle all image loading and scaling in one place."""
        self.scaled_dirt_tiles = []

        for dirt_path in AssetPaths.DIRT_TILES:
            dirt_surf = pygame.image.load(dirt_path).convert_alpha()
            scaled_dirt = pygame.transform.scale(
                dirt_surf,
                (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE)
            )
            self.scaled_dirt_tiles.append(scaled_dirt)
        
        dug_surf = pygame.image.load(AssetPaths.DUG_TILE).convert_alpha()
        self.scaled_dug_tile = pygame.transform.scale(dug_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE))

        wall_surf = pygame.image.load(AssetPaths.WALL_TILE).convert_alpha()
        self.scaled_wall_tile = pygame.transform.scale(wall_surf, (GridSettings.TILE_SIZE, GridSettings.TILE_SIZE))

    # -------------------------
    # ENTITY SPAWNING --> SpawnManager Class? (probably not a priority)
    # -------------------------

    def spawn_player(self):
        """Spawn the player sprite at the precomputed dungeon spawn tile."""
        col, row = self.dungeon.player_grid_pos
        x, y = self.grid_to_screen(col, row)
        self.player = Player(self, (x, y), self.all_sprites)

    def spawn_monster(self):
        """Spawn all monster sprites at the precomputed dungeon spawn tiles."""
        self.monsters = []
        for col, row in self.dungeon.monster_grid_positions:
            x, y = self.grid_to_screen(col, row)
            monster = Monster(self, (x, y), self.all_sprites)
            self.monsters.append(monster)

    def spawn_door(self):
        """Spawn the level door sprite at the precomputed dungeon door tile."""
        col, row = self.dungeon.door_grid_pos
        x, y = self.grid_to_screen(col, row)
        self.door = Door(self, (x, y), self.all_sprites)

    def spawn_npcs(self):
        """Spawn NPC sprites at the precomputed dungeon NPC positions."""
        self.npcs = []
        for col, row in self.dungeon.npc_grid_positions:
            x, y = self.grid_to_screen(col, row)
            npc = NPC(self, (x, y), self.all_sprites)
            self.npcs.append(npc)

    def _trigger_npc_interaction(self, npc) -> None:
        """Give the player a random item from an NPC then remove it."""
        self.log_message("IT'S DANGEROUS TO GO ALONE! TAKE THIS!")

        found_item, amount = self.dungeon.roll_random_loot()
        if found_item:
            display_name = found_item
            if amount > 1:
                if found_item == "TORCH":
                    display_name = "TORCHES"
                elif found_item == "MATCH":
                    display_name = "MATCHES"
                elif found_item.endswith("Y"):
                    display_name = found_item[:-1] + "IES"
                elif not found_item.endswith("S"):
                    display_name = found_item + "S"

            if found_item in ItemSettings.TREASURE_SCORE_VALUES:
                self.add_score(found_item, amount)

            if amount > 1:
                self.log_message(f"YOU FOUND {amount} {display_name}!")
            elif found_item == "MONSTER REPELLENT":
                self.log_message("YOU FOUND A CAN OF MONSTER REPELLENT!")
            else:
                article = 'AN' if found_item[0] in 'AEIOU' else 'A'
                self.log_message(f"YOU FOUND {article} {found_item}!")

            if found_item == "GOLD COINS" or found_item in ["RUBY", "SAPPHIRE", "EMERALD", "DIAMOND"]:
                self.audio.play_coin_sound()

            if found_item == "MAGIC MAP" and self.player.inventory.get("MAP", 0) > 0:
                self.player.inventory["MAP"] -= 1
                if self.player.inventory["MAP"] <= 0:
                    self.player.inventory.pop("MAP", None)

            self.player.inventory[found_item] = self.player.inventory.get(found_item, 0) + amount
            self.player.discovered_items.add(found_item)

            if found_item in ["MAP", "MAGIC MAP"]:
                self.map_memory.reveal_full_terrain_memory()

        npc.fade_pending = True
        self.npcs.remove(npc)

    # TODO: Refactor spawning helpers into a dedicated SpawnManager when setup logic grows further.

    # -------------------------
    # COORDINATE + MAP HELPERS --> Future MapUtils Class?
    # -------------------------

    def grid_to_screen(self, col, row):
        """Convert grid coordinates to top-left screen pixel coordinates.

        Args:
            col: Grid column.
            row: Grid row.

        Returns:
            tuple[int, int]: Screen-space pixel coordinates.
        """
        return (
            UISettings.ACTION_WINDOW_X + col * GridSettings.TILE_SIZE,
            UISettings.ACTION_WINDOW_Y + row * GridSettings.TILE_SIZE,
        )

    def screen_to_grid(self, x, y):
        """Convert screen pixel coordinates to grid coordinates.

        Args:
            x: Screen-space x position.
            y: Screen-space y position.

        Returns:
            tuple[int, int]: Grid column and row indices.
        """
        return (
            int((x - UISettings.ACTION_WINDOW_X) // GridSettings.TILE_SIZE),
            int((y - UISettings.ACTION_WINDOW_Y) // GridSettings.TILE_SIZE),
        )

    # TODO: Refactor coordinate conversion helpers into a small utility class/module shared by gameplay systems.

    # -------------------------
    # TURN / GAME STATE --> TurnManager Class (maybe not is_busy())
    # -------------------------

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

        # Handle Light Shrinking
        if self.player.light_turns_left > 0:
            self.player.light_turns_left -= 1
            
            if self.player.light_turns_left > 0:
                # Calculate how much radius we have per turn of life
                # We use the starting radius of the current light source
                unit_radius = self.player.active_light_max_radius / self.player.active_light_max_duration
                self.player.light_radius = unit_radius * self.player.light_turns_left
            else:
                # It hit zero
                self.player.light_radius = LightSettings.DEFAULT_RADIUS
                self.log_message("YOUR LIGHT FLICKERS OUT...")

        # Handle Repellent Duration
        if self.player.repellent_turns > 0:
            self.player.repellent_turns -= 1
            if self.player.repellent_turns == 0:
                self.log_message("THE SCENT OF THE REPELLENT FADES AWAY...")

        # Handle Invisibility Cloak Duration
        if self.player.invisibility_turns > 0:
            self.player.invisibility_turns -= 1
            if self.player.invisibility_turns == 0:
                self.log_message("THE INVISIBILITY WEARS OFF.")
                if self.player.invisibility_from_cloak:
                    self.player.invisibility_cooldown_turns = (
                        ItemSettings.INVISIBILITY_CLOAK_COOLDOWN + GameSettings.STATUS_EFFECT_TURN_BUFFER
                    )
                    self.player.invisibility_from_cloak = False

        # Handle Invisibility Cloak Cooldown
        if self.player.invisibility_cooldown_turns > 0:
            self.player.invisibility_cooldown_turns -= 1

        # Check NPC adjacency: trigger interaction when player moves to a tile adjacent to an NPC.
        if self.player.is_moving:
            dest_col, dest_row = self.screen_to_grid(
                self.player.target_pos.x, self.player.target_pos.y)
            for npc in list(self.npcs):
                npc_col, npc_row = self.screen_to_grid(npc.position.x, npc.position.y)
                if abs(dest_col - npc_col) + abs(dest_row - npc_row) == 1:
                    self._trigger_npc_interaction(npc)

        for monster in self.monsters:
            monster.resolve_turn()

        # Remove any NPC that a monster has landed on.
        for monster in self.monsters:
            dest = monster.target_pos if monster.is_moving else monster.position
            m_col, m_row = self.screen_to_grid(dest.x, dest.y)
            for npc in list(self.npcs):
                npc_col, npc_row = self.screen_to_grid(npc.position.x, npc.position.y)
                if m_col == npc_col and m_row == npc_row:
                    npc.kill()
                    self.npcs.remove(npc)

        self.check_player_caught_by_monster()

    def check_player_caught_by_monster(self) -> bool:
        """Return True and end the game if any monster occupies the player's tile."""
        if not self.game_active:
            return False

        if self.player.is_invisible():
            return False

        for monster in self.monsters:
            if self.player.position == monster.position:
                self.log_message("YOU WERE CAUGHT BY THE MONSTER!")
                self.audio.play_scream_sound()
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
    # -------------------------
    # UI / GAME FEEDBACK
    # -------------------------
    # -------------------------
    
    def log_message(self, text, type_speed=None):
        """The central hub for all game objects to send text to the UI."""
        self.message_log.add_message(text, type_speed=type_speed)

    # -------------------------
    # Score
    # -------------------------

    def add_score(self, item_name: str, amount: int = 1) -> None:
        """Increase the run score based on treasure value and quantity.

        Args:
            item_name (str): Treasure item key used to look up score value.
            amount (int): Quantity of the item collected.
        """
        self.score_manager.add_score(item_name, amount)

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def run(self):
        """
        Run the game loop.
        """
        # TODO: Split run() into process_events(), update_state(), and render_frame() for maintainability.
        # TODO: Introduce an InputMap/Controls constants group to remove button/axis magic numbers in this loop.
        # Main game loop
        while True:
            if self.quit_combo_pressed():
                self.close_game()

            if self.ui_state == 'playing':
                self.update_level_transition()
                self.update_door_unlock_sequence()
                self.update_treasure_conversion()

            self.update_game_over_flow()

            # -------- Event handling --------
            for event in pygame.event.get():
                # Exit request.
                if event.type == pygame.QUIT:
                    self.close_game()

                # Keyboard input routes.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

                    if self.is_in_shop_phase:
                        self.handle_shop_event(event)

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.handle_start_press()

                    self.handle_initials_event(event)

                # Controller button input routes.
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.quit_combo_pressed():
                        self.close_game()

                    if event.button == InputSettings.JOY_BUTTON_FULLSCREEN:
                        pygame.display.toggle_fullscreen()

                    if self.is_in_shop_phase:
                        self.handle_shop_event(event)

                    if event.button == InputSettings.JOY_BUTTON_START:
                        self.handle_start_press()

                    self.handle_initials_event(event)

                if event.type == pygame.JOYHATMOTION and self.is_in_shop_phase:
                    self.handle_shop_event(event)

                if event.type == pygame.JOYHATMOTION:
                    self.handle_initials_event(event)

                # Controller trigger mute toggle (edge-triggered).
                if event.type == pygame.JOYAXISMOTION and event.axis in (InputSettings.JOY_AXIS_L2, InputSettings.JOY_AXIS_R2):
                    trigger_pressed = event.value > InputSettings.JOY_TRIGGER_THRESHOLD
                    if trigger_pressed and not self.l2_trigger_is_pressed:
                        is_muted = self.audio.toggle_mute(
                            resume_music=self.game_active and not self.is_transitioning
                        )
                        self.log_message("AUDIO MUTED." if is_muted else "AUDIO UNMUTED.")
                    self.l2_trigger_is_pressed = trigger_pressed

            # -------- Per-frame update --------
            self.message_log.update()
            if self.ui_state == 'playing' and self.game_active:
                if not self.is_transitioning and not self.is_busy and not self.is_in_treasure_conversion_phase and not self.is_in_shop_phase:
                    self.all_sprites.update()

                if not self.is_transitioning and not self.is_in_treasure_conversion_phase and not self.is_in_shop_phase:
                    # Always advance movement animation to complete in-flight motion.
                    # TODO: Replace hasattr('animate') with a protocol/base class for animatable sprites.
                    for sprite in self.all_sprites:
                        if hasattr(sprite, 'animate'):
                            sprite.animate()

                    # Resolve collisions immediately after movement completes.
                    self.check_player_caught_by_monster()

            # -------- Rendering --------
            self.screen.fill(ColorSettings.SCREEN_BACKGROUND)

            if self.ui_state in {'playing', 'game_over'}:
                self.render.draw_grid_background()
                self.all_sprites.draw(self.screen)

                if not DebugSettings.NO_FOG:
                    self.render.draw_fog_of_war()
                self.render.draw_ui_frames()
                self.message_log.draw(self.screen)
                self.inventory_window.draw(self.screen)
                self.map_window.draw(self.screen)
                self.render.draw_level_transition()
                self.render.draw_treasure_conversion()
                self.render.draw_shop_menu()

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

            pygame.display.flip()
            self.clock.tick(ScreenSettings.FPS)
 
if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()