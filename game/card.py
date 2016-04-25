from game.constants import *

class Card:
    def __init__(self, number, suit, card_sprites, card_down):
        self.number    = number
        self.suit      = suit
        self.sprite    = card_sprites[number]
        self.card_down = card_down
        self.face_down = True

    def draw(self, screen, xpos, ypos):
        if self.face_down:
            screen.blit(
                    self.card_down,
                    (xpos, ypos))
        else:
            screen.blit(
                    self.sprite,
                    (xpos, ypos))

    def can_go_on(self, lower_card):
        print("self=%s"%self)
        print("lower_card=%s"%lower_card)

        if self.suit != lower_card.suit:
            return False

        if self.number != lower_card.number-1:
            return False

        return True 

    def __str__(self):
        return "%s of %s"%(CARD_NAMES[self.number], SUIT_NAMES[self.suit])


