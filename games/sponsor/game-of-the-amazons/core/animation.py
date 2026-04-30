import pygame
from settings import GridSettings
from core.board import grid_to_pixel_topleft

class PieceAnimator:
    def __init__(self):
        self.moving_piece = None  # Stores the current animation data
        self.is_animating = False

    def start(self, piece_type, start_grid, end_grid):
        """Initializes the sliding movement."""
        self.is_animating = True
        start_px = list(grid_to_pixel_topleft(*start_grid))
        end_px = grid_to_pixel_topleft(*end_grid)
        
        self.moving_piece = {
            'type': piece_type,
            'current_px': start_px,
            'target_px': end_px,
            'end_grid': end_grid
        }

    def update(self):
        """Calculates the new position for the current frame."""
        if not self.moving_piece:
            return False # Animation finished or not started

        curr = self.moving_piece['current_px']
        target = self.moving_piece['target_px']
        speed = GridSettings.ANIMATION_SPEED

        # Move X and Y incrementally toward target
        for i in range(2):
            if curr[i] < target[i]:
                curr[i] = min(curr[i] + speed, target[i])
            elif curr[i] > target[i]:
                curr[i] = max(curr[i] - speed, target[i])

        # Check if we arrived at the destination tile
        if curr[0] == target[0] and curr[1] == target[1]:
            self.is_animating = False
            return True # Signal that we just finished
            
        return False

    def get_render_data(self):
        """Returns data needed by BoardView to draw the 'ghost' piece."""
        if self.moving_piece:
            return self.moving_piece['type'], self.moving_piece['current_px']
        return None