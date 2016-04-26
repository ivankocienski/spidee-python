
from game.constants import *

class DonePile:
    def __init__(self, card_sprites):
        self.done_count = 0;
        self.card_sprites = card_sprites
        pass

    def deposite_run(self):
        self.done_count += 1

    def draw(self, screen):
        xpos = PADDING
        ypos = screen.get_height() - PADDING - CARD_HEIGHT
        for i in range(self.done_count):
            screen.blit(
                    card_sprites[12],
                    xpos,
                    ypos)
            xpos += PADDING
