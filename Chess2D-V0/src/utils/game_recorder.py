"""Utility for recording and saving chess games."""
import os
import json
from datetime import datetime

class GameRecorder:
    """Records and saves chess game states and moves.
    
    Attributes:
        game_states (list): List of recorded game states.
        save_json (bool): Whether to save detailed JSON records.
    """
    
    def __init__(self, save_json=False):
        """Initialize the game recorder.
        
        Args:
            save_json (bool, optional): Whether to save detailed JSON records.
                Defaults to False.
        """
        self.game_states = []
        self.save_json = save_json
        
    def record_state(self, board):
        """Record the current game state.
        
        Args:
            board (ChessBoard): The chess board to record state from.
        """
        state = board.get_game_state()
        self.game_states.append(state)
        
    def save_game(self, directory='game_records'):
        """Save the recorded game to files.
        
        Args:
            directory (str, optional): Directory to save game records.
                Defaults to 'game_records'.
        """
        if not self.game_states:
            return

        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON record if enabled
        if self.save_json:
            json_filename = os.path.join(directory, f'game_{timestamp}.json')
            game_record = {
                'moves': len(self.game_states) - 1,  # Subtract initial state
                'states': self.game_states
            }
            with open(json_filename, 'w') as f:
                json.dump(game_record, f, indent=2)
        
        # Save simple FEN record (one per line)
        fen_filename = os.path.join(directory, f'game_{timestamp}.txt')
        with open(fen_filename, 'w') as f:
            for state in self.game_states:
                f.write(state['fen'] + '\n') 