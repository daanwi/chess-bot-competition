import chess
import random
import math
from enum import Enum

from abc import ABC, abstractmethod

class ChessBotClass(ABC):
    @abstractmethod
    def __call__(self, board_fen: str) -> chess.Move:
        pass


# keep the bot named ChessBot when submitting
class ChessBot(ChessBotClass):
    def __init__(self):
        self.board = chess.Board()
        self.pieceValues = {chess.PAWN: 1, chess.KNIGHT: 3, 
                            chess.BISHOP: 3, chess.ROOK: 5,
                            chess.QUEEN: 9, chess.KING: 10000}
                
    def __call__(self, board_fen):
        self.board = chess.Board(board_fen)
        return self.findMoveRecursive(2)[1]
        
    def findRandomMove(self):
        moves = list(self.board.legal_moves)
        idx = int(random.random() * len(moves))
        return moves[idx]
        
    def findMoveRecursive(self, depth):
        return self.recurse(depth, 1 if self.board.turn == chess.WHITE else -1)
        
    def recurse(self, depth, turnMultiplier):
        outcome = self.board.outcome(claim_draw = True)
        if outcome:
            if not outcome.winner:
                    return 0, None
            elif outcome.winner == chess.WHITE:
                    return math.inf, None
            return -math.inf, None
        if not depth:
            return self.evaluate(), None
        
        bestEval = -math.inf * turnMultiplier
        bestMove = None
        
        moves = list(self.board.legal_moves)
        random.shuffle(moves)
        for move in moves:
            self.board.push(move)
            evaluation, _ = self.recurse(depth - 1, -turnMultiplier)
            #print("Eval: ", evaluation, "BestEval: ", bestEval, "Move: ", move, "BestMove: ", bestMove, "Depth: ", depth, "Turn: ", turnMultiplier)
            if evaluation * turnMultiplier > bestEval * turnMultiplier:
                bestEval = evaluation
                bestMove = move
            self.board.pop()
                
        return bestEval, bestMove
        
    def evaluate(self):
        # Check if the game is over
        outcome = self.board.outcome(claim_draw = True)
        if outcome:
            if not outcome.winner:
                    return 0
            elif outcome.winner == chess.WHITE:
                    return math.inf
            return -math.inf
            
        # The game is not over. Evaluate the board
        blackTotal = 0
        whiteTotal = 0
        pieces = self.board.piece_map()
        for piece in pieces.values():
            if piece.color == chess.WHITE:
                whiteTotal += self.pieceValues[piece.piece_type]
                self.pieceValues[piece.piece_type]
            else:
                blackTotal += self.pieceValues[piece.piece_type]
        return whiteTotal - blackTotal
                
if __name__ == "__main__":
    #bot = ChessBot("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    bot = ChessBot()
    bot.evaluate()
