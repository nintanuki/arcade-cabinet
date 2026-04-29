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

# components
from game import Game
from score import Score
from preview import Preview

from random import choice

class Main:
	def __init__(self):

		# general
		pygame.init()
		# SCALED lets pygame auto-scale our fixed-size game to the actual
		# window/screen, so toggling fullscreen still fills the display.
		self.display_surface = pygame.display.set_mode(
			(WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
		self.fullscreen = False
		self.clock = pygame.time.Clock()
		pygame.display.set_caption('Tetris')

		# shapes
		self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]

		# components
		self.game = Game(self.get_next_shape, self.update_score)
		self.score = Score()
		self.preview = Preview()

		# audio
		self.music = pygame.mixer.Sound(join(BASE_PATH, 'sound', 'music.wav'))
		self.music.set_volume(0.05)
		self.music.play(-1)

	def update_score(self, lines, score, level):
		self.score.lines = lines
		self.score.score = score
		self.score.level = level

	def get_next_shape(self):
		next_shape = self.next_shapes.pop(0)
		self.next_shapes.append(choice(list(TETROMINOS.keys())))
		return next_shape

	def toggle_fullscreen(self):
		pygame.display.toggle_fullscreen()
		self.fullscreen = not self.fullscreen

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_F11:
						self.toggle_fullscreen()
					# Allow Escape to exit fullscreen
					elif event.key == pygame.K_ESCAPE and self.fullscreen:
						self.toggle_fullscreen()

			# display
			self.display_surface.fill(GRAY)

			# components
			self.game.run()
			self.score.run()
			self.preview.run(self.next_shapes)

			# updating the game
			pygame.display.update()
			self.clock.tick()

if __name__ == '__main__':
	main = Main()
	main.run()
