import pygame
import io


def load_and_scale_svg(filename, scale):
    with open(filename, "rt") as svg_string:
        svg_string = svg_string.read()
        start = svg_string.find('<svg')
        if start > 0:
            svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]

        # skalerer width og height op i svg (legendarisk kode)
        width = svg_string.find('width="')
        if width > 0:
            svg_string = svg_string[:width + 7] + str(int(svg_string[width + 7:svg_string[width + 7:].find('\"') + len(svg_string[:width + 7])]) * scale) + svg_string[svg_string[width + 7:].find('\"') + len(svg_string[:width + 7]):]
        height = svg_string.find('height="')
        if height > 0:
            svg_string = svg_string[:height + 8] + str(int(svg_string[height + 8:svg_string[height + 8:].find('\"') + len(svg_string[:height + 8])]) * scale) + svg_string[svg_string[height + 8:].find('\"') + len(svg_string[:height + 8]):]

    return pygame.image.load(io.BytesIO(svg_string.encode()))


NONE = 0
KING = 1
PAWN = 2
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 6
PIECES = 7

WHITE = 8
BLACK = 16
COLORS = WHITE + BLACK

SCALE_FACTOR = 2.2
graphics = {
    KING + WHITE: load_and_scale_svg('graphics/Chess_klt45.svg', SCALE_FACTOR),
    KING + BLACK: load_and_scale_svg('graphics/Chess_kdt45.svg', SCALE_FACTOR),
    PAWN + WHITE: load_and_scale_svg('graphics/Chess_plt45.svg', SCALE_FACTOR),
    PAWN + BLACK: load_and_scale_svg('graphics/Chess_pdt45.svg', SCALE_FACTOR),
    KNIGHT + WHITE: load_and_scale_svg('graphics/Chess_nlt45.svg', SCALE_FACTOR),
    KNIGHT + BLACK: load_and_scale_svg('graphics/Chess_ndt45.svg', SCALE_FACTOR),
    BISHOP + WHITE: load_and_scale_svg('graphics/Chess_blt45.svg', SCALE_FACTOR),
    BISHOP + BLACK: load_and_scale_svg('graphics/Chess_bdt45.svg', SCALE_FACTOR),
    ROOK + WHITE: load_and_scale_svg('graphics/Chess_rlt45.svg', SCALE_FACTOR),
    ROOK + BLACK: load_and_scale_svg('graphics/Chess_rdt45.svg', SCALE_FACTOR),
    QUEEN + WHITE: load_and_scale_svg('graphics/Chess_qlt45.svg', SCALE_FACTOR),
    QUEEN + BLACK: load_and_scale_svg('graphics/Chess_qdt45.svg', SCALE_FACTOR)
}

print((KING + WHITE) % ((KING + WHITE) & 24))


def is_white(p):
    if p & WHITE == 8:
        return True
    return False


def is_same_color(p1, p2):
    if p1 & COLORS == p2 & COLORS:
        return True
    return False


def is_same_piece(p1, p2):
    if p1 & PIECES == p2 & PIECES:
        return True
    return False
