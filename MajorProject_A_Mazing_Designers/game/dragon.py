from chess_engine import Chess
import numpy as np, pygame as pg

class Dragon:
    def __init__(self, name, difficulty=1):
        self.name = name
        self.difficulty = difficulty
        self.beaten = False
        self.piece_values = {
            1: 10,   # White Pawn
            2: 30,   # White Knight
            3: 30,   # White Bishop
            4: 50,   # White Rook
            5: 90,   # White Queen
            6: 900,  # White King
            
            9: -10,  # Black Pawn
            10: -30, # Black Knight
            11: -30, # Black Bishop
            12: -50, # Black Rook
            13: -90, # Black Queen
            14: -900 # Black King
        }
    
    def get_move(self, game):
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        if self.difficulty == 0:
            return valid_moves[np.random.randint(len(valid_moves))]
        else:
            return self.find_best_move(game, valid_moves, depth=4)
    
    def find_best_move(self, game, valid_moves, depth):
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

        best_score = float('inf')
        alpha = float('-inf')
        beta = float('inf')

        np.random.shuffle(valid_moves) # have to improve later to optimize better with alpha beta pruning
        for move in valid_moves:
            game.make_move(move)
            score = self.minimax(game, depth-1, alpha, beta, True)
            game.undo_move()

            if score < best_score:
                best_score = score
                best_move = move
            
            beta = min(beta, best_score)

        return best_move

    def minimax(self, game, depth, alpha, beta, mazimizing_player):
        """
        Recursive search function that builds a decision tree.
        Alpha-Beta Pruning:
        - Alpha: The best score the Maximizer (AI) can guarantee so far.
        - Beta: The best score the Minimizer (Player) can guarantee so far.
        If Beta <= Alpha, the branch is 'pruned' (skipped) because the opponent 
        would never allow that to happen.
        """
        if depth == 0:
            return self.evaluate_board(game.board)
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return self.evaluate_board(game.board)
        
        if mazimizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                game.make_move(move)
                evaluation = self.minimax(game, depth - 1, alpha, beta, False)
                game.undo_move()

                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game.make_move(move)
                evaluation = self.minimax(game, depth - 1, alpha, beta, True)
                game.undo_move()
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval
            
    def evaluate_board(self, board):
        score = 0
        fl_board = board.flatten()
        for piece in fl_board:
            if piece != 0:
                score += self.piece_values.get(piece, 0)
        return score
    
