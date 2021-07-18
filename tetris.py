from sys import exit
from time import sleep, time
from random import randint
import pygame
from pygame.constants import RESIZABLE

# Tetramino definitions on a 4x4 grid. 1 means the tile exists.
TETRAMINO_I = (((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 1, 1), (0, 0, 0, 0)),
               ((0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 1, 1), (0, 0, 0, 0)),
               ((0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0)))
TETRAMINO_J = (((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 1, 0), (0, 0, 1, 0)),
               ((0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 0, 0), (0, 1, 0, 0)),
               ((0, 0, 0, 0), (1, 0, 0, 0), (1, 1, 1, 0), (0, 0, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0)))
TETRAMINO_L = (((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 1, 0), (1, 0, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 1, 0), (1, 1, 1, 0), (0, 0, 0, 0)),
               ((0, 0, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0)))
TETRAMINO_O = (((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 1, 0)))
TETRAMINO_S = (((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (1, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (1, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 0)))
TETRAMINO_T = (((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 1, 0), (0, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (1, 1, 1, 0), (0, 0, 0, 0)),
               ((0, 0, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 0, 0)))
TETRAMINO_Z = (((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 0, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 0)),
               ((0, 0, 0, 0), (0, 0, 0, 0), (1, 1, 0, 0), (0, 1, 1, 0)),
               ((0, 0, 0, 0), (0, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 0)))

# Array used for randomly picking tetraminos
TETRAMINOS = [(TETRAMINO_I, (0xFF, 0xFF, 0x00)), (TETRAMINO_J, (0xFF, 0x00, 0x00)),
              (TETRAMINO_L, (0xFF, 0x00, 0xFF)), (TETRAMINO_O, (0x00, 0xFF, 0x00)),
              (TETRAMINO_S, (0x00, 0xFF, 0xFF)), (TETRAMINO_T, (0x00, 0x00, 0xFF)),
              (TETRAMINO_Z, (0x01, 0x82, 0x50))]

# Constant colors
COLOR_BACKGROUND = (0x22, 0x22, 0x22)
COLOR_SHADOW = (0x44, 0x44, 0x44)
COLOR_BORDER = (0xAA, 0xAA, 0xAA)
COLOR_FLASH = (0xFF, 0xFF, 0xFF)
COLOR_PAUSE = (0x00, 0x00, 0x00)
COLOR_TEXT = (0xFF, 0xFF, 0xFF)

# Max framerate
FRAMERATE = 1 / 60

# Time to show that a line has been cleared
FLASH_TIME = 0.5

PREVIEW_OFFSET = 4
KEYDOWN_TIME_CONST = 0.036


# Definition for a tile
class TetrisTile(pygame.Rect):
    def __init__(self, left, top, width, height, empty, color):
        super().__init__(left, top, width, height)
        self.empty = empty
        self.color = color


class TetrisGame:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.rows = 22
        self.cols = 10
        self.speed = 0.7
        self.scale = 11
        self.tile_length = 15
        self.fallspeed = 1

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height), RESIZABLE)

        # Loop gameplay until the player closes the window
        # Initialize grid
        welcome = True
        while True:
            self.grid = self.grid = [
                [None] * self.cols for _ in range(self.rows)
            ]
            for y in range(self.rows):
                for x in range(self.cols):
                    dy = y * self.tile_length + self.tile_length
                    dx = x * self.tile_length + self.tile_length
                    self.grid[y][x] = TetrisTile(
                        dx, dy, self.tile_length, self.tile_length, True, COLOR_BACKGROUND
                    )

            # Create the grid for the tetris tile preview
            self.preview_grid = [[None] * 4 for _ in range(4)]
            for y in range(4):
                for x in range(4):
                    dy = y * self.tile_length
                    dx = x * self.tile_length + \
                        (self.cols + PREVIEW_OFFSET) * self.tile_length
                    self.preview_grid[y][x] = pygame.Rect(
                        dx, dy, self.tile_length, self.tile_length)

            # Draw the board
            self.draw_everything(init=True, resize=True, welcome=welcome)
            pygame.display.flip()

            # Initial wait for user to start the game
            if welcome:
                welcome = False
                new_game = False
                while not new_game:
                    frame_time = time()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.sysexit()
                        elif event.type == pygame.WINDOWRESIZED:
                            self.draw_everything(resize=True, welcome=True, init=True)
                            pygame.display.flip()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            new_game = True
                    delta = time() - frame_time
                    if delta < FRAMERATE:
                        sleep(FRAMERATE - delta)
                self.draw_everything(init=True)

            # Start the game
            self.eventloop()
            
            self.draw_everything(gameover=True)
            pygame.display.flip()

            new_game = False
            while not new_game:
                frame_time = time()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.sysexit()
                    elif event.type == pygame.WINDOWRESIZED:
                        self.draw_everything(resize=True, gameover=True)
                        pygame.display.flip()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        new_game = True
                delta = time() - frame_time
                if delta < FRAMERATE:
                    sleep(FRAMERATE - delta)

    # Main event loop. Will block until the game ends.
    def eventloop(self):
        self.next_tetramino = None
        self.cur_keydown = None
        self.keydown_time = None
        self.do_next_tetramino()
        self.draw(color=COLOR_SHADOW, y=self.lowest_y())
        self.draw(next=True)
        self.draw()
        pygame.display.flip()

        gravity_time = time()
        while True:
            frame_time = time()
            self.handle_events()

            if time() - gravity_time >= self.fallspeed:
                if self.can_be_placed(y=self.y + 1):
                    self.draw(color=COLOR_BACKGROUND, y=self.lowest_y())
                    self.draw(color=COLOR_BACKGROUND)
                    self.y += 1
                    self.draw(color=COLOR_SHADOW, y=self.lowest_y())
                    self.draw()
                    pygame.display.flip()
                else:
                    self.place()
                    self.do_next_tetramino()
                    self.draw(next=True)
                    self.draw(color=COLOR_SHADOW, y=self.lowest_y())
                    self.draw()
                    pygame.display.flip()
                    if not self.can_be_placed():
                        return
                gravity_time = time()

            delta = time() - frame_time
            if delta < FRAMERATE:
                sleep(FRAMERATE - delta)

    # Handle game and window controls
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sysexit()
            elif event.type == pygame.WINDOWRESIZED:
                self.draw_everything(resize=True)
            elif event.type == pygame.KEYUP:
                self.cur_keydown = None
                self.keydown_time = None
            elif event.type == pygame.KEYDOWN:
                self.cur_keydown = event.key
                self.keydown_time = time()
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    self.move(event.key)
                if event.key == pygame.K_SPACE:
                    self.autoplace()
                if event.key == pygame.K_RETURN:
                    self.pause()

        if self.cur_keydown == pygame.K_DOWN and self.keydown_time and time() - self.keydown_time >= KEYDOWN_TIME_CONST:
            self.keydown_time = time()
            if self.cur_keydown == pygame.K_DOWN:
                self.move(self.cur_keydown)

    def pause(self):
        self.draw_everything(paused=True)
        pygame.display.flip()

        while True:
            frame_time = time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sysexit()
                elif event.type == pygame.WINDOWRESIZED:
                    self.draw_everything(resize=True, paused=True)
                    pygame.display.flip()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.draw_everything()
                    pygame.display.flip()
                    return
            delta = time() - frame_time
            if delta < FRAMERATE:
                sleep(FRAMERATE - delta)

    # Move the current tetramino in a given direction based on user input

    def move(self, direction):
        newx = self.x
        newy = self.y
        newr = self.r
        if direction == pygame.K_DOWN:
            newy += 1
        elif direction == pygame.K_UP:
            newr = (self.r + 1) % 4
        elif direction == pygame.K_LEFT:
            newx -= 1
        elif direction == pygame.K_RIGHT:
            newx += 1

        if self.can_be_placed(x=newx, y=newy, r=newr):
            self.draw(color=COLOR_BACKGROUND, y=self.lowest_y())
            self.draw(color=COLOR_BACKGROUND)
            self.x, self.y, self.r = newx, newy, newr
            self.draw(color=COLOR_SHADOW, y=self.lowest_y())
            self.draw()
            pygame.display.flip()

    # Draw the current tetramino
    # kwargs modify x, y, r drawn
    def draw(self, **kwargs):
        if 'next' in kwargs and kwargs['next']:
            dy = 2
            dx = 0
            for row in self.next_tetramino[0][2:]:
                for i in row:
                    if i:
                        pygame.draw.rect(
                            self.screen, self.next_color, self.preview_grid[dy][dx])
                    else:
                        pygame.draw.rect(
                            self.screen, COLOR_BACKGROUND, self.preview_grid[dy][dx])
                    dx += 1
                dy += 1
                dx = 0

        elif not None in kwargs.values():
            dy = self.y if 'y' not in kwargs else kwargs['y']
            dx = self.x if 'x' not in kwargs else kwargs['x']
            color = self.color if 'color' not in kwargs else kwargs['color']
            for row in self.tetramino[self.r if 'r' not in kwargs else kwargs['r']]:
                for i in row:
                    if i:
                        pygame.draw.rect(self.screen, color, self.grid[dy][dx])
                    dx += 1
                dy += 1
                dx = self.x if 'x' not in kwargs else kwargs['x']

    # Place the current tetramino
    def place(self):
        dy = self.y
        dx = self.x
        for row in self.tetramino[self.r]:
            for i in row:
                if i:
                    self.grid[dy][dx].empty = False
                    self.grid[dy][dx].color = self.color
                dx += 1
            dy += 1
            dx = self.x
        self.lineclear()

    # Place the current tetramino immediately (pressing spacebar)
    def autoplace(self):
        self.draw(color=COLOR_BACKGROUND)
        self.y = self.lowest_y()
        self.draw()
        self.place()
        self.do_next_tetramino()
        self.draw(next=True)
        self.draw(color=COLOR_SHADOW, y=self.lowest_y())
        self.draw()
        pygame.display.flip()

    # Clear filled rows
    def lineclear(self):
        to_clear = []
        not_to_clear = []
        for row in self.grid:
            if any(tile.empty for tile in row):
                not_to_clear.append(row)
            else:
                to_clear.append(row)

        # Return if nothing to do
        if len(to_clear) == 0:
            return

        # Do a flash "animation"
        for row in to_clear:
            pygame.draw.rect(self.screen, COLOR_FLASH, pygame.Rect(
                row[0].left, row[0].top, row[-1].left +
                self.tile_length - row[0].left, self.tile_length
            ))
        pygame.display.flip()
        sleep(FLASH_TIME / 3)
        for row in to_clear:
            for tile in row:
                pygame.draw.rect(self.screen, tile.color, tile)
        pygame.display.flip()
        sleep(FLASH_TIME / 3)
        for row in to_clear:
            pygame.draw.rect(self.screen, COLOR_FLASH, pygame.Rect(
                row[0].left, row[0].top, row[-1].left +
                self.tile_length - row[0].left, self.tile_length
            ))
        pygame.display.flip()
        sleep(FLASH_TIME / 3)

        # self.grid is now a reference to to_clear
        # rows in not_to_clear will be added later
        self.grid = to_clear
        amt_rows_cleared = len(to_clear)

        # Reset rows in to_clear to blank and move them to the top
        for y in range(len(to_clear)):
            for x in range(self.cols):
                dy = y * self.tile_length + self.tile_length
                dx = x * self.tile_length + self.tile_length
                to_clear[y][x].empty = True
                to_clear[y][x].color = COLOR_BACKGROUND
                to_clear[y][x].update(
                    dx, dy, self.tile_length, self.tile_length)

        # Update the existing rows
        for i in range(len(not_to_clear)):
            for x in range(self.cols):
                dy = (i + amt_rows_cleared) * \
                    self.tile_length + self.tile_length
                dx = x * self.tile_length + self.tile_length
                not_to_clear[i][x].update(
                    dx, dy, self.tile_length, self.tile_length)
            self.grid.append(not_to_clear[i])

        # Finally, redraw everything
        for row in self.grid:
            for tile in row:
                pygame.draw.rect(self.screen, tile.color, tile)
        pygame.display.flip()

    # Select a new random tetramino
    def do_next_tetramino(self):
        if self.next_tetramino:
            self.tetramino = self.next_tetramino
            self.color = self.next_color
        else:
            i = randint(0, len(TETRAMINOS) - 1)
            self.tetramino = TETRAMINOS[i][0]
            self.color = TETRAMINOS[i][1]
        i = randint(0, len(TETRAMINOS) - 1)
        self.next_tetramino = TETRAMINOS[i][0]
        self.next_color = TETRAMINOS[i][1]
        self.x = (self.cols - 1) // 2 - 1
        self.y = 0
        self.r = 0
        if self.fallspeed > 0.1:
            self.fallspeed -= 0.005
        elif self.fallspeed > 0.05:
            self.fallspeed -= 0.0001

    # Calculate the lowest (greatest) possible y value for the current tetramino
    def lowest_y(self):
        dy = self.y + 1
        while self.can_be_placed(y=dy):
            dy += 1
        dy -= 1
        return dy

    # Return True/False if the current tetramino can/can't be place in its current position
    # Modify x, y, or the rotation depending on kwargs
    def can_be_placed(self, **kwargs):
        dy = self.y if not 'y' in kwargs else kwargs['y']
        dx = self.x if not 'x' in kwargs else kwargs['x']
        dr = self.r if not 'r' in kwargs else kwargs['r']
        for row in self.tetramino[dr]:
            for i in row:
                if i:
                    if (dy not in range(0, self.rows) or dx not in range(0, self.cols)) or not self.grid[dy][dx].empty:
                        return False
                dx += 1
            dy += 1
            dx = self.x if not 'x' in kwargs else kwargs['x']
        return True

    def draw_everything(self, **kwargs):
        if kwargs.get('resize'):
            width, height = self.screen.get_size()
            t_h = height // (self.rows + 2)
            t_w = width // (self.cols + PREVIEW_OFFSET + 6)
            new_tile_length = min(t_h, t_w)

            if new_tile_length != self.tile_length:
                self.tile_length = new_tile_length
                for y in range(self.rows):
                    for x in range(self.cols):
                        dy = y * self.tile_length + self.tile_length
                        dx = x * self.tile_length + self.tile_length
                        self.grid[y][x].update(
                            dx, dy, self.tile_length, self.tile_length
                        )
                for y in range(4):
                    for x in range(4):
                        dy = y * self.tile_length
                        dx = x * self.tile_length + \
                            (self.cols + PREVIEW_OFFSET) * self.tile_length
                        self.preview_grid[y][x].update(
                            dx, dy, self.tile_length, self.tile_length
                        )

        self.screen.fill(COLOR_BACKGROUND)
        border = pygame.Rect(0, 0,
                             self.tile_length * (self.cols + 2),
                             self.tile_length * (self.rows + 2))
        pygame.draw.rect(self.screen, COLOR_BORDER, border)

        if kwargs.get('paused'):
            curtain = pygame.Rect(
                self.tile_length,
                self.tile_length,
                self.cols * self.tile_length,
                self.rows * self.tile_length
            )
            pygame.draw.rect(self.screen, COLOR_PAUSE, curtain)

            font1 = pygame.font.SysFont(
                pygame.font.get_default_font(),
                self.tile_length * 2
            )
            font2 = pygame.font.SysFont(
                pygame.font.get_default_font(),
                int(self.tile_length * 1.5)
            )
            s1 = font1.render("PAUSED", True, COLOR_TEXT)
            s2 = font2.render("PRESS ENTER", True, COLOR_TEXT)
            s3 = font2.render("TO UNPAUSE", True, COLOR_TEXT)
            self.screen.blit(s1, (
                (self.tile_length * (self.cols // 2) + self.tile_length) -
                s1.get_size()[0] // 2,
                (self.tile_length * (self.rows // 2)) - + s1.get_size()[1]
            ))
            self.screen.blit(s2, (
                (self.tile_length * (self.cols // 2) + self.tile_length)
                - s2.get_size()[0] // 2,
                (self.tile_length * (self.rows // 2)) + s2.get_size()[1] // 2
            ))
            self.screen.blit(s3, (
                (self.tile_length * (self.cols // 2) + self.tile_length)
                - s3.get_size()[0] // 2,
                (self.tile_length * (self.rows // 2)) +
                s2.get_size()[1] // 2 + s3.get_size()[1]
            ))
        else:
            for row in self.grid:
                for tile in row:
                    pygame.draw.rect(self.screen, tile.color, tile)
            if not kwargs.get('init'):
                self.draw(color=COLOR_SHADOW, y=self.lowest_y())
                self.draw()
                self.draw(next=True)
            if kwargs.get('gameover') or kwargs.get('welcome'):
                font1 = pygame.font.SysFont(
                    pygame.font.get_default_font(),
                    self.tile_length * 2
                )
                font2 = pygame.font.SysFont(
                    pygame.font.get_default_font(),
                    int(self.tile_length * 1.3)
                )
                s1 = font1.render(
                    "GAME OVER" if kwargs.get('gameover') else "WELCOME",
                    True,
                    COLOR_TEXT
                )
                s2 = font2.render("PRESS ENTER TO", True, COLOR_TEXT)
                s3 = font2.render("START A NEW GAME", True, COLOR_TEXT)

                text_begin = (self.tile_length * (self.rows // 2)
                              ) - + s1.get_size()[1]
                text_end = (self.tile_length * (self.rows // 2)) + \
                    s2.get_size()[1] // 2 + s3.get_size()[1]

                background = pygame.Rect(
                    self.tile_length,
                    text_begin - self.tile_length,
                    self.cols * self.tile_length,
                    (text_end + s3.get_size()[1] + self.tile_length) -
                    (text_begin - self.tile_length)
                )

                pygame.draw.rect(self.screen, COLOR_PAUSE, background)
                self.screen.blit(s1, (
                    (self.tile_length * (self.cols // 2) + self.tile_length) -
                    s1.get_size()[0] // 2,
                    text_begin
                ))
                self.screen.blit(s2, (
                    (self.tile_length * (self.cols // 2) + self.tile_length)
                    - s2.get_size()[0] // 2,
                    (self.tile_length * (self.rows // 2)) +
                    s2.get_size()[1] // 2
                ))
                self.screen.blit(s3, (
                    (self.tile_length * (self.cols // 2) + self.tile_length)
                    - s3.get_size()[0] // 2,
                    text_end
                ))

        font = pygame.font.SysFont(
            pygame.font.get_default_font(), int(self.tile_length * 1.5))
        text_next = font.render("NEXT", True, COLOR_TEXT)
        self.screen.blit(text_next,
                         (self.tile_length * (self.cols + PREVIEW_OFFSET), self.tile_length // 2))

    def sysexit(self):
        pygame.quit()
        exit()


if __name__ == "__main__":
    TetrisGame()
