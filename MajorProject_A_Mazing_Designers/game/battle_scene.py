from scene import Scene
from battle import Battle
import pygame as pg
from menu_scenes import EndScreen
from ui import Button

class BattleScene(Scene):
    def __init__(self, game, is_boss=False, super_mode=None):
        super().__init__(game)
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        drag_name = "King" if is_boss else "Dragon Minion"
        self.battle = Battle(
            surface=game.screen,
            dragon_level=1 if is_boss else 0,
            dragon_name= drag_name,
            player=game.player,
            super_mode=super_mode
        )

        self.quit_button = Button(810, 600, 180, 50, game.graphic2d_surf, 
                               on_click=self.surrender, 
                               text="SURRENDER", ACTIVE_COLOR=(255, 80, 80))
        self.resolved = False

    def surrender(self):
        self.battle.player_lost()
        print("Player surrendered!")
        if self.game.player.lives <= 0:
            print("Game Over by Surrender")
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.game.change_scene(EndScreen(self.game, victory=False))
            return
        self.game.player.playing_chess = False
        self.game.player.speed = 0.1
        self.game.player.pos[0] = 2.0
        self.game.player.pos[1] = 2.0
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.change_scene(self.game.maze_scene)

    def handle_event(self, event):
        self.battle.handle_event(event)
        self.quit_button.handle_event(event) 
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.surrender()
    
    def update(self):
        if self.battle.check_game_over(self.game.player):
            if self.resolved :
                return
            self.resolved = True
            if self.battle.chess_engine.is_checkmate() and not self.battle.chess_engine.white_turn:
                if self.battle.dragon_level == 1:
                    print("YOU WIN!!!")
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
                    self.game.change_scene(EndScreen(self.game, victory=True))
                    return

                r, c = self.game.current_battle_pos                
                self.game.grid[r, c] = 0
                print("One Battle cleared!")
            if self.game.player.lives <= 0:
                print("Game Over")
                pg.event.set_grab(False)
                pg.mouse.set_visible(True)
                self.game.change_scene(EndScreen(self.game, victory=False))
                return
            self.game.player.playing_chess = False
            self.game.player.speed = 0.1

            pg.event.set_grab(True)
            pg.mouse.set_visible(False)
            
            self.game.change_scene(self.game.maze_scene)
    
    def render(self):
        game = self.game

        game.graphic2d_surf.fill((0,0,0,0))
        game.graphic2d.draw_chess_board(
            self.battle.chess_engine,
            selected_sq=self.battle.selected_sq,
            hover_sq=self.battle.hover_sq,
            valid_moves= self.battle.hover_moves)
        game.graphic2d.draw_fps()
        self.quit_button.draw()
        game.graphic3d.render_2d_surf(game.graphic2d_surf)
