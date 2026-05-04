import os
import sys

# Make sure imports of sibling modules work whether this file is launched
# directly (python main.py) or imported by an external launcher (e.g. the
# arcade-cabinet launcher), where cwd may be different.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
	sys.path.insert(0, _HERE)

from settings import *
from sys import exit
from os.path import join
from ui.crt import CRT

# components
from game import Game
from score import Score
from preview import Preview

from random import choice

# Controller button mapping shared with the rest of the arcade so the same
# physical buttons keep the same meaning across every game.
SELECT_BUTTON = 6
START_BUTTON = 7
L1_BUTTON = 4
R1_BUTTON = 5
QUIT_COMBO_BUTTONS = (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)


class Main:
	def __init__(self):

		# general
		pygame.init()
		# SCALED lets pygame auto-scale our fixed-size game to the actual
		# window/screen, so toggling fullscreen still fills the display.
		self.display_surface = pygame.display.set_mode(
			(WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
		self.clock = pygame.time.Clock()
		pygame.display.set_caption('Tetris')

		self.setup_controllers()

		# shapes
		self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]

		# components — Game reads the live joystick list every frame so
		# D-pad input survives controller hot-plug.
		self.game = Game(self.get_next_shape, self.update_score, self.connected_joysticks)
		self.score = Score()
		self.preview = Preview()

		# audio
		self.music = pygame.mixer.Sound(join(BASE_PATH, 'sound', 'music.wav'))
		self.music.set_volume(0.05)
		self.music.play(-1)

		self.full_screen = False
		self.crt  = CRT(self.display_surface)

	def setup_controllers(self):
		"""Cache currently-connected controllers so quit-combo polling is cheap.

		Returns:
			None.
		"""
		pygame.joystick.init()
		self.connected_joysticks = [
			pygame.joystick.Joystick(index)
			for index in range(pygame.joystick.get_count())
		]

	def quit_combo_pressed(self):
		"""Return True when L1 + R1 + START + SELECT are held on any controller.

		Returns:
			bool: True when the four buttons are held simultaneously on any pad.
		"""
		for joystick in self.connected_joysticks:
			try:
				if all(joystick.get_button(button) for button in QUIT_COMBO_BUTTONS):
					return True
			except pygame.error:
				# A device disconnect can race with the polling call.
				continue
		return False

	def close_game(self):
		"""Shut down pygame and exit so the launcher reopens cleanly."""
		pygame.quit()
		exit()

	def update_score(self, lines, score, level):
		self.score.lines = lines
		self.score.score = score
		self.score.level = level

	def get_next_shape(self):
		next_shape = self.next_shapes.pop(0)
		self.next_shapes.append(choice(list(TETROMINOS.keys())))
		return next_shape

	def run(self):
		while True:
			if self.quit_combo_pressed():
				self.close_game()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_game()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_F11:
						pygame.display.toggle_fullscreen()
						self.full_screen = not self.full_screen
					# ESC always exits the game and returns to the launcher,
					# matching the L1+R1+START+SELECT controller combo.
					elif event.key == pygame.K_ESCAPE:
						self.close_game()
				if event.type == pygame.JOYBUTTONDOWN:
					# SELECT mirrors F11 so the controller has a fullscreen toggle.
					if event.button == SELECT_BUTTON:
						pygame.display.toggle_fullscreen()
						self.full_screen = not self.full_screen

			# display
			self.display_surface.fill(GRAY)

			# components
			self.game.run()
			self.score.run()
			self.preview.run(self.next_shapes)

			# overlay
			if not self.full_screen:
				self.crt.draw()

			# updating the game
			pygame.display.update()
			self.clock.tick()

if __name__ == '__main__':
	main = Main()
	main.run()
