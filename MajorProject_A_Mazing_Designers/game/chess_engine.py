# Documentation:
# The pieces are stored as integers in the following binary method.
# The 4th bit determines color: so, 0 for white, 1 for black
# First 3 bits show type to (val 1-7) the piece types are title below.
# (piece & 7) is used to find type and (piece & 8) to find color (Bitwise operations)
# Example: 1110 (14 - shows black king = black(8) + king(6)=14)
#          0110 (6 - shows white king = white(0) + king(6)=6)
# Some of the complicated functions have docstring explaining their use.
# A pseudo valid move is a move that a piece can do, but it is not checked that it would
# cause check on the same color, so a black pawn moving can allow a check to the black king if
# we just looked at pseudo valid moves, but valid moves are checked moves
#  
import pygame as pg
import numpy as np
import os
from numba import njit
from constants import ROWS, COLS, SQSIZE, WIDTH, HEIGHT, color

# ============ PIECE TYPES =================
w_p, w_k, w_b, w_r, w_q, w_K = 1, 2, 3, 4, 5, 6
b_p, b_k, b_b, b_r, b_q, b_K = 9, 10, 11, 12, 13, 14
empty = 0
# black 1000 binary + piece value

# ============ OFFSETS =================
knight_offsets = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-1, -2), (-1, 2))
diag_offsets = ((-1, -1),(-1, 1),(1, 1),(1, -1))
straight_offsets = ((-1,0),(1,0),(0,-1),(0,1))
king_offsets = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),  (1, 0),  (1, 1))


class Chess:
    def __init__(self, points=None, super_mode=0):

        self.points = points
        pawn_row = np.array([w_p] * COLS)
        # To add exta queens if more dragons beaten
        if super_mode is not None:
            cnt = min(super_mode, COLS)
            idxs = np.random.choice(len(pawn_row), cnt, replace=False)
            pawn_row[idxs] = w_q

        self.board = np.array([
            [b_r, b_k, b_b, b_q, b_K, b_b, b_k, b_r],
            [b_p] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            pawn_row,
            [w_r, w_k, w_b, w_q, w_K, w_b, w_k, w_r]
        ], dtype=np.int8)
        self.white_turn = True
        self.move_log = []
        self.images = {}
        self.load_images()
    
    def make_move(self, move):
        """ This makes the move and stores it in the move_log"""
        start, end = move
        start_row, start_col = start
        end_row, end_col = end

        moved_piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = moved_piece
        self.board[start_row][start_col] = 0
        # move_log syntax [(move, captured piece, whose turn)...]
        self.move_log.append((move, captured_piece, self.white_turn))
        self.white_turn = not self.white_turn
        
    def undo_move(self):
        """ This undos the last move and removes it from the move_log"""
        if not self.move_log:
            return
        move, captured_piece, prev_turn = self.move_log.pop()
        start, end = move

        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = captured_piece
        self.white_turn = prev_turn
    
    def get_valid_moves(self):
        """This function gets all pseudo valid moves and validates each one."""
        pseuodo_valid_moves = self.get_all_pos_moves()
        return self.validate_moves(pseuodo_valid_moves)

    def get_all_pos_moves(self):
        """This is a method in the chess class that calls on a numba function with all
        parameters added (numba can not accept self)"""
        board = self.board
        return get_pos_moves(self.white_turn, board)

    def load_images(self):
        """This just loads the image with a library called Pathlib"""
        base_path = os.path.dirname(__file__)
        image_folder = os.path.join(base_path, "images")

        pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']
        for c in colors:
            for p in pieces:
                key = f"{c}_{p}"
                full_path = os.path.join(image_folder, f"{key}.png")
                img = pg.image.load(full_path).convert_alpha()
                img = pg.transform.smoothscale(img, (SQSIZE, SQSIZE))
                self.images[key] = img

    def validate_moves(self, pseudo_moves):
        """The validation function that calls on the helper function is_check to
        validate pseudo moves"""
        valid_moves=[]

        for move in pseudo_moves:
            self.make_move(move)

            if not self.is_in_check(not self.white_turn):
                valid_moves.append(move)

            self.undo_move()

        return valid_moves

    def is_in_check(self, is_white_king):
        """Finds where the king is of the color and uses the is_square_attacked function
        to find if the king is attacked"""
        king_val = w_K if is_white_king else b_K
        pos = np.where(self.board == king_val)
        if len(pos[0]) == 0: return False
        king_row, king_col = pos[0][0], pos[1][0]
        attacker_is_white = not is_white_king
        return is_square_attacked(self.board, king_row, king_col, attacker_is_white)
    
    def is_checkmate(self):
        """is_checkmate function returns true if a color is checked and no other moves."""
        if self.is_in_check(self.white_turn):
            valid_moves = self.get_valid_moves()
            if len(valid_moves) == 0:
                return True
        return False
    
    def is_stalemate(self):
        """is_stalemate function return true if a color is not checked and no other moves."""
        if not self.is_in_check(self.white_turn):
            if len(self.get_valid_moves()) == 0:
                return True
        return False

@njit
def get_pos_moves(white_turn, board):
    """This function uses numba and a helper function for each piece to find all pos moves"""
    moves = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            
            if piece == 0: continue
            piece_is_black = bool(piece & 8)
            if white_turn and piece_is_black:
                continue
            if not white_turn and not piece_is_black:
                continue

            color = -1 if not piece_is_black else 1
            piece_type = piece & 7

            if piece_type == 1:
                moves_to_add = pawn_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
            elif piece_type == 2:
                moves_to_add = knight_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
            elif piece_type == 3:
                moves_to_add = bishop_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
            elif piece_type == 4:
                moves_to_add = rook_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
            elif piece_type == 5:
                moves_to_add = queen_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
            elif piece_type == 6:
                moves_to_add = king_moves(board, r, c, color)
                for m in moves_to_add:
                    moves.append(m)
    return moves

#============== HELPER FUNCTIONS FOR MOVE FINDING  =================
@njit
def pawn_moves(board, r, c, direction):
    moves = []
    if in_range(r+direction) and board[r+direction][c] == 0:
        moves.append(((r, c),(r+direction, c)))

        start_r = 6 if direction == -1 else 1
        if r == start_r and board[r + 2*direction][c] == 0:
            moves.append(((r, c),(r + 2*direction, c)))
    
    for attack in [-1, 1]:
        end_c = c + attack
        end_r = r + direction
        if in_range(end_r) and in_range(end_c):
            target = board[end_r][end_c]
            
            if direction == -1:
                if target > 0 and (target & 8):
                    moves.append(((r, c),(end_r, end_c)))
            elif direction == 1:
                if target > 0 and not (target & 8):
                    moves.append(((r, c),(end_r, end_c)))
    return moves # optional en passant

@njit
def knight_moves(board, r, c, color):
    moves = []
    for dr, dc in knight_offsets:
        en_r, en_c = r+dr, c+dc
        if in_range(en_r) and in_range(en_c):
            if board[en_r][en_c] == 0:
                moves.append(((r, c),(en_r, en_c)))
            elif color==-1:
                if board[en_r][en_c] & 8:
                    moves.append(((r, c),(en_r, en_c)))
            else:
                if not board[en_r][en_c] & 8:
                    moves.append(((r, c),(en_r, en_c)))    
    return moves
@njit
def bishop_moves(board, r, c, color, king=False):
    return sliding_piece_move_finder(board, diag_offsets, r, c, color, king=king)
@njit
def rook_moves(board, r, c, color, king=False):
    return sliding_piece_move_finder(board, straight_offsets, r, c, color, king=king)
@njit
def queen_moves(board, r, c, color, king=False):
    return bishop_moves(board, r, c, color, king=king) + rook_moves(board, r, c, color, king=king)
@njit
def king_moves(board, r, c, color):
    return queen_moves(board, r, c, color, king=True) # will handle castling and all later if possible
@njit
def in_range(num, st=0, en=8):
    return st<=num<en


@njit
def sliding_piece_move_finder(board, dirs, r, c, color, king=False):
    """ This function is a helper function for the bishop, rook, king and queen and adds on each direction
    until the board ends and/or a piece is found"""
    moves = []
    max_range = 2 if king else 8
    # Iterate through all standard directions for this piece type
    for dr, dc in dirs:
        for i in range(1,max_range):
            target_r, target_c = r+dr*i, c+dc*i
            if in_range(target_r) and in_range(target_c):# 1. Check bounds
                target = board[target_r][target_c]
                if target == 0: # 2. If Empty Square -> Add Move
                    moves.append(((r, c),(target_r, target_c)))
                else: # 3. If Occupied -> Check Color
                    # Bitwise '& 8' extracts the color bit. 
                    # If bytes match, it's a friendly piece (Stop).
                    # If bytes differ, it's an enemy (Capture & Stop).
                    current_black = bool(board[r][c] & 8)
                    target_black = bool(target & 8)
                    if current_black != target_black: # if not same
                        moves.append(((r,c), (target_r, target_c)))
                    break
            else: break
    return moves

@njit
def is_square_attacked(board, r, c, attacker_is_white):
    """Helper func of is_check and finds all moves that would have an end destination
    at the square asked for."""
    attacker_is_black = not attacker_is_white

    if attacker_is_white:
        pawn_val = w_p
        pawn_row = r + 1
    else:
        pawn_val = b_p
        pawn_row = r - 1

    for dc in (-1, 1):
        nr, nc = pawn_row, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            if board[nr][nc] == pawn_val:
                return True
            
    knight_val = 2 | (8 if attacker_is_black else 0)
    for dr, dc in knight_offsets:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            if board[nr][nc] == knight_val:
                return True
    
    bishop_val = 3 | (8 if attacker_is_black else 0)
    queen_val = 5 | (8 if attacker_is_black else 0)

    for dr, dc in diag_offsets:
        for i in range(1, 8):
            nr, nc = r + dr*i, c + dc*i
            if not 0 <= nr < 8 or not 0 <= nc < 8:
                break

            targ = board[nr][nc]
            if targ == 0: continue
            if targ == bishop_val or targ == queen_val:
                return True
            break
    
    rook_val = 4 | (8 if attacker_is_black else 0)
    for dr, dc in straight_offsets:
        for i in range(1, 8):
            nr, nc = r +dr*i, c + dc*i
            if not 0 <= nr < 8 or not 0 <= nc < 8:
                break
            
            targ = board[nr][nc]
            if targ == 0: continue
            if targ == rook_val or targ == queen_val:
                return True
            break
    
    king_val = 6 | (8 if attacker_is_black else 0)

    for dr, dc in king_offsets:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            if board[nr][nc] == king_val:
                return True
    
    return False
# move = ((start row, start col),(end row, end col))
