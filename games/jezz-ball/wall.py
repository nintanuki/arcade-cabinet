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
	"""Wall that grows outward in both directions until it hits a boundary.

	Each direction is tracked independently so a ball collision can take out
	just one side. A "dead" side stops growing, vanishes from rendering, and
	contributes nothing to the committed wall — letting the surviving side
	finish on its own and become a permanent black wall.
	"""

	origin: pygame.Vector2
	orientation: Orientation
	negative_length: float = 0.0
	positive_length: float = 0.0
	negative_done: bool = False
	positive_done: bool = False
	negative_dead: bool = False
	positive_dead: bool = False

	@property
	def complete(self) -> bool:
		"""Return ``True`` when both directions have finished growing.

		A side is considered finished if it reached a natural stopper or was
		killed by a ball. Either way, ``complete`` triggers the commit step in
		the main game loop.
		"""
		return self.negative_done and self.positive_done

	@property
	def fully_dead(self) -> bool:
		"""Return ``True`` when both sides were destroyed (a center hit)."""
		return self.negative_dead and self.positive_dead

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

	def kill_side(self, side: str) -> None:
		"""Destroy one side of the wall so the other can complete on its own.

		The killed side is set to zero length and marked done so ``update``
		stops growing it and ``get_segments`` returns a degenerate rect that
		is filtered out by drawing and grid-marking helpers.

		Args:
			side: ``"negative"`` or ``"positive"``.
		"""
		if side == "negative":
			self.negative_dead = True
			self.negative_done = True
			self.negative_length = 0.0
		elif side == "positive":
			self.positive_dead = True
			self.positive_done = True
			self.positive_length = 0.0

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

	def detect_hit_side(self, ball: Ball) -> str | None:
		"""Return which side of the wall the ball touched.

		Returns one of ``"negative"``, ``"positive"``, ``"center"`` (when the
		ball straddles both segments at the spawn point), or ``None`` when no
		hit is registered. Already-dead sides cannot register a hit.

		Args:
			ball: Ball whose bounding rect is tested against each segment.
		"""
		segments = self.get_segments()
		if len(segments) < 2:
			return None

		negative_segment, positive_segment = segments[0], segments[1]
		negative_hit = (
			not self.negative_dead
			and negative_segment.width > 0
			and negative_segment.height > 0
			and negative_segment.colliderect(ball.rect)
		)
		positive_hit = (
			not self.positive_dead
			and positive_segment.width > 0
			and positive_segment.height > 0
			and positive_segment.colliderect(ball.rect)
		)

		if negative_hit and positive_hit:
			return "center"
		if negative_hit:
			return "negative"
		if positive_hit:
			return "positive"
		return None

	def draw(self, surface: pygame.Surface) -> None:
		"""Render the currently growing wall segments."""
		segment_colors = (ColorSettings.WALL_GROW_NEGATIVE, ColorSettings.WALL_GROW_POSITIVE)
		for rect, color in zip(self.get_segments(), segment_colors, strict=False):
			if rect.width > 0 and rect.height > 0:
				pygame.draw.rect(surface, color, rect)
