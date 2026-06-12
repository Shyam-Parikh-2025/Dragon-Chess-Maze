from Chess_Engine.chess_engine import sort_moves
from Chess_Engine.chess_engine import Chess
import constants
import time, random
from Chess_Engine.piece_points import *

class Dragon:
    def __init__(self, name, dragon_level, drag_time_limit=0):
        self.name = name
        self.dragon_level = dragon_level
        self.time_limit_bonus = drag_time_limit
        self.nodes_visited = 0
    
    def get_move(self, game: Chess, drag_level, chess_difficulty=1):
        # Endgame Overdrive Check
        is_endgame = game.phase < 6
        
        extra_depth = 0
        if chess_difficulty > 0.85: extra_depth +=1
        if chess_difficulty > 0.95: extra_depth +=1
        if chess_difficulty > 0.99: extra_depth +=1
        if chess_difficulty < 0.3: extra_depth -= 1
        if chess_difficulty < 0.1: extra_depth -=1


        if drag_level == constants.BOSS_DRAG_LEVEL:
            max_depth = max(constants.MAX_BOSS_DEPTH + (3 if is_endgame else 0) + int(extra_depth), 1)
        elif drag_level == constants.MINION_DRAG_LEVEL:
            max_depth = max(constants.MAX_MINION_DEPTH + (2 if is_endgame else 0) + int(extra_depth), 1)
            if chess_difficulty <= 0.1:
                max_depth = 2
        else:
            max_depth = 1
            
        if game.ai_fatigue:
            fatigue_reduction = (game.move_count // 10) * 2
            max_depth = max( 1+ (int(extra_depth) if extra_depth <= 2 else 2), max_depth - fatigue_reduction)           
        valid_moves = game.get_valid_moves()
        if not valid_moves: return None
        
        if chess_difficulty <= 0.35:
            blunder_chance = (0.35 - chess_difficulty) * 2
            if random.random() < blunder_chance:
                return random.choice(valid_moves)
            
        if self.dragon_level == 0 or chess_difficulty<0.05:
            return random.choice(valid_moves)
        
        start_time = time.time()
        extra_time = 0
        if chess_difficulty > 0.85: extra_time +=1
        if chess_difficulty > 0.95: extra_time +=1
        if chess_difficulty > 0.99: extra_time +=1
        if chess_difficulty < 0.3: extra_time -= 1
        if chess_difficulty < 0.1: extra_time -=1

        

        time_limit = max(3.0 + self.time_limit_bonus + (3.0 if is_endgame else 0.0) + extra_time, 1)
        self.nodes_visited = 0

        best_move_so_far = valid_moves[0]
        for depth in range(1, max_depth+1):
            curr_time = time.time()
            if curr_time - start_time >= time_limit:
                break
            move = self.find_best_move_v2(game, valid_moves, depth, start_time, time_limit)
            if move is not None:
                best_move_so_far = move
            else:
                break
        print("Nodes searched:", self.nodes_visited)
        return best_move_so_far

    def find_best_move_v2(self, game: Chess, valid_moves, depth, start_time, time_limit):
        """this function analyzes the score to help select the best possible move using a minimax algorithm"""
        # Prevent Infinite Shuffle by tracking tied moves
        best_moves_list = []
        infinity   =  float('inf')
        best_score = -infinity
        alpha      = -infinity
        beta       =  infinity
        turn_multiplier = 1 if game.white_turn else -1

        ordered_moves = sort_moves(valid_moves, game.board)

        for move in ordered_moves:
            if (time.time() - start_time) >= time_limit:
                return None
            
            game.make_move(move)
            score = self.minimax_v2(game, depth-1, -beta, -alpha, -turn_multiplier, start_time, time_limit)
            game.undo_move()

            if score is None: return None
            score = -score

            if score > best_score:
                best_score = score
                best_moves_list = [move]
            elif score == best_score:
                best_moves_list.append(move)
            
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        if game.dragons_blunder and len(ordered_moves) >= 3:
            if random.random() < 0.5:
                return ordered_moves[2]
            
        return random.choice(best_moves_list) if best_moves_list else ordered_moves[0]

    def minimax_v2(self, game: Chess, depth, alpha, beta, turn_multiplier, start_time, time_limit):
        self.nodes_visited += 1

        if self.nodes_visited % 3600 == 0:
            if time.time() - start_time >= time_limit: return None

        if depth == 0:
            return turn_multiplier * game.eval_board()
        
        valid_moves = game.get_valid_moves()

        if len(valid_moves) == 0:
            if game.is_in_check(game.white_turn):
                # Weighting Checkmate for Faster Mates
                return -200000 + (100 * depth)
            else:
                return 0
        
        ordered_moves = sort_moves(valid_moves, game.board)
        max_eval = float('-inf')

        for move in ordered_moves:
            game.make_move(move)
            board_eval = self.minimax_v2(game, depth - 1, -beta, -alpha, -turn_multiplier, start_time, time_limit)
            game.undo_move()

            if board_eval is None: return None

            evaluation = -board_eval
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)

            if alpha >= beta: break
        
        return max_eval