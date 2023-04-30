import pygame
from sys import exit
import numpy as np
import piece
from config import *


class Chess:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SQUARE_LENGTH * 8 + 200, SQUARE_LENGTH * 8))
        pygame.display.set_caption('gnagna')
        self.clock = pygame.time.Clock()
        self.game_active = True

        self.board = np.array([0] * 64, dtype='i')
        self.preview_board = self.board

        self.turn = 0
        self.en_passant_square = (-1, -1)
        self.available_moves = []

        self.clicked_square = None

        self.move_history = []

        self.castle_rights_white = [True, True]
        self.castle_rights_black = [True, True]

    def play(self, fen):
        self.fen_to_board(fen)
        self.clicked_square = None

        while True:
            for event in pygame.event.get():  # Event loop
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:  # Checked always
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    square = pos[0] // SQUARE_LENGTH, 7 - pos[1] // SQUARE_LENGTH
                    self.clicked_square = square[0] + square[1] * 8
                    if self.board[self.clicked_square] != 0:
                        self.find_legal_moves(self.clicked_square)
                elif event.type == pygame.MOUSEBUTTONUP:
                    end_square = pos[0] // SQUARE_LENGTH, 7 - pos[1] // SQUARE_LENGTH
                    if self.turn % 2 == 0:
                        if piece.is_same_color(self.board[self.clicked_square], piece.WHITE):
                            self.move(self.clicked_square, end_square[0] + end_square[1] * 8, self.available_moves)
                    else:
                        if piece.is_same_color(self.board[self.clicked_square], piece.BLACK):
                            self.move(self.clicked_square, end_square[0] + end_square[1] * 8, self.available_moves)

                    self.clicked_square = None
                    self.available_moves = []
                elif event.type == pygame.K_a:
                    print('aaaaa')

            if self.game_active:  # Game loop
                self.screen.fill(WHITE) if self.turn % 2 == 0 else self.screen.fill(BLACK)
                self.draw_graphical_board()
                self.draw_pieces()
            else:
                self.screen.fill((94, 129, 162))

            pygame.display.update()
            self.clock.tick(60)

    def fen_to_board(self, fen):
        char_to_piece = {
            'r': piece.ROOK,
            'n': piece.KNIGHT,
            'b': piece.BISHOP,
            'q': piece.QUEEN,
            'k': piece.KING,
            'p': piece.PAWN,
        }

        file = 0
        rank = 7

        for char in fen.split(' ')[0]:
            if char == "/":
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                self.board[rank * 8 + file] = char_to_piece[char.lower()] + (piece.BLACK if char.islower() else piece.WHITE)
                file += 1

    def draw_graphical_board(self):
        for rank in range(8):
            for file in range(8):
                is_light_square = (rank + file) % 2 == 0
                if file + (7 - rank) * 8 in self.available_moves:
                    square_color = MOVE_SQUARE
                elif is_light_square:
                    square_color = LIGHT_SQUARE
                else:
                    square_color = DARK_SQUARE
                pygame.draw.rect(self.screen, square_color,
                                 pygame.Rect(file * SQUARE_LENGTH, rank * SQUARE_LENGTH, SQUARE_LENGTH, SQUARE_LENGTH))

    def draw_pieces(self):
        for i, p in enumerate(self.preview_board):
            if p != 0:
                if i != self.clicked_square:
                    self.screen.blit(piece.graphics[p], ((i % 8) * SQUARE_LENGTH, (7 - (i // 8)) * SQUARE_LENGTH))
                else:
                    pos = pygame.mouse.get_pos()
                    self.screen.blit(piece.graphics[p], (pos[0] - SQUARE_LENGTH // 2, pos[1] - SQUARE_LENGTH // 2))

    def move(self, start, end, available_moves):
        if type(start) == int and self.board[start] != 0 and start != end:
            if end in available_moves:
                self.move_history.append((start, end, self.board[end]))
                self.turn += 1
                self.board[end] = self.board[start]
                self.board[start] = 0

                # ---castle checks---
                if piece.is_same_piece(self.board[end], piece.ROOK):
                    if start == 0:
                        self.castle_rights_white[1] = False
                    elif start == 7:
                        self.castle_rights_white[0] = False
                    elif start == 56:
                        self.castle_rights_black[1] = False
                    elif start == 63:
                        self.castle_rights_black[0] = False
                if piece.is_same_piece(self.board[end], piece.KING):
                    if start == 4:
                        self.castle_rights_white[1] = False
                        self.castle_rights_white[0] = False
                    elif start == 60:
                        self.castle_rights_black[1] = False
                        self.castle_rights_black[0] = False
                    if abs(start - end) == 2:
                        if end == 2:
                            self.board[3] = self.board[0]
                            self.board[0] = 0
                        elif end == 6:
                            self.board[5] = self.board[7]
                            self.board[7] = 0
                        elif end == 58:
                            self.board[59] = self.board[56]
                            self.board[56] = 0
                        elif end == 62:
                            self.board[61] = self.board[63]
                            self.board[63] = 0

                print(self.castle_rights_white)
                print(self.castle_rights_black)

                # ---en passant checks---
                if piece.is_same_piece(self.board[end], piece.PAWN):
                    if end == self.en_passant_square[0]:
                        self.board[self.en_passant_square[1]] = 0
                    elif abs(start - end) == 16:
                        self.en_passant_square = (start + (end - start) // 2, end)
                    else:
                        self.en_passant_square = (-1, -1)
        self.preview_board = self.board.copy()

    def find_legal_moves(self, piece_pos):
        self.available_moves = []

        if piece.is_white(self.board[piece_pos]):
            opponent = piece.BLACK
            friend = piece.WHITE
        else:
            opponent = piece.WHITE
            friend = piece.BLACK
        # --------PAWN LOGIC------------
        if piece.is_same_piece(self.board[piece_pos], piece.PAWN):
            if friend == piece.WHITE:
                move_offset = 8
                capture_offsets = [7, 9]
                directions = [min(piece_pos % 8, 7 - piece_pos // 8), min(7 - piece_pos % 8, 7 - piece_pos // 8)]
                squares_forward = 7 - piece_pos // 8
            else:
                move_offset = -8
                capture_offsets = [-7, -9]
                directions = [min(piece_pos // 8, piece_pos % 8), min(piece_pos // 8, 7 - piece_pos % 8)]
                squares_forward = piece_pos // 8

            # --Forward movement--
            if (piece_pos // 8 == 1 and friend == piece.WHITE) or (piece_pos // 8 == 6 and opponent == piece.WHITE):
                move_squares = min(squares_forward, 2)
            else:
                move_squares = min(squares_forward, 1)

            test_pos = piece_pos
            for _ in range(move_squares):
                test_pos += move_offset
                if self.board[test_pos] != 0:
                    break
                else:
                    self.available_moves.append(test_pos)
            # --Capture movement--
            for i, offset in enumerate(capture_offsets):
                test_pos = piece_pos + offset
                if directions[i] > 0:
                    if piece.is_same_color(self.board[test_pos], opponent) or test_pos == self.en_passant_square[0]:
                        self.available_moves.append(test_pos)

        # ---------OTHER PIECES LOGIC-----------
        else:
            if piece.is_same_piece(self.board[piece_pos], piece.ROOK):
                offsets = [-8, -1, 1, 8]
                squares_to_edge = [piece_pos // 8, piece_pos % 8, 7 - piece_pos % 8, 7 - piece_pos // 8]

            elif piece.is_same_piece(self.board[piece_pos], piece.BISHOP):
                offsets = [-9, -7, 7, 9]
                squares_to_edge = [min(piece_pos // 8, piece_pos % 8),
                                   min(piece_pos // 8, 7 - piece_pos % 8),
                                   min(piece_pos % 8, 7 - piece_pos // 8),
                                   min(7 - piece_pos % 8, 7 - piece_pos // 8)]

            elif piece.is_same_piece(self.board[piece_pos], piece.QUEEN) or piece.is_same_piece(self.board[piece_pos], piece.KING):
                offsets = [-8, -1, 1, 8, -9, -7, 7, 9]
                directions = [piece_pos // 8, piece_pos % 8, 7 - piece_pos % 8, 7 - piece_pos // 8,
                              min(piece_pos // 8, piece_pos % 8),
                              min(piece_pos // 8, 7 - piece_pos % 8),
                              min(piece_pos % 8, 7 - piece_pos // 8),
                              min(7 - piece_pos % 8, 7 - piece_pos // 8)]

                if piece.is_same_piece(self.board[piece_pos], piece.KING):
                    squares_to_edge = []
                    for direction in directions:
                        squares_to_edge.append(min(direction, 1))
                    # --check if can castle--
                    if friend == piece.WHITE:
                        if self.castle_rights_white[1]:  # queenside castle
                            if self.board[1] == 0 and self.board[2] == 0 and self.board[3] == 0:
                                self.available_moves.append(2)
                        if self.castle_rights_white[0]:  # kingside castle
                            if self.board[5] == 0 and self.board[6] == 0:
                                self.available_moves.append(6)
                    else:
                        if self.castle_rights_black[1]:  # queenside castle
                            if self.board[57] == 0 and self.board[58] == 0 and self.board[59] == 0:
                                self.available_moves.append(58)
                        if self.castle_rights_black[0]:  # kingside castle
                            if self.board[61] == 0 and self.board[62] == 0:
                                self.available_moves.append(62)
                else:
                    squares_to_edge = directions

            elif piece.is_same_piece(self.board[piece_pos], piece.KNIGHT):
                file = piece_pos % 8
                offsets = []
                if file > 0:
                    offsets.append(-17)
                    offsets.append(15)
                if file > 1:
                    offsets.append(-10)
                    offsets.append(6)
                if file < 7:
                    offsets.append(-15)
                    offsets.append(17)
                if file < 6:
                    offsets.append(-6)
                    offsets.append(10)
                remove_offsets = []
                for offset in offsets:
                    if 0 > piece_pos + offset or piece_pos + offset > 63:
                        remove_offsets.append(offset)
                for offset in remove_offsets:
                    offsets.remove(offset)
                squares_to_edge = [1] * len(offsets)

            else:
                offsets = []
                squares_to_edge = []

            for i, offset in enumerate(offsets):
                test_pos = piece_pos
                for _ in range(squares_to_edge[i]):
                    test_pos += offset
                    if piece.is_same_color(self.board[test_pos], opponent):
                        self.available_moves.append(test_pos)
                        break
                    elif piece.is_same_color(self.board[test_pos], friend):
                        break
                    else:
                        self.available_moves.append(test_pos)


board_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

chess = Chess()
chess.play(board_fen)
