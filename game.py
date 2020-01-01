import numpy as np


class Board:
    def __init__(self, size=(6, 7)):
        self.size = size
        self.board = Board.create_board(size)
        self.next_location = np.array([0]*size[1])
        self.move_count = 0
        self.game_over = False

    def __str__(self):
        return np.flipud(self.board).__str__()

    def __repr__(self):
        return np.flipud(self.board).__repr__()

    @staticmethod
    def create_board(size):
        if len(size) != 2:
            raise ValueError('Invalid size; board size must contain exactly 2 dimensions.')

        valid_dims = 0
        for dim in size:
            if dim == 0:
                raise ValueError('Invalid size; board size cannot contain 0.')
            elif dim >= 4:
                valid_dims += 1

        if not valid_dims:
            raise ValueError('Invalid size; board size must contain at least one value greater than 4.')

        return np.zeros(size)

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
        row = self.next_location[column]-1

        # Get the horizontal and vertical search spaces
        horizontal = self.board[row, max(0, column-3):min(self.size[1], column+4)]
        vertical = self.board[max(0, row-3):min(self.size[0], row+1), column]

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

            for i in range(size-3):
                # noinspection PyTypeChecker
                if all(array[i:i+4] == token):
                    self.game_over = True
                    return True

        return False


def main():
    board = Board(size=(4, 4))
    switch = {1: 2, 2: 1}
    token = 1
    winner = None
    print(board)

    while not board.game_over:
        column = None
        while not board.is_valid_move(column):
            column = int(input())

        board.place_token(column, token)
        print(board)
        if board.is_winning_move(column, token):
            winner = token
            break
        token = switch[token]

    if not winner:
        print('There were no winners.')

    else:
        print('Player {} is the winner!'.format(winner))


if __name__ == '__main__':
    main()
