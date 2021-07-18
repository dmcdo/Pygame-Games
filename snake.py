import sys
import time
import math
import queue
import random
import pygame

COLOR_SNAKE = 234, 198, 69
COLOR_BACKGROUND = 47, 49, 54
COLOR_PELLET = 255, 0, 0
DIRMAP = {
    pygame.K_w:     ("UP", "DOWN"),
    pygame.K_UP:    ("UP", "DOWN"),
    pygame.K_s:     ("DOWN", "UP"),
    pygame.K_DOWN:  ("DOWN", "UP"),
    pygame.K_a:     ("LEFT", "RIGHT"),
    pygame.K_LEFT:  ("LEFT", "RIGHT"),
    pygame.K_d:     ("RIGHT", "LEFT"),
    pygame.K_RIGHT: ("RIGHT", "LEFT"),
}


class Tile(pygame.Rect):
    def __init__(self, left, top, width, height, type):
        super().__init__(left, top, width, height)
        self.type = type


class SnakeGame:
    def __init__(self, width, height, rows, cols, speed):
        # Init
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.speed = speed

        pygame.font.init()
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Loop gameplay until the player closes the windows
        while True:
            # Create the grid
            self.grid = [[None] * self.cols for _ in range(self.rows)]
            for y in range(self.rows):
                for x in range(self.cols):
                    height = self.height / self.rows
                    width = self.height / self.cols
                    dy = y * height
                    dx = x * width
                    self.grid[y][x] = Tile(math.ceil(dx), math.ceil(dy),
                                           math.ceil(width), math.ceil(height), "EMPTY")

            self.length = 5
            self.length_not_drawn = self.length - 1
            self.in_bounds = True

            self.dirqueue = queue.SimpleQueue()
            self.tilequeue = queue.SimpleQueue()

            # Draw on screen
            self.screen.fill(COLOR_BACKGROUND)
            self.x, self.y = 0, 0
            self.grid[0][0].type = "SNAKE"
            pygame.draw.rect(self.screen, COLOR_SNAKE, self.grid[0][0])
            self.random_pellet()
            msg_surface = self.font.render(
                "<-- Use WASD or an arrow key to move", True, (255, 255, 255))
            self.screen.blit(msg_surface, (self.width // self.rows + 2, 2))
            pygame.display.flip()

            # Wait for player to start the game
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.sysexit()
                    if event.type == pygame.KEYDOWN and event.key in DIRMAP:
                        waiting = False
                        self.direction = DIRMAP[event.key][0]
                time.sleep(self.speed)

            # Play the game
            msg_surface.fill(COLOR_BACKGROUND)
            self.screen.blit(msg_surface, (self.width // self.rows + 2, 2))
            self.event_loop()
            self.game_over()

    def event_loop(self):
        while True:
            self.handle_events()
            time_begin = time.time()

            # Erase this tile later
            self.tilequeue.put_nowait(self.grid[self.y][self.x])

            # Check if the snake wants to change direction
            if not self.dirqueue.empty():
                self.direction = self.dirqueue.get_nowait()

            self.next_xy()

            # If out of bounds, game over
            if not self.in_bounds:
                return

            next_tile = self.grid[self.y][self.x]

            if next_tile.type != "SNAKE":
                # Check if snake ate a pellet
                if next_tile.type == "PELLET":
                    self.length_not_drawn += 4
                    self.random_pellet()

                # Update the next tile to be the snake's head
                next_tile.type = "SNAKE"
                pygame.draw.rect(self.screen, COLOR_SNAKE, next_tile)

                # Grow the snake if applicable. Otherwise, move it
                if self.length_not_drawn:
                    self.length_not_drawn -= 1
                else:
                    front = self.tilequeue.get_nowait()
                    front.type = "EMPTY"
                    pygame.draw.rect(self.screen, COLOR_BACKGROUND, front)

                # Draw the changes
                pygame.display.flip()

                # Wait for next frame
                delta = time.time() - time_begin
                time.sleep(self.speed - delta if delta < self.speed else 0)
            else:
                return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sysexit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.pause()
                elif event.key in DIRMAP and DIRMAP[event.key][1] != self.direction:
                    self.dirqueue.put_nowait(DIRMAP[event.key][0])

    def pause(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sysexit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
                    if event.key in DIRMAP and DIRMAP[event.key][1] != self.direction:
                        self.dirqueue.put_nowait(DIRMAP[event.key][0])
                        return
            time.sleep(self.speed)

    def game_over(self):
        # Display game over message and wait for user to take action
        msg_surface = self.font.render(
            "You died. Press enter to start a new game.", True, (255, 255, 255))
        self.screen.blit(msg_surface, (self.width / 2 - msg_surface.get_width() / 2,
                                       self.height / 2 - msg_surface.get_height() / 2))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sysexit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return
            time.sleep(self.speed)

    # Calculate the next (x, y) position based on the current direction
    def next_xy(self):
        if self.direction == "UP":
            self.y -= 1
            if self.y < 0:
                self.in_bounds = False
        elif self.direction == "DOWN":
            self.y += 1
            if self.y >= self.rows:
                self.in_bounds = False
        elif self.direction == "LEFT":
            self.x -= 1
            if self.x < 0:
                self.in_bounds = False
        elif self.direction == "RIGHT":
            self.x += 1
            if self.x >= self.cols:
                self.in_bounds = False

    def random_pellet(self):
        pellet_placed = False
        while not pellet_placed:
            tile = self.grid[random.randint(
                0, self.rows - 1)][random.randint(0, self.cols - 1)]
            if tile.type == "EMPTY":
                tile.type = "PELLET"
                pygame.draw.rect(self.screen, COLOR_PELLET, tile)
                pellet_placed = True

    def sysexit(self):
        pygame.font.quit()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    SnakeGame(500, 500, 30, 30, 0.07)
