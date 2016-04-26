from game.constants import *
from game.card import Card

class Column:
    def __init__(self, empty_card): 
        self.empty_card = empty_card
        self.cards      = []
        self.pos        = 0
        self.card_gap   = PADDING

    def _card_down_count(self):
        down_count = 0
        for c in self.cards:
            if not c.face_down:
                break
            down_count += 1
        return down_count

    def set_pos(self, pos):
        self.pos = pos

    def push(self, cards):
        #print("type=%s"%type(cards))
        if type(cards) is Card:
            self.cards.append(cards)
        elif type(cards) is list: 
            self.cards.extend(cards)
        else:
            raise BaseException("Column#push: Unknown type '%s'"%type(cards))

    def pop(self, card):
        pos = 0
        for c in self.cards:
            if c == card:
                break
            pos += 1

        ret = self.cards[pos:len(self.cards)]
        self.cards = self.cards[0:pos]
        return ret

    def adjust_gap(self, screen):

        if len(self.cards) > 0:
            down_count = self._card_down_count()

            height  = screen.get_height()
            height -= PADDING     * 3 # margins
            height -= CARD_HEIGHT * 2
            height -= down_count  * PADDING

            gap = int(height / (len(self.cards) - down_count))
            if gap > CARD_MAX_GAP:
                gap = CARD_MAX_GAP

            self.card_gap = gap

    def ends_in_run(self):
        if len(self.cards) < CARD_COUNT:
            return None

        for i in range(0, CARD_COUNT):
            if self.cards[-i-1].number != i:
                return None

        return self.cards[-CARD_COUNT]

    def over_card(self, cursor_xpos, cursor_ypos):

        if len(self.cards) == 0:
            return None 

        ypos      = PADDING 
        last_card = self.cards[0]
        last_ypos = ypos

        for card in self.cards:
            if ypos > cursor_ypos:
                return (last_card, self.pos-cursor_xpos, last_ypos-cursor_ypos)

            last_card = card
            last_ypos = ypos
            if card.face_down:
                ypos += PADDING
            else:
                ypos += self.card_gap
        
        return (self.cards[-1], self.pos-cursor_xpos, last_ypos-cursor_ypos)

    def can_card_be_pushed(self, card):
        return len(self.cards) == 0 or card.can_go_on(self.cards[-1])

    def is_point_over(self, xp, yp):
        if xp < self.pos or xp >= (self.pos+CARD_WIDTH):
            return False

        down_count = self._card_down_count()
        max_y  = PADDING
        max_y += PADDING * down_count
        max_y += self.card_gap * (len(self.cards)-down_count)
        max_y += CARD_HEIGHT
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
                if c.face_down:
                    ypos += PADDING
                else:
                    ypos += self.card_gap



