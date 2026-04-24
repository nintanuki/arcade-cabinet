"""Wall orientation and build logic for Jezz Ball."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

from ball import Ball
from settings import ColorSettings, GameplaySettings, GridSettings


class Orientation(Enum):
	"""Wall orientations supported by the placement cursor."""

	VERTICAL = auto()
	HORIZONTAL = auto()


@dataclass
class BuildingWall:
	"""Wall that grows outward in both directions until it hits a boundary."""

	origin: pygame.Vector2
	orientation: Orientation
	negative_length: float = 0.0
	positive_length: float = 0.0
	negative_done: bool = False
	positive_done: bool = False

	@property
	def complete(self) -> bool:
		"""Return ``True`` when both directions have finished growing."""
		return self.negative_done and self.positive_done

	def update(self, dt: float, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> None:
		"""Grow the wall toward both ends until each side reaches a stopper."""
		growth = GameplaySettings.WALL_BUILD_SPEED * dt

		if not self.negative_done:
			self.negative_length += growth
			if self._reached_stop(-1, bounds, solid_rects):
				self.negative_done = True

		if not self.positive_done:
			self.positive_length += growth
			if self._reached_stop(1, bounds, solid_rects):
				self.positive_done = True

	def _reached_stop(self, direction: int, bounds: pygame.Rect, solid_rects: list[pygame.Rect]) -> bool:
		"""Return whether the current wall tip has hit a boundary or solid area."""
		tip = self._tip(direction)
		probe = pygame.Rect(
			int(tip.x - GridSettings.WALL_THICKNESS // 2),
			int(tip.y - GridSettings.WALL_THICKNESS // 2),
			GridSettings.WALL_THICKNESS,
			GridSettings.WALL_THICKNESS,
		)

		if not bounds.contains(probe):
			return True

		return any(probe.colliderect(rect) for rect in solid_rects)

	def _tip(self, direction: int) -> pygame.Vector2:
		"""Return the current tip position for one end of the wall."""
		length = self.positive_length if direction > 0 else self.negative_length
		if self.orientation is Orientation.VERTICAL:
			return pygame.Vector2(self.origin.x, self.origin.y + (direction * length))
		return pygame.Vector2(self.origin.x + (direction * length), self.origin.y)

	def get_segments(self) -> list[pygame.Rect]:
		"""Return the temporary wall segments used during growth and collision checks."""
		half = GridSettings.WALL_THICKNESS // 2
		thickness = GridSettings.WALL_THICKNESS

		if self.orientation is Orientation.VERTICAL:
			up = pygame.Rect(
				int(self.origin.x - half),
				int(self.origin.y - self.negative_length),
				thickness,
				int(self.negative_length),
			)
			down = pygame.Rect(
				int(self.origin.x - half),
				int(self.origin.y),
				thickness,
				int(self.positive_length),
			)
			return [up, down]

		left = pygame.Rect(
			int(self.origin.x - self.negative_length),
			int(self.origin.y - half),
			int(self.negative_length),
			thickness,
		)
		right = pygame.Rect(
			int(self.origin.x),
			int(self.origin.y - half),
			int(self.positive_length),
			thickness,
		)
		return [left, right]

	def collides_with_ball(self, ball: Ball) -> bool:
		"""Return whether any in-progress segment intersects the given ball."""
		return any(segment.colliderect(ball.rect) for segment in self.get_segments())

	def draw(self, surface: pygame.Surface) -> None:
		"""Render the currently growing wall segments."""
		segment_colors = (ColorSettings.WALL_GROW_NEGATIVE, ColorSettings.WALL_GROW_POSITIVE)
		for rect, color in zip(self.get_segments(), segment_colors, strict=False):
			if rect.width > 0 and rect.height > 0:
				pygame.draw.rect(surface, color, rect)
