"""Pygame-based GUI for chess game visualization."""
import pygame
import chess
import os

class ChessGUI:
    """GUI for chess game visualization."""
    
    # Colors
    WHITE = (255, 255, 255)
    DARK = (118, 150, 86)
    HIGHLIGHT = (186, 202, 68)
    MOVE_INDICATOR = (247, 247, 105, 128)
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, window_size=600):  # 600 is a good middle ground
        """Initialize the chess GUI."""
        pygame.init()
        self.window_size = window_size
        self.square_size = window_size // 8
        
        # Initialize window with alpha support
        self.screen = pygame.display.set_mode((window_size, window_size), pygame.SRCALPHA)
        pygame.display.set_caption('Chess')
        
        # Surface for transparent overlays
        self.overlay = pygame.Surface((window_size, window_size), pygame.SRCALPHA)
        
        # Load piece images
        self.pieces = {}
        self.load_pieces()
        
        self.selected_square = None
        self.last_move = None
        
        # Create font
        self.status_font = pygame.font.SysFont('Arial', 20)

    def load_pieces(self):
        """Load piece images from the images directory."""
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
                    original = pygame.image.load(image_path)
                    scaled = pygame.transform.smoothscale(
                        original,
                        (int(self.square_size * 0.8), int(self.square_size * 0.8))
                    )
                    self.pieces[f'{piece_letter}{color}'] = scaled

    def get_square_from_pos(self, pos):
        """Convert mouse position to chess square index."""
        x, y = pos
        file = x // self.square_size
        rank = 7 - (y // self.square_size)
        return chess.square(file, rank)

    def draw_board(self, board):
        """Draw the chess board."""
        # Clear overlay
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

        # Highlight last move with transparency
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

    def draw_pieces(self, board):
        """Draw chess pieces."""
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                color = 'l' if piece.color else 'd'
                piece_key = f'{piece.symbol().lower()}{color}'
                
                if piece_key in self.pieces:
                    file = chess.square_file(square)
                    rank = chess.square_rank(square)
                    x = file * self.square_size + self.square_size * 0.1
                    y = (7 - rank) * self.square_size + self.square_size * 0.1
                    self.screen.blit(self.pieces[piece_key], (x, y))

    def highlight_legal_moves(self, board, square):
        """Highlight legal moves for selected piece."""
        for move in board.legal_moves:
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

    def draw_game_status(self, board):
        """Draw game status."""
        status_rect = pygame.Rect(0, 0, self.window_size, 30)
        if board.is_checkmate():
            status = "Checkmate! " + ("Black" if board.turn else "White") + " wins!"
            pygame.draw.rect(self.screen, (200, 0, 0), status_rect)
        elif board.is_stalemate():
            status = "Stalemate!"
            pygame.draw.rect(self.screen, (100, 100, 100), status_rect)
        elif board.is_check():
            status = "Check!"
            pygame.draw.rect(self.screen, (255, 200, 0), status_rect)
        else:
            return

        text = self.status_font.render(status, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.window_size // 2, 15))
        self.screen.blit(text, text_rect)

    def update_display(self, board):
        """Update the display with current game state."""
        self.draw_board(board)
        if self.selected_square is not None:
            file = chess.square_file(self.selected_square)
            rank = chess.square_rank(self.selected_square)
            pygame.draw.rect(
                self.screen,
                self.HIGHLIGHT,
                (file * self.square_size, (7 - rank) * self.square_size, self.square_size, self.square_size),
                3
            )
            self.highlight_legal_moves(board, self.selected_square)
        
        self.draw_pieces(board)
        self.draw_game_status(board)
        pygame.display.flip() 