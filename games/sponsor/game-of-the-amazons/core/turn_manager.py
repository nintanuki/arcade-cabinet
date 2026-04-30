import random

class TurnManager:
    def __init__(self, board):
        self.board = board
        self.current_player = "WHITE"  # Human starts
        
    def switch_turn(self):
        """Switches player and triggers AI if it is Black's turn."""
        self.current_player = "BLACK" if self.current_player == "WHITE" else "WHITE"
        
        if self.current_player == "BLACK":
            self.ai_move()

    def ai_move(self):
        """Randomly selects a black piece and a random valid destination."""
        black_pieces = []
        for tile in self.board.all_tiles():
            if tile.piece == "black_queen":
                black_pieces.append((tile.col, tile.row))

        random.shuffle(black_pieces)
        
        for start_pos in black_pieces:
            # Get all tiles on the board
            possible_destinations = [(t.col, t.row) for t in self.board.all_tiles()]
            random.shuffle(possible_destinations)
            
            for end_pos in possible_destinations:
                if self.board.move_piece(start_pos, end_pos):
                    # Successfully moved! Switch back to Human.
                    self.switch_turn()
                    return