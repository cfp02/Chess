"""Base class for chess AI implementations."""
from abc import ABC, abstractmethod

class BaseChessAI(ABC):
    """Abstract base class for chess AI implementations."""
    
    @abstractmethod
    def get_move(self, board):
        """Get the best move for the current position.
        
        Args:
            board (chess.Board): The current chess board state.
            
        Returns:
            chess.Move: The best move found, or None if no moves available.
        """
        pass
    
    @abstractmethod
    def evaluate_position(self, board):
        """Evaluate the current position.
        
        Args:
            board (chess.Board): The chess board position to evaluate.
            
        Returns:
            float: A numerical evaluation of the position from the perspective
                  of the player to move. Higher values indicate a better position.
        """
        pass 