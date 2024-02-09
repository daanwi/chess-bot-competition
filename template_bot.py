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
        self.board = None
        self.pieceValues = {chess.PAWN: 1, chess.KNIGHT: 3, 
                            chess.BISHOP: 3, chess.ROOK: 5,
                            chess.QUEEN: 9}
                
    def __call__(self, board_fen):
        board = chess.Board(board_fen)
        return findMoveRecursive(3)
        
    def getPieceValues(self):
                return 
        
    def findRandomMove(self):
                moves = list(board.legal_moves)
                idx = int(random.random() * len(moves))
        return moves[idx]
        
    def findMoveRecursive(depth):
                turnMultiplier = 1
                if (board.turn == chess.BLACK)
                        turnMultiplier = -1
                return recurse(depth, turnMultiplier)
        
    def recurse(self, depth, turnMultiplier):
        if not depth:
                return evaluate(), None
        
        bestEval = math.inf * turnMultiplier
        bestMove = None
        
        for move in board.legal_moves:
                board.push(move)
                evaluation, _ = findMoveRecursive(depth - 1, -turnMultiplier)
                if evaluation * turnMultiplier > bestEval * turnMultiplier:
                        bestEval = evaluation
                        bestMove = move
                board.pop()
                
        return bestEval, bestMove
        
        def evaluate():
                # Check if the game is over
                outcome = board.outcome(True)
                if outcome:
                        if not outcome.winner:
                                return 0
                        else if outcome.winner == chess.WHITE
                                return math.inf
                        return -math.inf
                        
                # The game is not over. Evaluate the board
                pieces = board.piece_map()
                
