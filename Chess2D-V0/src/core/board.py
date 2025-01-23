"""Core chess board functionality that can be extended for different variants."""
import chess

class ChessBoard:
    """Base class for chess boards that can be extended for variants.
    
    Attributes:
        board (chess.Board): The underlying chess board instance.
        move_stack (list): List of moves made in the game.
    """
    
    def __init__(self):
        """Initialize a new chess board."""
        self.board = chess.Board()
        self.move_stack = []
        
    def make_move(self, move):
        """Make a move on the board.
        
        Args:
            move (chess.Move): The move to make.
            
        Returns:
            bool: True if the move was legal and made, False otherwise.
        """
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False
    
    def undo_move(self):
        """Undo the last move.
        
        Returns:
            chess.Move or None: The move that was undone, or None if no moves to undo.
        """
        if self.board.move_stack:
            return self.board.pop()
        return None
    
    def get_legal_moves(self):
        """Get all legal moves for current position.
        
        Returns:
            list: List of legal chess.Move objects.
        """
        return list(self.board.legal_moves)
    
    def is_game_over(self):
        """Check if the game is over.
        
        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.board.is_game_over()
    
    def get_game_state(self):
        """Get current game state.
        
        Returns:
            dict: Dictionary containing current game state information.
        """
        return {
            'fen': self.board.fen(),
            'turn': 'white' if self.board.turn else 'black',
            'is_check': self.board.is_check(),
            'is_checkmate': self.board.is_checkmate(),
            'is_stalemate': self.board.is_stalemate(),
            'is_insufficient_material': self.board.is_insufficient_material(),
            'legal_moves': [move.uci() for move in self.board.legal_moves]
        }
    
    def get_outcome(self):
        """Get game outcome.
        
        Returns:
            str: Description of the game outcome.
        """
        if self.board.is_checkmate():
            return "checkmate - " + ("black wins" if self.board.turn else "white wins")
        elif self.board.is_stalemate():
            return "draw - stalemate"
        elif self.board.is_insufficient_material():
            return "draw - insufficient material"
        elif self.board.is_fifty_moves():
            return "draw - fifty-move rule"
        elif self.board.is_repetition():
            return "draw - repetition"
        else:
            return "game in progress" 