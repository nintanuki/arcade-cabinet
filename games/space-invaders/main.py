import pygame, sys
from pathlib import Path
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser


ASSET_DIR = Path(__file__).resolve().parent
ARCADE_ROOT = ASSET_DIR.parent.parent

# Controller button mapping shared with the rest of the arcade so the same
# physical buttons keep the same meaning across every game.
A_BUTTON = 0
SELECT_BUTTON = 6
START_BUTTON = 7
L1_BUTTON = 4
R1_BUTTON = 5
QUIT_COMBO_BUTTONS = (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)


def refresh_joysticks():
	"""Reinitialize all currently connected joysticks.

	Returns:
		list[pygame.joystick.Joystick]: Initialized joystick handles.
	"""
	connected = []
	for index in range(pygame.joystick.get_count()):
		joystick = pygame.joystick.Joystick(index)
		if not joystick.get_init():
			joystick.init()
		connected.append(joystick)
	return connected


def quit_combo_pressed(connected_joysticks):
	"""Check whether the L1+R1+START+SELECT exit combo is held on any controller.

	Args:
		connected_joysticks (list[pygame.joystick.Joystick]): Currently cached joysticks.

	Returns:
		bool: True when the four buttons are simultaneously held on any pad.
	"""
	for joystick in connected_joysticks:
		try:
			if all(joystick.get_button(button) for button in QUIT_COMBO_BUTTONS):
				return True
		except pygame.error:
			continue
	return False


def close_game():
	"""Shut down pygame and exit the process so the launcher reopens."""
	pygame.quit()
	sys.exit()


def load_pause_font(size=20):
	"""Load the shared Pixeled font used for the pause overlay.

	Args:
		size (int): Font height in pixels.

	Returns:
		pygame.font.Font: A ready-to-render font instance, with sensible fallbacks.
	"""
	candidate_paths = (
		ASSET_DIR / 'font' / 'Pixeled.ttf',
		ARCADE_ROOT / 'font' / 'Pixeled.ttf',
	)
	for font_path in candidate_paths:
		try:
			return pygame.font.Font(str(font_path), size)
		except (FileNotFoundError, OSError):
			continue
	return pygame.font.SysFont(None, size)


def load_optional_sound(sound_path):
	"""Load a sound file when present, returning ``None`` for missing assets.

	Args:
		sound_path (Path): Filesystem location of the candidate sound.

	Returns:
		pygame.mixer.Sound | None: Loaded sound, or ``None`` when unavailable.
	"""
	try:
		if sound_path.exists():
			return pygame.mixer.Sound(str(sound_path))
	except pygame.error:
		return None
	return None


class Game:
	def __init__(self):
		# Player setup
		player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
		self.player = pygame.sprite.GroupSingle(player_sprite)

		# health and score setup
		self.lives = 3
		self.live_surf = pygame.image.load(str(ASSET_DIR / 'graphics' / 'player.png')).convert_alpha()
		self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
		self.score = 0
		self.font = pygame.font.Font(str(ASSET_DIR / 'font' / 'Pixeled.ttf'),20)

		# Obstacle setup
		self.shape = obstacle.shape
		self.block_size = 6
		self.blocks = pygame.sprite.Group()
		self.obstacle_amount = 4
		self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
		self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

		# Alien setup
		self.aliens = pygame.sprite.Group()
		self.alien_lasers = pygame.sprite.Group()
		self.alien_setup(rows = 6, cols = 8)
		self.alien_direction = 1

		# Extra setup
		self.extra = pygame.sprite.GroupSingle()
		self.extra_spawn_time = randint(40,80)

		# Audio
		music = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'music.wav'))
		music.set_volume(0.2)
		music.play(loops = -1)
		self.laser_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'laser.wav'))
		self.laser_sound.set_volume(0.5)
		self.explosion_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'explosion.wav'))
		self.explosion_sound.set_volume(0.3)

	def create_obstacle(self, x_start, y_start,offset_x):
		for row_index, row in enumerate(self.shape):
			for col_index,col in enumerate(row):
				if col == 'x':
					x = x_start + col_index * self.block_size + offset_x
					y = y_start + row_index * self.block_size
					block = obstacle.Block(self.block_size,(241,79,80),x,y)
					self.blocks.add(block)

	def create_multiple_obstacles(self,*offset,x_start,y_start):
		for offset_x in offset:
			self.create_obstacle(x_start,y_start,offset_x)

	def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
		for row_index, row in enumerate(range(rows)):
			for col_index, col in enumerate(range(cols)):
				x = col_index * x_distance + x_offset
				y = row_index * y_distance + y_offset
				
				if row_index == 0: alien_sprite = Alien('yellow',x,y)
				elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
				else: alien_sprite = Alien('red',x,y)
				self.aliens.add(alien_sprite)

	def alien_position_checker(self):
		all_aliens = self.aliens.sprites()
		for alien in all_aliens:
			if alien.rect.right >= screen_width:
				self.alien_direction = -1
				self.alien_move_down(2)
			elif alien.rect.left <= 0:
				self.alien_direction = 1
				self.alien_move_down(2)

	def alien_move_down(self,distance):
		if self.aliens:
			for alien in self.aliens.sprites():
				alien.rect.y += distance

	def alien_shoot(self):
		if self.aliens.sprites():
			random_alien = choice(self.aliens.sprites())
			laser_sprite = Laser(random_alien.rect.center,6,screen_height)
			self.alien_lasers.add(laser_sprite)
			self.laser_sound.play()

	def extra_alien_timer(self):
		self.extra_spawn_time -= 1
		if self.extra_spawn_time <= 0:
			self.extra.add(Extra(choice(['right','left']),screen_width))
			self.extra_spawn_time = randint(400,800)

	def collision_checks(self):

		# player lasers 
		if self.player.sprite.lasers:
			for laser in self.player.sprite.lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()
					

				# alien collisions
				aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
				if aliens_hit:
					for alien in aliens_hit:
						self.score += alien.value
					laser.kill()
					self.explosion_sound.play()

				# extra collision
				if pygame.sprite.spritecollide(laser,self.extra,True):
					self.score += 500
					laser.kill()

		# alien lasers 
		if self.alien_lasers:
			for laser in self.alien_lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()

				if pygame.sprite.spritecollide(laser,self.player,False):
					laser.kill()
					self.lives -= 1
					if self.lives <= 0:
						pygame.quit()
						sys.exit()

		# aliens
		if self.aliens:
			for alien in self.aliens:
				pygame.sprite.spritecollide(alien,self.blocks,True)

				if pygame.sprite.spritecollide(alien,self.player,False):
					pygame.quit()
					sys.exit()
	
	def display_lives(self):
		for live in range(self.lives - 1):
			x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
			screen.blit(self.live_surf,(x,8))

	def display_score(self):
		score_surf = self.font.render(f'score: {self.score}',False,'white')
		score_rect = score_surf.get_rect(topleft = (10,-10))
		screen.blit(score_surf,score_rect)

	def victory_message(self):
		if not self.aliens.sprites():
			victory_surf = self.font.render('You won',False,'white')
			victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
			screen.blit(victory_surf,victory_rect)

	def run(self):
		self.player.update()
		self.alien_lasers.update()
		self.extra.update()
		
		self.aliens.update(self.alien_direction)
		self.alien_position_checker()
		self.extra_alien_timer()
		self.collision_checks()
		
		self.player.sprite.lasers.draw(screen)
		self.player.draw(screen)
		self.blocks.draw(screen)
		self.aliens.draw(screen)
		self.alien_lasers.draw(screen)
		self.extra.draw(screen)
		self.display_lives()
		self.display_score()
		self.victory_message()

class CRT:
	def __init__(self):
		self.tv = pygame.image.load(str(ASSET_DIR / 'graphics' / 'tv.png')).convert_alpha()
		self.tv = pygame.transform.scale(self.tv,(screen_width,screen_height))

	def create_crt_lines(self):
		line_height = 3
		line_amount = int(screen_height / line_height)
		for line in range(line_amount):
			y_pos = line * line_height
			pygame.draw.line(self.tv,'black',(0,y_pos),(screen_width,y_pos),1)

	def draw(self):
		self.tv.set_alpha(randint(75,90))
		self.create_crt_lines()
		screen.blit(self.tv,(0,0))

def render_pause_overlay(screen, screen_width, screen_height, pause_font):
	"""Render the centered ``PAUSED`` overlay across an active Space Invaders frame.

	Args:
		screen (pygame.Surface): Active display surface.
		screen_width (int): Width of the playfield in pixels.
		screen_height (int): Height of the playfield in pixels.
		pause_font (pygame.font.Font): Font used for the pause label.
	"""
	# Translucent backdrop keeps the pause text readable on the busy alien
	# field underneath without fully obscuring the run state.
	overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 140))
	screen.blit(overlay, (0, 0))

	pause_text = pause_font.render('PAUSED', False, 'white')
	pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
	screen.blit(pause_text, pause_rect)


def run_pause_loop(screen, clock, frozen_frame, pause_overlay_renderer, joysticks_ref, pause_sound, unpause_sound):
	"""Block the main loop until the player resumes, exits, or quits.

	The pause loop only redraws a snapshot of the frame captured when pause
	began so alien movement, lasers, and collision checks do not advance
	while the player is paused.

	Args:
		screen (pygame.Surface): Active display surface used for repainting.
		clock (pygame.time.Clock): Frame timer to keep the pause loop responsive.
		frozen_frame (pygame.Surface): Snapshot of the frame to redisplay each tick.
		pause_overlay_renderer (Callable[[], None]): Draws the PAUSED overlay on top.
		joysticks_ref (list): Mutable reference to the cached joystick list.
		pause_sound (pygame.mixer.Sound | None): Pause-in sound, played on entry when present.
		unpause_sound (pygame.mixer.Sound | None): Pause-out sound, played on resume when present.
	"""
	if pause_sound is not None:
		pause_sound.play()

	while True:
		if quit_combo_pressed(joysticks_ref):
			close_game()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				close_game()
			if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
				# Keep the cached list current so the quit combo keeps working.
				joysticks_ref[:] = refresh_joysticks()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_F11:
					pygame.display.toggle_fullscreen()
				elif event.key == pygame.K_ESCAPE:
					close_game()
				elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					if unpause_sound is not None:
						unpause_sound.play()
					return
			if event.type == pygame.JOYBUTTONDOWN:
				if event.button == SELECT_BUTTON:
					pygame.display.toggle_fullscreen()
				elif event.button == START_BUTTON:
					if unpause_sound is not None:
						unpause_sound.play()
					return

		# Repaint the frozen pre-pause frame each tick so the screen stays
		# alive (and the overlay survives fullscreen transitions) without
		# advancing alien movement or laser timing.
		screen.blit(frozen_frame, (0, 0))
		pause_overlay_renderer()
		pygame.display.flip()
		clock.tick(60)


if __name__ == '__main__':
	pygame.init()
	pygame.joystick.init()
	screen_width = 600
	screen_height = 600
	# pygame.SCALED keeps the playfield centered and uniformly scaled when
	# pygame.display.toggle_fullscreen() flips into fullscreen mode.
	screen = pygame.display.set_mode((screen_width,screen_height), pygame.SCALED)
	pygame.display.set_caption('Space Invaders')
	clock = pygame.time.Clock()
	game = Game()
	crt = CRT()
	pause_font = load_pause_font(20)

	joysticks = refresh_joysticks()

	# TODO: pause sound assets are added by the user; the playback hook below
	# guards against a missing file so the game keeps running until then.
	pause_sound = load_optional_sound(ASSET_DIR / 'audio' / 'sfx_sounds_pause2_in.wav')
	unpause_sound = load_optional_sound(ASSET_DIR / 'audio' / 'sfx_sounds_pause2_out.wav')

	ALIENLASER = pygame.USEREVENT + 1
	pygame.time.set_timer(ALIENLASER,800)

	def draw_pause_overlay():
		"""Draw the PAUSED label on top of the current display surface."""
		render_pause_overlay(screen, screen_width, screen_height, pause_font)

	def enter_pause():
		"""Snapshot the current frame and run the pause loop until resume/exit.

		Capturing the frame here means alien movement, lasers, and obstacle
		blocks all keep their pre-pause state; the loop simply redraws the
		snapshot each tick instead of stepping the simulation.
		"""
		frozen_frame = screen.copy()
		run_pause_loop(screen, clock, frozen_frame, draw_pause_overlay, joysticks, pause_sound, unpause_sound)

	while True:
		if quit_combo_pressed(joysticks):
			close_game()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				close_game()
			if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
				joysticks = refresh_joysticks()
			if event.type == ALIENLASER:
				game.alien_shoot()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_F11:
					pygame.display.toggle_fullscreen()
				elif event.key == pygame.K_ESCAPE:
					close_game()
				elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					enter_pause()
			if event.type == pygame.JOYBUTTONDOWN:
				if event.button == SELECT_BUTTON:
					pygame.display.toggle_fullscreen()
				elif event.button == START_BUTTON:
					enter_pause()

		screen.fill((30,30,30))
		game.run()
		crt.draw()

		pygame.display.flip()
		clock.tick(60)