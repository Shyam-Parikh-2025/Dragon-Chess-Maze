from installers import install
print("All the libraries needed are about to be installed: ")
install()

from game import Game
from maze_scene import MazeScene
from menu_scenes import StartScreen
import pygame as pg

def main():
    game = Game()
    maze_scene = MazeScene(game)
    #print(game.map_gen)
    game.maze_scene = maze_scene
    start_screen = StartScreen(game)
    game.change_scene(start_screen)

    pg.event.set_grab(True)
    pg.mouse.set_visible(True)
    game.run()

if __name__ == "__main__":
    main()