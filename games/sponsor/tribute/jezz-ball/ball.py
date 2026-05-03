"""Ball physics and rendering for Jezz Ball."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from settings import ColorSettings, GameplaySettings


@dataclass
class Ball:
	"""Moving ball that bounces off the playfield edges and solid regions."""

	position: pygame.Vector2
	velocity: pygame.Vector2
	radius: int = GameplaySettings.BALL_RADIUS
	spin_phase: float = 0.0

	@property
	def rect(self) -> pygame.Rect:
		"""Return the current collision rectangle for the ball."""
		return pygame.Rect(
			int(self.position.x - self.radius),
			int(self.position.y - self.radius),
			self.radius * 2,
			self.radius * 2,
		)

	def update(self, dt: float, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> None:
		"""Advance the ball and bounce it off bounds or solid geometry."""
		self.position.x += self.velocity.x * dt
		self._resolve_axis_collision(bounds, solid_rects, axis="x")
		self.position.y += self.velocity.y * dt
		self._resolve_axis_collision(bounds, solid_rects, axis="y")
		speed_ratio = self.velocity.length() / max(1.0, GameplaySettings.BASE_BALL_SPEED)
		self.spin_phase = (self.spin_phase + (GameplaySettings.BALL_SPIN_RATE * speed_ratio * dt)) % (2 * math.pi)

	def _resolve_axis_collision(
		self,
		bounds: pygame.Rect,
		solid_rects: list[pygame.Rect],
		axis: str,
	) -> None:
		"""Resolve collisions for a single movement axis."""
		if axis == "x":
			if self.position.x - self.radius < bounds.left:
				self.position.x = bounds.left + self.radius
				self.velocity.x *= -1
			elif self.position.x + self.radius > bounds.right:
				self.position.x = bounds.right - self.radius
				self.velocity.x *= -1
		else:
			if self.position.y - self.radius < bounds.top:
				self.position.y = bounds.top + self.radius
				self.velocity.y *= -1
			elif self.position.y + self.radius > bounds.bottom:
				self.position.y = bounds.bottom - self.radius
				self.velocity.y *= -1

		ball_rect = self.rect
		for solid in solid_rects:
			if not ball_rect.colliderect(solid):
				continue

			if axis == "x":
				if self.velocity.x > 0:
					self.position.x = solid.left - self.radius
				else:
					self.position.x = solid.right + self.radius
				self.velocity.x *= -1
			else:
				if self.velocity.y > 0:
					self.position.y = solid.top - self.radius
				else:
					self.position.y = solid.bottom + self.radius
				self.velocity.y *= -1

			break

	def draw(self, surface: pygame.Surface) -> None:
		"""Render the ball onto the provided surface."""
		center = (int(self.position.x), int(self.position.y))
		pygame.draw.circle(surface, ColorSettings.BALL, center, self.radius)

		wedge_points = [center]
		segments = 18
		for step in range(segments + 1):
			angle = self.spin_phase + (math.pi * (step / segments))
			wedge_points.append(
				(
					int(self.position.x + math.cos(angle) * self.radius),
					int(self.position.y + math.sin(angle) * self.radius),
				)
			)
		pygame.draw.polygon(surface, ColorSettings.BALL_WHITE, wedge_points)
		pygame.draw.circle(surface, ColorSettings.BALL_OUTLINE, center, self.radius, 1)
