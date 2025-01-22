import chess
board = chess.Board()
print(board)
move = chess.Move.from_uci("e2e4")
if move in board.legal_moves:
    board.push(move)
    print(board)