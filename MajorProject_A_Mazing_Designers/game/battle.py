from chess_engine import Chess
from constants import SQSIZE
from dragon import Dragon
from player import Player
import pygame as pg

class Battle:
    def __init__(self, surface, dragon_level, dragon_name, player, super_mode=None):
        self.surface = surface
        self.super_mode = super_mode
        self.chess_engine = Chess(super_mode=self.super_mode)
        self.is_active = True
        self.selected_sq = None
        self.hover_sq = None
        self.hover_moves = []
        self.player = player
        self.player.can_move = False
        self.dragon = Dragon(dragon_name, dragon_level)
        self.dragon_level = dragon_level
        self.game_over_processed = False
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            col = mouse_x // SQSIZE
            row = mouse_y // SQSIZE
            if 0<= row < 8 and 0 <= col < 8:
                self.click_process(row, col)
        
        if event.type == pg.MOUSEMOTION:
            mouse_x, mouse_y = pg.mouse.get_pos()
            col = mouse_x // SQSIZE
            row = mouse_y // SQSIZE

            if 0 <= row < 8 and 0 <= col < 8:
                self.hover_sq = (row, col)
                self.update_hover_moves()
            else:
                self.hover_sq = None
                self.hover_moves = []
        
    def update_hover_moves(self):
        self.hover_moves = []
        if self.selected_sq:
            for move in self.chess_engine.get_valid_moves():
                if move[0] == self.selected_sq:
                    self.hover_moves.append(move[1])
        elif self.hover_sq:
            r, c = self.hover_sq
            piece = self.chess_engine.board[r][c]
            if piece != 0 and not (piece & 8) and self.chess_engine.white_turn:
                for move in self.chess_engine.get_valid_moves():
                    if move[0] == self.hover_sq:
                        self.hover_moves.append(move[1])
    
    def click_process(self, row, col):
            if self.selected_sq is None:
                piece = self.chess_engine.board[row][col]
                if piece != 0:
                    is_black = bool(piece  & 8)
                    if self.chess_engine.white_turn and not is_black:
                        self.selected_sq = (row, col)
                        print(f"Selected: {self.selected_sq}")
        
            else:
                if self.selected_sq == (row, col):
                    self.selected_sq = None
                    return
                move = (self.selected_sq, (row, col))
                if move in self.chess_engine.get_valid_moves():
                    self.chess_engine.make_move(move)
                    self.selected_sq = None
                    if not self.check_game_over(self.player):
                        self.trigger_dragon_move()
                else:
                    n_piece = self.chess_engine.board[row][col]
                    if self.chess_engine.white_turn and n_piece != 0 and not (n_piece & 8):
                        self.selected_sq = (row, col)
                    else:
                        self.selected_sq = None
    
    def trigger_dragon_move(self):
        if not self.chess_engine.white_turn:
            move = self.dragon.get_move(self.chess_engine)
            if move == None:
                return
                # self.player
            self.chess_engine.make_move(move)
            self.check_game_over(self.player)

    def player_won(self):
        if self.game_over_processed: return
        self.game_over_processed = True
        self.player.dragons_beaten += 1
        self.player.playing_chess = False
        self.player.can_move = True
        self.update_score(self.dragon_level)
    
    def player_lost(self):
        if self.game_over_processed: return
        self.game_over_processed = True
        self.player.lives -= 1
        self.player.playing_chess = False
        self.player.can_move = True
        print("Lost a Life! You can do it!")


    def update_score(self, difficulty):
        self.player.score += (difficulty + 1)*100
    
    def check_game_over(self, player):
        if self.chess_engine.is_checkmate():
            if self.chess_engine.white_turn:
                self.player_lost()
            else:
                self.player_won()
            return True
        elif self.chess_engine.is_stalemate():
            print("Good Progress! Try again!")
            player.playing_chess = False
            return True
        return False
                
