from game.constants import *
from game.card import Card

class Column:
    def __init__(self, empty_card): 
        self.empty_card = empty_card
        self.cards      = []
        self.pos        = 0

    def set_pos(self, pos):
        self.pos = pos

    def push(self, cards):
        if type(cards) is Card:
            self.cards.append(cards)
        else: 
            self.cards.extend(cards)

    def pop(self, card):
        pos = 0
        for c in self.cards:
            if c == card:
                break
            pos += 1

        ret = self.cards[pos:len(self.cards)]
        self.cards = self.cards[0:pos]
        return ret

    def over_card(self, cursor_xpos, cursor_ypos):
        ypos      = PADDING 
        last_card = self.cards[0]

        for card in self.cards:
            if ypos > cursor_ypos:
                return (last_card, self.pos-cursor_xpos, ypos-cursor_ypos-PADDING)

            last_card = card
            ypos     += PADDING
        
        return (self.cards[-1], self.pos-cursor_xpos, ypos-cursor_ypos-PADDING)

    def can_card_be_pushed(self, card):
        return len(self.cards) == 0 or card.can_go_on(self.cards[-1])

    def is_point_over(self, xp, yp):
        if xp < self.pos or xp >= (self.pos+CARD_WIDTH):
            return False

        max_y = PADDING + CARD_HEIGHT + (len(self.cards)-1) * PADDING 
        if yp < PADDING or yp >= max_y:
            return False

        return True


    def turn_over_top_card(self):
        if len(self.cards) > 0:
            self.cards[-1].face_down = False

    def draw(self, screen):
        if len(self.cards) == 0:
            screen.blit(self.empty_card, (self.pos, PADDING))

        else: 
            ypos = PADDING
            for c in self.cards:
                c.draw(screen, self.pos, ypos)
                ypos += PADDING



