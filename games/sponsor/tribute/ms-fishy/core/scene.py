"""Base class for all scenes in the game."""

from __future__ import annotations

import pygame


class Scene:
    """Base class for scenes. Subclasses override the methods they need.
    
    A scene is a discrete game state (title, play, game-over, etc.) that
    handles its own events, updates, and rendering. The scene manager
    ensures only one scene is active at a time.
    """

    def __init__(self, game):
        """Initialize the scene with a back-reference to GameManager.
        
        Args:
            game: The GameManager instance that owns this scene.
        """
        self.game = game

    def on_enter(self) -> None:
        """Called once when this scene becomes active."""
        pass

    def on_exit(self) -> None:
        """Called once when leaving this scene."""
        pass

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle a single pygame event. Override in subclasses.
        
        Args:
            event: The pygame event to process.
        """
        pass

    def update(self) -> None:
        """Advance the scene by one frame. Override in subclasses."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Draw the current scene state to the screen. Override in subclasses.
        
        Args:
            screen: The pygame surface to draw to.
        """
        pass
