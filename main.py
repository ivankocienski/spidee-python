
import os
import random
import pygame as pg

from game.game import Game

class Loader:
    def __init__(self, screen, base):
        self.base_dir = base
        self.screen   = screen

    def load_image(self, path):
        print("load_image: %s" % path)
        img = pg.image.load(os.path.join(self.base_dir, path))
        img.set_colorkey((255, 0, 255))
        return img
        #return .convert_alpha(self.screen)

    def load_ttf(self, path, size):
        print("load_font: %s" % path)
        fnt = pg.font.Font(os.path.join(self.base_dir, path), size)
        return fnt

    def load_wav(self, path):
        pass

def main():

    random.seed()
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode([800, 600])
    loader = Loader(screen, os.getcwd() + "/data")

    pg.display.set_caption('Spidee')

    g = Game(loader)
    g.resize(screen)
    g.reset()

    while(True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 
        
        g.draw(screen)
    
        pg.display.flip()

if __name__ == "__main__": main()
