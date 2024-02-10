import chess
import random
import math
from enum import Enum

from abc import ABC, abstractmethod
import cProfile

class ChessBotClass(ABC):
    @abstractmethod
    def __call__(self, board_fen: str) -> chess.Move:
        pass
        

# keep the bot named ChessBot when submitting
class ChessBot(ChessBotClass):
    def __init__(self, maxDepth=5):
        self.board = chess.Board()
        self.pieceValues = {chess.PAWN: 1, chess.KNIGHT: 3, 
                            chess.BISHOP: 3, chess.ROOK: 5,
                            chess.QUEEN: 9, chess.KING: 0}
        self.maxDepth = maxDepth
        self.checkers = []
                
    def __call__(self, board_fen = None):
        if board_fen:
            self.board = chess.Board(board_fen)
        return self.findMoveRecursive(self.maxDepth)[1]
        
    def captureValue(self, move):
        # Incorrectly valuates en passant captures as 0
        pieceType = self.board.piece_type_at(move.to_square)
        if move.from_square in self.checkers:
            return 50
        if pieceType is None:
            return 0
        return self.pieceValues[pieceType]
        
    def findRandomMove(self):
        moves = list(self.board.legal_moves)
        idx = int(random.random() * len(moves))
        return moves[idx]
        
    def findMoveRecursive(self, depth):
        return self.recurse(depth, 1 if self.board.turn == chess.WHITE else -1)
        
    def getOutcome(self, depth):
        outcome = self.board.outcome(claim_draw = False)
        if outcome is None:
            return None
        if outcome.winner is None:
            return 0
        # Depth is added to incentivise quick checkmates
        elif outcome.winner == chess.WHITE:
            return 10000 + depth
        return -10000 - depth
        
    def recurse(self, depth, turnMultiplier, alpha=-math.inf, beta=math.inf):
        # Check if the game has ended
        outcome = self.getOutcome(depth)
        if outcome is not None:
            return outcome, None
        if not depth:
            return self.evaluate(), None
        
        bestEval = -math.inf * turnMultiplier
        bestMove = None
        
        moves = list(self.board.legal_moves)
        random.shuffle(moves)
        # Killer move heuristic
        self.checkers = self.board.checkers()
        moves.sort(reverse=True, key=self.captureValue)
        # print(moves)
        
        for move in moves:
            self.board.push(move)
            evaluation, _ = self.recurse(depth - 1, -turnMultiplier, alpha, beta)
            #print("evaluation: ", evaluation, "bestEval: ", bestEval, "move: ", move, "bestMove: ", bestMove, "depth: ", depth, "turnMultiplier: ", turnMultiplier)
            if evaluation * turnMultiplier > bestEval * turnMultiplier:
                bestEval = evaluation
                bestMove = move
                
                if (turnMultiplier == 1):
                    alpha = max(alpha, bestEval)
                    if bestEval >= beta:
                        self.board.pop()
                        break
                if (turnMultiplier == -1):
                    beta = min(beta, bestEval)
                    if bestEval <= alpha:
                        self.board.pop()
                        break
                
            self.board.pop()
        if not moves:
            print("No moves found!")
            print("depth: ", depth, "turnMultiplier: ", turnMultiplier, "outcome: ", outcome)
            print(self.board)
            raise "AAAAA"
        if not bestMove:
            print("No move selected!")
            print("depth: ", depth, "turnMultiplier: ", turnMultiplier, "outcome: ", outcome, "bestMove: ", bestMove)
            print(self.board)
            raise "AAAAA"
        return bestEval, bestMove
        
    def evaluate(self):
        # Assumes the game has not ended
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
    cProfile.runctx('bot()', globals(), locals())
