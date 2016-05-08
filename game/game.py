
import random

import pygame as pg

from game.constants import *
from game.dealer    import Dealer
from game.card      import Card
from game.column    import Column
from game.done_pile import DonePile
from game.undo      import Undo
from game.fireworks import FireworkScreen

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
        def __init__(self, game, columns):
            self.app      = game.app
            self.game     = game
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
                self.game.snd_play(SND_NO_HINT)
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

            self.game.snd_play(SND_HINT)

            from_column.set_hint(from_card)
            self.app.set_callback(50, flash_to)
            self.app.repaint()

    class Automator:
        def __init__(self, app):
            self.animator_stack = []
            self.app = app

        def _tick(self):
            def next_tick():
                self._tick()
            
            anim = self.animator_stack[-1]
            anim.tick();

            if anim.has_ended(): 
                self.animator_stack = self.animator_stack[0:(len(self.animator_stack)-1)]
            else:
                self.app.set_callback(2, next_tick)

        def is_active(self):
            return len(self.animator_stack) > 0

        def push_animator(self, anim):
            def tick_callback():
                self._tick()

            self.animator_stack.append(anim)
            self.app.set_callback(2, tick_callback)


    def __init__(self, app):
        self.app          = app
        self.bg_image     = app.loader.load_image("bg.png")
        self.card_sprites = [ app.loader.load_image("card-%02x.png" % (x+1)) for x in range(13)]
        self.card_empty   = app.loader.load_image("card-empty.png")
        self.card_down    = app.loader.load_image("card-down.png")
        self.card_hint    = app.loader.load_image("card-hint.png")
        self.font         = app.loader.load_ttf("liberation-sans.ttf", 15)

        self.snd_capable = app.sound_capable
        self.snd_enabled = True
        self.snd_samples = [
                app.loader.load_wav("click-deal.wav"),
                app.loader.load_wav("click-pick-up.wav"),
                app.loader.load_wav("click-put-down.wav"),
                app.loader.load_wav("hint.wav"),
                app.loader.load_wav("no-hint.wav"),
                app.loader.load_wav("win.wav")
                ]

        # game structures
        self.columns   = [ Column(self.card_empty) for x in range(10)]
        self.dealer    = Dealer(self.card_sprites, self.card_down)
        self.done_pile = DonePile(self.card_sprites)
        self.undo      = Undo(self)
        self.fireworks = FireworkScreen(self)
        self.game_over = False

        # helper systems
        self.automator = Game.Automator(app)
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

        self.hover_cards = None
        self.hover_xpos  = 0
        self.hover_ypos  = 0

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

    def set_hover_cards(self, cards):
        if not cards:
            self.hover_cards = None
        elif type(cards) is Card:
            self.hover_cards = [cards]
        elif type(cards) is list: 
            self.hover_cards = cards
        else:
            raise BaseException("Game.Automator#set_hover_cards: Unknown type '%s'"%type(cards))

    def set_hover_pos(self, xpos, ypos):
        self.hover_xpos = xpos
        self.hover_ypos = ypos

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

        
        self.automator.push_animator(Dealer.DealAnimator(self))
        #self.dealer.deal(self.app.screen, self.columns)

    def mouse_move(self, xp, yp):

        self.drag_xpos = xp
        self.drag_ypos = yp

        if self.automator.is_active() or self.game_over:
            return

        self.over = -1
        for i in range(0, len(self.columns)):
            if self.columns[i].is_point_over(xp, yp):
                self.over = i
                break

        if self.over == -1:
            self.over_card = None
            self.run_over_card = None

        else:
            self.over_gap = self.columns[self.over].card_gap
            found = self.columns[self.over].over_card(xp, yp)
            if found:
                self.over_card  = found[0]
                self.over_xoffs = found[1]
                self.over_yoffs = found[2]

        self.app.repaint()

    def test_if_player_done(self):

        if self.done_pile.is_full():
            self.snd_play(SND_GAME_OVER)
            self.fireworks.reset()
            self.game_over = True
            self.app.repaint()
            
    def mouse_down(self):

        if self.automator.is_active() or self.game_over:
            return

        over_column = self.columns[self.over]
        if self.over_card and over_column.can_card_be_picked_up(self.over_card):
            self.snd_play(SND_PICK_UP)
            self.drag_from_column = over_column
            self.drag_cards = over_column.pop(self.over_card)
            self.drag_xoffs = self.over_xoffs
            self.drag_yoffs = self.over_yoffs
            self.drag_gap   = self.over_gap
            self.app.repaint()
            return

        if self.dealer.is_mouse_over(self.app.screen, self.drag_xpos, self.drag_ypos):
            self.automator.push_animator(Dealer.DealAnimator(self))
            self.undo.flush()
            #self.dealer.deal(self.app.screen, self.columns)
            #self.app.repaint()


    def mouse_up(self): 

        if self.automator.is_active() or self.game_over:
            return

        if self.drag_cards:
            try_column = self.columns[self.over]
            if try_column.can_card_be_pushed(self.drag_cards[0]):
                self.hints = None

                card_down = False
                last_card = self.drag_from_column.last_card()
                if last_card:
                    card_down = last_card.face_down

                try_column.push(self.drag_cards)
                try_column.adjust_gap(self.app.screen)
                self.drag_from_column.turn_over_top_card()
                self.drag_from_column.adjust_gap(self.app.screen)
                self.score_box.inc_moves()

                column_run = try_column.ends_in_run()
                if column_run:
                    self.undo.flush()
                    self.automator.push_animator(Column.RunAnimator(self, try_column))

                else:
                    self.snd_play(SND_PUT_DOWN)
                    self.undo.push(self.drag_from_column, card_down, try_column, self.drag_cards[0])

            else:
                self.snd_play(SND_PUT_DOWN)
                self.drag_from_column.push(self.drag_cards)

            self.drag_cards = None
            self.app.repaint()

    def key_down(self, key):

        if self.automator.is_active() or self.game_over:
            return

        #if key == pg.K_f:
        #    self.automator.push_animator(FireworkAnimator(self))

        if key == pg.K_u:
            self.undo.pop()
            return

        if key == pg.K_s:
            self.snd_play(SND_NO_HINT)

        if key == pg.K_m:
            for c in self.columns:
                c.set_hint(None)

            if self.hints:
                self.hints.flash_next()
            else:
                self.hints = Game.Hinter(
                        self,
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

        if self.hover_cards:
            ypos = self.hover_ypos
            for hc in self.hover_cards:
                hc.draw(self.app.screen, self.hover_xpos, ypos)
                ypos += PADDING

        if self.game_over:
            self.fireworks.draw()
            self.app.repaint()
        
        #self.app.draw_text(
                #self.font,
                #10, 530,
                #"#over=%d"%self.over,
                #(#255,255,255))


        #if self.over_card:
            #self.app.draw_text(
                    #self.font,
                    #10, 550,
                    #"#card=%s"%self.over_card,
                    #(#255,255,255))

            #self.app.draw_text(
                    #self.font,
                    #10, 570,
                    #"#xoffs=%d  yoffs=%d"%(self.over_xoffs, self.over_yoffs),
                    #(#255,255,255))

    def snd_play(self, sound_id):
        if self.snd_capable and self.snd_enabled:
            self.snd_samples[sound_id].play()


