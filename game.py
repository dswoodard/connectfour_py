import numpy as np
import pygame
import pygame.gfxdraw
import sys
import math
import tkinter as tk


class Popup:
    def __init__(self, winner=None):
        self.window_location = pygame.display.get_wm_info()
        self.winner = winner
        self.window = self.generic()
        self.populate()
        self.window.wm_attributes("-topmost", 1)
        self.window.mainloop()

    def generic(self):
        window = tk.Tk()
        window.title('Game over. Thanks for playing!')
        window.geometry('200x75')
        window.resizable(0, 0)
        return window

    def populate(self):
        main_text = 'It was a tie!' if not self.winner else 'Player {} is the winner!'.format(self.winner)
        winner = tk.Label(self.window, text=main_text)
        winner.pack()
        replay = tk.Label(self.window, text='Play again?')
        replay.pack()

        button_frame = tk.Frame(self.window)
        yes = tk.Button(button_frame, text='Yes', command=lambda: (self.window.destroy(), main()))
        no = tk.Button(button_frame, text='Quit', command=sys.exit)
        yes.pack(side=tk.LEFT)
        no.pack(side=tk.RIGHT)
        button_frame.pack()


class Board:
    def __init__(self, size):
        # common
        self.size = size
        # functions
        self.board = self.create()
        self.next_location = np.array([0] * size[1])
        self.move_count = 0
        self.game_over = False

    def __str__(self):
        return np.flipud(self.board).__str__()

    def __repr__(self):
        return np.flipud(self.board).__repr__()

    def create(self):
        if len(self.size) != 2:
            raise ValueError('Invalid size; board size must contain exactly 2 dimensions.')

        valid_dims = 0
        for dim in self.size:
            if dim == 0:
                raise ValueError('Invalid size; board size cannot contain 0.')
            elif dim >= 4:
                valid_dims += 1

        if not valid_dims:
            raise ValueError('Invalid size; board size must contain at least one value greater than 4.')

        return np.zeros(self.size)

    def update_location(self, column):
        self.next_location[column] += 1

    def is_valid_move(self, column):
        if column is None:
            return False

        if not 0 <= column < self.size[1]:
            return False

        return self.next_location[column] < self.size[0]

    def place_token(self, column, token):
        row = self.next_location[column]
        self.update_location(column)
        self.board[row, column] = token
        self.move_count += 1
        if self.move_count >= np.product(self.size):
            self.game_over = True

    def is_winning_move(self, column, token):
        row = self.next_location[column] - 1

        # Get the horizontal and vertical search spaces
        horizontal = self.board[row, max(0, column - 3):min(self.size[1], column + 4)]
        vertical = self.board[max(0, row - 3):min(self.size[0], row + 1), column]

        # Get the diagonal search spaces:
        r_coords = np.array((range(row - 3, row + 4), range(column - 3, column + 4)))
        l_coords = np.array((range(row - 3, row + 4), range(column + 3, column - 4, -1)))

        def valid(coords):
            filter1 = np.logical_and(0 <= coords[0, :], coords[0, :] < self.size[0])
            filter2 = np.logical_and(0 <= coords[1, :], coords[1, :] < self.size[1])
            return coords[:, np.logical_and(filter1, filter2)]

        ry, rx = valid(r_coords)
        ly, lx = valid(l_coords)

        r_diagonal = self.board[ry, rx]
        l_diagonal = self.board[ly, lx]

        for array in [horizontal, vertical, r_diagonal, l_diagonal]:
            size = len(array)
            if size < 4:
                continue

            for i in range(size - 3):
                # noinspection PyTypeChecker
                if all(array[i:i + 4] == token):
                    self.game_over = True
                    return True

        return False


class Window:
    def __init__(self, board_size, window_size=(600, 400)):
        self.size = board_size
        self.token_size = min(window_size) // (max(self.size)+2)
        self.radius = int(self.token_size * 0.95 // 2)
        self.screen = self.set_screen()
        self.board = self.set_board()

    def set_screen(self):
        height = self.token_size * (self.size[0] + 2)
        width = self.token_size * (self.size[1] + 2)
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Connect Four')
        return screen

    def draw_token(self, board, x, y, color):
        blue = [0, 0, 153]
        hole = pygame.Surface((self.token_size, self.token_size))
        hole.fill(blue)
        pygame.gfxdraw.aacircle(hole, self.token_size//2, self.token_size//2, self.radius, color)
        pygame.gfxdraw.filled_circle(hole, self.token_size//2, self.token_size//2, self.radius, color)
        board.blit(hole, (x, y))

    def set_board(self):
        white = [255, 255, 255]

        board = pygame.Surface(self.screen.get_size())
        board.fill(white)

        for row in range(1, self.size[0] + 1):
            cy = int(self.token_size * row)
            for col in range(1, self.size[1] + 1):
                cx = int(self.token_size * col)
                self.draw_token(board, cx, cy, white)

        board = board.convert()
        return board

    def place_token(self, x, y, color):
        x = (x + 1) * self.token_size
        y = y * self.token_size
        self.draw_token(self.board, x, y, color)


class Column(pygame.sprite.DirtySprite):
    def __init__(self, size, token_size):
        pygame.sprite.DirtySprite.__init__(self)
        self.color = [255, 255, 255, 75]
        self.size = size
        self.token_size = token_size
        self.image = pygame.Surface((token_size, token_size * size[0]), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.y = token_size

    def update(self):
        pos = pygame.mouse.get_pos()
        x = pos[0] // self.token_size
        if x >= 0:
            self.recolor()
            self.rect.x = self.token_size * x

    def recolor(self):
        self.color[-1] = 80 + 20 * math.sin(pygame.time.get_ticks() / 3 * math.pi / 180)
        self.image.fill(self.color)


class Token(pygame.sprite.DirtySprite):
    def __init__(self, token_size):
        pygame.sprite.DirtySprite.__init__(self)
        self.token_id = 1
        self.token_color = [204, 204, 0, 250]
        self.token_size = token_size
        self.radius = int(token_size * 0.95 // 2)
        self.token_data = {1: {'next': 2, 'color': [204, 204, 0, 250]},
                           2: {'next': 1, 'color': [204, 0, 0, 250]}}
        self.image = pygame.Surface((token_size, token_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        self.redraw()
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - self.token_size // 2
        self.rect.y = pos[1] - self.token_size // 2
        self.dirty = 1

    def switch(self):
        self.token_id = self.token_data[self.token_id]['next']
        self.token_color = self.token_data[self.token_id]['color']

    def redraw(self):
        pygame.gfxdraw.aacircle(self.image,
                                self.token_size // 2,
                                self.token_size // 2,
                                self.radius,
                                self.token_color)

        pygame.gfxdraw.filled_circle(self.image,
                                     self.token_size // 2,
                                     self.token_size // 2,
                                     self.radius,
                                     self.token_color)


class Game:
    def __init__(self, game_size=(6, 7)):
        self.clock = pygame.time.Clock()
        self.size = game_size
        self.board = Board(game_size)
        self.window = Window(game_size)
        self.token_size = self.window.token_size
        self.token = Token(self.token_size)
        self.column = Column(game_size, self.token_size)

    def play(self):
        winner = None
        token = pygame.sprite.Group()
        token.add(self.token)
        column = pygame.sprite.Group()
        column.add(self.column)

        while not self.board.game_over:
            self.clock.tick(60)
            token.update()
            column.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x = pygame.mouse.get_pos()[0] // self.token_size - 1
                    if self.board.is_valid_move(x):
                        y = self.size[0] - self.board.next_location[x]
                        draw_x = (x + 1) * self.token_size
                        draw_y = y * self.token_size
                        self.window.draw_token(self.window.board, draw_x, draw_y, self.token.token_color)
                        self.board.place_token(x, self.token.token_id)
                        if self.board.is_winning_move(x, self.token.token_id):
                            winner = self.token.token_id

                        self.token.switch()

            self.window.screen.blit(self.window.board, (0, 0))
            if self.token_size <= self.column.rect.x <= self.token_size*self.size[1]:
                column.draw(self.window.screen)
            token.draw(self.window.screen)
            pygame.display.flip()

        Popup(winner)


def main():
    game = Game(game_size=(6, 7))
    game.play()


if __name__ == '__main__':
    main()
