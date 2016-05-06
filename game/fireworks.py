
import pygame as pg
from random import randint, random

class Shooter:
    def __init__(self, screen):
        self.screen = screen
        self.randomize()

    def randomize(self):
        hp = int(self.screen.get_width()/2)
        self.x = randint(hp-50, hp+50)
        self.y = self.screen.get_height()
        self.xdelta = 1 - 2.0 * random()
        self.ydelta = 6.0
        self.cutoff = randint(100, 400)

    def is_busy(self):
        return self.y > self.cutoff

    def move(self):
        self.y -= self.ydelta
        self.x += self.xdelta
        self.ydelta *= 0.990

    def draw(self):
        pg.draw.line(
                self.screen,
                (0, 0, 0),
                (self.x, self.y), 
                (self.x - (20*self.xdelta), self.y+20))

class Banger:

    COLORS = [
            (255,   0,   0),
            (255,  80,   0),
            (200, 255,   0),
            (  0, 255, 100),
            (  0, 255,   0),
            (255,   0, 255)]

    def random_color():
        return Banger.COLORS[randint(0, len(Banger.COLORS)-1)]

    def __init__(self):
        pass
    
    def randomize(self, xp, yp, xd, color):
        self.brightness = 1.0
        self.color      = color
        self.x          = xp
        self.y          = yp
        self.ydelta     = -(1 + 3.0 * random())
        self.xdelta     = xd + (1 - 2.0 * random())
        self.size       = 10

    def is_busy(self):
        return self.ydelta < 4.0

    def move(self):
        if self.brightness > 0:
            self.brightness -= 0.01
        else:
            self.brightness = 0

        if self.size > 3:
            self.size -= 0.08
        else:
            self.size = 3

        self.y += self.ydelta
        self.x += self.xdelta
        self.ydelta += 0.07

    def draw(self, screen):
        if self.is_busy():
            pg.draw.circle(
                    screen,
                    [int(c * self.brightness) for c in self.color],
                    (int(self.x), int(self.y)),
                    int(self.size))

class Firework:

    PHASE_SHOOT = 0
    PHASE_WAIT  = 1
    PHASE_BANG  = 2
    PHASE_IDLE  = 3 

    def __init__(self, screen):
        self.screen  = screen
        self.bangers = [Banger() for x in range(50)]
        self.shooter = Shooter(screen)
        self.reset()

    def reset(self):
        self.phase    = Firework.PHASE_WAIT
        self.wait_len = randint(10, 50)

    def is_busy(self):
        return self.phase != Firework.PHASE_IDLE

    def move(self):

        if self.phase == Firework.PHASE_WAIT:
            if self.wait_len > 0:
                self.wait_len -= 1
            else:
                self.shooter.randomize()
                self.phase = Firework.PHASE_SHOOT

        elif self.phase == Firework.PHASE_SHOOT: 
            if self.shooter.is_busy():
                self.shooter.move()

            else:
                self.phase = Firework.PHASE_BANG
                color = Banger.random_color()
                for b in self.bangers:
                    b.randomize(
                            self.shooter.x,
                            self.shooter.y,
                            self.shooter.xdelta,
                            color)

        elif self.phase == Firework.PHASE_BANG:
            done = True
            for b in self.bangers:
                if b.is_busy():
                    b.move()
                    done = False

            if done:
                self.phase = Firework.PHASE_IDLE

        # else self.phase == Firework.PHASE_IDLE

    def draw(self):
        if self.phase == Firework.PHASE_SHOOT:
            self.shooter.draw()

        elif self.phase == Firework.PHASE_BANG:
            for b in self.bangers:
                b.draw(self.screen)

        # else self.phase == Firework.PHASE_IDLE

class FireworkScreen:
    def __init__(self, game):
        self.app       = game.app
        self.screen    = game.app.screen
        self.fireworks = [Firework(self.screen) for x in range(10)]

    def reset(self):
        for fw in self.fireworks:
            fw.reset()

    def draw(self):
        done = True
        for fw in self.fireworks:
            if fw.is_busy():
                fw.move()
                done = False

        if done:
            for fw in self.fireworks:
                fw.reset()

        self.screen.lock()

        for fw in self.fireworks:
            fw.draw()

        self.screen.unlock()


