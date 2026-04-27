from pathlib import Path

import pygame,sys,random
from pygame.math import Vector2


ASSET_DIR = Path(__file__).resolve().parent
ARCADE_ROOT = ASSET_DIR.parent.parent
SELECT_BUTTON = 6
START_BUTTON = 7
L1_BUTTON = 4
R1_BUTTON = 5
A_BUTTON = 0
QUIT_COMBO_BUTTONS = (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)
LEFT_STICK_HORIZONTAL_AXIS = 0
LEFT_STICK_VERTICAL_AXIS = 1
AXIS_DEADZONE = 0.6


def refresh_joysticks():
	"""Reinitialize all currently-connected joysticks.

	Returns:
		list[pygame.joystick.Joystick]: Initialized joystick handles.
	"""
	joysticks = []
	for index in range(pygame.joystick.get_count()):
		joystick = pygame.joystick.Joystick(index)
		joystick.init()
		joysticks.append(joystick)
	return joysticks


def quit_combo_pressed(joysticks):
	"""Check whether the L1+R1+START+SELECT exit combo is held on any controller.

	Args:
		joysticks (list[pygame.joystick.Joystick]): Connected joysticks to inspect.

	Returns:
		bool: True when the four buttons are held simultaneously on any pad.
	"""
	for joystick in joysticks:
		try:
			if all(joystick.get_button(button) for button in QUIT_COMBO_BUTTONS):
				return True
		except pygame.error:
			# A device disconnect can race with the polling call.
			continue
	return False


def close_game():
	"""Close pygame and exit the process so the launcher reopens cleanly."""
	pygame.quit()
	sys.exit()


def set_snake_direction(snake, direction):
	"""Update snake heading while preventing 180-degree reversals.

	Args:
		snake (SNAKE): Active snake instance whose direction may change.
		direction (Vector2): Requested unit-length heading.
	"""
	if direction.y and snake.direction.y != -direction.y:
		snake.direction = direction
	elif direction.x and snake.direction.x != -direction.x:
		snake.direction = direction


def controller_direction(joysticks):
	"""Resolve a heading from the dominant axis on the active analog stick.

	Args:
		joysticks (list[pygame.joystick.Joystick]): Connected joysticks to poll.

	Returns:
		Vector2 | None: Heading vector, or ``None`` when no stick is engaged.
	"""
	strongest_axis_value = 0.0
	selected_direction = None

	for joystick in joysticks:
		try:
			horizontal = joystick.get_axis(LEFT_STICK_HORIZONTAL_AXIS)
			vertical = joystick.get_axis(LEFT_STICK_VERTICAL_AXIS)
		except pygame.error:
			continue

		if abs(horizontal) >= AXIS_DEADZONE and abs(horizontal) >= abs(vertical):
			if abs(horizontal) > strongest_axis_value:
				strongest_axis_value = abs(horizontal)
				selected_direction = Vector2(1,0) if horizontal > 0 else Vector2(-1,0)
		elif abs(vertical) >= AXIS_DEADZONE:
			if abs(vertical) > strongest_axis_value:
				strongest_axis_value = abs(vertical)
				selected_direction = Vector2(0,1) if vertical > 0 else Vector2(0,-1)

	return selected_direction


def toggle_fullscreen():
	"""Toggle fullscreen using pygame's SCALED-aware path.

	The previous implementation reset the display via ``set_mode`` with the
	plain ``FULLSCREEN`` flag, which left the gameplay rendered in a
	720p-sized region in the top-left of the monitor. ``toggle_fullscreen``
	keeps the SCALED renderer's letterboxed scaling intact so the playfield
	fills the screen uniformly.
	"""
	pygame.display.toggle_fullscreen()


def hat_direction(hat_value):
	"""Convert a D-pad hat reading into a snake heading vector.

	Args:
		hat_value (tuple[int, int]): Pygame ``JOYHATMOTION`` ``(x, y)`` reading.

	Returns:
		Vector2 | None: Resulting heading, or ``None`` when the hat is centered.
	"""
	hat_x, hat_y = hat_value
	# Pygame reports y=1 for up and y=-1 for down; the playfield uses screen
	# coordinates where down is positive, so we flip the sign on Y.
	if hat_y == 1:
		return Vector2(0, -1)
	if hat_y == -1:
		return Vector2(0, 1)
	if hat_x == 1:
		return Vector2(1, 0)
	if hat_x == -1:
		return Vector2(-1, 0)
	return None


def load_pause_font(size=32):
	"""Load the shared Pixeled font used for pause overlays across the arcade.

	Falling back to a system font keeps the game playable even if the shared
	asset is missing on a stripped-down install.

	Args:
		size (int): Font height in pixels.

	Returns:
		pygame.font.Font: A ready-to-render font instance.
	"""
	candidate_paths = (
		ARCADE_ROOT / 'font' / 'Pixeled.ttf',
		ASSET_DIR / 'Font' / 'PoetsenOne-Regular.ttf',
	)
	for font_path in candidate_paths:
		try:
			return pygame.font.Font(str(font_path), size)
		except (FileNotFoundError, OSError):
			continue
	return pygame.font.SysFont(None, size)

class SNAKE:
	def __init__(self):
		self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
		self.direction = Vector2(0,0)
		self.new_block = False

		self.head_up = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'head_up.png')).convert_alpha()
		self.head_down = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'head_down.png')).convert_alpha()
		self.head_right = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'head_right.png')).convert_alpha()
		self.head_left = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'head_left.png')).convert_alpha()
		
		self.tail_up = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'tail_up.png')).convert_alpha()
		self.tail_down = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'tail_down.png')).convert_alpha()
		self.tail_right = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'tail_right.png')).convert_alpha()
		self.tail_left = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'tail_left.png')).convert_alpha()

		self.body_vertical = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_vertical.png')).convert_alpha()
		self.body_horizontal = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_horizontal.png')).convert_alpha()

		self.body_tr = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_tr.png')).convert_alpha()
		self.body_tl = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_tl.png')).convert_alpha()
		self.body_br = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_br.png')).convert_alpha()
		self.body_bl = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'body_bl.png')).convert_alpha()
		self.crunch_sound = pygame.mixer.Sound(str(ASSET_DIR / 'Sound' / 'crunch.wav'))

	def draw_snake(self):
		self.update_head_graphics()
		self.update_tail_graphics()

		for index,block in enumerate(self.body):
			x_pos = int(block.x * cell_size)
			y_pos = int(block.y * cell_size)
			block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)

			if index == 0:
				screen.blit(self.head,block_rect)
			elif index == len(self.body) - 1:
				screen.blit(self.tail,block_rect)
			else:
				previous_block = self.body[index + 1] - block
				next_block = self.body[index - 1] - block
				if previous_block.x == next_block.x:
					screen.blit(self.body_vertical,block_rect)
				elif previous_block.y == next_block.y:
					screen.blit(self.body_horizontal,block_rect)
				else:
					if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
						screen.blit(self.body_tl,block_rect)
					elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
						screen.blit(self.body_bl,block_rect)
					elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
						screen.blit(self.body_tr,block_rect)
					elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
						screen.blit(self.body_br,block_rect)

	def update_head_graphics(self):
		head_relation = self.body[1] - self.body[0]
		if head_relation == Vector2(1,0): self.head = self.head_left
		elif head_relation == Vector2(-1,0): self.head = self.head_right
		elif head_relation == Vector2(0,1): self.head = self.head_up
		elif head_relation == Vector2(0,-1): self.head = self.head_down

	def update_tail_graphics(self):
		tail_relation = self.body[-2] - self.body[-1]
		if tail_relation == Vector2(1,0): self.tail = self.tail_left
		elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
		elif tail_relation == Vector2(0,1): self.tail = self.tail_up
		elif tail_relation == Vector2(0,-1): self.tail = self.tail_down

	def move_snake(self):
		if self.new_block == True:
			body_copy = self.body[:]
			body_copy.insert(0,body_copy[0] + self.direction)
			self.body = body_copy[:]
			self.new_block = False
		else:
			body_copy = self.body[:-1]
			body_copy.insert(0,body_copy[0] + self.direction)
			self.body = body_copy[:]

	def add_block(self):
		self.new_block = True

	def play_crunch_sound(self):
		self.crunch_sound.play()

	def reset(self):
		self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
		self.direction = Vector2(0,0)


class FRUIT:
	def __init__(self):
		self.randomize()

	def draw_fruit(self):
		fruit_rect = pygame.Rect(int(self.pos.x * cell_size),int(self.pos.y * cell_size),cell_size,cell_size)
		screen.blit(apple,fruit_rect)
		#pygame.draw.rect(screen,(126,166,114),fruit_rect)

	def randomize(self):
		self.x = random.randint(0,cell_number - 1)
		self.y = random.randint(0,cell_number - 1)
		self.pos = Vector2(self.x,self.y)

class MAIN:
	def __init__(self):
		self.snake = SNAKE()
		self.fruit = FRUIT()

	def update(self):
		self.snake.move_snake()
		self.check_collision()
		self.check_fail()

	def draw_elements(self):
		self.draw_grass()
		self.fruit.draw_fruit()
		self.snake.draw_snake()
		self.draw_score()

	def check_collision(self):
		if self.fruit.pos == self.snake.body[0]:
			self.fruit.randomize()
			self.snake.add_block()
			self.snake.play_crunch_sound()

		for block in self.snake.body[1:]:
			if block == self.fruit.pos:
				self.fruit.randomize()

	def check_fail(self):
		if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
			self.game_over()

		for block in self.snake.body[1:]:
			if block == self.snake.body[0]:
				self.game_over()
		
	def game_over(self):
		self.snake.reset()

	def draw_grass(self):
		grass_color = (167,209,61)
		for row in range(cell_number):
			if row % 2 == 0: 
				for col in range(cell_number):
					if col % 2 == 0:
						grass_rect = pygame.Rect(col * cell_size,row * cell_size,cell_size,cell_size)
						pygame.draw.rect(screen,grass_color,grass_rect)
			else:
				for col in range(cell_number):
					if col % 2 != 0:
						grass_rect = pygame.Rect(col * cell_size,row * cell_size,cell_size,cell_size)
						pygame.draw.rect(screen,grass_color,grass_rect)			

	def draw_score(self):
		score_text = str(len(self.snake.body) - 3)
		score_surface = game_font.render(score_text,True,(56,74,12))
		score_x = int(cell_size * cell_number - 60)
		score_y = int(cell_size * cell_number - 40)
		score_rect = score_surface.get_rect(center = (score_x,score_y))
		apple_rect = apple.get_rect(midright = (score_rect.left,score_rect.centery))
		bg_rect = pygame.Rect(apple_rect.left,apple_rect.top,apple_rect.width + score_rect.width + 6,apple_rect.height)

		pygame.draw.rect(screen,(167,209,61),bg_rect)
		screen.blit(score_surface,score_rect)
		screen.blit(apple,apple_rect)
		pygame.draw.rect(screen,(56,74,12),bg_rect,2)

pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
pygame.joystick.init()
cell_size = 40
cell_number = 20
# Keep SCALED on the initial display so pygame.display.toggle_fullscreen()
# scales the playfield uniformly instead of leaving the gameplay rendered in
# the top-left corner during fullscreen.
screen = pygame.display.set_mode((cell_number * cell_size,cell_number * cell_size), pygame.SCALED)
clock = pygame.time.Clock()
apple = pygame.image.load(str(ASSET_DIR / 'Graphics' / 'apple.png')).convert_alpha()
game_font = pygame.font.Font(str(ASSET_DIR / 'Font' / 'PoetsenOne-Regular.ttf'), 25)
pause_font = load_pause_font(32)

# TODO: pause sound assets are added by the user; the playback hook below
# guards against a missing file so the game keeps running until then.
PAUSE_SOUND_PATH = ASSET_DIR / 'Sound' / 'sfx_sounds_pause2_in.wav'
UNPAUSE_SOUND_PATH = ASSET_DIR / 'Sound' / 'sfx_sounds_pause2_out.wav'


def load_optional_sound(sound_path):
	"""Load a sound file, returning None when the asset is missing.

	Args:
		sound_path (Path): Filesystem location of the candidate sound.

	Returns:
		pygame.mixer.Sound | None: Loaded sound, or ``None`` when unavailable.
	"""
	try:
		if sound_path.exists():
			return pygame.mixer.Sound(str(sound_path))
	except pygame.error:
		# Mixer can refuse to load malformed assets; treat that as missing.
		return None
	return None


pause_sound = load_optional_sound(PAUSE_SOUND_PATH)
unpause_sound = load_optional_sound(UNPAUSE_SOUND_PATH)


def play_optional_sound(sound):
	"""Play a sound when one is available; do nothing otherwise."""
	if sound is not None:
		sound.play()


def render_pause_overlay():
	"""Draw a centered PAUSED label above the current snake field."""
	pause_text = pause_font.render('PAUSED', True, (56, 74, 12))
	pause_rect = pause_text.get_rect(center=(cell_number * cell_size // 2, cell_number * cell_size // 2))
	# Soft tinted backdrop so the pause label remains readable on the
	# bright grass tiles.
	overlay = pygame.Surface((cell_number * cell_size, cell_number * cell_size), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 110))
	screen.blit(overlay, (0, 0))
	screen.blit(pause_text, pause_rect)


def run_pause_loop():
	"""Block updates with a PAUSED overlay until the player resumes or quits."""
	# Reassign the module-level joysticks list when controllers are added or
	# removed so the quit-combo check keeps working through the pause window.
	global joysticks
	play_optional_sound(pause_sound)
	while True:
		if quit_combo_pressed(joysticks):
			close_game()

		for pause_event in pygame.event.get():
			if pause_event.type == pygame.QUIT:
				close_game()
			if pause_event.type == pygame.JOYDEVICEADDED or pause_event.type == pygame.JOYDEVICEREMOVED:
				joysticks = refresh_joysticks()
			if pause_event.type == pygame.KEYDOWN:
				if pause_event.key == pygame.K_F11:
					toggle_fullscreen()
				elif pause_event.key == pygame.K_ESCAPE:
					close_game()
				elif pause_event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					play_optional_sound(unpause_sound)
					return
			if pause_event.type == pygame.JOYBUTTONDOWN:
				if pause_event.button == SELECT_BUTTON:
					toggle_fullscreen()
				elif pause_event.button == START_BUTTON:
					play_optional_sound(unpause_sound)
					return

		# Repaint the last frame plus the pause overlay each tick so the
		# screen stays alive (and the overlay stays visible during fullscreen
		# transitions) without advancing snake state.
		screen.fill((175, 215, 70))
		main_game.draw_elements()
		render_pause_overlay()
		pygame.display.update()
		clock.tick(60)

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE,150)

main_game = MAIN()
joysticks = refresh_joysticks()
controller_axis_engaged = False
hat_engaged = False

while True:
	if quit_combo_pressed(joysticks):
		close_game()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			close_game()
		if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
			joysticks = refresh_joysticks()
		if event.type == SCREEN_UPDATE:
			main_game.update()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				set_snake_direction(main_game.snake, Vector2(0,-1))
			if event.key == pygame.K_RIGHT:
				set_snake_direction(main_game.snake, Vector2(1,0))
			if event.key == pygame.K_DOWN:
				set_snake_direction(main_game.snake, Vector2(0,1))
			if event.key == pygame.K_LEFT:
				set_snake_direction(main_game.snake, Vector2(-1,0))
			if event.key == pygame.K_F11:
				# Use pygame.display.toggle_fullscreen so the SCALED window
				# stretches uniformly instead of leaving the playfield in the
				# top-left corner of a native-resolution fullscreen surface.
				toggle_fullscreen()
			if event.key == pygame.K_ESCAPE:
				close_game()
			if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
				run_pause_loop()
		if event.type == pygame.JOYBUTTONDOWN:
			if event.button == SELECT_BUTTON:
				toggle_fullscreen()
			if event.button == START_BUTTON:
				run_pause_loop()
		if event.type == pygame.JOYHATMOTION:
			# Edge-trigger D-pad input: only steer once per push so the snake
			# does not whip back and forth while the hat is held.
			direction = hat_direction(event.value)
			if direction is None:
				hat_engaged = False
			elif not hat_engaged:
				set_snake_direction(main_game.snake, direction)
				hat_engaged = True

	analog_direction = controller_direction(joysticks)
	if analog_direction is None:
		controller_axis_engaged = False
	elif not controller_axis_engaged:
		set_snake_direction(main_game.snake, analog_direction)
		controller_axis_engaged = True

	screen.fill((175,215,70))
	main_game.draw_elements()
	pygame.display.update()
	clock.tick(60)