from chess_engine import sort_moves
import numpy as np
from constants import BOSS_DRAG_LEVEL, MINION_DRAG_LEVEL
import time, random
from numba import njit
from piece_points import *
from constants import *

class Dragon:
    def __init__(self, name, dragon_level, drag_time_limit=0):
        self.name = name
        self.dragon_level = dragon_level
        self.beaten = False
        self.time_limit_bonus = drag_time_limit
        self.piece_values = {
            1: 100,   # White Pawn
            2: 320,   # White Knight
            3: 330,   # White Bishop
            4: 500,   # White Rook
            5: 900,   # White Queen
            6: 99999999,  # White King
            
            9: -100,  # Black Pawn
            10: -320, # Black Knight
            11: -330, # Black Bishop
            12: -500, # Black Rook
            13: -900, # Black Queen
            14: -99999999 # Black King
        }
    
    def get_move(self, game, drag_level):
        if drag_level == BOSS_DRAG_LEVEL:
            max_depth = 4
        elif drag_level == MINION_DRAG_LEVEL:
            max_depth = 1
        else:
            max_depth = 1
        valid_moves = game.get_valid_moves()
        if not valid_moves: return None
        
        if self.dragon_level == 0:
            return valid_moves[random.randint(0, len(valid_moves)-1)]
        start_time = time.time()
        time_limit = 3.0 + self.time_limit_bonus
        best_move_so_far = valid_moves[0]
        for depth in range(1, max_depth+1):
            curr_time = time.time()
            if curr_time - start_time >= time_limit:
                break
            move = self.find_best_move(game, valid_moves, depth, start_time, time_limit)
            if move:
                best_move_so_far = move
            else:
                break
        return best_move_so_far
    

    def find_best_move(self, game, valid_moves, depth, start_time, time_limit):
        """
        Starts the Minimax algorithm with Alpha-Beta pruning to find the best move.
        Arguments:
            game (chess): A copy of the game engine to simulate moves on.
            valid_moves (list): List of currently available legal moves.
            depth (int): How many turns ahead the AI should calculate.
        Returns:
            tuple: The best move ((start_r, start_c), (end_r, end_c))
        """
        best_move = valid_moves[0]

        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        turn_multiplier = 1 if game.white_turn else -1

        ordered_moves = sort_moves(valid_moves, game.board) # have to improve later to optimize better with alpha beta pruning
        for move in ordered_moves:
            if time.time() - start_time >= time_limit:
                return None
            game.make_move(move)
            score = self.minimax(game, depth - 1, -beta, -alpha, -turn_multiplier, 
                                       start_time, time_limit)
            game.undo_move()

            if score is None: return None
            score = -score
            if score > best_score:
                best_score = score
                best_move = move
             
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_move

    def minimax(self, game, depth, alpha, beta, turn_multiplier, start_time, time_limit):
        """
        Recursive search function that builds a decision tree.
        Alpha-Beta Pruning:
        - Alpha: The best score the Maximizer (AI) can guarantee so far.
        - Beta: The best score the Minimizer (Player) can guarantee so far.
        If Beta <= Alpha, the branch is 'pruned' (skipped) because the opponent 
        would never allow that to happen.
        """
        if time.time() - start_time >= time_limit:
            return None
        
        if depth == 0:
            return turn_multiplier * evaluate_board(game.board)
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            if game.is_in_check(game.white_turn):
                    return depth - 200000
            else:
                return 0
            
        ordered_moves = sort_moves(valid_moves, game.board)
        max_eval = float('-inf')

        for move in ordered_moves:
            game.make_move(move)
            eval = self.minimax(game, depth - 1, -beta, -alpha, -turn_multiplier, 
                                       start_time, time_limit)
            
            game.undo_move()
            
            if eval is None: return None
            evaluation = -eval
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if alpha >= beta:
                break
        return max_eval

@njit
def evaluate_board(board):
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == 0: continue
            score += PIECE_VALUES[piece]
            piece_type = piece & 7
            is_black = bool(piece & 8)
            val = 0
            if is_black:
                idx = (7 - r) * 8 + c
            else:
                idx = r * 8 + c
            val = 0
            if piece_type == 1:
                val = PAWN_TABLE[idx]
            elif piece_type == 2:
                val = KNIGHT_TABLE[idx]
            elif piece_type == 3:
                val = BISHOP_TABLE[idx]
            elif piece_type == 4:
                val = ROOK_TABLE[idx]
            elif piece_type == 5:
                val = QUEEN_TABLE[idx]
            elif piece_type == 6:
                val = KING_TABLE[idx]

            if is_black:
                score -= val
            else:
                score += val
    return score

