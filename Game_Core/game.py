import pygame as pg, random
from pathlib import Path
import constants
from Game_Core.player import Player
from Graphics.graphics import Graphics2d, Graphics3d
from Game_Core.chat_ui import ChatBox
from Game_Core.map_gen import MapGen

base_path = Path(__file__).resolve().parent

class Game:
    def __init__(self):
        pg.init()
        self.is_fullscreen = False
        self.screen = pg.display.set_mode((constants.WIDTH, constants.HEIGHT), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

        self.clock = pg.time.Clock()
        icon_path = base_path.parent / 'images' / 'white_queen.png'
        try:
            game_icon = pg.image.load(icon_path) 
            pg.display.set_icon(game_icon)
        except FileNotFoundError:
            print("Icon file not found.")
        pg.display.set_caption("Dragon Chess Maze")

        self.terminal = ChatBox(
            x=self.screen.get_width() - 200, 
            y=int(self.screen.get_height() * 0.5), 
            width=200, 
            height=int(self.screen.get_height() * 0.3),
            on_submit=self.process_term_cmd
        )
        self.terminal.log_msg(False, "Type /help for commands.", color=(150, 150, 255))
        
        self.map_gen = MapGen(numBattles=81, maze_size=(45,45)) 
        self.grid, self.portals = self.map_gen.generate_full()
        self.player = Player(start_pos=(2, 2), game=self)
        self.graphic3d = Graphics3d(self.screen, self.grid)
        self.graphic2d_surf = pg.Surface((constants.WIDTH, constants.HEIGHT), pg.SRCALPHA).convert_alpha()
        self.graphic2d = Graphics2d(self.graphic2d_surf, self.player, terminal=self.terminal)

        self.current_battle_pos = (0,0)
        self.current_scene = None
        self.running = True
        self.wall_color = (0.3, 0.3, 0.3)
        self.portal_color = (0.6, 0.6, 0.6)
        self.maze_scene = None
        self.player.time_limit_of_AI = 0
        self.retry = False

        # msg history
        self.old_msgs = []
        self.old_dev_msgs = [] 
    
    def change_scene(self, new_scene):
        self.current_scene = new_scene
    
    def run(self):
        self.running = True
        while self.running:
            self.delta_time = self.clock.tick(60) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_F11:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.screen = pg.display.set_mode((constants.WIDTH,constants.HEIGHT),
                                                          pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN)
                    else:
                        self.screen = pg.display.set_mode((constants.WIDTH, constants.HEIGHT), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE) 
                # Resizing Fix
                if event.type == pg.VIDEORESIZE:
                    width, height = event.size
                    self.graphic3d.ctx.viewport = (0, 0, width, height)
                    self.graphic3d.update_projection(width=width, height=height)
                    self.graphic2d_surf = pg.Surface((width, height), pg.SRCALPHA).convert_alpha()
                    self.graphic2d.surface = self.graphic2d_surf
                    self.graphic2d.minimap_radius = int(min(width, height) * 0.1125)
                    self.terminal.resize(width, height)
                    if hasattr(self.current_scene, 'resize'):
                        self.current_scene.resize(width, height)  #type: ignore
                if self.current_scene:
                    self.current_scene.handle_event(event)
            
            if self.current_scene:
                self.current_scene.update()
                self.current_scene.render()
            
            pg.display.flip()
            if self.retry:
                return True
        return False

    def process_term_cmd(self, cmd: str):
        dev_active = False
        if getattr(self, 'maze_scene', None) is not None:
            dev_active = getattr(self.maze_scene, 'dev_mode', False)

        self.terminal.log_msg(dev_active, f"> {cmd}", color=(50, 255, 50), sender="Player")

        cmd_lower = cmd.lower().strip()

        if "help" in cmd_lower:
            self.terminal.log_msg(dev_active, "--- COMMANDS ---", color=(0, 255, 255))
            self.terminal.log_msg(dev_active, "/stats : View your stats", color=(200, 200, 200))
            self.terminal.log_msg(dev_active, "/taunt : Yell at the Dragon", color=(200, 200, 200))
            self.terminal.log_msg(dev_active, "/clear : Clear the chat", color=(200, 200, 200))
            self.terminal.log_msg(dev_active, "/hint : Gives a random hint", color=(200, 200, 200))
            self.terminal.log_msg(dev_active, "/skills : Prints unlocked skills", color=(200, 200, 200))
            
        elif "stats" in cmd_lower:
            self.terminal.log_msg(dev_active, f"Score: {self.player.score} | Lives: {self.player.lives}", color=(255, 215, 0))
            self.terminal.log_msg(dev_active, f"Dragons Defeated: {self.player.dragons_beaten}", color=(255, 215, 0))
            
        elif "taunt" in cmd_lower:
            from Game_Core.chat_ui import Message
            msg = Message("Foolish Tamer... My pieces will crush you!", sender="Dragon", color=(255, 255, 255), max_width=self.terminal.rect.width-20, shape="oval", bg_color=(150, 0, 0, 255))
            self.terminal.add_message(msg, is_dev=dev_active)
            
        elif "clear" in cmd_lower:
            self.old_msgs.append(list(self.terminal.msgs))
            self.old_dev_msgs.append(list(self.terminal.dev_msgs))
            self.terminal.msgs.clear()
            self.terminal.dev_msgs.clear()
            
        elif "hint" in cmd_lower:
            all_hints = [
                "Hint: Unlock 'Beacon' in the Skill Tree to find portals quicker!",
                "Hint: Spend your score on skills early!",
                "Hint: Press F2 or H in the taming arena to view dragon hitboxes.",
                "Hint: Can't beat the dragons in chess? Lower the Chess Difficulty in the main menu to make them blunder more often!",
                "Hint: Must defeat 2 minions to be deemed worthy of defeating the dragon.",
                "Hint: Unlock 'Warp' in the Skill Tree to teleport near the boss arena!"
            ]
            unlocked = ", ".join(self.player.unlocked_skills)
            if "beacon" in unlocked:
                hints = all_hints[2:]
            else: 
                hints = all_hints
            self.terminal.log_msg(dev_active, random.choice(hints), color=(255, 150, 0))
            
        elif "skills" in cmd_lower:
            unlocked = ", ".join(self.player.unlocked_skills)
            self.terminal.log_msg(dev_active, f"Unlocked: {unlocked}", color=(100, 255, 255))
            
        elif "warp" in cmd_lower or "teleport" in cmd_lower:
            if self.player.warp and self.player.teleport_to_end_available:
                rows, cols = self.grid.shape
                self.player.pos[0] = float(cols - 4)
                self.player.pos[1] = float(rows - 4)
                self.player.teleport_to_end_available = False
                self.terminal.log_msg(dev_active, "WARP! TELEPORTED near the boss!", color=(215,215, 0))
                
            elif dev_active:
                # Safely parse coordinates like "/teleport 10,15"
                cmd_end = cmd_lower.split(" ")[-1].strip("()")
                try:
                    parts = cmd_end.split(",")
                    if len(parts) == 2:
                        r_c, g_c = int(parts[0]), int(parts[1])
                        self.player.pos[0] = float(r_c)
                        self.player.pos[1] = float(g_c)
                        self.terminal.log_msg(dev_active, f"Teleported to ({r_c}, {g_c})", color=(215, 215, 0))
                    else:
                        self.terminal.log_msg(dev_active, "Format: /teleport x,y", color=(215, 215, 0))
                except Exception:
                    self.terminal.log_msg(dev_active, "Incorrect format. Use: /teleport x,y", color=(215, 215, 0))
            else:
                self.terminal.log_msg(dev_active, "Warp not unlocked or already used!", color=(255, 100, 100))

        else:
            if getattr(self, 'maze_scene', None) is not None:
                dev_pswds = getattr(self.maze_scene, 'dev_passwords', None)
                if dev_pswds is not None:
                    for name, pswd in dev_pswds.items():
                        # Use .lower() so it matches cmd_lower
                        if pswd.lower() in cmd_lower:
                            self.maze_scene.dev_mode = not self.maze_scene.dev_mode
                            dev_active = self.maze_scene.dev_mode
                            self.terminal.log_msg(dev_active, "=" * 20, color=(255, 50, 50))
                            self.terminal.log_msg(dev_active, f"DEV MODE: {'ACTIVATED' if dev_active else 'DEACTIVATED'}", color=(255, 50, 50))
                            self.terminal.log_msg(dev_active, "=" * 20, color=(255, 50, 50))
                            return  # Stop executing so it doesn't print "Unknown Command"
                            
            self.terminal.log_msg(dev_active, "Unknown command. Type: /help", color=(255, 100, 100))