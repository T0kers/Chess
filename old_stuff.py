chess_board = [
    ['R', 'K', 'B', 'Q', 'K', 'B', 'K', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'k', 'b', 'q', 'k', 'b', 'k', 'r']
]


class Game:
    def __init__(self, players, board):
        self.players = players[0:2]
        self.board = self.init_board(board)

        self.x_to_index = {
            'a': 0,
            'b': 1,
            'c': 2,
            'd': 3,
            'e': 4,
            'f': 5,
            'g': 6,
            'h': 7
        }
        self.y_to_index = {
            '1': 7,
            '2': 6,
            '3': 5,
            '4': 4,
            '5': 3,
            '6': 2,
            '7': 1,
            '8': 0
        }

        while True:
            for index, player in enumerate(self.players):
                if index == 0:
                    self.take_turn('white')
                else:
                    self.take_turn('black')


    def init_board(self, board):



    def take_turn(self, color):
        print(self.show_board())
        while True:
            move_from = input('move from>')
            move_to = input('move to>')
            move_from = [self.x_to_index[move_from[0].lower()], self.y_to_index[move_from[1].lower()]]
            move_to = [self.x_to_index[move_to[0].lower()], self.y_to_index[move_to[1].lower()]]

            if self.move_is_legal(move_from, move_to):
                self.move_piece(move_from, move_to)
                break

    def move_is_legal(self, move_from, move_to):
        piece = self.board[move_from[1]][move_from[0]]
        return True

    def move_piece(self, move_from, move_to):
        piece_to_move = self.board[move_from[1]][move_from[0]]
        self.board[move_to[1]][move_to[0]] = piece_to_move
        self.board[move_from[1]][move_from[0]] = ''

    def show_board(self):
        board = ''
        for line_nr, line in enumerate(self.board):
            board += f'{-line_nr + 8} '
            for square in line:
                if square == '':
                    square = ' '
                board += f'|{square}'
            board += '|\n'
        board += '   A B C D E F G H '
        return board


Game(('player1', 'player2'), chess_board)
