from game.constants import *
from game.dealer import Dealer
from game.card import Card
from game.column import Column
from game.done_pile import DonePile

class Undo:

    class UndoSlide:

        # return card -> to_column -> from_column

        def __init__(self, game, args):
            self.game = game

            self.from_column    = args[0]
            self.from_card_down = args[1]
            self.to_column      = args[2]
            
            self.slide_cards = self.to_column.pop(args[3])
            self.game.set_hover_cards(self.slide_cards)

            self.slide_xpos = self.to_column.pos
            self.slide_ypos = self.to_column.last_card_ypos()
            
            target_xpos = self.from_column.pos
            target_ypos = self.from_column.last_card_ypos()

            self.slide_count = 3
            self.slide_xdelta = (target_xpos-self.slide_xpos)/(self.slide_count)
            self.slide_ydelta = (target_ypos-self.slide_ypos)/(self.slide_count)

        def has_ended(self):
            return self.slide_count == 0

        def tick(self):
            if self.slide_count == 0:
                return

            self.slide_count -= 1
            self.game.app.repaint()

            if self.slide_count == 0:
                if self.from_card_down:
                    last_card = self.from_column.last_card()
                    if last_card:
                        last_card.face_down = True

                self.from_column.push(self.slide_cards)
                self.from_column.adjust_gap(self.game.app.screen)
                self.to_column.adjust_gap(self.game.app.screen)
                self.game.set_hover_cards(None)
                return

            self.slide_xpos += self.slide_xdelta
            self.slide_ypos += self.slide_ydelta
            
            self.game.set_hover_pos(self.slide_xpos, self.slide_ypos)

    def __init__(self, game):
        self.game = game
        self.move_stack = []

    def flush(self):
        self.move_stack = []

    def push(self, from_column, from_card_down, to_column, card):
        self.move_stack.append((from_column, from_card_down, to_column, card))

    def pop(self):
        if len(self.move_stack) == 0:
            return

        self.game.score_box.inc_moves()
        self.game.automator.push_animator(Undo.UndoSlide(self.game, self.move_stack[-1])) 
        self.move_stack = self.move_stack[0:(len(self.move_stack)-1)]



