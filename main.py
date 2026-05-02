"""Top-level launcher that allows players to choose which arcade game to run."""

import json
import random
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


import pygame

from settings import (
	CRTSettings,
	CategorySettings,
	ColorSettings,
	ControlSettings,
	FontSettings,
	GameSettings,
	GroupSettings,
	InputSchemeSettings,
	LauncherSettings,
	MenuSettings,
	MenuTreeSettings,
	ScreenSettings,
	StudentGameSettings,
)


@dataclass(frozen=True)
class StudentGameRecord:
	"""Discovered metadata for a single student-contributed game.

	Sponsor games are curated in settings.GameSettings; student games are
	scanned from disk so a teacher can drop a folder into games/student/
	without editing any code. Records bundle every override the launcher
	might apply (label, attribution, preview, input scheme, free-form
	note, under-construction flag) so the merge step in
	ArcadeLauncher._build_games stays straightforward.
	"""

	label: str
	main_path: Path
	attribution: str
	preview_path: Path | None
	input_scheme_key: str | None
	note: str | None
	under_construction: bool


@dataclass
class MenuNode:
	"""One row in a menu frame.

	A node is either a game (selecting it launches a subprocess) or a
	submenu (selecting it pushes its children onto the menu stack). The
	game-only fields stay at their defaults on submenu nodes; the
	``children`` list stays empty on game nodes and on category leaves
	that currently have no games (e.g. an empty Student Games folder).
	"""

	kind: str  # "game" or "submenu"
	label: str
	description: str = ""
	children: list["MenuNode"] = field(default_factory=list)
	# Game-only fields below. Defaults match "no metadata available".
	main_path: Path | None = None
	preview_path: Path | None = None
	preview_label: str | None = None
	attribution: str = ""
	input_scheme_key: str | None = None
	note: str | None = None
	under_construction: bool = False
	category_key: str | None = None


@dataclass
class MenuFrame:
	"""One level on the navigation stack.

	Tracks the items rendered for this level plus the cursor position so
	that backing out and re-entering a submenu lands on the same row.
	"""

	items: list[MenuNode]
	selected_index: int = 0


def _read_student_manifest(manifest_path: Path) -> dict:
	"""Load a student game manifest, returning {} on any read or parse error.

	Args:
		manifest_path (Path): Absolute path to the candidate game.json file.

	Returns:
		dict: Parsed manifest dictionary, or an empty dict if the file is
		missing, unreadable, malformed JSON, or not a JSON object. The
		launcher must keep starting even if one student's manifest is broken.
	"""
	if not manifest_path.is_file():
		return {}
	try:
		parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
	except (OSError, json.JSONDecodeError):
		return {}
	return parsed if isinstance(parsed, dict) else {}


def discover_student_games(student_root: Path) -> list[StudentGameRecord]:
	"""Scan student_root for game folders and return one record per game.

	A folder qualifies if it contains StudentGameSettings.ENTRY_FILENAME
	(typically main.py). A sibling StudentGameSettings.MANIFEST_FILENAME
	(game.json) may override label, attribution, preview, input scheme,
	free-form note, and under-construction flag; any field omitted from
	the manifest falls back to the launcher's default. The folder is
	created if missing so a fresh clone of the repo still runs without
	errors -- the directory is .gitignored, not committed.

	Args:
		student_root (Path): Absolute path to the games/student/ directory.

	Returns:
		list[StudentGameRecord]: One record per discovered game, sorted by
		folder name so menu order stays stable across runs.
	"""
	student_root.mkdir(parents=True, exist_ok=True)

	records: list[StudentGameRecord] = []
	for entry in sorted(student_root.iterdir()):
		# Hidden folders (e.g. .git, .vscode) are intentionally skipped so a
		# tooling directory dropped in by accident never shows up as a game.
		if not entry.is_dir() or entry.name.startswith("."):
			continue

		main_path = entry / StudentGameSettings.ENTRY_FILENAME
		if not main_path.is_file():
			continue

		# Folder name -> "Red Square" so a manifest is optional. Hyphens and
		# underscores both turn into spaces because students use both.
		default_label = entry.name.replace("-", " ").replace("_", " ").title()

		manifest = _read_student_manifest(entry / StudentGameSettings.MANIFEST_FILENAME)

		label_value = manifest.get(StudentGameSettings.MANIFEST_KEY_LABEL)
		label = label_value if isinstance(label_value, str) and label_value else default_label

		attribution_value = manifest.get(StudentGameSettings.MANIFEST_KEY_ATTRIBUTION)
		attribution = (
			attribution_value
			if isinstance(attribution_value, str) and attribution_value
			else StudentGameSettings.DEFAULT_ATTRIBUTION
		)

		preview_value = manifest.get(StudentGameSettings.MANIFEST_KEY_PREVIEW)
		preview_path = entry / preview_value if isinstance(preview_value, str) and preview_value else None

		# input_scheme is only honored if it matches a known scheme key.
		# Anything else (typo, removed key) is silently ignored so the menu
		# never crashes on a malformed manifest.
		input_scheme_value = manifest.get(StudentGameSettings.MANIFEST_KEY_INPUT_SCHEME)
		input_scheme_key = (
			input_scheme_value
			if isinstance(input_scheme_value, str) and input_scheme_value in InputSchemeSettings.LABELS
			else None
		)

		note_value = manifest.get(StudentGameSettings.MANIFEST_KEY_NOTE)
		note = note_value if isinstance(note_value, str) and note_value else None

		records.append(
			StudentGameRecord(
				label=label,
				main_path=main_path,
				attribution=attribution,
				preview_path=preview_path,
				input_scheme_key=input_scheme_key,
				note=note,
				under_construction=bool(manifest.get(StudentGameSettings.MANIFEST_KEY_UNDER_CONSTRUCTION)),
			)
		)

	return records


class LauncherCRT:
	"""Render a CRT-style overlay on top of the launcher scene."""

	def __init__(self, screen: pygame.Surface, tv_image_path: Path) -> None:
		"""Initialize overlay texture and target render surface."""
		self.screen = screen
		# Fall back to a transparent surface if the CRT texture is missing.
		try:
			self.base_tv = pygame.image.load(str(tv_image_path)).convert_alpha()
			self.base_tv = pygame.transform.scale(self.base_tv, ScreenSettings.RESOLUTION)
		except (FileNotFoundError, pygame.error):
			self.base_tv = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)

	def create_crt_lines(self, surf: pygame.Surface) -> None:
		"""Draw scan lines onto a temporary overlay surface."""
		for y_pos in range(0, ScreenSettings.HEIGHT, CRTSettings.SCANLINE_HEIGHT):
			pygame.draw.line(
				surf,
				ColorSettings.BLACK,
				(0, y_pos),
				(ScreenSettings.WIDTH, y_pos),
				1,
			)

	def draw(self) -> None:
		"""Blit a flickering CRT overlay for retro visual treatment."""
		tv = self.base_tv.copy()
		tv.set_alpha(random.randint(*CRTSettings.ALPHA_RANGE))
		self.create_crt_lines(tv)
		self.screen.blit(tv, (0, 0))


class ArcadeLauncher:
	"""Coordinate input, menu rendering, and launching selected games."""

	def __init__(self) -> None:
		"""Create launcher systems, load resources, and initialize menu state."""
		self.root_dir = Path(__file__).resolve().parent
		self.font_path = self.root_dir / FontSettings.FILE
		self.tv_path = self.root_dir / CRTSettings.OVERLAY_IMAGE
		self.menu_move_sound_path = self.root_dir / LauncherSettings.MENU_MOVE_SOUND
		self.menu_select_sound_paths = [
			self.root_dir / candidate for candidate in LauncherSettings.MENU_SELECT_SOUND_CANDIDATES
		]
		self.menu_move_sfx: pygame.mixer.Sound | None = None
		self.menu_select_sfx: pygame.mixer.Sound | None = None

		# Prepare logo path, but load after display is initialized.
		self.jil_logo_path = self.root_dir / LauncherSettings.JIL_LOGO_PATH
		self.jil_logo_surface = None

		self.initialize_runtime()
		# Logo loads after initialize_runtime so the convert_alpha() call has
		# a real display context. A missing or corrupt file is non-fatal; the
		# draw path falls back to a placeholder rect.
		try:
			logo_img = pygame.image.load(str(self.jil_logo_path)).convert_alpha()
			self.jil_logo_surface = pygame.transform.smoothscale(logo_img, LauncherSettings.JIL_LOGO_SIZE)
		except (FileNotFoundError, pygame.error):
			self.jil_logo_surface = None
		self.load_menu_audio()

		# Build the unified games dict (sponsor + student) and load preview
		# images keyed by label. Then walk MenuTreeSettings.ROOT to construct
		# the navigation tree, attaching games to category leaves.
		self.games: dict[str, MenuNode] = self._build_games()
		self.preview_images: dict[str, pygame.Surface] = self._load_preview_images()
		root_items = self._build_root_items()

		self.menu_stack: list[MenuFrame] = [MenuFrame(items=root_items)]
		self.menu_option_hitboxes: list[pygame.Rect] = []
		self.vertical_axis_engaged = False
		self.status_message = ""
		self.status_message_until = 0

	def show_status_message(self, message: str, duration_ms: int = 3500) -> None:
		"""Display a temporary status/error message at the bottom of the screen."""
		self.status_message = message
		self.status_message_until = pygame.time.get_ticks() + duration_ms

	def initialize_runtime(self) -> None:
		"""Initialize Pygame systems required for rendering and input handling."""
		pygame.init()
		pygame.joystick.init()
		self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
		self.screen = pygame.display.set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)
		pygame.display.set_caption(LauncherSettings.WINDOW_TITLE)
		self.clock = pygame.time.Clock()

		self.title_font = pygame.font.Font(str(self.font_path), FontSettings.TITLE_SIZE)
		self.subtitle_font = pygame.font.Font(str(self.font_path), FontSettings.SUBTITLE_SIZE)
		self.option_font = pygame.font.Font(str(self.font_path), FontSettings.OPTION_SIZE)
		self.hint_font = pygame.font.Font(str(self.font_path), FontSettings.HINT_SIZE)
		self.description_font = pygame.font.Font(str(self.font_path), FontSettings.DESCRIPTION_SIZE)

		self.crt = LauncherCRT(self.screen, self.tv_path)

	def _load_sound_if_available(self, sound_path: Path) -> pygame.mixer.Sound | None:
		"""Load a sound if both mixer and file are available."""
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
		self.menu_move_sfx = self._load_sound_if_available(self.menu_move_sound_path)
		for candidate in self.menu_select_sound_paths:
			loaded = self._load_sound_if_available(candidate)
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
		"""Combine sponsor and student games into MenuNode objects keyed by label."""
		games: dict[str, MenuNode] = {}

		for label, relative_path in GameSettings.OPTIONS:
			category_key = GameSettings.GAME_CATEGORIES.get(label)
			attribution = (
				CategorySettings.ATTRIBUTIONS.get(category_key, "")
				if category_key
				else ""
			)
			preview_relative = GameSettings.PREVIEW_IMAGES.get(label)
			preview_path = self.root_dir / preview_relative if preview_relative else None
			games[label] = MenuNode(
				kind="game",
				label=label,
				main_path=self.root_dir / relative_path,
				preview_path=preview_path,
				preview_label=label,
				attribution=attribution,
				input_scheme_key=GameSettings.GAME_INPUT_SCHEMES.get(label),
				note=GameSettings.GAME_NOTES.get(label),
				under_construction=label in GameSettings.UNDER_CONSTRUCTION_GAMES,
				category_key=category_key,
			)

		student_records = discover_student_games(self.root_dir / StudentGameSettings.ROOT)
		for record in student_records:
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
		"""Load and scale preview screenshots keyed by game label."""
		preview_images: dict[str, pygame.Surface] = {}
		max_width = MenuSettings.PREVIEW_BOX_WIDTH - (MenuSettings.PREVIEW_INNER_PADDING * 2)
		max_height = MenuSettings.PREVIEW_BOX_HEIGHT - (MenuSettings.PREVIEW_INNER_PADDING * 2)

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
		"""Return all game nodes belonging to ``category_key``, sorted by label."""
		return sorted(
			(g for g in self.games.values() if g.category_key == category_key),
			key=lambda g: g.label,
		)

	def _build_menu_node_for_spec(self, spec: dict) -> MenuNode:
		"""Walk one MenuTreeSettings entry and return its MenuNode subtree."""
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
		"""Build the top-level menu items from MenuTreeSettings.ROOT."""
		return [self._build_menu_node_for_spec(spec) for spec in MenuTreeSettings.ROOT]

	# ------------------------------------------------------------------
	# Navigation
	# ------------------------------------------------------------------
	def current_frame(self) -> MenuFrame:
		"""Return the currently visible menu frame (top of the stack)."""
		return self.menu_stack[-1]

	def current_node(self) -> MenuNode | None:
		"""Return the currently highlighted node, or None if the frame is empty."""
		frame = self.current_frame()
		if not frame.items:
			return None
		return frame.items[frame.selected_index]

	def _set_selected_index(self, new_index: int) -> None:
		"""Update selection in the active frame and play the move SFX on change."""
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
		"""Pop one level off the menu stack. Returns True if a level was popped."""
		if len(self.menu_stack) > 1:
			self._play_move_sfx()
			self.menu_stack.pop()
			return True
		return False

	# ------------------------------------------------------------------
	# Game launch
	# ------------------------------------------------------------------
	def suspend_runtime(self) -> None:
		"""Shut down launcher rendering/input systems before child game launch."""
		pygame.display.quit()
		pygame.joystick.quit()
		pygame.quit()

	def launch_selected_game(self, node: MenuNode) -> None:
		"""Launch the given game node, then restore launcher runtime after exit."""
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
			self.initialize_runtime()
			self.show_status_message(f"Failed to launch {node.label}: {error}")
			self.vertical_axis_engaged = False
			return
		finally:
			if not pygame.get_init():
				self.initialize_runtime()
				self.vertical_axis_engaged = False

	def show_loading_screen(self, duration_ms: int = 2200) -> None:
		"""Show a temporary loading screen before launching a selected game."""
		start_time = pygame.time.get_ticks()
		while pygame.time.get_ticks() - start_time < duration_ms:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			# Animate trailing dots so players can tell the launcher is active.
			dot_count = ((pygame.time.get_ticks() - start_time) // 350) % 4
			loading_text = f"LOADING{'.' * dot_count}"

			self.screen.fill(ColorSettings.BLACK)
			loading_surface = self.option_font.render(loading_text, False, ColorSettings.WHITE)
			loading_rect = loading_surface.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))
			self.screen.blit(loading_surface, loading_rect)
			pygame.display.flip()
			self.clock.tick(ScreenSettings.FPS)

	# ------------------------------------------------------------------
	# Menu rendering
	# ------------------------------------------------------------------
	def draw_menu(self) -> None:
		"""Pick the carousel or static-list renderer based on the active frame."""
		frame = self.current_frame()
		if len(frame.items) > MenuSettings.CAROUSEL_THRESHOLD:
			self.draw_carousel_menu(frame)
		else:
			self.draw_list_menu(frame)

	def draw_carousel_menu(self, frame: MenuFrame) -> None:
		"""Draw a vertical carousel centered on the selected item in this frame."""
		count = len(frame.items)
		# Reset hitboxes to the active frame's item count so only currently
		# visible carousel items react to the mouse.
		self.menu_option_hitboxes = [pygame.Rect(0, 0, 0, 0) for _ in range(count)]
		if count == 0:
			return

		for offset in range(-MenuSettings.CAROUSEL_VISIBLE_RADIUS, MenuSettings.CAROUSEL_VISIBLE_RADIUS + 1):
			option_index = (frame.selected_index + offset) % count
			node = frame.items[option_index]
			distance = abs(offset)
			is_selected = offset == 0

			color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
			text_surface = self.option_font.render(node.label.upper(), False, color).convert_alpha()

			scale = max(
				MenuSettings.CAROUSEL_MIN_SCALE,
				MenuSettings.CAROUSEL_SELECTED_SCALE - (distance * MenuSettings.CAROUSEL_SCALE_STEP),
			)
			if scale != 1.0:
				text_surface = pygame.transform.smoothscale(
					text_surface,
					(
						max(1, int(text_surface.get_width() * scale)),
						max(1, int(text_surface.get_height() * scale)),
					),
				)

			alpha = max(
				MenuSettings.CAROUSEL_MIN_ALPHA,
				MenuSettings.CAROUSEL_SELECTED_ALPHA - (distance * MenuSettings.CAROUSEL_ALPHA_STEP),
			)
			text_surface.set_alpha(alpha)

			item_center = (
				MenuSettings.CAROUSEL_CENTER_X,
				MenuSettings.CAROUSEL_CENTER_Y + (offset * MenuSettings.CAROUSEL_ITEM_SPACING),
			)
			text_rect = text_surface.get_rect(center=item_center)
			self.screen.blit(text_surface, text_rect)
			self.menu_option_hitboxes[option_index] = text_rect.inflate(36, 16)

	def draw_list_menu(self, frame: MenuFrame) -> None:
		"""Draw a static vertical list with a `>` cursor on the selected item."""
		count = len(frame.items)
		self.menu_option_hitboxes = [pygame.Rect(0, 0, 0, 0) for _ in range(count)]
		if count == 0:
			return

		total_height = (count - 1) * MenuSettings.LIST_ITEM_SPACING
		start_y = MenuSettings.CAROUSEL_CENTER_Y - total_height // 2

		for index, node in enumerate(frame.items):
			is_selected = index == frame.selected_index
			color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
			label_surface = self.option_font.render(node.label.upper(), False, color)
			label_rect = label_surface.get_rect(
				center=(MenuSettings.CAROUSEL_CENTER_X, start_y + index * MenuSettings.LIST_ITEM_SPACING)
			)
			self.screen.blit(label_surface, label_rect)

			if is_selected:
				cursor_text = MenuSettings.LIST_CURSOR_TEXT.strip() or ">"
				cursor_surface = self.option_font.render(cursor_text, False, color)
				cursor_rect = cursor_surface.get_rect(
					midright=(label_rect.left - 8, label_rect.centery)
				)
				self.screen.blit(cursor_surface, cursor_rect)

			# Inflate hitbox enough to cover the cursor area on the left.
			self.menu_option_hitboxes[index] = label_rect.inflate(80, 16)

	def draw_preview_panel(self) -> None:
		"""Draw the preview box; contents depend on game-vs-submenu highlight."""
		preview_rect = pygame.Rect(
			MenuSettings.PREVIEW_BOX_X,
			MenuSettings.PREVIEW_BOX_Y,
			MenuSettings.PREVIEW_BOX_WIDTH,
			MenuSettings.PREVIEW_BOX_HEIGHT,
		)
		inner_rect = preview_rect.inflate(
			-(MenuSettings.PREVIEW_INNER_PADDING * 2),
			-(MenuSettings.PREVIEW_INNER_PADDING * 2),
		)

		pygame.draw.rect(
			self.screen,
			ColorSettings.WHITE,
			preview_rect,
			MenuSettings.PREVIEW_BORDER_WIDTH,
			MenuSettings.PREVIEW_BORDER_RADIUS,
		)

		node = self.current_node()
		if node is None:
			return

		if node.kind == "game":
			self._draw_game_preview(node, inner_rect, preview_rect)
		else:
			self._draw_description(node, inner_rect)

	def _draw_game_preview(self, node: MenuNode, inner_rect: pygame.Rect, preview_rect: pygame.Rect) -> None:
		"""Render the screenshot (or fallback) plus the under-construction stamp."""
		preview_surface = self.preview_images.get(node.preview_label) if node.preview_label else None
		if preview_surface is not None:
			preview_surface_rect = preview_surface.get_rect(center=inner_rect.center)
			self.screen.blit(preview_surface, preview_surface_rect)
		else:
			fallback_surface = self.subtitle_font.render("PREVIEW NOT AVAILABLE", False, ColorSettings.WHITE)
			fallback_rect = fallback_surface.get_rect(center=inner_rect.center)
			self.screen.blit(fallback_surface, fallback_rect)

		if node.under_construction:
			# White outline so the red label stays legible over busy preview
			# screenshots -- straight red text disappears against warm-toned
			# panels (e.g. the dungeon previews).
			self.draw_outlined_text(
				MenuSettings.UNDER_CONSTRUCTION_TEXT,
				self.option_font,
				ColorSettings.RED,
				ColorSettings.WHITE,
				preview_rect.center,
			)

	def _draw_description(self, node: MenuNode, inner_rect: pygame.Rect) -> None:
		"""Render a wrapped category description centered inside the preview panel.

		Specific phrases listed in MenuSettings.DESCRIPTION_HIGHLIGHTS render
		in their assigned colors; everything else falls back to white. Each
		line is centered horizontally based on its total rendered width so a
		colored phrase doesn't pull the line off-axis.
		"""
		description = (node.description or "").upper()
		if not description.strip():
			return
		color_map = self._build_description_color_map(description)
		lines = self._wrap_description_with_colors(
			description, color_map, self.description_font, inner_rect.width
		)
		if not lines:
			return
		line_height = self.description_font.get_linesize()
		spacing = MenuSettings.DESCRIPTION_LINE_SPACING
		block_height = len(lines) * line_height + (len(lines) - 1) * spacing
		start_y = inner_rect.centery - block_height // 2
		for index, runs in enumerate(lines):
			if not runs:
				continue
			run_surfaces = [
				self.description_font.render(segment, False, color)
				for segment, color in runs
			]
			total_width = sum(surface.get_width() for surface in run_surfaces)
			x = inner_rect.centerx - total_width // 2
			y = start_y + index * (line_height + spacing)
			for surface in run_surfaces:
				self.screen.blit(surface, (x, y))
				x += surface.get_width()

	def _build_description_color_map(self, text: str) -> list[tuple[int, int, int]]:
		"""Return a per-character color list for ``text`` (already uppercased).

		Default color is white. Each entry in MenuSettings.DESCRIPTION_HIGHLIGHTS
		paints its phrase characters with the assigned color when found at a
		word boundary. Longer phrases win over shorter ones if they overlap,
		because they are applied first.
		"""
		color_map: list[tuple[int, int, int]] = [ColorSettings.WHITE] * len(text)
		highlights = sorted(
			MenuSettings.DESCRIPTION_HIGHLIGHTS.items(),
			key=lambda item: -len(item[0]),
		)
		for phrase, color in highlights:
			needle = phrase.upper()
			if not needle:
				continue
			search_from = 0
			while True:
				idx = text.find(needle, search_from)
				if idx < 0:
					break
				before_ok = idx == 0 or not text[idx - 1].isalnum()
				end = idx + len(needle)
				after_ok = end == len(text) or not text[end].isalnum()
				if before_ok and after_ok:
					for i in range(idx, end):
						color_map[i] = color
				search_from = idx + 1
		return color_map

	def _wrap_description_with_colors(
		self,
		text: str,
		color_map: list[tuple[int, int, int]],
		font: pygame.font.Font,
		max_width: int,
	) -> list[list[tuple[str, tuple[int, int, int]]]]:
		"""Greedy word-wrap ``text`` into per-line color runs.

		Each line in the returned list is a sequence of (segment, color)
		pairs to render side-by-side. Single inter-word spaces are added
		back at render time and inherit the color of the following word.
		"""
		# Tokenize into (word_text, start_index_in_text) pairs.
		words: list[tuple[str, int]] = []
		i = 0
		n = len(text)
		while i < n:
			if text[i].isspace():
				i += 1
				continue
			start = i
			while i < n and not text[i].isspace():
				i += 1
			words.append((text[start:i], start))

		# Greedy line packing: keep adding words while the joined line still fits.
		raw_lines: list[list[tuple[str, int]]] = []
		current_line: list[tuple[str, int]] = []
		current_str = ""
		for word, start in words:
			candidate = (current_str + " " + word).strip() if current_str else word
			if font.size(candidate)[0] <= max_width:
				current_line.append((word, start))
				current_str = candidate
				continue
			if current_line:
				raw_lines.append(current_line)
				current_line = [(word, start)]
				current_str = word
			else:
				# Single word wider than the box -- emit it on its own line
				# rather than infinite-looping trying to fit it.
				raw_lines.append([(word, start)])
				current_line = []
				current_str = ""
		if current_line:
			raw_lines.append(current_line)

		# For each line, walk word-by-word and merge same-colored chars into runs.
		rendered_lines: list[list[tuple[str, tuple[int, int, int]]]] = []
		for line in raw_lines:
			chars: list[str] = []
			colors: list[tuple[int, int, int]] = []
			for word_index, (word, start) in enumerate(line):
				if word_index > 0:
					# Inter-word space inherits the next word's color so a
					# highlight phrase that spans multiple words renders as
					# one continuous colored run.
					chars.append(" ")
					colors.append(color_map[start])
				for offset, ch in enumerate(word):
					chars.append(ch)
					colors.append(color_map[start + offset])
			runs: list[tuple[str, tuple[int, int, int]]] = []
			if not chars:
				rendered_lines.append(runs)
				continue
			run_text = chars[0]
			run_color = colors[0]
			for ch, color in zip(chars[1:], colors[1:]):
				if color == run_color:
					run_text += ch
				else:
					runs.append((run_text, run_color))
					run_text = ch
					run_color = color
			runs.append((run_text, run_color))
			rendered_lines.append(runs)
		return rendered_lines

	def draw_outlined_text(
		self,
		text: str,
		font: pygame.font.Font,
		fg_color: tuple[int, int, int],
		outline_color: tuple[int, int, int],
		center: tuple[int, int],
	) -> None:
		"""Render text with a 1-pixel outline by stamping the outline color around the foreground."""
		fg_surface = font.render(text, False, fg_color)
		outline_surface = font.render(text, False, outline_color)
		fg_rect = fg_surface.get_rect(center=center)
		# All eight neighbors so the outline traces the full glyph silhouette,
		# not just the cardinal sides.
		outline_offsets = (
			(-1, -1), (0, -1), (1, -1),
			(-1, 0),           (1, 0),
			(-1, 1),  (0, 1),  (1, 1),
		)
		for offset_x, offset_y in outline_offsets:
			self.screen.blit(outline_surface, fg_rect.move(offset_x, offset_y))
		self.screen.blit(fg_surface, fg_rect)

	def collect_warning_lines(self, node: MenuNode) -> list[str]:
		"""Return red-text warnings for the given game node in render order.

		The input-scheme label (when set to anything other than STANDARD)
		takes the upper slot; the optional free-form note sits beneath it.
		If only the note is present, it promotes into the upper slot.
		"""
		lines: list[str] = []
		scheme_label = (
			InputSchemeSettings.LABELS.get(node.input_scheme_key)
			if node.input_scheme_key
			else None
		)
		if scheme_label:
			lines.append(scheme_label)
		if node.note:
			lines.append(node.note)
		return [line.upper() for line in lines]

	def draw_preview_warnings(self) -> None:
		"""Render attribution + up to two warning lines under the preview, only for games."""
		node = self.current_node()
		if node is None or node.kind != "game":
			return

		preview_center_x = MenuSettings.PREVIEW_BOX_X + (MenuSettings.PREVIEW_BOX_WIDTH // 2)

		# Attribution always renders first in light blue.
		attribution_text = node.attribution or "BY UNKNOWN"
		attr_surface = self.hint_font.render(attribution_text.upper(), False, ColorSettings.LIGHT_BLUE)
		attr_rect = attr_surface.get_rect(
			center=(preview_center_x, MenuSettings.ATTRIBUTION_LINE_CENTER_Y)
		)
		self.screen.blit(attr_surface, attr_rect)

		slot_y_positions = (
			MenuSettings.WARNING_LINE_1_CENTER_Y,
			MenuSettings.WARNING_LINE_2_CENTER_Y,
		)
		warnings = self.collect_warning_lines(node)
		for slot_index, warning_text in enumerate(warnings):
			warning_surface = self.hint_font.render(warning_text, False, ColorSettings.RED)
			warning_rect = warning_surface.get_rect(
				center=(preview_center_x, slot_y_positions[slot_index])
			)
			self.screen.blit(warning_surface, warning_rect)

	def draw(self) -> None:
		"""Render the launcher title, subtitle, current menu, preview, and CRT overlay."""
		self.screen.fill(ColorSettings.BLACK)

		# Center the JIL logo + title group horizontally as one unit so the
		# fixed gap between them stays the same regardless of title length.
		logo_w = LauncherSettings.JIL_LOGO_SIZE[0]
		title_surface = self.title_font.render(MenuSettings.TITLE_TEXT, False, ColorSettings.GREEN)
		title_w = title_surface.get_width()
		total_width = logo_w + LauncherSettings.JIL_LOGO_TITLE_SPACING + title_w
		start_x = (ScreenSettings.WIDTH - total_width) // 2
		logo_y = MenuSettings.TITLE_CENTER_Y - (LauncherSettings.JIL_LOGO_SIZE[1] // 2)
		if self.jil_logo_surface is not None:
			self.screen.blit(self.jil_logo_surface, (start_x, logo_y))
		else:
			pygame.draw.rect(
				self.screen,
				LauncherSettings.JIL_LOGO_PLACEHOLDER_COLOR,
				(start_x, logo_y, *LauncherSettings.JIL_LOGO_SIZE),
				2,
			)

		title_rect = title_surface.get_rect(
			midleft=(start_x + logo_w + LauncherSettings.JIL_LOGO_TITLE_SPACING, MenuSettings.TITLE_CENTER_Y)
		)
		self.screen.blit(title_surface, title_rect)

		subtitle_surface = self.subtitle_font.render(
			MenuSettings.SUBTITLE_TEXT,
			False,
			ColorSettings.LIGHT_BLUE,
		)
		subtitle_rect = subtitle_surface.get_rect(
			center=(ScreenSettings.WIDTH // 2, MenuSettings.SUBTITLE_CENTER_Y)
		)
		self.screen.blit(subtitle_surface, subtitle_rect)

		self.draw_menu()
		self.draw_preview_panel()
		self.draw_preview_warnings()

		hint_line_1_surface = self.hint_font.render(
			MenuSettings.FOOTER_TEXT_LINE_1,
			False,
			ColorSettings.LIGHT_BLUE,
		)
		hint_line_1_rect = hint_line_1_surface.get_rect(
			center=(ScreenSettings.WIDTH // 2, MenuSettings.FOOTER_LINE_1_CENTER_Y)
		)
		self.screen.blit(hint_line_1_surface, hint_line_1_rect)

		footer_line_2_text = MenuSettings.FOOTER_TEXT_LINE_2
		if self.status_message and pygame.time.get_ticks() < self.status_message_until:
			footer_line_2_text = self.status_message

		hint_line_2_surface = self.hint_font.render(
			footer_line_2_text,
			False,
			ColorSettings.LIGHT_BLUE,
		)
		hint_line_2_rect = hint_line_2_surface.get_rect(
			center=(ScreenSettings.WIDTH // 2, MenuSettings.FOOTER_LINE_2_CENTER_Y)
		)
		self.screen.blit(hint_line_2_surface, hint_line_2_rect)
		self.crt.draw()
		pygame.display.flip()

	# ------------------------------------------------------------------
	# Input handling
	# ------------------------------------------------------------------
	def handle_controller_buttons(self, event: pygame.event.Event) -> None:
		"""Process controller button presses for launcher actions."""
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
		"""Process D-pad/hat navigation input."""
		if event.value[1] > 0:
			self.move_selection_up()
		elif event.value[1] < 0:
			self.move_selection_down()

	def handle_axis_navigation(self, event: pygame.event.Event) -> None:
		"""Process analog-stick vertical navigation with edge-triggered debounce."""
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
		"""Process keyboard input and report whether the launcher should continue."""
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
		"""Support hover-to-select and click-to-launch for menu options."""
		if not self.menu_option_hitboxes:
			return

		if event.type == pygame.MOUSEMOTION:
			for index, hitbox in enumerate(self.menu_option_hitboxes):
				if hitbox.collidepoint(event.pos):
					self._set_selected_index(index)
					break
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			for index, hitbox in enumerate(self.menu_option_hitboxes):
				if hitbox.collidepoint(event.pos):
					self._set_selected_index(index)
					self.enter_selected_node()
					break

	def run(self) -> None:
		"""Run the launcher event loop until the user quits."""
		running = True
		self.draw()
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

			self.draw()
			self.clock.tick(ScreenSettings.FPS)

		pygame.quit()


if __name__ == "__main__":
	ArcadeLauncher().run()
