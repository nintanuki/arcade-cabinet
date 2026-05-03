import pygame, sys, time
from settings import *
from sprites import BG, Ground, Plane, Obstacle
from crt import CRT

# Controller button constants (for XInput/SDL2 mappings)
START_BUTTON = 7
SELECT_BUTTON = 6
BACK_BUTTON = 6  # alias for select
A_BUTTON = 0
L1_BUTTON = 4
R1_BUTTON = 5

# Quit combo: START + SELECT + L1 + R1
QUIT_COMBO = [START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON]

class Game:
	def __init__(self):
		
		# setup
		pygame.init()
		self.display_surface = pygame.display.set_mode((ScreenSettings.WIDTH,ScreenSettings.HEIGHT))
		pygame.display.set_caption('Flappy Bird')
		self.clock = pygame.time.Clock()
		self.active = True

		# sprite groups
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		# scale factor
		bg_height = pygame.image.load('assets/graphics/environment/background.png').get_height()
		self.scale_factor = ScreenSettings.HEIGHT / bg_height

		# sprite setup 
		BG(self.all_sprites, self.scale_factor)
		Ground([self.all_sprites, self.collision_sprites], self.scale_factor)
		self.plane = Plane(self.all_sprites, self.scale_factor / 1.7)

		# timer
		self.obstacle_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obstacle_timer, 1400)

		# text
		self.font = pygame.font.Font('assets/graphics/font/BD_Cartoon_Shout.ttf', 30)
		self.score = 0
		self.start_offset = 0

		# menu
		self.menu_surf = pygame.image.load('assets/graphics/ui/menu.png').convert_alpha()
		self.menu_rect = self.menu_surf.get_rect(center=(ScreenSettings.WIDTH / 2, ScreenSettings.HEIGHT / 2))

		# CRT
		self.crt = CRT(self.display_surface)

		# music 
		self.music = pygame.mixer.Sound('assets/sounds/music.wav')
		self.music.play(loops=-1)

		# Pause state
		self.paused = False
		self.pause_font = pygame.font.Font('assets/graphics/font/BD_Cartoon_Shout.ttf', 48)
		self.pause_sfx_in = pygame.mixer.Sound('assets/sounds/sfx_sounds_pause2_in.ogg')
		self.pause_sfx_out = pygame.mixer.Sound('assets/sounds/sfx_sounds_pause2_out.ogg')

		# Controller support
		pygame.joystick.init()
		self.joysticks = []
		self.refresh_joysticks()
	def refresh_joysticks(self):
		self.joysticks = []
		for i in range(pygame.joystick.get_count()):
			js = pygame.joystick.Joystick(i)
			if not js.get_init():
				js.init()
			self.joysticks.append(js)

	def quit_combo_pressed(self):
		# Return True if START + SELECT + L1 + R1 are held on any controller
		if len(self.joysticks) != pygame.joystick.get_count():
			self.refresh_joysticks()
		for js in self.joysticks:
			try:
				if all(js.get_button(btn) for btn in QUIT_COMBO):
					return True
			except pygame.error:
				continue
		return False

	def toggle_fullscreen(self):
		pygame.display.toggle_fullscreen()

	def toggle_pause(self):
		self.paused = not self.paused
		if self.paused:
			self.pause_sfx_in.play()
			self.music.set_volume(0.2)
		else:
			self.pause_sfx_out.play()
			self.music.set_volume(1.0)

	def collisions(self):
		if pygame.sprite.spritecollide(self.plane,self.collision_sprites,False,pygame.sprite.collide_mask)\
		or self.plane.rect.top <= 0:
			for sprite in self.collision_sprites.sprites():
				if sprite.sprite_type == 'obstacle':
					sprite.kill()
			self.active = False
			self.plane.kill()

	def display_score(self):
		if self.active:
			self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
			y = ScreenSettings.HEIGHT / 10
		else:
			y = ScreenSettings.HEIGHT / 2 + (self.menu_rect.height / 1.5)

		score_surf = self.font.render(str(self.score),True,'black')
		score_rect = score_surf.get_rect(midtop = (ScreenSettings.WIDTH / 2,y))
		self.display_surface.blit(score_surf,score_rect)


	def run(self):
		last_time = time.time()
		while True:
			dt = time.time() - last_time
			last_time = time.time()

			# Quit combo
			if self.quit_combo_pressed():
				pygame.quit()
				sys.exit()

			for event in pygame.event.get():
				# Hotplug controllers
				if event.type in (getattr(pygame, 'JOYDEVICEADDED', None), getattr(pygame, 'JOYDEVICEREMOVED', None)):
					self.refresh_joysticks()
					continue

				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()
					if event.key == pygame.K_F11:
						self.toggle_fullscreen()
					if event.key == pygame.K_p:
						self.toggle_pause()

				if event.type == pygame.JOYBUTTONDOWN:
					# A button = jump
					if event.button == A_BUTTON:
						if self.active and not self.paused:
							self.plane.jump()
					# Start or Select/Back toggles pause/fullscreen
					if event.button == START_BUTTON:
						self.toggle_pause()
					if event.button == BACK_BUTTON or event.button == SELECT_BUTTON:
						self.toggle_fullscreen()

				if event.type == pygame.MOUSEBUTTONDOWN:
					if self.active and not self.paused:
						self.plane.jump()
					elif not self.active and not self.paused:
						self.plane = Plane(self.all_sprites, self.scale_factor / 1.7)
						self.active = True
						self.start_offset = pygame.time.get_ticks()

				if event.type == self.obstacle_timer and self.active and not self.paused:
					Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 1.1)

			# game logic
			self.display_surface.fill('black')
			if not self.paused:
				self.all_sprites.update(dt)
			self.all_sprites.draw(self.display_surface)
			self.display_score()

			if self.active and not self.paused:
				self.collisions()
			elif not self.active:
				self.display_surface.blit(self.menu_surf, self.menu_rect)

			if self.paused:
				pause_surf = self.pause_font.render('PAUSED', True, 'yellow')
				pause_rect = pause_surf.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))
				self.display_surface.blit(pause_surf, pause_rect)

			self.crt.draw()
			pygame.display.update()
			# self.clock.tick(ScreenSettings.FPS)

if __name__ == '__main__':
	game = Game()
	game.run()