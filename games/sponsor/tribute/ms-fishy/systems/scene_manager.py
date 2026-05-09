"""Scene manager for coordinating scene transitions and state."""

from __future__ import annotations

from core.scene import Scene


class SceneManager:
    """Manages the currently-active scene and transitions between scenes."""

    def __init__(self):
        """Initialize with no active scene."""
        self._current: Scene | None = None

    @property
    def current(self) -> Scene:
        """Return the currently-active scene.
        
        Returns:
            Scene: The active scene instance.
            
        Raises:
            RuntimeError: If no scene is currently active.
        """
        if self._current is None:
            raise RuntimeError("No scene is currently active")
        return self._current

    def change_to(self, scene: Scene) -> None:
        """Transition to a new scene, calling exit/enter hooks.
        
        Args:
            scene: The new scene to activate.
        """
        if self._current is not None:
            self._current.on_exit()
        self._current = scene
        scene.on_enter()
