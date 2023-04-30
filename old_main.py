import pygame
from sys import exit
import numpy as np
import piece


LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
MOVE_SQUARE = (220, 136, 99)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SQUARE_LENGTH = 100

pygame.init()
screen = pygame.display.set_mode((SQUARE_LENGTH * 8 + 200, SQUARE_LENGTH * 8))
pygame.display.set_caption('gnagna')
clock = pygame.time.Clock()
game_active = True

board = np.array([0] * 64, dtype='i')

board_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


# board_fen = '8/1r1b1n1k/4q3/8/1R1B1N1K/8/5Q2/8 w - - 0 1'


def fen_to_board(fen):
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
            board[rank * 8 + file] = char_to_piece[char.lower()] + (piece.BLACK if char.islower() else piece.WHITE)
            file += 1


def draw_graphical_board():
    for rank in range(8):
        for file in range(8):
            is_light_square = (rank + file) % 2 == 0
            if file + (7 - rank) * 8 in available_squares:
                square_color = MOVE_SQUARE
            elif is_light_square:
                square_color = LIGHT_SQUARE
            else:
                square_color = DARK_SQUARE
            pygame.draw.rect(screen, square_color,
                             pygame.Rect(file * SQUARE_LENGTH, rank * SQUARE_LENGTH, SQUARE_LENGTH, SQUARE_LENGTH))


def draw_pieces():
    for i, p in enumerate(board):
        if p != 0:
            if i != clicked_square:
                screen.blit(piece.graphics[p], ((i % 8) * SQUARE_LENGTH, (7 - (i // 8)) * SQUARE_LENGTH))
            else:
                pos = pygame.mouse.get_pos()
                screen.blit(piece.graphics[p], (pos[0] - SQUARE_LENGTH // 2, pos[1] - SQUARE_LENGTH // 2))


def move(start, end, available_moves):
    global turn
    global en_passant_square
    if type(start) == int and board[start] != 0 and start != end:
        if end in available_moves:
            turn += 1
            board[end] = board[start]
            board[start] = 0
            # ---en passant checks---
            if piece.is_same_piece(board[end], piece.PAWN):
                if end == en_passant_square[0]:
                    board[en_passant_square[1]] = 0
                elif abs(start - end) == 16:
                    en_passant_square = (start + (end - start) // 2, end)
                else:
                    en_passant_square = (-1, -1)


def find_legal_moves(piece_pos):
    global en_passant_square
    available_moves = []

    if piece.is_white(board[piece_pos]):
        opponent = piece.BLACK
        friend = piece.WHITE
    else:
        opponent = piece.WHITE
        friend = piece.BLACK
    # --------PAWN LOGIC------------
    if piece.is_same_piece(board[piece_pos], piece.PAWN):
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
            if board[test_pos] != 0:
                break
            else:
                available_moves.append(test_pos)
        # --Capture movement--
        for i, offset in enumerate(capture_offsets):
            test_pos = piece_pos + offset
            if directions[i] > 0:
                if piece.is_same_color(board[test_pos], opponent) or test_pos == en_passant_square[0]:
                    available_moves.append(test_pos)

        return available_moves
    # ---------OTHER PIECES LOGIC-----------
    else:
        if piece.is_same_piece(board[piece_pos], piece.ROOK):
            offsets = [-8, -1, 1, 8]
            squares_to_edge = [piece_pos // 8, piece_pos % 8, 7 - piece_pos % 8, 7 - piece_pos // 8]

        elif piece.is_same_piece(board[piece_pos], piece.BISHOP):
            offsets = [-9, -7, 7, 9]
            squares_to_edge = [min(piece_pos // 8, piece_pos % 8),
                               min(piece_pos // 8, 7 - piece_pos % 8),
                               min(piece_pos % 8, 7 - piece_pos // 8),
                               min(7 - piece_pos % 8, 7 - piece_pos // 8)]

        elif piece.is_same_piece(board[piece_pos], piece.QUEEN) or piece.is_same_piece(board[piece_pos], piece.KING):
            offsets = [-8, -1, 1, 8, -9, -7, 7, 9]
            directions = [piece_pos // 8, piece_pos % 8, 7 - piece_pos % 8, 7 - piece_pos // 8,
                          min(piece_pos // 8, piece_pos % 8),
                          min(piece_pos // 8, 7 - piece_pos % 8),
                          min(piece_pos % 8, 7 - piece_pos // 8),
                          min(7 - piece_pos % 8, 7 - piece_pos // 8)]

            if piece.is_same_piece(board[piece_pos], piece.KING):
                squares_to_edge = []
                for direction in directions:
                    squares_to_edge.append(min(direction, 1))


            else:
                squares_to_edge = directions

        elif piece.is_same_piece(board[piece_pos], piece.KNIGHT):
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
                if piece.is_same_color(board[test_pos], opponent):
                    available_moves.append(test_pos)
                    break
                elif piece.is_same_color(board[test_pos], friend):
                    break
                else:
                    available_moves.append(test_pos)
        return available_moves


fen_to_board(board_fen)
clicked_square = None
available_squares = []

turn = 0
en_passant_square = (-1, -1)

while True:
    for event in pygame.event.get():  # Event loop
        pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:  # Checked always
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            square = pos[0] // SQUARE_LENGTH, 7 - pos[1] // SQUARE_LENGTH
            clicked_square = square[0] + square[1] * 8
            available_squares = find_legal_moves(clicked_square)
        elif event.type == pygame.MOUSEBUTTONUP:
            end_square = pos[0] // SQUARE_LENGTH, 7 - pos[1] // SQUARE_LENGTH
            if turn % 2 == 0:
                if piece.is_same_color(board[clicked_square], piece.WHITE):
                    move(clicked_square, end_square[0] + end_square[1] * 8, available_squares)
            else:
                if piece.is_same_color(board[clicked_square], piece.BLACK):
                    move(clicked_square, end_square[0] + end_square[1] * 8, available_squares)

            clicked_square = None
            available_squares = []

    if game_active:  # Game loop
        screen.fill(WHITE) if turn % 2 == 0 else screen.fill(BLACK)
        draw_graphical_board()
        draw_pieces()
    else:
        screen.fill((94, 129, 162))

    pygame.display.update()
    clock.tick(60)
