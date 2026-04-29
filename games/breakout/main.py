import pygame,sys,time,os

# Make all asset paths resolve relative to this script, regardless of cwd
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surfacemaker import SurfaceMaker
from random import choice, randint

class Game:
	def __init__(self):

		# general setup
		pygame.init()
		# SCALED keeps the playfield centered and uniformly scaled when
		# pygame.display.toggle_fullscreen() flips into fullscreen mode.
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT), pygame.SCALED)
		pygame.display.set_caption('Breakout')

		self.setup_controllers()

		# background
		self.bg = self.create_bg()

		# sprite group setup
		self.all_sprites = pygame.sprite.Group()
		self.block_sprites = pygame.sprite.Group()
		self.upgrade_sprites = pygame.sprite.Group()
		self.projectile_sprites = pygame.sprite.Group()

		# setup
		self.surfacemaker = SurfaceMaker()
		# Hand the live joystick list to the paddle so analog-stick polling
		# always reads the same controllers the Game tracks for hot-plug.
		self.player = Player(self.all_sprites,self.surfacemaker,self.joysticks)
		self.stage_setup()
		self.ball = Ball(self.all_sprites,self.player,self.block_sprites)

		# hearts
		self.heart_surf = pygame.image.load('graphics/other/heart.png').convert_alpha()

		# projectile
		self.projectile_surf = pygame.image.load('graphics/other/projectile.png').convert_alpha()
		self.can_shoot = True
		self.shoot_time = 0

		# crt
		self.crt = CRT()

		self.laser_sound = pygame.mixer.Sound('sounds/laser.wav')
		self.laser_sound.set_volume(0.1)

		self.powerup_sound = pygame.mixer.Sound('sounds/powerup.wav')
		self.powerup_sound.set_volume(0.1)

		self.laserhit_sound = pygame.mixer.Sound('sounds/laser_hit.wav')
		self.laserhit_sound.set_volume(0.02)

		self.music = pygame.mixer.Sound('sounds/music.wav')
		self.music.set_volume(0.1)
		self.music.play(loops = -1)

	def setup_controllers(self):
		"""Initialize joysticks and store them in a list for later use.

		The Player keeps a reference to this same list so analog-stick polling
		survives hot-plug events without re-wiring the paddle.
		"""
		pygame.joystick.init()
		self.joysticks = []
		for index in range(pygame.joystick.get_count()):
			joystick = pygame.joystick.Joystick(index)
			joystick.init()
			self.joysticks.append(joystick)

	def refresh_joysticks(self):
		"""Rebuild the joystick list in place after a connect/disconnect.

		Mutating the existing list (rather than reassigning) keeps the
		reference cached on Player valid.
		"""
		self.joysticks.clear()
		for index in range(pygame.joystick.get_count()):
			joystick = pygame.joystick.Joystick(index)
			joystick.init()
			self.joysticks.append(joystick)

	def quit_combo_pressed(self):
		"""Return True when L1 + R1 + START + SELECT are held on any controller.

		Returns:
			bool: True when the four buttons are held simultaneously on any pad.
		"""
		for joystick in self.joysticks:
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
		sys.exit()

	def fire(self):
		"""Activate the ball and, when ready, fire a laser projectile.

		Mirrors what SPACE does on the keyboard so the controller's A button
		matches the keyboard binding exactly.
		"""
		self.ball.active = True
		if self.can_shoot:
			self.create_projectile()
			self.can_shoot = False
			self.shoot_time = pygame.time.get_ticks()

	def create_upgrade(self,pos):
		upgrade_type = choice(UPGRADES)
		Upgrade(pos,upgrade_type,[self.all_sprites,self.upgrade_sprites])

	def create_bg(self):
		bg_original = pygame.image.load('graphics/other/bg.png').convert()
		scale_factor = WINDOW_HEIGHT / bg_original.get_height()
		scaled_width = bg_original.get_width() * scale_factor
		scaled_height = bg_original.get_height() * scale_factor
		scaled_bg = pygame.transform.scale(bg_original,(scaled_width,scaled_height)) 
		return scaled_bg

	def stage_setup(self):
		# cycle through all rows and columns of BLOCK MAP
		for row_index, row in enumerate(BLOCK_MAP):
			for col_index, col in enumerate(row):
				if col != ' ':
					# find the x and y position for each individual block
					x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
					y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
					Block(col,(x,y),[self.all_sprites,self.block_sprites],self.surfacemaker,self.create_upgrade)

	def display_hearts(self):
		for i in range(self.player.hearts):
			x = 2 + i * (self.heart_surf.get_width() + 2)
			self.display_surface.blit(self.heart_surf,(x,4))

	def upgrade_collision(self):
		overlap_sprites = pygame.sprite.spritecollide(self.player,self.upgrade_sprites,True)
		for sprite in overlap_sprites:
			self.player.upgrade(sprite.upgrade_type)
			self.powerup_sound.play()

	def create_projectile(self):
		self.laser_sound.play()
		for projectile in self.player.laser_rects:
			Projectile(
				projectile.midtop - pygame.math.Vector2(0,30),
				self.projectile_surf,
				[self.all_sprites, self.projectile_sprites])

	def laser_timer(self):
		if pygame.time.get_ticks() - self.shoot_time >= 500:
			self.can_shoot = True

	def projectile_block_collision(self):
		for projectile in self.projectile_sprites:
			overlap_sprites  = pygame.sprite.spritecollide(projectile,self.block_sprites,False)
			if overlap_sprites:
				for sprite in overlap_sprites:
					sprite.get_damage(1)
				projectile.kill()
				self.laserhit_sound.play()

	def run(self):
		last_time = time.time()
		while True:

			# delta time
			dt = time.time() - last_time
			last_time = time.time()

			# Held-button quit combo. Caught both here and on JOYBUTTONDOWN so a
			# combo that lands mid-frame still exits without a one-frame stall.
			if self.quit_combo_pressed():
				self.close_game()

			# event loop
			for event in pygame.event.get():
				if event.type == pygame.QUIT or self.player.hearts <= 0:
					self.close_game()
				if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
					self.refresh_joysticks()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_F11:
						pygame.display.toggle_fullscreen()
					elif event.key == pygame.K_ESCAPE:
						# ESC always exits the game and returns to the
						# launcher, matching the L1+R1+START+SELECT combo.
						self.close_game()
					elif event.key == pygame.K_SPACE:
						self.fire()
				if event.type == pygame.JOYBUTTONDOWN:
					if event.button == SELECT_BUTTON:
						# SELECT mirrors F11 so the controller has a
						# fullscreen toggle that matches the keyboard.
						pygame.display.toggle_fullscreen()
					elif event.button == A_BUTTON:
						self.fire()

			# draw bg
			self.display_surface.blit(self.bg,(0,0))
			
			# update the game
			self.all_sprites.update(dt)
			self.upgrade_collision()
			self.laser_timer()
			self.projectile_block_collision()

			# draw the frame
			self.all_sprites.draw(self.display_surface)
			self.display_hearts()

			# crt styling
			self.crt.draw()

			# update window
			pygame.display.update()

class CRT:
	def __init__(self):
		vignette = pygame.image.load('graphics/other/tv.png').convert_alpha()
		self.scaled_vignette = pygame.transform.scale(vignette,(WINDOW_WIDTH,WINDOW_HEIGHT))
		self.display_surface = pygame.display.get_surface()
		self.create_crt_lines()

	def create_crt_lines(self):
		line_height = 4
		line_amount = WINDOW_HEIGHT // line_height
		for line in range(line_amount):
			y = line * line_height
			pygame.draw.line(self.scaled_vignette, (20,20,20), (0,y), (WINDOW_WIDTH,y),1)

	def draw(self):
		self.scaled_vignette.set_alpha(randint(60,75))
		self.display_surface.blit(self.scaled_vignette,(0,0))

if __name__ == '__main__':
	game = Game()
	game.run()
