"""ArcadeLauncher: coordinator for input, navigation, audio, and game launching."""

import subprocess
import sys
from pathlib import Path

import pygame

from launcher.crt import LauncherCRT
from launcher.discovery import discover_student_games
from launcher.models import MenuFrame, MenuNode
from launcher.renderer import LauncherRenderer
from settings import (
    CategorySettings,
    ColorSettings,
    ControlSettings,
    CRTSettings,
    GameSettings,
    GroupSettings,
    LauncherSettings,
    MenuTreeSettings,
    ScreenSettings,
    StudentGameSettings,
)


class ArcadeLauncher:
    """Coordinate input, menu navigation, audio, and game launching."""

    def __init__(self, root_dir: Path) -> None:
        """
        Create launcher systems, load resources, and initialize menu state.

        Args:
            root_dir (Path): Absolute path to the launcher's root directory.
        """
        self.root_dir = root_dir
        self.vertical_axis_engaged = False
        self.status_message = ""
        self.status_message_until = 0

        self.initialize_runtime()
        # Renderer loads fonts and logo after display init so convert_alpha() works.
        self.renderer = LauncherRenderer(self.screen, self.root_dir, self.crt)
        self.load_menu_audio()

        # Build the unified games dict (sponsor + student), load preview images,
        # then walk MenuTreeSettings.ROOT to construct the navigation tree.
        self.games: dict[str, MenuNode] = self._build_games()
        self.renderer.preview_images = self._load_preview_images()
        self.menu_stack: list[MenuFrame] = [MenuFrame(items=self._build_root_items())]

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize_runtime(self) -> None:
        """Initialize pygame systems required for rendering and input handling."""
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
        pygame.display.set_caption(LauncherSettings.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.crt = LauncherCRT(self.screen, self.root_dir / CRTSettings.OVERLAY_IMAGE)

    def _restore_runtime(self) -> None:
        """Reinitialize pygame and rebuild the renderer after a game exits."""
        self.initialize_runtime()
        self.renderer = LauncherRenderer(self.screen, self.root_dir, self.crt)
        # Reload previews because the old display context was destroyed.
        self.renderer.preview_images = self._load_preview_images()
        self.vertical_axis_engaged = False

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------

    def _load_sound_if_available(self, sound_path: Path) -> pygame.mixer.Sound | None:
        """
        Load a sound file if both the mixer and the file are available.

        Args:
            sound_path (Path): Absolute path to the sound file.

        Returns:
            pygame.mixer.Sound | None: The loaded sound, or None on failure.
        """
        if not sound_path.exists():
            return None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return pygame.mixer.Sound(str(sound_path))
        except pygame.error:
            return None

    def load_menu_audio(self) -> None:
        """Load menu move/select sounds with graceful fallback if files are missing."""
        self.menu_move_sfx = self._load_sound_if_available(
            self.root_dir / LauncherSettings.MENU_MOVE_SOUND
        )
        self.menu_select_sfx = None
        for candidate in LauncherSettings.MENU_SELECT_SOUND_CANDIDATES:
            loaded = self._load_sound_if_available(self.root_dir / candidate)
            if loaded is not None:
                self.menu_select_sfx = loaded
                break

    def _play_move_sfx(self) -> None:
        """Play the move SFX (used for cursor movement and back navigation)."""
        if self.menu_move_sfx is not None:
            self.menu_move_sfx.play()

    def _play_select_sfx(self) -> None:
        """Play the select SFX (used for launching games and entering submenus)."""
        if self.menu_select_sfx is not None:
            self.menu_select_sfx.play()

    # ------------------------------------------------------------------
    # Menu tree construction
    # ------------------------------------------------------------------

    def _build_games(self) -> dict[str, MenuNode]:
        """
        Combine sponsor and student games into MenuNode objects keyed by label.

        Returns:
            dict[str, MenuNode]: All discovered games, keyed by display label.
        """
        games: dict[str, MenuNode] = {}

        for label, relative_path in GameSettings.OPTIONS:
            # Infer category from the sponsor subfolder (original, tribute, tutorial)
            try:
                category_folder = relative_path.parts[2]  # games/sponsor/<category>/<game>
            except IndexError:
                category_folder = None
            if category_folder == "original":
                category_key = CategorySettings.ORIGINAL
            elif category_folder == "tribute":
                category_key = CategorySettings.TRIBUTE
            elif category_folder == "tutorial":
                category_key = CategorySettings.TUTORIAL
            else:
                category_key = None

            preview_relative = GameSettings.PREVIEW_IMAGES.get(label)
            games[label] = MenuNode(
                kind="game",
                label=label,
                main_path=self.root_dir / relative_path,
                preview_path=self.root_dir / preview_relative if preview_relative else None,
                preview_label=label,
                attribution=GameSettings.GAME_DESCRIPTIONS.get(label, ""),
                input_scheme_key=GameSettings.GAME_INPUT_SCHEMES.get(label),
                note=GameSettings.GAME_NOTES.get(label),
                under_construction=label in GameSettings.UNDER_CONSTRUCTION_GAMES,
                category_key=category_key,
            )

        for record in discover_student_games(self.root_dir / StudentGameSettings.ROOT):
            games[record.label] = MenuNode(
                kind="game",
                label=record.label,
                main_path=record.main_path,
                preview_path=record.preview_path,
                preview_label=record.label,
                attribution=record.attribution,
                input_scheme_key=record.input_scheme_key,
                note=record.note,
                under_construction=record.under_construction,
                category_key=CategorySettings.STUDENT,
            )

        return games

    def _load_preview_images(self) -> dict[str, pygame.Surface]:
        """
        Load and scale preview screenshots keyed by game label.

        Returns:
            dict[str, pygame.Surface]: Scaled preview surfaces, keyed by label.
        """
        preview_images: dict[str, pygame.Surface] = {}
        max_width = LauncherSettings.PREVIEW_MAX_WIDTH
        max_height = LauncherSettings.PREVIEW_MAX_HEIGHT

        for label, node in self.games.items():
            if node.preview_path is None:
                continue
            try:
                surface = pygame.image.load(str(node.preview_path)).convert()
            except (FileNotFoundError, pygame.error):
                continue
            if surface.get_width() == 0 or surface.get_height() == 0:
                continue
            scale_ratio = min(
                max_width / surface.get_width(),
                max_height / surface.get_height(),
            )
            target_size = (
                max(1, int(surface.get_width() * scale_ratio)),
                max(1, int(surface.get_height() * scale_ratio)),
            )
            preview_images[label] = pygame.transform.smoothscale(surface, target_size)

        return preview_images

    def _filter_games_by_category(self, category_key: str) -> list[MenuNode]:
        """
        Return all game nodes belonging to ``category_key``, sorted by label.

        Args:
            category_key (str): The category constant to filter by.

        Returns:
            list[MenuNode]: Matching game nodes in alphabetical order.
        """
        return sorted(
            (g for g in self.games.values() if g.category_key == category_key),
            key=lambda g: g.label,
        )

    def _build_menu_node_for_spec(self, spec: dict) -> MenuNode:
        """
        Walk one MenuTreeSettings entry and return its MenuNode subtree.

        Args:
            spec (dict): A menu spec dict with ``kind`` and ``key`` fields.

        Returns:
            MenuNode: The constructed node (and its children, recursively).
        """
        kind_in_spec = spec["kind"]
        key = spec["key"]
        if kind_in_spec == MenuTreeSettings.KIND_CATEGORY:
            return MenuNode(
                kind="submenu",
                label=CategorySettings.LABELS[key],
                description=CategorySettings.DESCRIPTIONS.get(key, ""),
                children=self._filter_games_by_category(key),
            )
        if kind_in_spec == MenuTreeSettings.KIND_GROUP:
            return MenuNode(
                kind="submenu",
                label=GroupSettings.LABELS[key],
                description=GroupSettings.DESCRIPTIONS.get(key, ""),
                children=[self._build_menu_node_for_spec(child) for child in spec.get("children", [])],
            )
        raise ValueError(f"Unknown menu spec kind: {kind_in_spec!r}")

    def _build_root_items(self) -> list[MenuNode]:
        """
        Build the top-level menu items from MenuTreeSettings.ROOT.

        Returns:
            list[MenuNode]: Root-level menu nodes.
        """
        return [self._build_menu_node_for_spec(spec) for spec in MenuTreeSettings.ROOT]

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def current_frame(self) -> MenuFrame:
        """
        Return the currently visible menu frame (top of the stack).

        Returns:
            MenuFrame: The active menu frame.
        """
        return self.menu_stack[-1]

    def current_node(self) -> MenuNode | None:
        """
        Return the currently highlighted node, or None if the frame is empty.

        Returns:
            MenuNode | None: The highlighted node, or None.
        """
        frame = self.current_frame()
        if not frame.items:
            return None
        return frame.items[frame.selected_index]

    def _set_selected_index(self, new_index: int) -> None:
        """
        Update selection in the active frame and play the move SFX on change.

        Args:
            new_index (int): The desired index (will be wrapped around the item count).
        """
        frame = self.current_frame()
        count = len(frame.items)
        if count == 0:
            return
        wrapped_index = new_index % count
        if wrapped_index == frame.selected_index:
            return
        frame.selected_index = wrapped_index
        self._play_move_sfx()

    def move_selection_up(self) -> None:
        """Move the cursor to the previous item with wrap-around."""
        self._set_selected_index(self.current_frame().selected_index - 1)

    def move_selection_down(self) -> None:
        """Move the cursor to the next item with wrap-around."""
        self._set_selected_index(self.current_frame().selected_index + 1)

    def enter_selected_node(self) -> None:
        """Forward action: launch a game, push a submenu, or no-op on empty submenus."""
        node = self.current_node()
        if node is None:
            return
        if node.kind == "game":
            self.launch_selected_game(node)
            return
        # Submenu node. Always play the select SFX so empty leaves still
        # give audio feedback ("ka-chunk, nothing here yet").
        self._play_select_sfx()
        if node.children:
            self.menu_stack.append(MenuFrame(items=list(node.children)))

    def back_to_previous(self) -> bool:
        """
        Pop one level off the menu stack.

        Returns:
            bool: True if a level was popped, False if already at root.
        """
        if len(self.menu_stack) > 1:
            self._play_move_sfx()
            self.menu_stack.pop()
            return True
        return False

    # ------------------------------------------------------------------
    # Status message
    # ------------------------------------------------------------------

    def show_status_message(self, message: str, duration_ms: int = 3500) -> None:
        """
        Display a temporary status/error message at the bottom of the screen.

        Args:
            message (str): The message to display.
            duration_ms (int): How long (in ms) to show the message.
        """
        self.status_message = message
        self.status_message_until = pygame.time.get_ticks() + duration_ms

    # ------------------------------------------------------------------
    # Game launch
    # ------------------------------------------------------------------

    def suspend_runtime(self) -> None:
        """Shut down launcher rendering/input systems before child game launch."""
        pygame.display.quit()
        pygame.joystick.quit()
        pygame.quit()

    def show_loading_screen(self, duration_ms: int = 2200) -> None:
        """
        Show a temporary loading screen before launching a selected game.

        Args:
            duration_ms (int): How long (in ms) to display the loading screen.
        """
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # Animate trailing dots so players can tell the launcher is active.
            dot_count = ((pygame.time.get_ticks() - start_time) // 350) % 4
            self.renderer.draw_loading_frame(f"LOADING{'.' * dot_count}")
            self.clock.tick(ScreenSettings.FPS)

    def launch_selected_game(self, node: MenuNode) -> None:
        """
        Launch the given game node, then restore launcher runtime after exit.

        Args:
            node (MenuNode): The game node to launch.
        """
        self._play_select_sfx()
        self.show_loading_screen()
        game_main = node.main_path
        if game_main is None:
            self.show_status_message(f"Cannot launch {node.label}: no entry path.")
            return
        game_dir = game_main.parent

        if not game_dir.exists():
            self.show_status_message(f"Cannot launch {node.label}: folder not found.")
            return

        if not game_main.exists():
            self.show_status_message(f"Cannot launch {node.label}: main.py not found.")
            return

        self.suspend_runtime()

        try:
            subprocess.run(
                [sys.executable, str(game_main)],
                cwd=str(game_dir),
                check=False,
            )
        except OSError as error:
            self._restore_runtime()
            self.show_status_message(f"Failed to launch {node.label}: {error}")
            return
        finally:
            if not pygame.get_init():
                self._restore_runtime()

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def handle_controller_buttons(self, event: pygame.event.Event) -> None:
        """
        Process controller button presses for launcher actions.

        Args:
            event (pygame.event.Event): A JOYBUTTONDOWN event.
        """
        if event.button == ControlSettings.CONTROLLER_BUTTON_SELECT:
            pygame.display.toggle_fullscreen()
        elif event.button in (
            ControlSettings.CONTROLLER_BUTTON_A,
            ControlSettings.CONTROLLER_BUTTON_START,
        ):
            self.enter_selected_node()
        elif event.button == ControlSettings.CONTROLLER_BUTTON_B:
            # B at root is a no-op; ESC or the window close button quits.
            self.back_to_previous()

    def handle_hat_navigation(self, event: pygame.event.Event) -> None:
        """
        Process D-pad/hat navigation input.

        Args:
            event (pygame.event.Event): A JOYHATMOTION event.
        """
        if event.value[1] > 0:
            self.move_selection_up()
        elif event.value[1] < 0:
            self.move_selection_down()

    def handle_axis_navigation(self, event: pygame.event.Event) -> None:
        """
        Process analog-stick vertical navigation with edge-triggered debounce.

        Args:
            event (pygame.event.Event): A JOYAXISMOTION event.
        """
        if event.axis != ControlSettings.CONTROLLER_NAV_AXIS:
            return

        if event.value <= -ControlSettings.CONTROLLER_AXIS_DEADZONE and not self.vertical_axis_engaged:
            self.move_selection_up()
            self.vertical_axis_engaged = True
        elif event.value >= ControlSettings.CONTROLLER_AXIS_DEADZONE and not self.vertical_axis_engaged:
            self.move_selection_down()
            self.vertical_axis_engaged = True
        elif -ControlSettings.CONTROLLER_AXIS_DEADZONE < event.value < ControlSettings.CONTROLLER_AXIS_DEADZONE:
            self.vertical_axis_engaged = False

    def handle_keyboard(self, event: pygame.event.Event) -> bool:
        """
        Process keyboard input and report whether the launcher should continue.

        Args:
            event (pygame.event.Event): A KEYDOWN event.

        Returns:
            bool: False if the launcher should quit, True otherwise.
        """
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.move_selection_up()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection_down()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.enter_selected_node()
        elif event.key == pygame.K_ESCAPE:
            # ESC backs out of nested menus; at the root it quits so keyboard
            # users always have an exit.
            if not self.back_to_previous():
                return False
        return True

    def handle_mouse(self, event: pygame.event.Event) -> None:
        """
        Support hover-to-select and click-to-launch for menu options.

        Args:
            event (pygame.event.Event): A MOUSEMOTION or MOUSEBUTTONDOWN event.
        """
        hitboxes = self.renderer.menu_option_hitboxes
        if not hitboxes:
            return

        if event.type == pygame.MOUSEMOTION:
            for index, hitbox in enumerate(hitboxes):
                if hitbox.collidepoint(event.pos):
                    self._set_selected_index(index)
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, hitbox in enumerate(hitboxes):
                if hitbox.collidepoint(event.pos):
                    self._set_selected_index(index)
                    self.enter_selected_node()
                    break

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the launcher event loop until the user quits."""
        running = True
        self.renderer.draw(
            self.current_frame(), self.current_node(),
            self.status_message, self.status_message_until,
        )
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.handle_controller_buttons(event)
                elif event.type == pygame.JOYHATMOTION:
                    self.handle_hat_navigation(event)
                elif event.type == pygame.JOYAXISMOTION:
                    self.handle_axis_navigation(event)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    self.handle_mouse(event)
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_keyboard(event)

            self.renderer.draw(
                self.current_frame(), self.current_node(),
                self.status_message, self.status_message_until,
            )
            self.clock.tick(ScreenSettings.FPS)

        pygame.quit()

