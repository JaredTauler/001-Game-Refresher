# Author    : Jared Tauler
# Date      : 8/31/21
# Class     : PM
# Year      : Sr
# Assignment: 001 - Game Refresher

# Imports
import random
import pygame as pg
import pygame.sprite
import pygame.font
from pygame.locals import (
    RLEACCEL,
    K_w,
    K_s,
    K_a,
    K_d,
    K_SPACE,
    K_DOWN,
    MOUSEBUTTONDOWN,
    KEYDOWN,
    KEYUP,
    QUIT
)


# Player class
class goodsquare(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.KeyState = {"order": []}

        self.surf = pg.Surface((20, 20))
        self.rect = self.surf.get_rect()
        self.rect.center = screen.get_rect().center

        pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())
        self.frame = {"x": 0, "y": 0}
        self.velocity = {"x": 0, "y": 0}
        self.LastDir = {"x": 0, "y": 0}

        self.dead = False
        self.deathcenter = None

    def InputHandle(self, event):
        # Keys
        if list(event.__dict__)[0] == "unicode":
            Key = event.key
            State = event.type
            # Keep track of what keys are pressed. Their order in the list is important.
            for i, j in enumerate(self.KeyState["order"]):
                if j == Key:
                    self.KeyState["order"].pop(i)

            if State == KEYDOWN:
                self.KeyState[Key] = True
                self.KeyState["order"].append(Key)

            else:
                self.KeyState[Key] = False

    def Refresh(self):
        # Just for color changing.
        def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)

        global Score
        global HiScore

        # Death loop
        if self.dead:
            try:
                # Death animation
                self.surf = pygame.transform.smoothscale(self.surf,
                                                         (self.surf.get_width() - 1, self.surf.get_height() - 1))
                self.rect = self.surf.get_rect()
                self.rect.center = self.deathcenter
                pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())
                return
            except:
                # Reset everything
                self.frame = {"x": 0, "y": 0}
                self.velocity = {"x": 0, "y": 0}
                self.LastDir = {"x": 0, "y": 0}
                Score = 0
                self.surf = pg.Surface((20, 20))
                self.rect = self.surf.get_rect()
                self.rect.center = screen.get_rect().center
                self.dead = False

        ## Movement ##
        Dir = {"x": 0, "y": 0}
        newrect = {"x": self.rect.x, "y": self.rect.y}

        for i in self.KeyState["order"]:
            if i == KEYS["left"] and self.KeyState[KEYS["left"]]:
                Dir["x"] = -1
            elif i == KEYS["right"] and self.KeyState[KEYS["right"]]:
                Dir["x"] = 1
            elif i == KEYS["up"] and self.KeyState[KEYS["up"]]:
                Dir["y"] = -1
            elif i == KEYS["down"] and self.KeyState[KEYS["down"]]:
                Dir["y"] = 1

        # Friction
        self.velocity["x"] *= .96
        self.velocity["y"] *= .96

        # Will endlessly multiply little tiny floats that make the player move when they shouldnt be.
        if round(self.velocity["x"], 1) == 0:
            self.velocity["x"] = 0
        if round(self.velocity["y"], 1) == 0:
            self.velocity["y"] = 0

        # Calculate Velocity
        self.velocity["x"] = self.velocity["x"] + (Dir["x"] / 4)
        self.velocity["y"] = self.velocity["y"] + (Dir["y"] / 4)

        # Calculate next position.
        newrect["x"] = self.rect.x + (self.velocity["x"])
        newrect["y"] = self.rect.y + (self.velocity["y"])

        # Prevent from going out of bounds
        if newrect["x"] < 0:  # If going to go out of bounds....
            newrect["x"] = 0  # Move to inbounds.
            self.velocity["x"] = 0  # Take away all velocity

        elif newrect["x"] > screen.get_width() - self.rect.width:
            newrect["x"] = screen.get_width() - self.rect.width
            self.velocity["x"] = 0

        if newrect["y"] < 0:
            newrect["y"] = 0
            self.velocity["y"] = 0

        elif newrect["y"] > screen.get_height() - self.rect.height:
            newrect["y"] = screen.get_height() - self.rect.height
            self.velocity["y"] = 0

        # Change color based off velocity. This totally counts as animating my character.
        r = clamp(abs(25 * self.velocity["y"]), 0, 255)
        g = clamp(0, 0, 255)
        b = clamp(abs(25 * self.velocity["x"]), 0, 255)

        pg.draw.rect(self.surf, (r, g, b), self.surf.get_rect())

        # Move to calculated new position
        self.rect.x = newrect["x"]
        self.rect.y = newrect["y"]

        ### Collision ###
        if pygame.sprite.groupcollide(GroupPlayer, GroupEnemy, False, False) != {}:
            for i in GroupEnemy:  # no more enemies
                i.kill()

            self.dead = True  # Put self in death loop.
            # Make surface big for death animation.
            self.surf = pg.Surface((100, 100))
            self.deathcenter = self.rect.center

            # Write score to file if its higher.
            if HiScore < Score:
                ScoreWrite(Score)
                HiScore = Score


class badsquare(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.square = pg.Surface((10, 10))
        self.surf = self.square
        pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())
        self.rect = self.surf.get_rect()

        self.newpos = None
        self.color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        # Decide where enemy will start and go.
        axis = random.choice(["x", "y"])

        if axis == "x":
            self.rect.y = random.randrange(0, screen.get_width() - self.rect.width)
            self.dir = random.choice(["left", "right"])
            if self.dir == "right":
                self.rect.x = self.rect.width * -1
                self.newpos = ["x", 5]
            elif self.dir == "left":
                self.rect.x = screen.get_width()
                self.newpos = ["x", -5]

        elif axis == "y":
            self.rect.x = random.randrange(0, screen.get_width() - self.rect.width)
            self.dir = random.choice(["down", "up"])
            if self.dir == "down":
                self.rect.y = self.rect.height * -1
                self.newpos = ["y", 5]
            elif self.dir == "up":
                self.rect.y = screen.get_height() + self.rect.height
                self.newpos = ["y", -5]

    def Die(self):
        global Score
        Score += 1
        self.kill()

    def Refresh(self):
        # Move to next position.
        if self.newpos[0] == "x":
            self.rect.x += self.newpos[1]
        elif self.newpos[0] == "y":
            self.rect.y += self.newpos[1]

        # Check if out of bounds. Die if so
        if self.dir == "left":
            if self.rect.x < 0:
                self.Die()
        elif self.dir == "right":
            if self.rect.x > screen.get_width() - self.rect.width:
                self.Die()
        elif self.dir == "up":
            if self.rect.y < 0:
                self.Die()
        elif self.dir == "down":
            if self.rect.y > screen.get_height() - self.rect.height:
                self.Die()

        # This is definitely an animtion.
        pg.draw.rect(self.surf, self.color[0], self.surf.get_rect())
        self.color.append(self.color[0])
        self.color.pop(0)


# Read score
def ScoreRead():
    try:
        f = open("score.txt", "r")
    except:
        f = open("score.txt", "w+")

    l = f.read()

    f.close()
    try:
        return int(l)
    except:
        return 0


# update higschore
def ScoreWrite(new):
    f = open("score.txt", "w+")
    f.write(str(new))
    f.close()  # update


pg.init()
screen = pg.display.set_mode((800, 800))

clock = pg.time.Clock()
Score = 0
HiScore = ScoreRead()
KEYS = {
    "left": K_a,
    "right": K_d,
    "up": K_w,
    "down": K_s,

}

font = pygame.font.SysFont("calibri", 18)

GroupEnemy = pygame.sprite.Group()
GroupPlayer = pygame.sprite.Group()

Player = goodsquare()
GroupPlayer.add(Player)

# Main loop.
while True:
    for event in pg.event.get():
        if event.type in [KEYDOWN, KEYUP] and event.key in KEYS.values() or event.type == MOUSEBUTTONDOWN:
            Player.InputHandle(event)
        elif event.type == QUIT:
            quit()

    # Add enemies more enemies as score gets higher.
    if len(list(GroupEnemy)) < 1 + round(Score / 2) and Player.dead is False:
        if random.randrange(1, 10) == 1:
            GroupEnemy.add(badsquare())

    pg.Surface.fill(screen, (0, 0, 0))  # Backgground
    for i in list(GroupEnemy) + [Player]:
        screen.blit(i.surf, i.rect)
        i.Refresh()

    screen.blit(pygame.font.Font.render(font, "Score: " + str(Score), True, (0, 255, 0), (0, 0, 0)), (10, 10))
    screen.blit(pygame.font.Font.render(font, "High Score: " + str(HiScore), True, (0, 255, 0), (0, 0, 0)), (10, 30))

    pg.display.update()
    clock.tick(60)
