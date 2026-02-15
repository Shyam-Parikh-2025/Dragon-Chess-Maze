import pygame as pg
from scene import Scene
from ui import UI_MANAGER, Button, Slider
from constants import WIDTH, HEIGHT

class StartScreen(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.manager = UI_MANAGER()
        self.font = pg.font.Font(None, 50)
        self.small_font = pg.font.Font(None, 50)

        self.edit_mode = 0
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        self.button_wall = Button(center_x - 220, 200, 200, 50, game.graphic2d_surf,
                                  on_click=lambda: self.set_mode(0),
                                  text="Edit Walls", toggle=False)
        self.button_portal = Button(center_x + 20, 200, 200, 50, game.graphic2d_surf, 
                                 on_click=lambda: self.set_mode(1), 
                                 text="Edit Portals", toggle=False)
        
        self.slider_r = Slider(center_x - 100, 300, 200, 20, game.graphic2d_surf, initial_val=0.3)
        self.slider_g = Slider(center_x - 100, 350, 200, 20, game.graphic2d_surf, initial_val=0.3)
        self.slider_b = Slider(center_x - 100, 400, 200, 20, game.graphic2d_surf, initial_val=0.3)

        self.button_start = Button(center_x - 100, 600, 200, 60, game.graphic2d_surf, 
                                   on_click=self.start_game, text="Begin Game", 
                                   ACTIVE_COLOR=(100, 255, 100))
        
        self.manager.elements.extend([
            self.button_wall, self.button_portal, 
            self.slider_r, self.slider_g, self.slider_b,
            self.button_start
        ])
        self.button_wall.is_active = True
    
    def set_mode(self, mode):
        self.edit_mode = mode
        self.button_wall.is_active = (mode == 0)
        self.button_portal.is_active  = (mode == 1)
        current_color = self.game.wall_color if mode == 0 else self.game.portal_color

        self.slider_r.value = current_color[0]
        self.slider_g.value = current_color[1]
        self.slider_b.value = current_color[2]
        self.slider_r.update_knob_pos()
        self.slider_g.update_knob_pos()
        self.slider_b.update_knob_pos()
    
    def start_game(self):
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.change_scene(self.game.maze_scene)
    
    def handle_event(self, event):
        self.manager.handle_event(event)
    
    def update(self):
        self.manager.update()
        r = self.slider_r.get_val(0, 1)
        g = self.slider_g.get_val(0, 1)
        b = self.slider_b.get_val(0, 1)
        n_color = (r, g, b)
        if self.edit_mode == 0:
            self.game.wall_color = n_color
        else:
            self.game.portal_color = n_color
    
    def render(self):
        self.game.graphic2d_surf.fill((30, 30, 40))
        title = self.font.render("MAZE FORGE", True, (255, 215, 0))
        rect = title.get_rect(center=(WIDTH//2, 100))
        self.game.graphic2d_surf.blit(title, rect)

        labels = ["R", "G", "B"]
        y_pos = [300, 350, 400]
        for i, label in enumerate(labels):
            text = self.small_font.render(label, True, (255, 255, 255))
            self.game.graphic2d_surf.blit(text, (WIDTH//2 - 130, y_pos[i]))
        
        preview_color_box = (int(self.slider_r.get_val(0, 255)),
                             int(self.slider_g.get_val(0, 255)),
                             int(self.slider_b.get_val(0, 255)))
        pg.draw.rect(self.game.graphic2d_surf, preview_color_box, (WIDTH//2 - 50, 450, 100, 100))
        pg.draw.rect(self.game.graphic2d_surf, (255, 255, 255), (WIDTH//2 - 50, 450, 100, 100), 3)

        self.manager.draw()
        self.game.graphic3d.render_2d_surf(self.game.graphic2d_surf)

class EndScreen(Scene):
    def __init__(self, game, victory=True):
        super().__init__(game)
        self.manager = UI_MANAGER()
        self.victory = victory
        self.font = pg.font.Font(None, 50)

        self.button_quit = Button(WIDTH//2 - 300, HEIGHT//2 + 100, 200, 60, game.graphic2d_surf, 
                               on_click=self.quit_game, text="QUIT GAME")
        self.manager.elements.append(self.button_quit)
    
    def quit_game(self):
        self.game.running = False
    
    def handle_event(self, event):
        self.manager.handle_event(event)
    
    def update(self):
        self.manager.update()
    
    def render(self):
        self.game.graphic2d_surf.fill((0, 0, 0))
        msg = "VICTORY!" if self.victory else "GAME OVER! BETTER LUCK NEXT TIME!"
        color = (215, 215, 0) if self.victory else (200, 50, 50)

        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.game.graphic2d_surf.blit(text, rect)
        score_font = pg.font.Font(None, 50)
        score_text = score_font.render(f"Final Score: {self.game.player.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2+50))
        self.game.graphic2d_surf.blit(score_text, score_rect)

        self.manager.draw()
        self.game.graphic3d.render_2d_surf(self.game.graphic2d_surf)
