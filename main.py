import pygame
import os
import random
#import neat
import time
pygame.font.init()

pygame.init()

#dimension of the screen
WIN_WIDTH = 500
WIN_HEIGHT = 800

#get the images
BIRD_IMGS = [
    
    pygame.image.load("imgs/bird1.png"),
    pygame.image.load("imgs/bird2.png"),
    pygame.image.load("imgs/bird3.png")
]
PIPE_IMG = pygame.image.load("imgs/pipe.png")
BASE_IMG = pygame.image.load("imgs/base.png")
BG_IMG = pygame.image.load("imgs/bg.png")

#BIRD_IMGS[0] = pygame.transform.scale(BIRD_IMGS[0], (68, 68))
#BIRD_IMGS[1] = pygame.transform.scale(BIRD_IMGS[1], (68, 68))
#BIRD_IMGS[2] = pygame.transform.scale(BIRD_IMGS[2], (68, 68))
#BASE_IMG = pygame.transform.scale(BASE_IMG, (500, 70))
#BG_IMG = pygame.transform.scale(BG_IMG, (500, 800))


BIRD_IMGS[0] = pygame.transform.scale2x(BIRD_IMGS[0])
BIRD_IMGS[1] = pygame.transform.scale2x(BIRD_IMGS[1])
BIRD_IMGS[2] = pygame.transform.scale2x(BIRD_IMGS[2])

PIPE_IMG = pygame.transform.scale2x(PIPE_IMG)
BASE_IMG = pygame.transform.scale2x(BASE_IMG)
BG_IMG = pygame.transform.scale2x(BG_IMG)

STAT_FONT = pygame.font.SysFont("comicsans", 30)

#bird class

class Bird:
    #set bird images in bird class
    IMGS = BIRD_IMGS
    #set rotation parameters for bird
    MAX_ROTATION = 25
    ROT_VEL = 20
    #how long we're showing each bird animation
    ANIMATION_TIME = 5
     
    #bruh
    def __init__(self, x, y):
       #x and y is starting position when bird is initialized
       self.x = x
       self.y = y
       #bird starts out flat
       self.tilt = 0
       #used for physics of the bird
       self.tick_count = 0
       #self-explanatory
       self.vel = 0 
       self.height = self.y
       #which img it is currently on
       self.img_count = 0
       self.img = self.IMGS[0]

    #move
    def jump(self):
        #remember that top left corner is (0,0)
        self.vel = -10.5 
        #keep track of when we last jumped
        self.tick_count = 0
        #keep track of where we jumped from
        self.height = self.y

    def move(self):
        #frame goes by
        self.tick_count += 1

        #displacement calculation(how many pixels we move up or down)
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        #ensures terminal velocity
        if d >= 16:
            d = 16
        
        #if moving upwards, move up a little more
        if d < 0:
            d -=2

        self.y = self.y + d

        #tilting the bird
        if d < 0 or self.y < self.height + 50:
            #make sure bird doesn't tilt backwards
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            #downwards rotation
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        #keep track of how many times one image has shown
        self.img_count += 1
        #checks what image to show based on img_count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #bird stays in neutral wing position if tilting all the way down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #rotate bird around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        #draw onto window
        win.blit(rotated_image, new_rect.topleft)

    #used for collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100 #check back later as to why gap is defined twice
    
        self.top = 0
        self.bottom = 0
        #flips the top pipe picture
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        #if bird passed the pipe
        self.passed = False
        self.set_height()

    # randomly generates pipe length
    def set_height(self):
        self.height = random.randrange(50, 450)
        #remember we need to have top left of img
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        #pushes pipe to the left as time goes on
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird): #need to go over this method as a whole
        # creates masks for bird and top/bottom pipes
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #these two below will return None if no collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False
    
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    #for the base, remember the circular strat where there are two and it cycles
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        # when one of the bases is off the screen to the left, it 
        # gets moved back to its starting point on the right 
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
    
def draw_window(win, bird, pipes, base, score):
    #puts background
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    base.draw(win)

    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    #game loop
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass
        
        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()

main()

