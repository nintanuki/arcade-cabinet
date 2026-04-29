from pathlib import Path

import pygame
from laser import Laser


ASSET_DIR = Path(__file__).resolve().parent

# Controller mapping shared with main.py so input behavior stays consistent.
A_BUTTON = 0
JOYSTICK_DEADZONE = 0.4

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,constraint,speed):
		super().__init__()
		self.image = pygame.image.load(str(ASSET_DIR / 'graphics' / 'player.png')).convert_alpha()
		self.rect = self.image.get_rect(midbottom = pos)
		self.speed = speed
		self.max_x_constraint = constraint
		self.ready = True
		self.laser_time = 0
		self.laser_cooldown = 600

		self.lasers = pygame.sprite.Group()

		self.laser_sound = pygame.mixer.Sound(str(ASSET_DIR / 'audio' / 'laser.wav'))
		self.laser_sound.set_volume(0.5)

	def get_input(self):
		"""Read keyboard and controller input each frame to drive the player ship.

		The horizontal axis is polled from both the keyboard arrow keys and the
		first connected controller's D-pad / left analog stick. The fire input
		listens for ``Space`` on the keyboard and the controller A button so
		players can use whichever input device they prefer without changing any
		settings.
		"""
		keys = pygame.key.get_pressed()
		horizontal_input = 0

		if keys[pygame.K_RIGHT]:
			horizontal_input += 1
		elif keys[pygame.K_LEFT]:
			horizontal_input -= 1

		controller_fire = False
		# Poll every connected joystick so the player can use any controller
		# without us having to wire a "preferred" controller selection.
		for joystick_index in range(pygame.joystick.get_count()):
			joystick = pygame.joystick.Joystick(joystick_index)
			try:
				if not joystick.get_init():
					joystick.init()
				# Read the D-pad first because it gives a clean digital signal.
				if joystick.get_numhats() > 0:
					hat_x, _ = joystick.get_hat(0)
					if hat_x != 0:
						horizontal_input = hat_x
				# Fall back to the analog stick if the D-pad is centered.
				if horizontal_input == 0 and joystick.get_numaxes() > 0:
					axis_x = joystick.get_axis(0)
					if abs(axis_x) >= JOYSTICK_DEADZONE:
						horizontal_input = 1 if axis_x > 0 else -1
				if joystick.get_numbuttons() > 0 and joystick.get_button(A_BUTTON):
					controller_fire = True
			except pygame.error:
				# Device disconnects can race with the polling call.
				continue

		if horizontal_input > 0:
			self.rect.x += self.speed
		elif horizontal_input < 0:
			self.rect.x -= self.speed

		if (keys[pygame.K_SPACE] or controller_fire) and self.ready:
			self.shoot_laser()
			self.ready = False
			self.laser_time = pygame.time.get_ticks()
			self.laser_sound.play()

	def recharge(self):
		if not self.ready:
			current_time = pygame.time.get_ticks()
			if current_time - self.laser_time >= self.laser_cooldown:
				self.ready = True

	def constraint(self):
		if self.rect.left <= 0:
			self.rect.left = 0
		if self.rect.right >= self.max_x_constraint:
			self.rect.right = self.max_x_constraint

	def shoot_laser(self):
		self.lasers.add(Laser(self.rect.center,-8,self.rect.bottom))

	def update(self):
		self.get_input()
		self.constraint()
		self.recharge()
		self.lasers.update()