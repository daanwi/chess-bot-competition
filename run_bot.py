from template_bot import ChessBotClass, ChessBot
from itertools import count
import time
import numpy as np
import pandas as pd
import chess
import random
from IPython.display import clear_output, display


class RandomBot(ChessBotClass):
    def __call__(self, board_fen):
        board = chess.Board(board_fen)

        moves = list(board.legal_moves)

        idx = int(random.random() * len(moves))

        move = moves[idx]

        return move
        
class HumanPlayer(ChessBotClass):
    def __call__(self, board_fen):
        board = chess.Board(board_fen)

        moves = list(board.legal_moves)
        if not moves:
            return None
        move = None
        
        while(True):
            moveString = input("Enter a move to play.")
            try:
                move = chess.Move.from_uci(moveString)
            except chess.InvalidMoveError:
                print("Invalid move.")
                continue
            if move in moves:
                break
            else:
                print("Illegal move.")

        return move


INF = 1e10

class MiniMaxBot(ChessBotClass):
    def __init__(self, max_depth: int) -> None:
        self._max_depth = max_depth

    def evaluate_board(self, board, turn):
        return 0

    def minimax(self, depth: int,
                board: chess.Board,
                alpha: float, beta: float,
                maximizing: bool) -> float:

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board, board.turn) * -1**(not maximizing)
        if maximizing:
            value = -INF
            for move in board.legal_moves:
                board.push(move) #also switches turn
                value = max(value, self.minimax(depth - 1,
                                                board, alpha,
                                                beta, not maximizing))
                board.pop()
                if value > beta:
                    break
                alpha = max(alpha, value)
        else:
            value = INF
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self.minimax(depth - 1,
                                           board, alpha,
                                           beta, not maximizing))
                board.pop()
                if value < alpha:
                    break
                beta = min(beta, value)
        return value

    def __call__(self, board_fen: str) -> chess.Move:
        board = chess.Board(board_fen)

        best_move = None
        best_eval = -INF
        for move in board.legal_moves:
            board.push(move)
            value = self.minimax(self._max_depth, board, -INF, INF, True)
            if value > best_eval:
                best_eval = value
                best_move = move
            board.pop()
        return best_move


DEFAULT_PIECE_VALUES = {chess.PAWN : 1, chess.ROOK : 5, chess.KNIGHT : 3, chess.BISHOP : 3, chess.KING : 100, chess.QUEEN : 9}

class PieceValueBot(MiniMaxBot):
    def __init__(self,
            max_depth: int,
            piece_values: dict = DEFAULT_PIECE_VALUES
        ) -> None:
        super().__init__(max_depth)
        self.piece_values = piece_values

    def evaluate_board(self, board: chess.Board, color: chess.Color) -> float:
        return sum([self.piece_values[piece.piece_type] for piece in board.piece_map().values() if piece.color == color])


class Judge():
    def __init__(self, player_1, player_2, time_limit=300000):
        self.player_1 = player_1
        self.player_2 = player_2
        self.time_limit = time_limit

    def run_game(self, initial_board_fen:str = None):
        board = chess.Board()

        player_times = [0, 0]

        for i in count(0, 1):
            if board.is_checkmate():
                print("GAME OVER")
                print("Winner is bot", (i + 1)%2 + 1, sep="_")
                clear_output(wait=True)
                print(f"---------Player {i % 2 + 1}----------")
                display(board)

                break
            if i > 200:
                print("GAME OVER")
                print("Exceeded move limits, it's a tie")
                clear_output(wait=True)
                print(f"---------Player {i % 2 + 1}----------")
                display(board)

                break

            board_fen = board.fen()

            start = time.time()
            if i % 2 == 0:
                move = self.player_1(board_fen)
            else:
                move = self.player_2(board_fen)
            end = time.time()

            player_times[i%2] += end - start

            if player_times[i%2] > self.time_limit:
                print("GAME OVER")
                print("Time limit exceeded, winner is bot", i%2+1, sep="_")

            if not board.is_legal(move):
                raise ValueError("Illegal board move. The bot it hallucinating...", move)

            board.push(move)

            clear_output(wait=True)
            print(f"---------Player {i % 2 + 1}----------")
            display(board)

            # slow down the bots so that we can see them
            # time.sleep(.25)
        print("Times used:", player_times)

if __name__ == "__main__":
    # initialize the bots
    bot_1 = ChessBot(maxDepth=1)
    bot_2 = ChessBot(maxDepth=1)

    # run tournament
    judge = Judge(bot_1, bot_2)
    judge.run_game()
