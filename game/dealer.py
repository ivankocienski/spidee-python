
import random

from game.constants import *
from game.card import Card


class Dealer:

    class DealAnimator:
        def __init__(self, game):
            self.game    = game
            self.dealer  = game.dealer
            self.app     = game.app
            self.columns = game.columns

            self.done = False

            self.column_num   = -1
            self.slide_count  = 0
            self.slide_card   = None
            self.slide_xpos   = 0
            self.slide_ypos   = 0
            self.slide_xdelta = 0
            self.slide_ydelta = 0
        
        def has_ended(self):
            return self.done

        def tick(self):
            if self.done:
                return

            self.app.repaint()

            if self.slide_count == 0:

                self.column_num += 1

                if self.column_num > 0:

                    # push what we were holding
                    self.columns[self.column_num-1].push(self.slide_card)

                    # stop now
                    if self.column_num > 9:
                        self.done = True
                        self.game.set_hover_cards(None)
                        self.dealer.deal()

                        for col in self.columns:
                            col.adjust_gap(self.app.screen)

                        return

                self.slide_card = self.dealer.next_card()
                self.slide_card.face_down = False
                self.game.set_hover_cards(self.slide_card)
                
                target_column = self.columns[self.column_num]
                target_xpos   = target_column.pos
                target_ypos   = target_column.last_card_ypos() - target_column.card_gap

                self.slide_count = 3
                self.slide_xpos = self.dealer.xpos
                self.slide_ypos = self.dealer.ypos

                self.slide_xdelta = (target_xpos-self.slide_xpos)/(self.slide_count+1)
                self.slide_ydelta = (target_ypos-self.slide_ypos)/(self.slide_count+1)

            self.slide_count -= 1

            self.slide_xpos += self.slide_xdelta
            self.slide_ypos += self.slide_ydelta

            self.game.set_hover_pos(self.slide_xpos, self.slide_ypos)


    def __init__(self, card_sprites, down_card):
        self.xpos = 0
        self.ypos = 0
        self.card_down    = down_card
        self.card_sprites = card_sprites

    def next_card(self):
        if self.source_pos < len(self.source_deck):
            card = self.source_deck[self.source_pos]
            self.source_pos += 1
            return card

        else:
            return None

    def is_mouse_over(self, screen, xpos, ypos):
        if self.runs_to_deal == 0:
            return

        max_y = screen.get_height() - PADDING
        min_y = max_y - CARD_HEIGHT 
        if ypos < min_y or ypos > max_y:
            return False

        max_x = screen.get_width() - PADDING
        min_x = max_x - CARD_WIDTH - (self.runs_to_deal-1)*PADDING
        if xpos < min_x or xpos > max_x:
            return False

        return True

    def deal(self): #, screen, columns):
        if self.runs_to_deal == 0:
            return

        self.runs_to_deal -= 1

        #for col in columns:
        #    col.push(self.next_card())
        #    col.turn_over_top_card()
        #    col.adjust_gap(screen)

    def reset(self):
        self.runs_to_deal = 6
        self.source_pos   = 0

        # build deck
        self.source_deck  = [
                Card(x%CARD_COUNT, SUIT_CLUBS, self.card_sprites, self.card_down)
                for x in range(0, 104)]
        

        return 

        # shuffle deck
        for i in range(0, len(self.source_deck)):
            other = random.randint(0, len(self.source_deck)-1)
            temp = self.source_deck[other]
            self.source_deck[other] = self.source_deck[i]
            self.source_deck[i] = temp

    def set_pos(self, screen):
        self.xpos = screen.get_width()  - CARD_WIDTH  - PADDING
        self.ypos = screen.get_height() - CARD_HEIGHT - PADDING

    def draw(self, screen):
        draw_x = self.xpos
        for i in range(self.runs_to_deal):
            screen.blit(
                    self.card_down,
                    (draw_x, self.ypos))
            draw_x -= PADDING


