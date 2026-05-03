"""Sprite classes for Pong paddles, ball movement, and collisions."""

import random
from settings import *

class Block(pygame.sprite.Sprite):
	"""Base sprite for image-backed game objects with a center-positioned rect."""

	def __init__(self,path,x_pos,y_pos):
		"""Load a sprite image and place it at the requested coordinates.

		Args:
			path (str): Relative path to the sprite image file.
			x_pos (float): Initial center x-coordinate.
			y_pos (float): Initial center y-coordinate.

		Returns:
			None.
		"""
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_pos,y_pos))

class Player(Block):
	"""Human-controlled paddle on the right side of the playfield."""

	def __init__(self,path,x_pos,y_pos,speed):
		"""Initialize player paddle movement configuration.

		Args:
			path (str): Relative path to paddle sprite image.
			x_pos (float): Initial center x-coordinate.
			y_pos (float): Initial center y-coordinate.
			speed (int): Per-frame paddle speed in pixels.

		Returns:
			None.
		"""
		super().__init__(path,x_pos,y_pos)
		self.speed = speed
		self.movement = 0

	def screen_constrain(self):
		"""Clamp paddle movement so it cannot leave the screen bounds.

		Args:
			None.

		Returns:
			None.
		"""
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT

	def update(self,ball_group): # does not use ball_group but still needs it
		"""Advance the player paddle and apply screen constraints.

		Args:
			ball_group (pygame.sprite.GroupSingle): Unused group kept for group.update compatibility.

		Returns:
			None.
		"""
		# TODO(refactor): Remove unused ball_group dependency from Player.update signature.
		self.rect.y += self.movement
		self.screen_constrain()

class Opponent(Block):
	"""Simple AI-controlled paddle on the left side of the playfield."""

	def __init__(self,path,x_pos,y_pos,speed):
		"""Initialize opponent paddle movement configuration.

		Args:
			path (str): Relative path to paddle sprite image.
			x_pos (float): Initial center x-coordinate.
			y_pos (float): Initial center y-coordinate.
			speed (int): Per-frame paddle speed in pixels.

		Returns:
			None.
		"""
		super().__init__(path,x_pos,y_pos)
		self.speed = speed

	def update(self,ball_group):
		"""Move the opponent paddle toward the ball's y position.

		Args:
			ball_group (pygame.sprite.GroupSingle): Group containing the active ball.

		Returns:
			None.
		"""
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y:
			self.rect.y -= self.speed
		self.constrain()

	def constrain(self):
		"""Clamp opponent paddle within the visible playfield.

		Args:
			None.

		Returns:
			None.
		"""
		if self.rect.top <= 0: self.rect.top = 0
		if self.rect.bottom >= SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

class Ball(Block):
	"""Ball sprite handling velocity, collisions, scoring reset, and countdown."""

	def __init__(self,path,x_pos,y_pos,speed_x,speed_y,paddles,audio,basic_font,screen):
		"""Initialize ball motion state and rendering dependencies.

		Args:
			path (str): Relative path to ball sprite image.
			x_pos (float): Initial center x-coordinate.
			y_pos (float): Initial center y-coordinate.
			speed_x (int): Base horizontal velocity magnitude.
			speed_y (int): Base vertical velocity magnitude.
			paddles (pygame.sprite.Group): Group of paddle sprites for collision checks.
			audio (Audio): Audio manager used to trigger SFX.
			basic_font (pygame.font.Font): Font used for countdown text.
			screen (pygame.Surface): Surface used to render countdown text.

		Returns:
			None.
		"""
		super().__init__(path,x_pos,y_pos)
		self.speed_x = speed_x * random.choice((-1,1))
		self.speed_y = speed_y * random.choice((-1,1))
		self.paddles = paddles
		self.active = False
		self.score_time = 0
		self.audio = audio

		# TODO(refactor): Decouple UI drawing from Ball by moving countdown rendering elsewhere.
		self.basic_font = basic_font
		self.screen = screen

	def update(self):
		"""Advance ball movement when active or show round restart countdown.

		Args:
			None.

		Returns:
			None.
		"""
		if self.active:
			self.rect.x += self.speed_x
			self.rect.y += self.speed_y
			self.collisions()
		else:
			self.restart_counter()
		
	def collisions(self):
		"""Resolve collisions with walls and paddles, then update velocity.

		Args:
			None.

		Returns:
			None.
		"""
		# TODO(refactor): Cache spritecollide result to avoid duplicate collision queries.
		if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
			self.audio.channel_1.play(self.audio.plob_sound)
			self.speed_y *= -1

		if pygame.sprite.spritecollide(self,self.paddles,False):
			self.audio.channel_1.play(self.audio.plob_sound)
			collision_paddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
			if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
				self.speed_x *= -1
			if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
				self.speed_x *= -1
			if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
				self.rect.top = collision_paddle.bottom
				self.speed_y *= -1
			if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
				self.rect.bottom = collision_paddle.top
				self.speed_y *= -1

	def reset_ball(self):
		"""Reset ball to center, randomize directions, and play score SFX.

		Args:
			None.

		Returns:
			None.
		"""
		self.active = False
		self.speed_x *= random.choice((-1,1))
		self.speed_y *= random.choice((-1,1))
		self.score_time = pygame.time.get_ticks()
		self.rect.center = (SCREEN_WIDTH /2,SCREEN_HEIGHT/2)
		self.audio.channel_2.play(self.audio.score_sound)

	def restart_counter(self):
		"""Render a short 3-2-1 countdown before reactivating the ball.

		Args:
			None.

		Returns:
			None.
		"""
		current_time = pygame.time.get_ticks()
		countdown_number = 3

		if current_time - self.score_time <= 700:
			countdown_number = 3
		if 700 < current_time - self.score_time <= 1400:
			countdown_number = 2
		if 1400 < current_time - self.score_time <= 2100:
			countdown_number = 1
		if current_time - self.score_time >= 2100:
			self.active = True

		time_counter = self.basic_font.render(str(countdown_number),True,ACCENT_COLOR)
		time_counter_rect = time_counter.get_rect(center = (SCREEN_WIDTH /2,SCREEN_HEIGHT/2 + 50))
		pygame.draw.rect(self.screen,BG_COLOR,time_counter_rect)
		self.screen.blit(time_counter,time_counter_rect)