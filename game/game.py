
import random

from game.constants import *
from game.dealer import Dealer
from game.card import Card
from game.column import Column

class Game:
    def __init__(self, app):
        self.app          = app
        self.bg_image     = app.loader.load_image("bg.png")
        self.card_sprites = [ app.loader.load_image("card-%02x.png" % (x+1)) for x in range(13)]
        self.card_empty   = app.loader.load_image("card-empty.png")
        self.card_down    = app.loader.load_image("card-down.png")
        self.card_hint    = app.loader.load_image("card-hint.png")
        self.font         = app.loader.load_ttf("liberation-sans.ttf", 15)

        # game structures
        self.columns = [ Column(self.card_empty) for x in  range(10)]
        self.dealer  = Dealer(self.card_sprites, self.card_down)
        
        self.drag_cards       = None
        self.drag_from_column = None
        self.drag_xoffs       = 0
        self.drag_yoffs       = 0
        self.drag_xpos        = 0
        self.drag_ypos        = 0

        self.over      = -1
        self.over_card = None

    def _draw_bg(self):

        s_width   = self.app.screen.get_width()
        s_height  = self.app.screen.get_height()
        bg_width  = self.bg_image.get_width()
        bg_height = self.bg_image.get_height()

        y = 0
        while y < s_height:
            x = 0
            while x < s_width:
                self.app.screen.blit(self.bg_image, (x, y))
                x += bg_width
            y += bg_height
    
    def resize(self):
        step = self.app.screen.get_width() / float(len(self.columns))
        xpos = (step - CARD_WIDTH) / 2.0
        for c in self.columns:
            c.set_pos(xpos)
            xpos += step

        self.dealer.set_pos(self.app.screen)

    def reset(self):
        self.dealer.reset()

        for i in range(0, 55):
            self.columns[i%len(self.columns)].push(self.dealer.next_card())

        for c in self.columns:
            c.turn_over_top_card()

    def mouse_move(self, xp, yp):

        self.drag_xpos = xp
        self.drag_ypos = yp

        # skip it if we're moving things about
        #if self.drag_cards:
        #    self.app.repaint()
        #    return


        self.over = -1
        for i in range(0, len(self.columns)):
            if self.columns[i].is_point_over(xp, yp):
                self.over = i
                break

        if self.over == -1:
            self.over_card = None
        else:
            found = self.columns[self.over].over_card(xp, yp)
            if found:
                self.over_card  = found[0]
                self.over_xoffs = found[1]
                self.over_yoffs = found[2]

        self.app.repaint()

    def mouse_down(self):
        if self.over_card:
            self.drag_from_column = self.columns[self.over]
            self.drag_cards = self.columns[self.over].pop(self.over_card)
            self.drag_xoffs = self.over_xoffs
            self.drag_yoffs = self.over_yoffs
            self.app.repaint()

    def mouse_up(self):
        if self.drag_cards:
            try_column = self.columns[self.over]
            if try_column.can_card_be_pushed(self.drag_cards[0]):
                try_column.push(self.drag_cards)
                self.drag_from_column.turn_over_top_card()

            else:
                self.drag_from_column.push(self.drag_cards)

            self.drag_cards = None
            self.app.repaint()


    def draw(self):
        self._draw_bg()

        self.dealer.draw(self.app.screen)

        for c in self.columns:
            c.draw(self.app.screen)

        if self.drag_cards:
            draw_x = self.drag_xpos + self.drag_xoffs
            draw_y = self.drag_ypos + self.drag_yoffs
            for card in self.drag_cards:
                card.draw(self.app.screen, draw_x, draw_y)
                draw_y += PADDING

        
        self.app.draw_text(
                self.font,
                10, 530,
                "over=%d"%self.over,
                (255,255,255))


        if self.over_card:
            self.app.draw_text(
                    self.font,
                    10, 550,
                    "card=%s"%self.over_card,
                    (255,255,255))

            self.app.draw_text(
                    self.font,
                    10, 570,
                    "xoffs=%d  yoffs=%d"%(self.over_xoffs, self.over_yoffs),
                    (255,255,255))

