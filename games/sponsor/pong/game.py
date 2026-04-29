"""Game state orchestration for Pong (scores, updates, and rendering)."""

from settings import *

class GameManager:
	"""Coordinate sprite updates and score rendering for a Pong round."""

	def __init__(self,ball_group,paddle_group,basic_font,screen):
		"""Create a game manager with references to core render/update objects.

		Args:
			ball_group (pygame.sprite.GroupSingle): Group containing the ball sprite.
			paddle_group (pygame.sprite.Group): Group containing player and opponent paddles.
			basic_font (pygame.font.Font): Font used for on-screen score text.
			screen (pygame.Surface): Display surface used for drawing.

		Returns:
			None.
		"""
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group
		self.basic_font = basic_font
		self.screen = screen

	def run_game(self):
		"""Draw and update all active sprites, then evaluate score changes.

		Args:
			None.

		Returns:
			None.
		"""
		# Drawing the game objects
		self.paddle_group.draw(self.screen)
		self.ball_group.draw(self.screen)

		# Updating the game objects
		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()

	def reset_ball(self):
		"""Update scores and reset the ball when either player concedes.

		Args:
			None.

		Returns:
			None.
		"""
		# TODO(bug): If the ball overlaps both bounds in one frame, both scores could increment.
		if self.ball_group.sprite.rect.right >= SCREEN_WIDTH :
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()

	def draw_score(self):
		"""Render current player and opponent score text near center court.

		Args:
			None.

		Returns:
			None.
		"""
		player_score = self.basic_font.render(str(self.player_score),True,ACCENT_COLOR)
		opponent_score = self.basic_font.render(str(self.opponent_score),True,ACCENT_COLOR)

		player_score_rect = player_score.get_rect(midleft = (SCREEN_WIDTH  / 2 + 40,SCREEN_HEIGHT/2))
		opponent_score_rect = opponent_score.get_rect(midright = (SCREEN_WIDTH  / 2 - 40,SCREEN_HEIGHT/2))

		self.screen.blit(player_score,player_score_rect)
		self.screen.blit(opponent_score,opponent_score_rect)