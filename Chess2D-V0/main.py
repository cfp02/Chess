"""Main entry point for the chess game."""
import pygame
import sys
import chess
import time
from src.core.board import ChessBoard
from src.gui.chess_gui import ChessGUI
from src.ai.minimax_ai import MinimaxAI
from src.utils.game_recorder import GameRecorder

class ChessGame:
    """Main game class that coordinates all components."""
    
    def __init__(self, window_size=512, save_json=False, vs_ai=True, play_as_white=True, 
                 ai_move_delay=1.0, ai_depth=3, ai_time_limit=2.0):
        self.board = ChessBoard()
        self.gui = ChessGUI(window_size)
        self.recorder = GameRecorder(save_json)
        
        # AI setup
        self.vs_ai = vs_ai
        self.play_as_white = play_as_white
        self.ai_move_delay = ai_move_delay  # Delay in seconds
        self.last_move_time = time.time()
        
        if vs_ai:
            self.ai = MinimaxAI(depth=ai_depth, time_limit=ai_time_limit)
            
            # If playing as black, let AI make first move
            if not play_as_white and self.board.board.turn:
                time.sleep(self.ai_move_delay)  # Add delay before first move
                ai_move = self.ai.get_move(self.board.board)
                if ai_move:
                    self.board.make_move(ai_move)
                    self.gui.last_move = ai_move
                    self.recorder.record_state(self.board)
                    self.last_move_time = time.time()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.recorder.save_game()
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = self.gui.get_square_from_pos(pos)
                
                if self.gui.selected_square is None:
                    piece = self.board.board.piece_at(square)
                    if piece and piece.color == self.board.board.turn:
                        self.gui.selected_square = square
                else:
                    move = chess.Move(self.gui.selected_square, square)
                    if move in self.board.board.legal_moves:
                        self.board.make_move(move)
                        self.gui.last_move = move
                        self.recorder.record_state(self.board)
                        self.last_move_time = time.time()  # Record time when move is actually made
                    self.gui.selected_square = None
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and self.board.board.move_stack:  # Undo
                    self.board.undo_move()
                    if self.board.board.move_stack:
                        self.gui.last_move = self.board.board.peek()
                    else:
                        self.gui.last_move = None
                    self.recorder.game_states.pop()
                    self.last_move_time = time.time()  # Reset timer after undo
                elif event.key == pygame.K_s:  # Save
                    self.recorder.save_game()
        
        return True

    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            current_time = time.time()
            
            # AI move if it's AI's turn and enough time has passed
            if (self.vs_ai and 
                ((self.board.board.turn and not self.play_as_white) or 
                 (not self.board.board.turn and self.play_as_white))):
                
                # Add delay before AI move
                if current_time - self.last_move_time >= self.ai_move_delay:
                    ai_move = self.ai.get_move(self.board.board)
                    if ai_move:
                        self.board.make_move(ai_move)
                        self.gui.last_move = ai_move
                        self.recorder.record_state(self.board)
                        self.last_move_time = current_time
            
            # Handle events and update display
            running = self.handle_events()
            self.gui.update_display(self.board.board)
            
            # Small delay to prevent excessive CPU usage
            pygame.time.delay(20)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # For 1v1 game
    game = ChessGame(
        vs_ai=True,
        ai_move_delay=0.5,  # Half second delay between moves
        ai_depth=2,         # Will try to search to depth 5
        ai_time_limit=2.0   # But will stop after 2 seconds
    )
    game.run()