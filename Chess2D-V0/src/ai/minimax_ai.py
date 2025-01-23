"""Minimax chess AI implementation with alpha-beta pruning and optimizations."""
import chess
import chess.polyglot
import random
import time
import os
import urllib.request
from .base_ai import BaseChessAI

class MinimaxAI(BaseChessAI):
    """Chess AI using minimax algorithm with alpha-beta pruning and optimizations."""
    
    # Opening book path
    BOOK_PATH = os.path.join(os.path.dirname(__file__), "Performance.bin")
    BOOK_URL = "https://raw.githubusercontent.com/michaeldv/donna_opening_books/master/Performance.bin"
    BOOK_URL_FALLBACK = "http://download.chessbase.com/mirror/tb/Performance.bin"  # Fallback URL if needed
    
    # Piece values for evaluation
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    # Position tables for piece-square evaluation
    PAWN_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]

    def __init__(self, depth=3, time_limit=5.0, use_book=True, book_randomness=0.1):
        """Initialize the AI with depth limit and time control.
        
        Args:
            depth (int): Maximum depth to search
            time_limit (float): Maximum time in seconds to search
            use_book (bool): Whether to use opening book
            book_randomness (float): Probability (0-1) of deviating from book moves
        """
        self.max_depth = depth
        self.time_limit = time_limit
        self.use_book = use_book
        self.book_randomness = book_randomness
        self.start_time = 0
        self.nodes = 0
        self.transposition_table = {}
        self.killer_moves = [[None] * 64 for _ in range(64)]  # Killer moves for each depth
        self.history_table = {}  # History heuristic scores
        
        # Download opening book if needed
        if self.use_book and not os.path.exists(self.BOOK_PATH):
            self._download_opening_book()

    def _download_opening_book(self):
        """Download the opening book if it doesn't exist."""
        try:
            os.makedirs(os.path.dirname(self.BOOK_PATH), exist_ok=True)
            print("Downloading opening book...")
            
            try:
                # First try: with SSL verification
                urllib.request.urlretrieve(self.BOOK_URL, self.BOOK_PATH)
            except Exception as ssl_error:
                print(f"SSL download failed, trying alternative methods...")
                
                # Second try: without SSL verification (if user approves)
                import ssl
                ssl_context = ssl._create_unverified_context()
                print("Attempting download without SSL verification...")
                try:
                    with urllib.request.urlopen(self.BOOK_URL, context=ssl_context) as response:
                        with open(self.BOOK_PATH, 'wb') as out_file:
                            out_file.write(response.read())
                except Exception as e:
                    print(f"Alternative download failed: {e}")
                    print("Please manually download the opening book from:")
                    print(f"1. {self.BOOK_URL}")
                    print(f"2. {self.BOOK_URL_FALLBACK}")
                    print(f"And place it at: {self.BOOK_PATH}")
                    self.use_book = False
                    return
                    
            print("Opening book downloaded successfully!")
        except Exception as e:
            print(f"Failed to download opening book: {e}")
            self.use_book = False

    def is_time_up(self):
        """Check if we've exceeded our time limit."""
        return time.time() - self.start_time > self.time_limit

    def order_moves(self, board, depth):
        """Order moves for better alpha-beta pruning.
        
        Prioritizes:
        1. Captures (ordered by MVV-LVA)
        2. Killer moves
        3. Moves with good history scores
        """
        moves = list(board.legal_moves)
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Score captures
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score = 10000 + self.PIECE_VALUES[victim.piece_type] - self.PIECE_VALUES[attacker.piece_type]
            
            # Score killer moves
            if self.killer_moves[depth][move.from_square] == move.to_square:
                score += 9000
            
            # Score history moves
            move_key = (move.from_square, move.to_square)
            if move_key in self.history_table:
                score += self.history_table[move_key]
            
            move_scores.append((move, score))
        
        # Sort moves by score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]

    def get_book_move_probability(self, board, total_weight):
        """Calculate probability of using a book move based on position and game stage.
        
        Args:
            board: Current board position
            total_weight: Total weight of all possible book moves
        
        Returns:
            float: Probability (0-1) of using a book move
        """
        # Decay probability based on number of moves played
        move_number = board.fullmove_number
        move_decay = max(0, 1.0 - (move_number / 20))  # Linear decay until move 20
        
        # Decay probability based on total weight of known moves
        weight_factor = min(1.0, total_weight / 10000)  # Scale based on how "known" the position is
        
        # Combine factors (can be tuned)
        probability = move_decay * weight_factor
        
        return probability

    def get_move(self, board):
        """Get the best move using opening book or iterative deepening."""
        # Try opening book first
        if self.use_book and os.path.exists(self.BOOK_PATH):
            try:
                with chess.polyglot.open_reader(self.BOOK_PATH) as reader:
                    entries = list(reader.find_all(board))
                    if entries:
                        total_weight = sum(entry.weight for entry in entries)
                        
                        # Calculate probability of using book move
                        use_book_prob = self.get_book_move_probability(board, total_weight)
                        
                        # Randomly decide whether to use book
                        if random.random() < use_book_prob and random.random() > self.book_randomness:
                            # Select a random move weighted by weight
                            choice = random.randint(0, total_weight - 1)
                            current_weight = 0
                            for entry in entries:
                                current_weight += entry.weight
                                if current_weight > choice:
                                    print(f"Using book move (probability: {use_book_prob:.2f})")
                                    return entry.move
                        else:
                            print("Deviating from book deliberately")
            except Exception as e:
                print(f"Error accessing opening book: {e}")
        
        # Fall back to regular search if no book move found or chosen
        self.start_time = time.time()
        self.nodes = 0
        best_move = None
        
        # Try each depth until we run out of time
        for depth in range(1, self.max_depth + 1):
            if self.is_time_up():
                break
                
            move = self.iterative_deepening_search(board, depth)
            if move and not self.is_time_up():
                best_move = move
        
        return best_move

    def iterative_deepening_search(self, board, depth):
        """Perform iterative deepening search to the specified depth."""
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Get ordered moves
        moves = self.order_moves(board, depth)
        
        for move in moves:
            if self.is_time_up():
                break
                
            board.push(move)
            value = -self.minimax(board, depth - 1, -beta, -alpha, False)
            board.pop()
            
            if value > alpha:
                alpha = value
                best_move = move
                
            # Update history table for good moves
            if best_move:
                move_key = (best_move.from_square, best_move.to_square)
                self.history_table[move_key] = self.history_table.get(move_key, 0) + depth * depth
        
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning and optimizations."""
        # Check transposition table
        board_hash = board.fen()
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]
        
        self.nodes += 1
        
        if depth == 0 or board.is_game_over() or self.is_time_up():
            eval = self.evaluate_position(board)
            self.transposition_table[board_hash] = eval
            return eval
            
        # Null Move Pruning
        # Skip in endgame or when in check (possible zugzwang)
        if depth >= 3 and not board.is_check() and self.has_major_pieces(board):
            R = 2  # Reduction depth
            board.push(chess.Move.null())
            null_value = -self.minimax(board, depth - 1 - R, -beta, -beta + 1, not maximizing_player)
            board.pop()
            
            if null_value >= beta:  # Position is so good we can prune
                return beta

        # Principal Variation Search
        first_move = True
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.order_moves(board, depth):
                board.push(move)
                
                if first_move:
                    # Full window search for first move
                    eval = -self.minimax(board, depth - 1, -beta, -alpha, False)
                else:
                    # Zero window search to prove this is worse than our best
                    eval = -self.minimax(board, depth - 1, -alpha - 1, -alpha, False)
                    if alpha < eval < beta:  # If it might be better, do a full search
                        eval = -self.minimax(board, depth - 1, -beta, -alpha, False)
                
                board.pop()
                first_move = False
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                
                if beta <= alpha:
                    # Store killer move
                    self.killer_moves[depth][move.from_square] = move.to_square
                    break
                    
            self.transposition_table[board_hash] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.order_moves(board, depth):
                board.push(move)
                
                if first_move:
                    eval = -self.minimax(board, depth - 1, -beta, -alpha, True)
                else:
                    eval = -self.minimax(board, depth - 1, -alpha - 1, -alpha, True)
                    if alpha < eval < beta:
                        eval = -self.minimax(board, depth - 1, -beta, -alpha, True)
                
                board.pop()
                first_move = False
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                if beta <= alpha:
                    # Store killer move
                    self.killer_moves[depth][move.from_square] = move.to_square
                    break
                    
            self.transposition_table[board_hash] = min_eval
            return min_eval

    def evaluate_position(self, board):
        """Evaluate the current position with more sophisticated evaluation."""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        
        score = 0
        
        # Material and position score
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                value = self.PIECE_VALUES[piece.piece_type]
                
                # Position value for pawns
                if piece.piece_type == chess.PAWN:
                    position_value = self.PAWN_TABLE[square if piece.color else chess.square_mirror(square)]
                    value += position_value
                
                # Bonus for bishops and knights in center
                elif piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
                    file = chess.square_file(square)
                    rank = chess.square_rank(square)
                    center_distance = abs(3.5 - file) + abs(3.5 - rank)
                    value -= center_distance * 10
                
                score += value if piece.color else -value
        
        # Mobility (number of legal moves)
        mobility = len(list(board.legal_moves))
        score += mobility * 10 if board.turn else -mobility * 10
        
        # Pawn structure
        pawns = board.pieces(chess.PAWN, chess.WHITE)
        score += bin(pawns).count('1') * 5  # Connected pawns bonus
        pawns = board.pieces(chess.PAWN, chess.BLACK)
        score -= bin(pawns).count('1') * 5
        
        # King safety
        if board.is_check():
            score += -50 if board.turn else 50
        
        return score if board.turn else -score 

    def has_major_pieces(self, board):
        """Check if the side to move has pieces other than king and pawns.
        Used to detect potential zugzwang positions where null move pruning should be avoided.
        """
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if (piece and piece.color == board.turn and 
                piece.piece_type not in [chess.KING, chess.PAWN]):
                return True
        return False 