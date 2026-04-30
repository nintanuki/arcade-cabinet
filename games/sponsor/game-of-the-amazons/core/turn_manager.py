import random

import pygame

class TurnManager:
    def __init__(self, board):
        """
        Manages turn order and triggers AI moves when it's Black's turn.
        
        Args:
            board: The game board instance.
        """
        self.board = board
        self.current_player = "WHITE"  # Human starts
        self.is_animating = False
        self.ai_timer = 0
        self.ai_delay = 1000 # 1 second pause before AI moves
        
    def switch_turn(self):
        """Switches player and triggers AI if it is Black's turn."""
        self.current_player = "BLACK" if self.current_player == "WHITE" else "WHITE"
        if self.current_player == "BLACK":
            self.ai_timer = pygame.time.get_ticks()

    def trigger_ai_move(self):
        """
        Randomly selects a black piece and a random valid destination.
        
        Returns:
            A tuple containing the start and end positions of the move, or None if no valid move is found.
        """
        black_pieces = [t for t in self.board.all_tiles() if t.piece == "black_queen"]
        random.shuffle(black_pieces)
        
        for start_tile in black_pieces:
            possible_dest = [t for t in self.board.all_tiles() if self.board.is_valid_path((start_tile.col, start_tile.row), (t.col, t.row))]
            if possible_dest:
                dest_tile = random.choice(possible_dest)
                # We return the move data to GameManager to start the animation
                return (start_tile.col, start_tile.row), (dest_tile.col, dest_tile.row)
        return None
                
    def update_ai(self):
        """
        Updates the AI timer and triggers AI move if delay has passed.
        Should be called every frame from the main loop.
        """
        if self.current_player == "BLACK" and not self.is_animating:
            current_time = pygame.time.get_ticks()
            if current_time - self.ai_timer >= self.ai_delay:
                return self.trigger_ai_move() 
        return None