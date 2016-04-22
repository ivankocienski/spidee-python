
PADDING     = 10
CARD_WIDTH  = 71
CARD_HEIGHT = 96

SUIT_CLUBS    = 0
SUIT_HEARTS   = 1
SUIT_SPADES   = 2
SUIT_DIAMONDS = 3

CARD_ACE   = 0
CARD_2     = 1
CARD_3     = 2
CARD_4     = 3
CARD_5     = 4
CARD_6     = 5
CARD_7     = 6
CARD_8     = 7
CARD_9     = 8
CARD_JOKER = 9
CARD_QUEEN = 10
CARD_KING  = 11
CARD_MAX   = 12

class Column:
    def __init__(self, empty_card): 
        self.empty_card = empty_card
        self.cards      = []
        self.pos        = 0

    def set_pos(self, pos):
        self.pos = pos

    def push(self, card):
        self.cards.append(card)


    def pop(self, count):
        pass

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

    def reset(self):
        self.runs_to_deal = 6
        self.source_pos   = 0
        self.source_deck  = [
                Card(x%CARD_MAX, SUIT_CLUBS, self.card_sprites, self.card_down)
                for x in range(0, 104)]

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

class Game:
    def __init__(self, loader):
        self.bg_image     = loader.load_image("bg.png")
        self.card_sprites = [ loader.load_image("card-%02x.png" % (x+1)) for x in range(13)]
        self.card_empty   = loader.load_image("card-empty.png")
        self.card_down    = loader.load_image("card-down.png")
        self.card_hint    = loader.load_image("card-hint.png")
        self.font         = loader.load_ttf("liberation-sans.ttf", 13)

        # game structures
        self.columns      = [ Column(self.card_empty) for x in  range(10)]
        self.dealer       = Dealer(self.card_sprites, self.card_down)

    def _draw_bg(self, screen):

        s_width   = screen.get_width()
        s_height  = screen.get_height()
        bg_width  = self.bg_image.get_width()
        bg_height = self.bg_image.get_height()

        y = 0
        while y < s_height:
            x = 0
            while x < s_width:
                screen.blit(self.bg_image, (x, y))
                x += bg_width
            y += bg_height
    
    def resize(self, screen):
        step = screen.get_width() / float(len(self.columns))
        xpos = (step - CARD_WIDTH) / 2.0
        for c in self.columns:
            c.set_pos(xpos)
            xpos += step

        self.dealer.set_pos(screen)

    def reset(self):
        self.dealer.reset()

        for i in range(0, 55):
            self.columns[i%len(self.columns)].push(self.dealer.next_card())

        for c in self.columns:
            c.turn_over_top_card()

    def draw(self, screen):
        self._draw_bg(screen)

        self.dealer.draw(screen)

        for c in self.columns:
            c.draw(screen)

        text_surface = self.font.render("Hello, world", False, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
