import pygame as pg
import numpy as np
import os
from numba import njit
from constants import ROWS, COLS, SQSIZE, WIDTH, HEIGHT, color

w_p, w_k, w_b, w_r, w_q, w_K = 1, 2, 3, 4, 5, 6
b_p, b_k, b_b, b_r, b_q, b_K = 9, 10, 11, 12, 13, 14
empty = 0
# black 1000 binary + piece value

knight_offsets = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-1, -2), (-1, 2))
diag_offsets = ((-1, -1),(-1, 1),(1, 1),(1, -1))
straight_offsets = ((-1,0),(1,0),(0,-1),(0,1))
king_offsets = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),  (1, 0),  (1, 1))


class Chess:
    def __init__(self, points=None, super_mode=None):
        self.points = points
        pawn_row = np.array([w_p] * COLS)
        if super_mode is not None:
            idxs = np.random.choice(len(pawn_row), super_mode, replace=False)
            pawn_row[idxs] = w_q

        self.board = np.array([
            [b_r, b_k, b_b, b_q, b_K, b_b, b_k, b_r],
            [b_p] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            [empty] * COLS,
            [w_p] * COLS,
            [w_r, w_k, w_b, w_q, w_K, w_b, w_k, w_r]
        ], dtype=np.int8)
        self.white_turn = True
        self.move_log = []
        self.images = {}
        self.load_images()
    
    def make_move(self, move):
        start, end = move
        start_row, start_col = start
        end_row, end_col = end

        moved_piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = moved_piece
        self.board[start_row][start_col] = 0
        self.move_log.append((move, captured_piece, self.white_turn))
        self.white_turn = not self.white_turn
        
    def undo_move(self):
        if not self.move_log:
            return
        move, captured_piece, prev_turn = self.move_log.pop()
        start, end = move

        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = captured_piece
        self.white_turn = prev_turn
    
    def get_valid_moves(self):
        pseuodo_valid_moves = self.get_all_pos_moves()
        return self.validate_moves(pseuodo_valid_moves)

    def get_all_pos_moves(self):
        board = self.board
        return get_pos_moves(self.white_turn, board)

    def load_images(self):
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
        valid_moves=[]

        for move in pseudo_moves:
            self.make_move(move)

            if not self.is_in_check(not self.white_turn):
                valid_moves.append(move)

            self.undo_move()

        return valid_moves

    def is_in_check(self, is_white_king):
        king_val = w_K if is_white_king else b_K
        pos = np.where(self.board == king_val)
        if len(pos[0]) == 0: return False
        king_row, king_col = pos[0][0], pos[1][0]
        attacker_is_white = not is_white_king
        return is_square_attacked(self.board, king_row, king_col, attacker_is_white)
    
    def is_checkmate(self):
        if self.is_in_check(self.white_turn):
            valid_moves = self.get_valid_moves()
            if len(valid_moves) == 0:
                return True
        return False
    
    def is_stalemate(self):
        if not self.is_in_check(self.white_turn):
            if len(self.get_valid_moves()) == 0:
                return True
        return False

@njit
def get_pos_moves(white_turn, board):
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
    moves = []
    max_range = 2 if king else 8

    for dr, dc in dirs:
        for i in range(1,max_range):
            target_r, target_c = r+dr*i, c+dc*i
            if in_range(target_r) and in_range(target_c):
                target = board[target_r][target_c]
                if target == 0:
                    moves.append(((r, c),(target_r, target_c)))
                else:
                    current_black = bool(board[r][c] & 8)
                    target_black = bool(target & 8)
                    if current_black != target_black: # if not same
                        moves.append(((r,c), (target_r, target_c)))
                    break
            else: break
    return moves

@njit
def is_square_attacked(board, r, c, attacker_is_white):
    
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