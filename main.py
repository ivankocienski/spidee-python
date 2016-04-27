
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

class App:

    def __init__(self):
        random.seed()
        print("pygame ver=%s"%pg.version.ver)
        pg.init()
        pg.font.init()
        self.screen = pg.display.set_mode([800, 600])
        self.loader = Loader(self.screen, os.getcwd() + "/data")
        self.repaint()
        self.callback_count = 0
        self.callback_code = None
        pg.display.set_caption('Spidee')

    def draw_text( self, font, x, y, text, color ):
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def repaint(self):
        self.do_repaint = True

    def set_callback(self, count, code):
        self.callback_count = count
        self.callback_code  = code

    def main(self):

        g = Game(self)
        g.resize()
        g.reset()

        while(True):
            pg.time.delay(10)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return 

                elif event.type == pg.MOUSEMOTION:
                    g.mouse_move(event.pos[0], event.pos[1])

                elif event.type == pg.MOUSEBUTTONDOWN:
                    g.mouse_down()

                elif event.type == pg.MOUSEBUTTONUP:
                    g.mouse_up()

                elif event.type == pg.KEYDOWN:
                    g.key_down(event.key)

            if self.callback_code:
                if self.callback_count > 0:
                    self.callback_count -= 1
                else: 
                    code = self.callback_code 
                    self.callback_code = None
                    code()
                    
            
            if self.do_repaint:
                self.do_repaint = False
                g.draw()
                pg.display.flip()

if __name__ == "__main__": App().main()
