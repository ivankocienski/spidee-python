
import random

from game.constants import *
from game.card import Card

class Dealer:
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

    def deal(self, columns):
        if self.runs_to_deal == 0:
            return

        self.runs_to_deal -= 1

        for col in columns:
            col.push(self.next_card())
            col.turn_over_top_card()

    def reset(self):
        self.runs_to_deal = 6
        self.source_pos   = 0

        # build deck
        self.source_deck  = [
                Card(x%CARD_COUNT, SUIT_CLUBS, self.card_sprites, self.card_down)
                for x in range(0, 104)]
        
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


