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
		self.base_tv = pygame.image.load(str(tv_image_path)).convert_alpha()
		self.base_tv = pygame.transform.scale(self.base_tv, ScreenSettings.RESOLUTION)

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

		self.initialize_runtime()

		self.options = [(label, self.root_dir / relative_path) for label, relative_path in GameSettings.OPTIONS]
		self.selected_index = 0
		self.vertical_axis_engaged = False

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

	def suspend_runtime(self) -> None:
		"""Shut down launcher rendering/input systems before child game launch."""
		pygame.display.quit()
		pygame.joystick.quit()
		pygame.quit()

	def move_selection_up(self) -> None:
		"""Move the menu cursor to the previous game option with wrap-around."""
		self.selected_index = (self.selected_index - 1) % len(self.options)

	def move_selection_down(self) -> None:
		"""Move the menu cursor to the next game option with wrap-around."""
		self.selected_index = (self.selected_index + 1) % len(self.options)

	def launch_selected_game(self) -> None:
		"""Launch the selected game, then restore launcher runtime after it exits."""
		_, game_main = self.options[self.selected_index]
		game_dir = game_main.parent
		self.suspend_runtime()

		try:
			subprocess.run(
				[sys.executable, str(game_main)],
				cwd=str(game_dir),
				check=False,
			)
		finally:
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
			option_y = MenuSettings.OPTIONS_START_Y + index * MenuSettings.OPTION_SPACING
			is_selected = index == self.selected_index
			color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
			text_surface = self.option_font.render(label.upper(), False, color)
			text_rect = text_surface.get_rect(center=(ScreenSettings.WIDTH // 2, option_y))
			self.screen.blit(text_surface, text_rect)

			if is_selected:
				cursor_surface = self.option_font.render(MenuSettings.CURSOR_SYMBOL, False, ColorSettings.YELLOW)
				cursor_rect = cursor_surface.get_rect(
					midright=(text_rect.left - MenuSettings.CURSOR_GAP, text_rect.centery)
				)
				self.screen.blit(cursor_surface, cursor_rect)

		hint_line_1_surface = self.hint_font.render(
			MenuSettings.FOOTER_TEXT_LINE_1,
			False,
			ColorSettings.LIGHT_BLUE,
		)
		hint_line_1_rect = hint_line_1_surface.get_rect(
			center=(ScreenSettings.WIDTH // 2, MenuSettings.FOOTER_LINE_1_CENTER_Y)
		)
		self.screen.blit(hint_line_1_surface, hint_line_1_rect)

		hint_line_2_surface = self.hint_font.render(
			MenuSettings.FOOTER_TEXT_LINE_2,
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

	def run(self) -> None:
		"""Run the launcher event loop until user quits."""
		running = True
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
				elif event.type == pygame.KEYDOWN:
					running = self.handle_keyboard(event)

			self.draw()
			self.clock.tick(ScreenSettings.FPS)

		pygame.quit()


if __name__ == "__main__":
	ArcadeLauncher().run()
