import chess
import pygame
import sys
import json
from datetime import datetime
import os

class ChessGame:
    # Colors
    WHITE = (255, 255, 255)
    DARK = (118, 150, 86)  # More pleasant green color for dark squares
    HIGHLIGHT = (186, 202, 68)
    MOVE_INDICATOR = (247, 247, 105, 128)  # Light yellow with transparency
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, window_size=512, save_json=False):
        pygame.init()
        self.window_size = window_size
        self.square_size = window_size // 8
        self.save_json = save_json  # Control JSON saving
        
        # Initialize window
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption('Chess')
        
        # Create surface for transparent overlays
        self.overlay = pygame.Surface((window_size, window_size), pygame.SRCALPHA)
        
        # Initialize game state
        self.board = chess.Board()
        self.selected_square = None
        self.last_move = None
        
        # Load piece images
        self.pieces = {}
        self.load_pieces()
        
        # Game recording
        self.game_states = []
        self.record_state()  # Record initial state

    def load_pieces(self):
        """Load piece images from the images directory"""
        piece_names = {
            'k': 'king',
            'q': 'queen',
            'r': 'rook',
            'b': 'bishop',
            'n': 'knight',
            'p': 'pawn'
        }
        
        for color in ['l', 'd']:  # light and dark pieces
            for piece_letter in piece_names:
                image_path = os.path.join('images', f'Chess_{piece_letter}{color}t45.svg.png')
                if os.path.exists(image_path):
                    # Load and scale the image
                    original = pygame.image.load(image_path)
                    scaled = pygame.transform.smoothscale(
                        original,
                        (int(self.square_size * 0.8), int(self.square_size * 0.8))
                    )
                    self.pieces[f'{piece_letter}{color}'] = scaled

    def record_state(self):
        """Record current game state"""
        state = {
            'fen': self.board.fen(),
            'turn': 'white' if self.board.turn else 'black',
            'is_check': self.board.is_check(),
            'is_checkmate': self.board.is_checkmate(),
            'is_stalemate': self.board.is_stalemate(),
            'is_insufficient_material': self.board.is_insufficient_material(),
            'legal_moves': [move.uci() for move in self.board.legal_moves]
        }
        self.game_states.append(state)

    def save_game(self):
        """Save the game record to a file"""
        if not self.game_states:
            return

        # Create game_records directory if it doesn't exist
        os.makedirs('game_records', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON record if enabled
        if self.save_json:
            json_filename = f'game_records/game_{timestamp}.json'
            game_record = {
                'moves': len(self.game_states) - 1,  # Subtract initial state
                'outcome': self.get_game_outcome(),
                'states': self.game_states
            }
            with open(json_filename, 'w') as f:
                json.dump(game_record, f, indent=2)
        
        # Save simple FEN record (one per line)
        fen_filename = f'game_records/game_{timestamp}.txt'
        with open(fen_filename, 'w') as f:
            for state in self.game_states:
                f.write(state['fen'] + '\n')

    def get_game_outcome(self):
        """Get the game outcome as a string"""
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
            return "game abandoned"

    def get_square_from_pos(self, pos):
        """Convert mouse position to chess square index"""
        x, y = pos
        file = x // self.square_size
        rank = 7 - (y // self.square_size)
        return chess.square(file, rank)

    def draw_board(self):
        """Draw the chess board with last move highlight"""
        # Clear the overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Draw base board
        for i in range(8):
            for j in range(8):
                color = self.WHITE if (i + j) % 2 == 0 else self.DARK
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (i * self.square_size, j * self.square_size, self.square_size, self.square_size)
                )

        # Highlight last move on overlay
        if self.last_move:
            for square in [self.last_move.from_square, self.last_move.to_square]:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                pygame.draw.rect(
                    self.overlay,
                    self.MOVE_INDICATOR,
                    (file * self.square_size, (7 - rank) * self.square_size, self.square_size, self.square_size)
                )
        
        # Blit overlay onto screen
        self.screen.blit(self.overlay, (0, 0))

    def draw_pieces(self):
        """Draw chess pieces using loaded images"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Get piece color and type
                color = 'l' if piece.color else 'd'
                piece_key = f'{piece.symbol().lower()}{color}'
                
                if piece_key in self.pieces:
                    # Calculate position
                    file = chess.square_file(square)
                    rank = chess.square_rank(square)
                    x = file * self.square_size + self.square_size * 0.1  # 10% padding
                    y = (7 - rank) * self.square_size + self.square_size * 0.1
                    
                    # Draw the piece
                    self.screen.blit(self.pieces[piece_key], (x, y))

    def draw_game_status(self):
        """Draw game status (checkmate, stalemate, check)"""
        status_rect = pygame.Rect(0, 0, self.window_size, 30)
        if self.board.is_checkmate():
            status = "Checkmate! " + ("Black" if self.board.turn else "White") + " wins!"
            pygame.draw.rect(self.screen, (200, 0, 0), status_rect)
        elif self.board.is_stalemate():
            status = "Stalemate!"
            pygame.draw.rect(self.screen, (100, 100, 100), status_rect)
        elif self.board.is_check():
            status = "Check!"
            pygame.draw.rect(self.screen, (255, 200, 0), status_rect)
        else:
            return

        text = pygame.font.SysFont('Arial', 20).render(status, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.window_size // 2, 15))
        self.screen.blit(text, text_rect)

    def highlight_legal_moves(self, square):
        """Highlight legal moves for selected piece"""
        for move in self.board.legal_moves:
            if move.from_square == square:
                file = chess.square_file(move.to_square)
                rank = chess.square_rank(move.to_square)
                pygame.draw.circle(
                    self.screen,
                    self.HIGHLIGHT,
                    (file * self.square_size + self.square_size // 2,
                     (7 - rank) * self.square_size + self.square_size // 2),
                    self.square_size // 6
                )

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()  # Save game before quitting
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    square = self.get_square_from_pos(pos)
                    
                    if self.selected_square is None:
                        piece = self.board.piece_at(square)
                        if piece and piece.color == self.board.turn:
                            self.selected_square = square
                    else:
                        move = chess.Move(self.selected_square, square)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            self.last_move = move
                            self.record_state()  # Record state after each move
                        self.selected_square = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u and self.board.move_stack:  # Undo with 'u' key
                        self.board.pop()
                        if self.board.move_stack:
                            self.last_move = self.board.peek()
                        else:
                            self.last_move = None
                        self.game_states.pop()  # Remove the last recorded state
                    elif event.key == pygame.K_s:  # Save with 's' key
                        self.save_game()

            # Draw current state
            self.draw_board()
            if self.selected_square is not None:
                file = chess.square_file(self.selected_square)
                rank = chess.square_rank(self.selected_square)
                pygame.draw.rect(
                    self.screen,
                    self.HIGHLIGHT,
                    (file * self.square_size, (7 - rank) * self.square_size, self.square_size, self.square_size),
                    3
                )
                self.highlight_legal_moves(self.selected_square)
            
            self.draw_pieces()
            self.draw_game_status()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()