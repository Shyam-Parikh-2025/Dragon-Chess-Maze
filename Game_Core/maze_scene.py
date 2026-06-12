import pygame as pg
import random
import math
from Game_Core.scene import Scene
from Game_Core.battle_scene import BattleScene
from Game_Core.taming_scene3 import TamingScene
from Game_Core.game import Game
from Game_Core.pause_scene import PauseScene

class MazeScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.map_mode = False

        # dev mode
        self.dev_sequence = ""
        self.dev_mode = False
        self.dev_passwords = {"Shyam": "DeVSHY@M5031@coders!",
                              "SAM": "DeVS@M5031@coders!"}
        self.dev_ = ""

    def handle_event(self, event):
        
        if self.game.terminal.handle_event(event):
            return

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.map_mode:
                    self._exit_map_mode()
                else:
                    self.game.change_scene(PauseScene(self.game, self))

            player = self.game.player

            if event.unicode:
                if event.key == pg.K_BACKSPACE:
                    self.dev_sequence = self.dev_sequence[:-1] if len(self.dev_sequence) >= 1 else []
                else:
                    self.dev_sequence += event.unicode
                
                if len(self.dev_sequence) > 30:
                    self.dev_sequence = self.dev_sequence[-30:]
                
                for dev_name, dev_pass in self.dev_passwords.items():
                    if self.dev_sequence.endswith(dev_pass):
                        self.dev_mode = not self.dev_mode
                        self.dev_ = dev_name if self.dev_mode else ""
                        self.game.player.log_msg( "=" * 20)
                        self.game.player.log_msg(f"DEV MODE: {'ACTIVATED' if self.dev_mode else 'DEACTIVATED'}")
                        self.game.player.log_msg( f"{'WELCOME' if self.dev_mode else 'Bye'} {dev_name.upper()}")
                        self.game.player.log_msg("=" * 20)
                        self.dev_sequence = ""
                        break

            if self.dev_mode:
                if event.key == pg.K_4:
                    player.score += 1000
                    self.game.player.log_msg( "DEV CHEAT: +1000 Score!")
                elif event.key == pg.K_5:
                    player.dragons_beaten += 2
                    self.game.player.log_msg( "DEV CHEAT: +2 Dragons Defeated!")
                elif event.key == pg.K_6:
                    rows, cols = self.game.grid.shape
                    player.pos[0] = float(cols - 4)   # x = column near boss
                    player.pos[1] = float(rows - 4)   # y = row near boss
                    self.game.player.log_msg( "DEV CHEAT: Teleported near the boss!")

            if event.key == pg.K_t:
                if player.warp and player.teleport_to_end_available:
                    rows, cols = self.game.grid.shape
                    player.pos[0] = float(cols - 4)   # x = column near boss
                    player.pos[1] = float(rows - 4)   # y = row near boss
                    player.teleport_to_end_available = False
                    self.game.player.log_msg( "WARP! Teleported near the boss battle!")

            if event.key == pg.K_m and player.beacon:
                if self.map_mode:
                    self._exit_map_mode()
                else:
                    self._enter_map_mode()
            
            if event.key == pg.K_h and player.home_beacon:
                player.set_named_waypoint('H', 2, 2)
                self.game.player.log_msg("Home Waypoint", "cleared" if 'H' not in player.waypoints else "set")
            if event.key == pg.K_p and player.portal_beacon:
                result = player.nearest_portal(self.game.grid)
                if result:
                    r, c = result
                    player.set_named_waypoint('P', r, c)
                    self.game.player.log_msg('Portal waypoint', "cleared" if 'P' not in player.waypoints else f"set at ({r},{c})")

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            player = self.game.player
            if self.map_mode and player.beacon:
                self._try_set_waypoint(event.pos)

    def _enter_map_mode(self):
        self.map_mode = True
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        self.game.player.can_move = False
 
    def _exit_map_mode(self):
        self.map_mode = False
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.player.can_move = True
    
    def _try_set_waypoint(self, mouse_pos):
        """A click on minimap => grid coord waypoint"""
        player = self.game.player
        surf = self.game.graphic2d_surf
        width, height = surf.get_size()

        radius_bonus = player.minimap_radius_bonus
        effective_r = int(self.game.graphic2d.minimap_radius * radius_bonus)
        padding = 10
        center_x = width - effective_r - padding
        center_y = height // 2
        mx, my = mouse_pos
        dx_px, dy_px = mx - center_x, my-center_y
        if dx_px * dx_px + dy_px * dy_px > effective_r * effective_r: return # using pythagorean theorem

        angle_deg = math.degrees(player.angle_x) + 90
        angle_rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        ux = dx_px * cos_a - dy_px * sin_a
        uy = dx_px * sin_a + dy_px * cos_a

        vision_range = 15 if player.gps else player.vision_range
        scale = effective_r / vision_range

        grid_c = int(player.pos[0] + ux / scale)
        grid_r = int(player.pos[1] + uy / scale)

        rows, cols = self.game.grid.shape
        grid_r = max(0, min(rows - 1, grid_r))
        grid_c = max(0, min(cols - 1, grid_c))

        player.place_custom_waypoint(grid_r, grid_c)
            
    def update(self):
        if self.map_mode: return 
        game = self.game
        keys = pg.key.get_pressed()
        game.player.update(keys, game.grid, game.delta_time)

        r, c = int(game.player.pos[1]), int(game.player.pos[0])
        tile_val = game.grid[r, c]

        if tile_val == 3:
            game.current_battle_pos = (r, c) #type: ignore
            game.player.playing_chess = True
            if random.random() < game.player.chance_of_chess:
                game.change_scene(BattleScene(game))
            else:
                game.change_scene(TamingScene(game))
        
        elif tile_val == 4:
            if game.player.dragons_beaten >= 2:
                self.game.player.log_msg("Time to fight the boss! You can do it!")
                game.current_battle_pos = (r, c) #type: ignore
                game.player.playing_chess = True

                power_up = 0
                if game.player.dragons_beaten > 2:
                    power_up = min(game.player.dragons_beaten, 8)

                if random.random() <= game.player.chance_of_chess:
                    game.change_scene(BattleScene(game, is_boss=True, super_mode=power_up))
                else:
                    game.change_scene(TamingScene(game, is_boss=True))
            else:
                game.player.pos[0] -= 0.3
                game.player.pos[1] -= 0.3
                self.game.player.log_msg("You have to defeat more dragons to be able to fight the boss!")
    
    def render(self):
        game: Game = self.game
        game.graphic3d.update_view(game.player)
        game.graphic3d.render_maze(game.grid, game.wall_color, game.portal_color, game.player)
        
        game.graphic2d.start_2d()
        game.graphic2d.draw_fps()
        game.graphic2d.draw_minimap(game.grid, game.player, game.wall_color, game.portal_color)

        game.graphic2d.draw_terminal(self.dev_mode)
        game.graphic3d.render_2d_surf(game.graphic2d_surf)

