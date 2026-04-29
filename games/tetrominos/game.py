from settings import *
from random import choice
from sys import exit
from os.path import join

from timer import Timer

class Game:
	def __init__(self, get_next_shape, update_score, joysticks=None):

		# general
		self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
		self.display_surface = pygame.display.get_surface()
		self.rect = self.surface.get_rect(topleft = (PADDING, PADDING))
		self.sprites = pygame.sprite.Group()

		# game connection
		self.get_next_shape = get_next_shape
		self.update_score = update_score
		# Cached reference to the live joystick list owned by Main so D-pad
		# polling sees the most up-to-date controllers each frame.
		self.joysticks = joysticks if joysticks is not None else []

		# lines
		self.line_surface = self.surface.copy()
		self.line_surface.fill((0,255,0))
		self.line_surface.set_colorkey((0,255,0))
		self.line_surface.set_alpha(120)

		# tetromino
		self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
		self.tetromino = Tetromino(
			choice(list(TETROMINOS.keys())),
			self.sprites,
			self.create_new_tetromino,
			self.field_data)

		# timer
		self.down_speed = UPDATE_START_SPEED
		self.down_speed_faster = self.down_speed * 0.3
		self.down_pressed = False
		self.timers = {
			'vertical move': Timer(self.down_speed, True, self.move_down),
			'horizontal move': Timer(MOVE_WAIT_TIME),
			'rotate': Timer(ROTATE_WAIT_TIME)
		}
		self.timers['vertical move'].activate()

		# Edge-detection memory for D-pad up so a held hat fires hard drop
		# exactly once per push (one tap = one piece slammed to the floor).
		self.previous_hat_y = 0

		# score
		self.current_level = 1
		self.current_score = 0
		self.current_lines = 0

		# sound
		self.landing_sound = pygame.mixer.Sound(join(BASE_PATH, 'sound', 'landing.wav'))
		self.landing_sound.set_volume(0.1)

	def calculate_score(self, num_lines):
		self.current_lines += num_lines
		self.current_score += SCORE_DATA[num_lines] * self.current_level

		if self.current_lines / 10 > self.current_level:
			self.current_level += 1
			self.down_speed *= 0.75
			self.down_speed_faster = self.down_speed * 0.3
			self.timers['vertical move'].duration = self.down_speed

		self.update_score(self.current_lines, self.current_score, self.current_level)

	def check_game_over(self):
		for block in self.tetromino.blocks:
			if block.pos.y < 0:
				exit()

	def create_new_tetromino(self):
		self.landing_sound.play()
		self.check_game_over()
		self.check_finished_rows()
		self.tetromino = Tetromino(
			self.get_next_shape(),
			self.sprites,
			self.create_new_tetromino,
			self.field_data)

	def timer_update(self):
		for timer in self.timers.values():
			timer.update()

	def move_down(self):
		self.tetromino.move_down()

	def draw_grid(self):

		for col in range(1, COLUMNS):
			x = col * CELL_SIZE
			pygame.draw.line(self.line_surface, LINE_COLOR, (x,0), (x,self.surface.get_height()), 1)

		for row in range(1, ROWS):
			y = row * CELL_SIZE
			pygame.draw.line(self.line_surface, LINE_COLOR, (0,y), (self.surface.get_width(),y))

		self.surface.blit(self.line_surface, (0,0))

	def controller_dpad(self):
		"""Return the active D-pad direction as a signed (x, y) tuple.

		Returns:
			tuple[int, int]: Hat reading from the first joystick reporting a
			pressed direction. ``(0, 0)`` when no D-pad is engaged.
		"""
		for joystick in self.joysticks:
			try:
				if joystick.get_numhats() <= 0:
					continue
				hat_x, hat_y = joystick.get_hat(0)
			except pygame.error:
				# A device disconnect can race with the polling call.
				continue
			if hat_x or hat_y:
				return hat_x, hat_y
		return 0, 0

	def controller_rotate_held(self):
		"""Return True when any rotate button (A or X) is held on any controller.

		Returns:
			bool: True when at least one rotate button is currently pressed.
		"""
		for joystick in self.joysticks:
			try:
				for button in ROTATE_BUTTONS:
					if joystick.get_button(button):
						return True
			except pygame.error:
				# A device disconnect can race with the polling call.
				continue
		return False

	def input(self):
		# Pygame's hat reports +1 for up and -1 for down, matching the screen
		# convention the keyboard arrows already use here, so the OR-merge is
		# direction-correct with no axis flip.
		keys = pygame.key.get_pressed()
		hat_x, hat_y = self.controller_dpad()

		# D-pad up is now hard drop, edge-triggered so a held hat doesn't
		# slam multiple pieces in quick succession. Keyboard K_UP keeps
		# rotating because the request only changed the controller binding.
		if hat_y == 1 and self.previous_hat_y != 1:
			self.tetromino.hard_drop()
		self.previous_hat_y = hat_y

		left_held = keys[pygame.K_LEFT] or hat_x == -1
		right_held = keys[pygame.K_RIGHT] or hat_x == 1
		rotate_held = keys[pygame.K_UP] or self.controller_rotate_held()
		down_held = keys[pygame.K_DOWN] or hat_y == -1

		# checking horizontal movement
		if not self.timers['horizontal move'].active:
			if left_held:
				self.tetromino.move_horizontal(-1)
				self.timers['horizontal move'].activate()
			if right_held:
				self.tetromino.move_horizontal(1)
				self.timers['horizontal move'].activate()

		# check for rotation
		if not self.timers['rotate'].active:
			if rotate_held:
				self.tetromino.rotate()
				self.timers['rotate'].activate()

		# down speedup
		if not self.down_pressed and down_held:
			self.down_pressed = True
			self.timers['vertical move'].duration = self.down_speed_faster

		if self.down_pressed and not down_held:
			self.down_pressed = False
			self.timers['vertical move'].duration = self.down_speed

	def check_finished_rows(self):

		# get the full row indexes
		delete_rows = []
		for i, row in enumerate(self.field_data):
			if all(row):
				delete_rows.append(i)

		if delete_rows:
			for delete_row in delete_rows:

				# delete full rows
				for block in self.field_data[delete_row]:
					block.kill()

				# move down blocks
				for row in self.field_data:
					for block in row:
						if block and block.pos.y < delete_row:
							block.pos.y += 1

			# rebuild the field data
			self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
			for block in self.sprites:
				self.field_data[int(block.pos.y)][int(block.pos.x)] = block

			# update score
			self.calculate_score(len(delete_rows))

	def run(self):

		# update
		self.input()
		self.timer_update()
		self.sprites.update()

		# drawing
		self.surface.fill(GRAY)
		self.sprites.draw(self.surface)

		self.draw_grid()
		self.display_surface.blit(self.surface, (PADDING,PADDING))
		pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Tetromino:
	def __init__(self, shape, group, create_new_tetromino, field_data):

		# setup
		self.shape = shape
		self.block_positions = TETROMINOS[shape]['shape']
		self.color = TETROMINOS[shape]['color']
		self.create_new_tetromino = create_new_tetromino
		self.field_data = field_data

		# create blocks
		self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

	# collisions
	def next_move_horizontal_collide(self, blocks, amount):
		collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
		return True if any(collision_list) else False

	def next_move_vertical_collide(self, blocks, amount):
		collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
		return True if any(collision_list) else False

	# movement
	def move_horizontal(self, amount):
		if not self.next_move_horizontal_collide(self.blocks, amount):
			for block in self.blocks:
				block.pos.x += amount

	def move_down(self):
		if not self.next_move_vertical_collide(self.blocks, 1):
			for block in self.blocks:
				block.pos.y += 1
		else:
			for block in self.blocks:
				self.field_data[int(block.pos.y)][int(block.pos.x)] = block
			self.create_new_tetromino()

	def hard_drop(self):
		"""Slam the tetromino to the lowest legal row and lock it in place.

		Mirrors what move_down does on a collision (write blocks into
		field_data, then spawn the next piece) but skips the per-row
		animation so D-pad up feels like an instant slam.
		"""
		while not self.next_move_vertical_collide(self.blocks, 1):
			for block in self.blocks:
				block.pos.y += 1
		for block in self.blocks:
			self.field_data[int(block.pos.y)][int(block.pos.x)] = block
		self.create_new_tetromino()

	# rotate
	def rotate(self):
		if self.shape != 'O':

			# 1. pivot point
			pivot_pos = self.blocks[0].pos

			# 2. new block positions
			new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

			# 3. collision check
			for pos in new_block_positions:
				# horizontal
				if pos.x < 0 or pos.x >= COLUMNS:
					return

				# field check -> collision with other pieces
				if self.field_data[int(pos.y)][int(pos.x)]:
					return

				# vertical / floor check
				if pos.y > ROWS:
					return

			# 4. implement new positions
			for i, block in enumerate(self.blocks):
				block.pos = new_block_positions[i]

class Block(pygame.sprite.Sprite):
	def __init__(self, group, pos, color):

		# general
		super().__init__(group)
		self.image = pygame.Surface((CELL_SIZE,CELL_SIZE))
		self.image.fill(color)

		# position
		self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
		self.rect = self.image.get_rect(topleft = self.pos * CELL_SIZE)

	def rotate(self, pivot_pos):

		return pivot_pos + (self.pos - pivot_pos).rotate(90)

	def horizontal_collide(self, x, field_data):
		if not 0 <= x < COLUMNS:
			return True

		if field_data[int(self.pos.y)][x]:
			return True

	def vertical_collide(self, y, field_data):
		if y >= ROWS:
			return True

		if y >= 0 and field_data[y][int(self.pos.x)]:
			return True

	def update(self):

		self.rect.topleft = self.pos * CELL_SIZE
