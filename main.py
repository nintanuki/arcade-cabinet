"""Top-level launcher that allows players to choose which arcade game to run."""

import random
import subprocess
import sys
from pathlib import Path

import pygame

from settings import (
	CRTSettings,
	ColorSettings,
	ControlSettings,
	FontSettings,
	GameSettings,
	LauncherSettings,
	MenuSettings,
	ScreenSettings,
)


class LauncherCRT:
	"""Render a CRT-style overlay on top of the launcher scene."""

	def __init__(self, screen: pygame.Surface, tv_image_path: Path) -> None:
		"""Initialize overlay texture and target render surface.

		Args:
			screen (pygame.Surface): Display surface the overlay is drawn onto.
			tv_image_path (Path): Path to the CRT overlay texture image.
		"""
		self.screen = screen
		# Fall back to a transparent surface if the CRT texture is missing.
		try:
			self.base_tv = pygame.image.load(str(tv_image_path)).convert_alpha()
			self.base_tv = pygame.transform.scale(self.base_tv, ScreenSettings.RESOLUTION)
		except (FileNotFoundError, pygame.error):
			self.base_tv = pygame.Surface(ScreenSettings.RESOLUTION, pygame.SRCALPHA)

	def create_crt_lines(self, surf: pygame.Surface) -> None:
		"""Draw scan lines onto a temporary overlay surface.

		Args:
			surf (pygame.Surface): Surface that receives horizontal scan lines.
		"""
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

		self.initialize_runtime()
		self.load_menu_audio()

		self.options = [(label, self.root_dir / relative_path) for label, relative_path in GameSettings.OPTIONS]
		self.preview_images = self.load_preview_images()
		self.selected_index = 0
		self.vertical_axis_engaged = False
		self.status_message = ""
		self.status_message_until = 0
		self.menu_option_hitboxes: list[pygame.Rect] = []

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

		self.crt = LauncherCRT(self.screen, self.tv_path)

	def _load_sound_if_available(self, sound_path: Path) -> pygame.mixer.Sound | None:
		"""Load a sound if both mixer and file are available.

		Args:
			sound_path (Path): File path to the candidate sound.

		Returns:
			pygame.mixer.Sound | None: Loaded sound, or ``None`` when unavailable.
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
		self.menu_move_sfx = self._load_sound_if_available(self.menu_move_sound_path)
		for candidate in self.menu_select_sound_paths:
			loaded = self._load_sound_if_available(candidate)
			if loaded is not None:
				self.menu_select_sfx = loaded
				break

	def _play_move_sfx(self) -> None:
		"""Play the move sound when changing highlighted menu option."""
		if self.menu_move_sfx is not None:
			self.menu_move_sfx.play()

	def _play_select_sfx(self) -> None:
		"""Play the select sound when launching a game."""
		if self.menu_select_sfx is not None:
			self.menu_select_sfx.play()

	def _set_selected_index(self, new_index: int) -> None:
		"""Update selection index and trigger menu-move SFX only on actual changes."""
		wrapped_index = new_index % len(self.options)
		if wrapped_index == self.selected_index:
			return
		self.selected_index = wrapped_index
		self._play_move_sfx()

	def suspend_runtime(self) -> None:
		"""Shut down launcher rendering/input systems before child game launch."""
		pygame.display.quit()
		pygame.joystick.quit()
		pygame.quit()

	def move_selection_up(self) -> None:
		"""Move the menu cursor to the previous game option with wrap-around."""
		self._set_selected_index(self.selected_index - 1)

	def move_selection_down(self) -> None:
		"""Move the menu cursor to the next game option with wrap-around."""
		self._set_selected_index(self.selected_index + 1)

	def load_preview_images(self) -> dict[str, pygame.Surface]:
		"""Load menu preview screenshots and scale them to fit the preview panel."""
		preview_images: dict[str, pygame.Surface] = {}
		max_preview_width = MenuSettings.PREVIEW_BOX_WIDTH - (MenuSettings.PREVIEW_INNER_PADDING * 2)
		max_preview_height = MenuSettings.PREVIEW_BOX_HEIGHT - (MenuSettings.PREVIEW_INNER_PADDING * 2)

		for label, relative_path in GameSettings.PREVIEW_IMAGES.items():
			preview_path = self.root_dir / relative_path
			try:
				preview_surface = pygame.image.load(str(preview_path)).convert()
			except (FileNotFoundError, pygame.error):
				continue

			if preview_surface.get_width() == 0 or preview_surface.get_height() == 0:
				continue

			scale_ratio = min(
				max_preview_width / preview_surface.get_width(),
				max_preview_height / preview_surface.get_height(),
			)
			target_size = (
				max(1, int(preview_surface.get_width() * scale_ratio)),
				max(1, int(preview_surface.get_height() * scale_ratio)),
			)
			preview_images[label] = pygame.transform.smoothscale(preview_surface, target_size)

		return preview_images

	def draw_preview_panel(self) -> None:
		"""Draw the selected game's screenshot in a rounded white-bordered panel."""
		preview_rect = pygame.Rect(
			MenuSettings.PREVIEW_BOX_X,
			MenuSettings.PREVIEW_BOX_Y,
			MenuSettings.PREVIEW_BOX_WIDTH,
			MenuSettings.PREVIEW_BOX_HEIGHT,
		)
		inner_rect = preview_rect.inflate(-(MenuSettings.PREVIEW_INNER_PADDING * 2), -(MenuSettings.PREVIEW_INNER_PADDING * 2))

		pygame.draw.rect(
			self.screen,
			ColorSettings.WHITE,
			preview_rect,
			MenuSettings.PREVIEW_BORDER_WIDTH,
			MenuSettings.PREVIEW_BORDER_RADIUS,
		)

		selected_label, _ = self.options[self.selected_index]
		preview_surface = self.preview_images.get(selected_label)

		if preview_surface is not None:
			preview_surface_rect = preview_surface.get_rect(center=inner_rect.center)
			self.screen.blit(preview_surface, preview_surface_rect)
		else:
			fallback_surface = self.subtitle_font.render("PREVIEW NOT AVAILABLE", False, ColorSettings.WHITE)
			fallback_rect = fallback_surface.get_rect(center=inner_rect.center)
			self.screen.blit(fallback_surface, fallback_rect)

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

	def launch_selected_game(self) -> None:
		"""Launch the selected game, then restore launcher runtime after it exits."""
		self._play_select_sfx()
		self.show_loading_screen()
		game_label, game_main = self.options[self.selected_index]
		game_dir = game_main.parent

		if not game_dir.exists():
			self.show_status_message(f"Cannot launch {game_label}: folder not found.")
			return

		if not game_main.exists():
			self.show_status_message(f"Cannot launch {game_label}: main.py not found.")
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
			self.show_status_message(f"Failed to launch {game_label}: {error}")
			self.vertical_axis_engaged = False
			return
		finally:
			if not pygame.get_init():
				self.initialize_runtime()
				self.vertical_axis_engaged = False

	def draw(self) -> None:
		"""Render the launcher title, subtitle, game options, and CRT overlay."""
		self.screen.fill(ColorSettings.BLACK)

		title_surface = self.title_font.render(MenuSettings.TITLE_TEXT, False, ColorSettings.LIGHT_PURPLE)
		title_rect = title_surface.get_rect(center=(ScreenSettings.WIDTH // 2, MenuSettings.TITLE_CENTER_Y))
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

		for index, (label, _) in enumerate(self.options):
			if len(self.menu_option_hitboxes) <= index:
				self.menu_option_hitboxes.append(pygame.Rect(0, 0, 0, 0))
			option_y = MenuSettings.OPTIONS_START_Y + index * MenuSettings.OPTION_SPACING
			is_selected = index == self.selected_index
			color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
			text_surface = self.option_font.render(label.upper(), False, color)
			text_rect = text_surface.get_rect(midleft=(MenuSettings.OPTIONS_LEFT_X, option_y))
			self.screen.blit(text_surface, text_rect)
			self.menu_option_hitboxes[index] = text_rect.inflate(36, 16)

			if is_selected:
				cursor_surface = self.option_font.render(MenuSettings.CURSOR_SYMBOL, False, ColorSettings.YELLOW)
				cursor_rect = cursor_surface.get_rect(
					midright=(text_rect.left - MenuSettings.CURSOR_GAP, text_rect.centery)
				)
				self.screen.blit(cursor_surface, cursor_rect)

		self.draw_preview_panel()

		selected_label, _ = self.options[self.selected_index]
		if selected_label in GameSettings.NO_CONTROLLER_SUPPORT_GAMES:
			no_controller_surface = self.hint_font.render(
				MenuSettings.NO_CONTROLLER_SUPPORT_TEXT,
				False,
				ColorSettings.RED,
			)
			no_controller_rect = no_controller_surface.get_rect(
				center=(ScreenSettings.WIDTH // 2, MenuSettings.NO_CONTROLLER_SUPPORT_CENTER_Y)
			)
			self.screen.blit(no_controller_surface, no_controller_rect)

		if selected_label == "Air Hockey":
			air_hockey_warning_surface = self.hint_font.render(
				MenuSettings.AIR_HOCKEY_WARNING_TEXT,
				False,
				ColorSettings.RED,
			)
			air_hockey_warning_rect = air_hockey_warning_surface.get_rect(
				center=(ScreenSettings.WIDTH // 2, MenuSettings.AIR_HOCKEY_WARNING_CENTER_Y)
			)
			self.screen.blit(air_hockey_warning_surface, air_hockey_warning_rect)

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

	def handle_controller_buttons(self, event: pygame.event.Event) -> None:
		"""Process controller button presses for launcher actions.

		Args:
			event (pygame.event.Event): Pygame controller button event.
		"""
		if event.button == ControlSettings.CONTROLLER_BUTTON_SELECT:
			pygame.display.toggle_fullscreen()
		elif event.button in (
			ControlSettings.CONTROLLER_BUTTON_A,
			ControlSettings.CONTROLLER_BUTTON_START,
		):
			self.launch_selected_game()

	def handle_hat_navigation(self, event: pygame.event.Event) -> None:
		"""Process D-pad/hat navigation input.

		Args:
			event (pygame.event.Event): Pygame hat-motion event.
		"""
		if event.value[1] > 0:
			self.move_selection_up()
		elif event.value[1] < 0:
			self.move_selection_down()

	def handle_axis_navigation(self, event: pygame.event.Event) -> None:
		"""Process analog-stick vertical navigation with edge-triggered debounce.

		Args:
			event (pygame.event.Event): Pygame joystick axis-motion event.
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
		"""Process keyboard input and report whether the launcher should continue.

		Args:
			event (pygame.event.Event): Pygame keydown event.

		Returns:
			bool: True to keep running, False to exit the launcher loop.
		"""
		if event.key == pygame.K_F11:
			pygame.display.toggle_fullscreen()
		elif event.key in (pygame.K_UP, pygame.K_w):
			self.move_selection_up()
		elif event.key in (pygame.K_DOWN, pygame.K_s):
			self.move_selection_down()
		elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
			self.launch_selected_game()
		elif event.key == pygame.K_ESCAPE:
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
					self.launch_selected_game()
					break

	def run(self) -> None:
		"""Run the launcher event loop until user quits."""
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
