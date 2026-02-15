import moderngl as mgl
import numpy as np
import pygame as pg
from pyrr import Matrix44, Vector3
from shaders.shaders_3D import VERTEX_SHADER_3D, FRAGMENT_SHADER_3D
from shaders.shaders_2D import VERTEX_SHADER_2D, FRAGMENT_SHADER_2D
from constants import ROWS, COLS, SQSIZE, color

class Graphics3d:
    def __init__(self, screen):
        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.DEPTH_TEST)
        self.ctx.disable(mgl.CULL_FACE)

        self.prog = self.ctx.program(
            vertex_shader=VERTEX_SHADER_3D,
            fragment_shader=FRAGMENT_SHADER_3D
        )

        self.vbo = self.ctx.buffer(self._cube_data())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, "in_pos")

        aspect_ratio_screen = screen.get_width() / screen.get_height()
        self.projection = Matrix44.perspective_projection(90.0, aspect_ratio_screen, 0.1, 100.0)
        self.prog["m_proj"].write(self.projection.astype("float32"))

        self.vertex_shader_2d = VERTEX_SHADER_2D
        self.frag_shader_2d = FRAGMENT_SHADER_2D
        self.prog_2d = self.ctx.program(
            vertex_shader=self.vertex_shader_2d,
            fragment_shader=self.frag_shader_2d
        )
        self.prog_2d['u_texture'].value = 0
        self.quad_buffer = self.ctx.buffer(np.array([
           -1,  1,    0, 0,
           -1, -1,    0, 1,
            1,  1,    1, 0,
            1, -1,    1, 1,
        ], dtype='float32'))

        self.vao_2d = self.ctx.simple_vertex_array(
            self.prog_2d,
            self.quad_buffer,
            "in_pos",
            "in_texcoord"
        )

    def _cube_data(self):
        vertices = np.array([
            -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5,  0.5, -0.5,
             0.5,  0.5, -0.5, -0.5,  0.5, -0.5, -0.5, -0.5, -0.5,
            -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
             0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5, -0.5,  0.5,
            -0.5,  0.5,  0.5, -0.5,  0.5, -0.5, -0.5, -0.5, -0.5,
            -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,
             0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
            -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5,  0.5,
             0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5, -0.5, -0.5,
            -0.5,  0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,
             0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5,  0.5, -0.5,
        ], dtype="float32")
        return vertices

    def update_view(self, player):
        cam = Vector3([player.pos[0], 0.5, player.pos[1]])
        dir_cam = Vector3([np.cos(player.angle_x), 0.0, np.sin(player.angle_x)])
        view = Matrix44.look_at(cam, cam + dir_cam, Vector3([0.0, 1.0, 0.0]))
        self.prog["m_view"].write(view.astype("float32"))

    def render_maze(self, grid, wall_color, portal_color):
        self.ctx.clear(0.1, 0.1, 0.1)
        self.ctx.enable(mgl.DEPTH_TEST)
        self.ctx.disable(mgl.CULL_FACE)

        rows, cols = grid.shape
        for r in range(rows):
            for c in range(cols):
                val = grid[r, c]
                if val == 0: continue # if room
                if val == 2: continue # if player start pos

                model = Matrix44.from_translation([c + 0.5, 0.5, r + 0.5])
                self.prog["m_model"].write(model.astype("float32"))
                if val == 1:                    
                    self.prog["u_color"].value = wall_color
                elif val == 3:
                    self.prog['u_color'].value = portal_color
                elif val == 4:
                    self.prog["u_color"].value = (1.0, 0.0, 0.0)
   
                self.vao.render(mgl.TRIANGLES)

    def render_2d_surf(self, surface):
        rgba = pg.image.tostring(surface, 'RGBA', False)
        texture = self.ctx.texture(surface.get_size(), 4, data=rgba)

        self.ctx.enable(mgl.BLEND)
        self.ctx.disable(mgl.DEPTH_TEST)
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA

        texture.use(0)
        self.vao_2d.render(mgl.TRIANGLE_STRIP)

        self.ctx.disable(mgl.BLEND)
        self.ctx.enable(mgl.DEPTH_TEST)
        texture.release()

class Graphics2d:
    def __init__(self, surface, player, txt_size=36, big_txt_size=72):
        self.surface = surface
        self.font = pg.font.Font(None, txt_size)
        self.large_font = pg.font.Font(None, big_txt_size)
        self.player = player

    def draw_chess_board(self, chess_engine, selected_sq=None,
                         hover_sq=None, valid_moves=None):
        if chess_engine is None or chess_engine.board is None:
            return
        
        board = chess_engine.board

        for r in range(min(ROWS, len(board))):
            for c in range(min(COLS, len(board[r]))):

                sq_color = color["light"] if (r + c) % 2 == 0 else color["dark"]
                pg.draw.rect(self.surface, sq_color,
                    (c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))
                
                if hover_sq == (r, c):
                    surf = pg.Surface((SQSIZE, SQSIZE))
                    surf.set_alpha(100)
                    surf.fill((100, 200, 255))
                    self.surface.blit(surf, (c*SQSIZE, r*SQSIZE))

                if selected_sq == (r, c):
                    surf = pg.Surface((SQSIZE, SQSIZE))
                    surf.set_alpha(100)
                    surf.fill((255, 255, 0))
                    self.surface.blit(surf, (c*SQSIZE, r*SQSIZE))
                
                if valid_moves and (r, c) in valid_moves:
                    center = (c*SQSIZE + SQSIZE//2, r*SQSIZE + SQSIZE//2)
                    targ_piece = board[r][c]
                    rect = pg.Rect(center[0] - SQSIZE//2, center[1]-SQSIZE//2, SQSIZE,SQSIZE)
                    if targ_piece == 0:
                        pg.draw.rect(self.surface, (100, 100, 100), rect, 5)
                    else:
                        pg.draw.rect(self.surface, (200, 50, 50), rect, 5)

                piece = chess_engine.board[r][c]
                if piece != 0:
                    piece_type_val = piece & 7
                    type_names = (None, 'pawn', 'knight', 'bishop', 'rook', 'queen', 'king')
                    type_piece = type_names[piece_type_val]
                    p_color = 'black' if bool(piece & 8) else 'white'
                    key = f"{p_color}_{type_piece}"
                    if key in chess_engine.images:
                        img = chess_engine.images[key]
                        img_rect = img.get_rect(center=(c*SQSIZE + SQSIZE//2, r*SQSIZE + SQSIZE//2))
                        self.surface.blit(img, img_rect)

    def draw_fps(self):
        player = self.player
        
        sidebar_x = 800
        sidebar_width = 200
        pg.draw.rect(self.surface, (40, 40, 50), (sidebar_x, 0, sidebar_width, 800))
        pg.draw.line(self.surface, (255, 255, 255), (sidebar_x, 0), (sidebar_x, 800), 3)
        text_x = sidebar_x + 30
        lives_txt = self.font.render(f"Lives: {player.lives}", True, (255, 50, 50))
        score_txt = self.font.render(f"Score: {player.score}", True, (255, 255, 255))
        dragon_txt = self.font.render(f"Dragons: {player.dragons_beaten}", True, (255, 215, 0))
        self.surface.blit(lives_txt, (text_x, 50))
        self.surface.blit(score_txt, (text_x, 100))
        self.surface.blit(dragon_txt, (text_x, 150))
