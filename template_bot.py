import chess
import random
import math
from enum import Enum

from abc import ABC, abstractmethod
import cProfile
import sys

class ChessBotClass(ABC):
    @abstractmethod
    def __call__(self, board_fen: str) -> chess.Move:
        pass
        

# keep the bot named ChessBot when submitting
class ChessBot(ChessBotClass):
    def __init__(self, maxDepth=5):
        #self.board = chess.Board("r4rk1/2p2pp1/2p4p/p3q2b/1p2P3/P6P/1PP1NPP1/R2Q1RK1 w - - 1 17")
        self.board = chess.Board()
        self.pieceValues = {chess.PAWN: 1, chess.KNIGHT: 3, 
                            chess.BISHOP: 3, chess.ROOK: 5,
                            chess.QUEEN: 9, chess.KING: 0}
        self.maxDepth = maxDepth
        self.checkers = []
        self.pastPositions = []
        self.initializeZobristHashNumbers()
        self.zobristHash = self.getZobristHash()
        self.skips = 0
        print(self.zobristHash)
    
    def __call__(self, board_fen = None):
        if board_fen:
            self.board = chess.Board(board_fen)
            self.zobristHash = self.getZobristHash()
        evaluation, ret = self.findMoveRecursive(self.maxDepth)
        print("Skips: ", self.skips)
        print("Evaluation: ", evaluation)
        return ret
    
    
    def initializeZobristHashNumbers(self):
        # Implemented according to https://www.chessprogramming.org/Zobrist_Hashing
        # And https://en.wikipedia.org/wiki/Zobrist_hashing
        self.piecePositionHashes = []
        for color in [chess.BLACK, chess.WHITE]:
            self.piecePositionHashes.append([])
            self.piecePositionHashes[color].append([])
            for pieceType in self.pieceValues:
                self.piecePositionHashes[color].append([])
                for itr in range(64):
                    self.piecePositionHashes[color][pieceType].append(random.randint(-sys.maxsize, sys.maxsize))
        self.blackToMoveHash = random.randint(-sys.maxsize, sys.maxsize)
        
        
        self.queenCastleHashes = [random.randint(-sys.maxsize, sys.maxsize), random.randint(-sys.maxsize, sys.maxsize)]
        self.kingCastleHashes = [random.randint(-sys.maxsize, sys.maxsize), random.randint(-sys.maxsize, sys.maxsize)]
        self.enPassantHashes = []
        for itr in range(8):
            self.enPassantHashes.append(random.randint(-sys.maxsize, sys.maxsize))
        
    def captureValue(self, move):
        # Incorrectly valuates en passant captures as 0
        pieceType = self.board.piece_type_at(move.to_square)
        if move.from_square in self.checkers:
            return 50
        if pieceType is None:
            return 0
        return self.pieceValues[pieceType]
        
    def findMoveRecursive(self, depth):
        #self.pastPositions = []
        self.skips = 0
        while(len(self.pastPositions) < depth + 1):
            self.pastPositions.append({})
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
        
    def verifyHash(self):
        checkHash = self.getZobristHash()
        if (checkHash != self.zobristHash):
            print("Wrong hash!")
            print(checkHash)
            print(self.zobristHash)
            print(move)
            print(self.board)
            self.zobristHash = checkHash
        
    def recurse(self, depth, turnMultiplier, alpha=-math.inf, beta=math.inf, ignoreStuff=True):
        # Check if the game has ended
        outcome = self.getOutcome(depth)
        if outcome is not None:
            return outcome, None
        
        moves = list(self.board.legal_moves)
        if depth < 1:
            moves = list(filter(self.board.is_capture, moves))
            if not moves:
                ret = self.evaluate()
                return ret, None
        
        bestEval = -math.inf * turnMultiplier
        bestMove = None
        
        
        #random.shuffle(moves)
        # Killer move heuristic?
        self.checkers = self.board.checkers()
        moves.sort(reverse=True, key=self.captureValue)
        
        for move in moves:
            # Make move
            if not ignoreStuff:
                #self.zobristHash = self.getZobristHash()
                # For exceptional cases: just generate a new one for now
                oldHash = self.zobristHash
                self.moveWithHash(move)
            else:
                self.board.push(move)
                
            if not ignoreStuff and self.zobristHash in self.pastPositions[depth]:
                evaluation = self.pastPositions[depth][self.zobristHash]
                self.skips += 1
            else:
                evaluation, _ = self.recurse(depth - 1, -turnMultiplier, alpha, beta)
                if not ignoreStuff:
                    self.pastPositions[depth][self.zobristHash] = evaluation
            self.board.pop()
            if not ignoreStuff:
                self.zobristHash = oldHash
            
            if evaluation * turnMultiplier > bestEval * turnMultiplier:
                bestEval = evaluation
                bestMove = move
                
                if (turnMultiplier == 1):
                    alpha = max(alpha, bestEval)
                    if bestEval >= beta:
                        #break
                        return 1000000, None
                    
                if (turnMultiplier == -1):
                    beta = min(beta, bestEval)
                    if bestEval <= alpha:
                        #break
                        return -1000000, None
            
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
        evaluation = whiteTotal - blackTotal
        opponentMoves = len([self.board.legal_moves])
        self.board.push(chess.Move.null())
        ownMoves = len([self.board.legal_moves])
        if self.board.turn == chess.WHITE:
            evaluation -= opponentMoves / 500
            evaluation += ownMoves / 300
        else:
            evaluation -= ownMoves / 300
            evaluation += opponentMoves / 500
        self.board.pop()
        return evaluation
        
    def moveWithHash(self, move):
        # Exceptional cases
        if self.board.is_castling(move):
            self.board.push(move)
            self.zobristHash = self.getZobristHash()
            return
        if self.board.is_en_passant(move):
            self.board.push(move)
            self.zobristHash = self.getZobristHash()
            return
            
        # Remove piece from starting square
        square = move.from_square
        piece = self.board.piece_at(square)
        self.zobristHash ^= self.piecePositionHashes[piece.color][piece.piece_type][square]
        # Remove piece from ending square
        square = move.to_square
        capturedPiece = self.board.piece_at(square)
        if capturedPiece:
            self.zobristHash ^= self.piecePositionHashes[capturedPiece.color][capturedPiece.piece_type][square]
        # Add piece to ending square
        self.zobristHash ^= self.piecePositionHashes[piece.color][piece.piece_type][square]
        # Change side to move
        self.zobristHash ^= self.blackToMoveHash
        # Remove old en passant flag
        if self.board.ep_square:
            self.zobristHash ^= self.enPassantHashes[chess.square_rank(self.board.ep_square)]
        # Save old castling flags
        self.oldQueenCastleWhite = self.board.has_queenside_castling_rights(chess.WHITE)
        self.oldQueenCastleBlack = self.board.has_queenside_castling_rights(chess.BLACK)
        self.oldKingCastleWhite = self.board.has_kingside_castling_rights(chess.WHITE)
        self.oldKingCastleBlack = self.board.has_kingside_castling_rights(chess.BLACK)
        # Make the move
        self.board.push(move)
        # Add new en passant flag
        if self.board.ep_square:
            self.zobristHash ^= self.enPassantHashes[chess.square_rank(self.board.ep_square)]
        # Remove old castling flags
        if not self.oldKingCastleBlack == self.board.has_kingside_castling_rights(chess.BLACK):
            self.zobristHash ^= self.kingCastleHashes[chess.BLACK]
        
        if not self.oldKingCastleWhite == self.board.has_kingside_castling_rights(chess.WHITE):
            self.zobristHash ^= self.kingCastleHashes[chess.WHITE]
            
        if not self.oldQueenCastleBlack == self.board.has_queenside_castling_rights(chess.BLACK):
            self.zobristHash ^= self.queenCastleHashes[chess.BLACK]
            
        if not self.oldQueenCastleWhite == self.board.has_queenside_castling_rights(chess.WHITE):
            self.zobristHash ^= self.queenCastleHashes[chess.WHITE]

        
    def getZobristHash(self):
        pieces = self.board.piece_map()
        boardHash = 0
        
        for square, piece in pieces.items():
            boardHash ^= self.piecePositionHashes[piece.color][piece.piece_type][square]
        
        if self.board.turn == chess.BLACK:
            boardHash ^= self.blackToMoveHash
        
        if self.board.has_kingside_castling_rights(chess.BLACK):
            boardHash ^= self.kingCastleHashes[chess.BLACK]
        
        if self.board.has_kingside_castling_rights(chess.WHITE):
            boardHash ^= self.kingCastleHashes[chess.WHITE]
            
        if self.board.has_queenside_castling_rights(chess.BLACK):
            boardHash ^= self.queenCastleHashes[chess.BLACK]
            
        if self.board.has_queenside_castling_rights(chess.WHITE):
            boardHash ^= self.queenCastleHashes[chess.WHITE]
        
        if (not self.board.ep_square):
            return boardHash
        
        boardHash ^= self.enPassantHashes[chess.square_rank(self.board.ep_square)]
        
        return boardHash
                
if __name__ == "__main__":
    bot = ChessBot(maxDepth=5)
    #bot.verifyEvaluation(depth=4)
    #bot()
    '''for _ in range(100):
        bot.pastPositions = []
        while(len(bot.pastPositions) < 2):
            bot.pastPositions.append({})
        print(bot.recurse(1, -1, 3, math.inf))'''
    cProfile.runctx('bot()', globals(), locals())
