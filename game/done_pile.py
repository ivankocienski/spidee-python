
from game.constants import *

class DonePile:
    def __init__(self, card_sprites):
        self.done_count   = 0
        self.card_sprites = card_sprites
        self.hover_card   = None

    def set_hover_card(self, card):
        self.hover_card = card

    def is_full(self):
        return self.done_count == 8

    def deposite_run(self):
        self.done_count += 1
        self.hover_card  = None

    def target_xpos(self):
        return PADDING + self.done_count*PADDING

    def target_ypos(self, screen):
        return screen.get_height() - PADDING - CARD_HEIGHT

    def draw(self, screen):
        xpos = PADDING
        ypos = screen.get_height() - PADDING - CARD_HEIGHT
        for i in range(self.done_count):
            screen.blit(
                    self.card_sprites[CARD_MAX],
                    (xpos, ypos))
            xpos += PADDING

        if self.hover_card:
            self.hover_card.draw(screen, xpos, ypos)
