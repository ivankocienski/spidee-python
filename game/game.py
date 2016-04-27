
import random

import pygame as pg

from game.constants import *
from game.dealer import Dealer
from game.card import Card
from game.column import Column
from game.done_pile import DonePile

class Game:

    class ScoreBox:
        def __init__(self, font):
            self.font  = font
            self.color = (255,255,255)
            self.reset()
        
        def reset(self):
            self.move_count = 0
            self.score      = 500
            self._render()

        def _render(self): 
            self.score_text_surface = self.font.render("Score: %d"%self.score, True, self.color)
            self.moves_text_surface = self.font.render("Moves: %d"%self.move_count, True, self.color)

        def inc_score(self):
            self.score += 100
            self._render()

        def inc_moves(self):
            self.score      -= 1
            self.move_count += 1
            self._render()

        def draw(self, screen):

            box_w = 200
            box_h = CARD_HEIGHT
            xpos = (screen.get_width() - box_w) / 2
            ypos = screen.get_height() - PADDING - box_h
            pg.draw.rect(
                    screen,
                    (0,150,0),
                    (xpos, ypos, box_w, box_h))

            pg.draw.rect(
                    screen,
                    (0,50,0),
                    (xpos, ypos, box_w, box_h),
                    1)

            screen.blit(
                    self.score_text_surface,
                    (xpos + 55, ypos + 25))

            screen.blit(
                    self.moves_text_surface,
                    (xpos + 55, ypos + 55))

    class Hinter:
        def __init__(self, app, columns):
            self.app      = app
            self.columns  = columns
            self.hints    = []
            self.hint_pos = 0

            for from_column in self.columns:

                longest_run_card = from_column.longest_run()
                if not longest_run_card:
                    continue

                for to_column in self.columns:
                    if from_column == to_column:
                        continue
                    
                    if to_column.can_card_be_pushed(longest_run_card):
                        self.hints.append((from_column, longest_run_card, to_column))
            
            # TODO: sort these...
            self.flash_next()


        def flash_next(self):
            if len(self.hints) == 0:
                return

            from_column = self.hints[self.hint_pos][0]
            from_card   = self.hints[self.hint_pos][1]
            to_column   = self.hints[self.hint_pos][2]
            self.hint_pos = (self.hint_pos+1)%len(self.hints)

            def flash_stop():
                to_column.set_hint(None)
                self.app.repaint() 

            def flash_to():
                from_column.set_hint(None);
                to_column.hint_last_card()
                self.app.set_callback(50, flash_stop)
                self.app.repaint()

            from_column.set_hint(from_card)
            self.app.set_callback(50, flash_to)
            self.app.repaint()


    def __init__(self, app):
        self.app          = app
        self.bg_image     = app.loader.load_image("bg.png")
        self.card_sprites = [ app.loader.load_image("card-%02x.png" % (x+1)) for x in range(13)]
        self.card_empty   = app.loader.load_image("card-empty.png")
        self.card_down    = app.loader.load_image("card-down.png")
        self.card_hint    = app.loader.load_image("card-hint.png")
        self.font         = app.loader.load_ttf("liberation-sans.ttf", 15)

        # game structures
        self.columns   = [ Column(self.card_empty) for x in range(10)]
        self.dealer    = Dealer(self.card_sprites, self.card_down)
        self.done_pile = DonePile(self.card_sprites)

        # helper systems
        self.hints     = None 
        self.score_box = Game.ScoreBox(self.font)
        
        self.drag_cards       = None
        self.drag_from_column = None
        self.drag_xoffs       = 0
        self.drag_yoffs       = 0
        self.drag_xpos        = 0
        self.drag_ypos        = 0
        self.drag_gap         = 0

        self.over      = -1
        self.over_card = None
        self.over_gap  = 0

        self.run_over_card = None

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

        for i in range(0, 44):
            self.columns[i%len(self.columns)].push(self.dealer.next_card())

        self.dealer.deal(self.app.screen, self.columns)

    def mouse_move(self, xp, yp):

        self.drag_xpos = xp
        self.drag_ypos = yp

        self.over = -1
        for i in range(0, len(self.columns)):
            if self.columns[i].is_point_over(xp, yp):
                self.over = i
                break

        if self.over == -1:
            self.over_card = None
            self.run_over_card = None
        else:
            #for c in self.columns:
            #    c.set_hint(None)

            #self.run_over_card = self.columns[self.over].longest_run()
            #if len(self.columns[self.over].cards) == 0:
            #    self.columns[self.over].set_hint(True)
            #else: 
            #    self.columns[self.over].set_hint(self.run_over_card)

            self.over_gap = self.columns[self.over].card_gap
            found = self.columns[self.over].over_card(xp, yp)
            if found:
                self.over_card  = found[0]
                self.over_xoffs = found[1]
                self.over_yoffs = found[2]

        self.app.repaint()

    def mouse_down(self):
        over_column = self.columns[self.over]
        if self.over_card and over_column.can_card_be_picked_up(self.over_card):
            self.drag_from_column = over_column
            self.drag_cards = over_column.pop(self.over_card)
            self.drag_xoffs = self.over_xoffs
            self.drag_yoffs = self.over_yoffs
            self.drag_gap   = self.over_gap
            self.app.repaint()
            return

        if self.dealer.is_mouse_over(self.app.screen, self.drag_xpos, self.drag_ypos):
            self.dealer.deal(self.app.screen, self.columns)
            self.app.repaint()


    def mouse_up(self):
        if self.drag_cards:
            try_column = self.columns[self.over]
            if try_column.can_card_be_pushed(self.drag_cards[0]):
                self.hints = None

                try_column.push(self.drag_cards)
                try_column.adjust_gap(self.app.screen)
                self.drag_from_column.turn_over_top_card()
                self.drag_from_column.adjust_gap(self.app.screen)
                self.score_box.inc_moves()

                column_run = try_column.ends_in_run()
                if column_run:
                    self.done_pile.deposite_run()
                    try_column.pop(column_run)
                    try_column.turn_over_top_card()
                    try_column.adjust_gap(self.app.screen)
                    self.score_box.inc_score()

            else:
                self.drag_from_column.push(self.drag_cards)

            self.drag_cards = None
            self.app.repaint()

    def key_down(self, key):
        if key == pg.K_m:
            for c in self.columns:
                c.set_hint(None)

            if self.hints:
                self.hints.flash_next()
            else:
                self.hints = Game.Hinter(
                        self.app,
                        self.columns)


    def draw(self):
        self._draw_bg()

        self.score_box.draw(self.app.screen)

        self.dealer.draw(self.app.screen)
        self.done_pile.draw(self.app.screen)

        for c in self.columns:
            c.draw(self.app.screen)

        if self.drag_cards:
            draw_x = self.drag_xpos + self.drag_xoffs
            draw_y = self.drag_ypos + self.drag_yoffs
            for card in self.drag_cards:
                card.draw(self.app.screen, draw_x, draw_y)
                draw_y += self.drag_gap

        
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

