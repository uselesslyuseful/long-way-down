import pygame
from pygame.locals import *
import random
import asyncio

async def main():
    pygame.init()

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    walls = [pygame.transform.scale(pygame.image.load("wall.png"), (560, 240)), pygame.transform.scale(pygame.image.load("wall3.png"), (560, 240)), pygame.transform.scale(pygame.image.load("wall3.png"), (560, 240)), pygame.transform.scale(pygame.image.load("wall4.png"), (560, 240))]
    floors = [pygame.transform.scale(pygame.image.load("floor.png"), (1280, 480)), pygame.transform.scale(pygame.image.load("floor2.png"), (1280, 480)), pygame.transform.scale(pygame.image.load("floor3.png"), (1280, 480))]

    font = pygame.font.Font(None, 32)
    heart = pygame.transform.scale(pygame.image.load("heart.png").convert_alpha(), (32, 32))

    class Doors():
        def __init__(self):
            self.target_open = False
            self.image = pygame.image.load("doors.png")
            self.scaled_image = pygame.transform.scale_by(self.image, 5)
            self.rect = Rect(560, 0, 160, 240)
            self.image_x = 0
            self.opening_frame = 0
            self.open = False
        def update(self, frame):
            if (frame - self.opening_frame) % 15 == 0:
                self.open = True
                if self.image_x < 960 and self.target_open:
                    self.image_x += 160
                elif not self.target_open and self.image_x > 0:
                    self.image_x -= 160
                elif self.image_x == 0:
                    self.open = False
        def draw(self, screen):
            screen.blit(self.scaled_image, self.rect, (self.image_x, 0, 160, 240))
        
    class Interactions:
        def __init__(self):
            roll = random.random()
            if roll <= 0.33:
                self.type = "worker"
                self.image = pygame.transform.scale_by(pygame.image.load("worker.png"), 4)
                self.image_x = 512
                self.image_y = 32
                self.length = 64
                self.rect = Rect(608, 245, 64, 96)
                self.height = 96
                self.end = False
                self.saved = False
            elif roll <= 0.67:
                self.type = "runner"
                self.image = pygame.transform.scale_by(pygame.image.load("runner.png"), 4)
                self.image_x = 384
                self.image_y = 32
                self.length = 64
                self.height = 96
                self.rect = Rect(608, 475, 64, 96)
                self.saved = False
                
                self.zombie_image = pygame.transform.scale_by(pygame.image.load("small_zombie_walk.png"), 6)
                self.zombie_image_x = 0
                self.zombie_image_y = 0
                self.zombie_length = 78
                self.zombie_height = 98
                self.zombie_rect = Rect(601, 720, 78, 96)

                self.end = False
            elif roll <= 1:
                self.type = "monster"
                self.image = pygame.transform.scale_by(pygame.image.load("big_zombie_walk.png"), 6)
                self.image_x = 0
                self.image_y = 0
                self.length = 96
                self.height = 144
                self.rect = Rect(592, 475, 96, 144)

                self.end = False
        def update(self, frame, game):
            if not self.end:
                if self.type == "worker":
                    if frame % 60 == 0:
                        self.image_x = 512
                        self.rect.move_ip(0, -5)
                    elif frame % 30 == 0:
                        self.image_x = 576
                        self.rect.move_ip(0, -5)
                    self.rect.y = max(156, self.rect.y)
                    if self.rect.centery <= 240:
                        if game.elevator.open:
                            game.transitioning = True
                            game.transition_frame = frame
                            self.end = True
                            self.saved = True
                elif self.type == "runner":
                    if frame % 15 == 0:
                        self.image_x += 64
                        if self.image_x >= 768:
                            self.image_x = 384
                        self.rect.move_ip(0, -9)
                        self.rect.y = max(156, self.rect.y)

                        self.zombie_image_x += 78
                        if self.zombie_image_x >= 468:
                            self.zombie_image_x = 0
                        self.zombie_rect.move_ip(0, -12)
                        self.zombie_rect.y = max(156, self.zombie_rect.y)

                    if self.rect.centery <= 240:
                        if game.elevator.open:
                            self.rect.y = 4000
                            self.saved = True
                    if self.zombie_rect.centery <= 240:
                        if game.elevator.open:
                            game.transitioning = True
                            game.transition_frame = frame
                            self.end = True
                            game.lose_life(frame)
                elif self.type == "monster":
                    if frame % 10 == 0:
                        self.image_x += self.length
                        if self.image_x >= self.image.get_width():
                            self.image_x = 0
                        self.rect.move_ip(0, -12)
                    self.rect.y = max(120, self.rect.y)
                    if self.rect.centery <= 240:
                        if game.elevator.open:
                            game.transitioning = True
                            game.transition_frame = frame
                            self.end = True
                            game.lose_life(frame)
                        else:
                            self.image = pygame.transform.scale_by(pygame.image.load("big_zombie_attack.png"), 6)
                            self.length = 162
                            self.image_x = self.image_x // 162 * 162
                            self.rect = Rect(559, self.rect.y, 162, 144)


                
        def draw(self, screen):
            if self.type == "worker" or self.type == "monster":
                screen.blit(self.image, self.rect, (self.image_x, self.image_y, self.length, self.height))
            elif self.type == "runner":
                screen.blit(self.image, self.rect, (self.image_x, self.image_y, self.length, self.height))
                screen.blit(self.zombie_image, self.zombie_rect, (self.zombie_image_x, self.zombie_image_y, self.zombie_length, self.zombie_height))

    class Game:
        def __init__(self):
            self.state = "travelling"
            self.state_frame = 0
            self.floor = 0
            self.interaction = None
            self.elevator = Doors()

            self.transitioning = False
            self.transition_frame = 0
            self.fade_alpha = 0
            self.floor_duration = 900
            self.fade_duration = 60 
            self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fade_surface.fill((0, 0, 0))

            self.max_lives = 3
            self.lives = self.max_lives
        
        def next_floor(self, frame):
            self.floor += 1
            self.state = "floor"
            self.state_frame = frame

            self.interaction = Interactions()

            self.wall = random.choice(walls)
            self.floor_image = random.choice(floors)
            self.elevator = Doors()
        def update(self, frame):
            self.elevator.update(frame)
            self.interaction.update(frame, self)

            if (not self.transitioning and
                frame - self.state_frame >= self.floor_duration):

                self.transitioning = True
                self.transition_frame = frame

                if self.interaction.type in ("worker", "runner") and not self.interaction.saved:
                    self.lose_life(frame)

            if self.transitioning:
                elapsed = frame - self.transition_frame

                if elapsed < self.fade_duration // 2:
                    self.fade_alpha = int(
                        255 * elapsed / (self.fade_duration // 2)
                    )

                elif elapsed == self.fade_duration // 2:
                    self.next_floor(frame)
                    self.fade_alpha = 255

                elif elapsed < self.fade_duration:
                    progress = elapsed - self.fade_duration // 2
                    self.fade_alpha = int(
                        255 * (1 - progress / (self.fade_duration // 2))
                    )
                else:
                    self.transitioning = False
                    self.fade_alpha = 0
        def lose_life(self, frame):
            self.lives -= 1

            if self.lives <= 0:
                self.reset(frame)
        def draw(self, screen):
            screen.blit(self.floor_image, (0,240))
            screen.blit(self.wall, (0,0))
            screen.blit(self.wall, (720,0))
            self.elevator.draw(screen)
            self.interaction.draw(screen)

            if self.fade_alpha > 0:
                self.fade_surface.set_alpha(self.fade_alpha)
                screen.blit(self.fade_surface, (0,0))

            floor_text = font.render(f"Floor: {self.floor}", True, (0, 0, 0))
            floor_rect = floor_text.get_rect(topleft=(12,9))
            screen.blit(floor_text, floor_rect)

            for i in range(self.lives):
                screen.blit(
                    heart,
                    (SCREEN_WIDTH - 44 - i * 40, 10)
                )
        def reset(self, frame):
            self.floor = 0
            self.lives = self.max_lives

            self.transitioning = False
            self.fade_alpha = 0

            self.next_floor(frame)

    clock = pygame.time.Clock()
    running = True
    frame = 0
    game = Game()
    game.next_floor(frame)
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    game.elevator.target_open = not game.elevator.target_open
                    game.elevator.opening_frame = frame
        
        game.update(frame)
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)
        frame += 1

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())