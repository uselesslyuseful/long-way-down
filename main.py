import pygame
from pygame.locals import *
import random

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Doors():
    def __init__(self):
        self.open = False
        self.image = pygame.image.load("doors.png")
        self.scaled_image = pygame.transform.scale_by(self.image, 5)
        self.rect = Rect(560, 0, 160, 240)
        self.image_x = 0
        self.opening = False
        self.opening_frame = 0
    def update(self, frame):
        if (frame - self.opening_frame) % 15 == 0:
            if self.image_x < 960 and self.opening:
                self.image_x += 160
            elif self.image_x == 960 and (frame - self.opening_frame) % 30 == 0:
                self.opening = False
            elif not self.opening and self.image_x > 0:
                self.image_x -= 160
        if self.image_x == 0:
            self.open = False
    def draw(self, screen):
        screen.blit(self.scaled_image, self.rect, (self.image_x, 0, 160, 240))
    
class Interactions:
    def __init__(self):
        roll = random.random()
        if roll <= 0.20:
            self.type = "worker"
        elif roll <= 0.40:
            self.type = "runner"
        elif roll <= 0.60:
            self.type = "mimic"
        elif roll <= 0.8:
            self.type = "monster"
        else:
            self.type = "package"

clock = pygame.time.Clock()
running = True
elevator = Doors()
wall = pygame.transform.scale(pygame.image.load("wall.png"), (560, 240))
floor = pygame.transform.scale(pygame.image.load("floor.png"), (1280, 480))
frame = 0
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                elevator.opening = True
                elevator.opening_frame = frame
                elevator.open = True

    screen.blit(wall, (0,0))
    screen.blit(wall, (720,0))
    screen.blit(floor, (0, 240))

    elevator.update(frame)    
    elevator.draw(screen)

    pygame.display.flip()
    clock.tick(60)
    frame += 1

pygame.quit()