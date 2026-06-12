from Game_Core.scene import Scene
from Chess_Engine.battle import Battle
from Game_Core.menu_scenes import EndScreen
from Game_Core.ui import Button
import constants, pygame as pg


class BattleScene(Scene):
    def __init__(self, game, is_boss=False, super_mode=0):
        super().__init__(game)
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        drag_name = "King" if is_boss else "Dragon Minion"
        self.battle = Battle(
            surface=game.graphic2d_surf,
            dragon_level=constants.BOSS_DRAG_LEVEL if is_boss else constants.MINION_DRAG_LEVEL,
            dragon_name=drag_name,
            player=game.player,
            game=game,
            super_mode=super_mode,
        )
        width, height = game.graphic2d_surf.get_size()
        self.quit_button = Button(
            width - 190, height - 60, 180, 50, game.graphic2d_surf,
            on_click=self.surrender,
            text="SURRENDER",
            ACTIVE_COLOR=(255, 80, 80),
        )

        # Prevents the post-game transition from firing more than once.
        self.resolved = False

    # ------------------------------------------------------------------
    # Surrender (Q key or Surrender button)
    # ------------------------------------------------------------------
    def surrender(self):
        self.battle.player_lost()
        if self.game.player.lives <= 0:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.game.change_scene(EndScreen(self.game, victory=False))
            return
        self.game.player.playing_chess = False
        self.game.player.speed = 0.1
        self._respawn_player()
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.change_scene(self.game.maze_scene)

    # ------------------------------------------------------------------
    # Respawn helper
    # ------------------------------------------------------------------
    def _respawn_player(self):
        if self.game.player.soft_landing:
            r, c = self.game.current_battle_pos
            grid = self.game.grid
            rows, cols = grid.shape
            for dist in [5, 4, 3, 2, 1]:
                nr = max(0, min(rows - 1, r + dist))
                nc = max(0, min(cols - 1, c))
                if grid[nr, nc] == 0:
                    self.game.player.pos[0] = float(nc)
                    self.game.player.pos[1] = float(nr)
                    return
        self.game.player.pos[0] = 2.0
        self.game.player.pos[1] = 2.0

    # ------------------------------------------------------------------
    # Event Handler
    # ------------------------------------------------------------------
    def handle_event(self, event):
        self.battle.handle_event(event)
        self.quit_button.handle_event(event)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.surrender()

    # ------------------------------------------------------------------
    # Update  — FIX: battle.update() already calls check_game_over()
    # internally via make_move/player_won/player_lost.  Calling it a
    # second time here caused player_won() / player_lost() to fire twice
    # on the same frame, producing double-life-loss and score glitches.
    # We now call check_game_over() exactly once, after update().
    # ------------------------------------------------------------------
    def update(self):
        self.battle.update()

        # Only evaluate the result once per battle outcome.
        if self.resolved:
            return

        game_ended = self.battle.game_over_processed  # set by player_won/player_lost
        if not game_ended:
            return

        self.resolved = True
        engine = self.battle.chess_engine

        # ── Player wins (dragon is checkmated) ────────────────────────
        if engine.is_checkmate() and not engine.white_turn:
            if self.battle.dragon_level == constants.BOSS_DRAG_LEVEL:
                # Final boss defeated -> victory screen
                pg.event.set_grab(False)
                pg.mouse.set_visible(True)
                self.game.change_scene(EndScreen(self.game, victory=True))
                return

            # Minion defeated -> remove portal tile from grid
            r, c = self.game.current_battle_pos
            self.game.grid[r, c] = 0
            self.game.graphic3d.refresh_instances(self.game.grid)

        # ── Player is out of lives ─────────────────────────────────────
        elif self.game.player.lives <= 0:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.game.change_scene(EndScreen(self.game, victory=False))
            return

        # ── Stalemate — respawn near the portal ───────────────────────
        else:
            self._respawn_player()

        # ── Return to maze (covers minion win and stalemate) ──────────
        self.game.player.playing_chess = False
        self.game.player.speed = 0.1
        self.game.player.can_move = True

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.change_scene(self.game.maze_scene)
        pg.time.wait(1)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def render(self):
        game = self.game
        game.graphic3d.ctx.clear(0.05, 0.05, 0.1)
        game.graphic2d_surf.fill((0, 0, 0, 0))
        game.graphic2d.draw_chess_board(
            self.battle.chess_engine,
            selected_sq=self.battle.selected_sq,
            hover_sq=self.battle.hover_sq,
            valid_moves=self.battle.hover_moves,
        )
        game.graphic2d.draw_fps(self.battle.ai_thinking, True)
        self.quit_button.draw()
        game.graphic3d.render_2d_surf(game.graphic2d_surf)

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------
    def resize(self, width, height):
        self.quit_button.surface = self.game.graphic2d_surf
        self.quit_button.rect.x = width - 190
        self.quit_button.rect.y = height - 60
        self.battle.surface = self.game.graphic2d_surf