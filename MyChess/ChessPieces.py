from PyQt5.QtCore import QRect
from PyQt5.QtGui import QImage


class Piece(object):
    "Класс шахматных фигур. Обладает цветом, соответствующей фигуре клеткой на доске, ссылкой на эту доску, etc."
    def __init__(self, board, cell, color):
        self.color = color
        self.cell = cell
        self.board = board
        self.turn = 0
        self.available_cells = set([self.cell])
        self.bounded = False

    def bind_cell(self, cell):
        self.cell = cell
        return True

    def cell_is(self):
        return self.cell

    def reset_available_cells(self):
        self.available_cells = set([self.cell])
        return True

    def add_available_cells(self, cell_to_move_on):
        self.available_cells.add(cell_to_move_on)
        return True

    def restrict_available_cells(self, set_to_intersect_with):
        if set_to_intersect_with.__class__.__name__ == 'list':
            set_to_intersect_with = set(set_to_intersect_with)
        self.available_cells.intersection_update(set_to_intersect_with)
        return self.available_cells

    def __bool__(self):
        return True

    def __del__(self):
        print(f'{type(self)} is deleted.')


class Pawn(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 1
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wP.png")
        else:
            self.image = QImage("Pictures/wikipedia/bP.png")

    def __str__(self):
        if self.color == 'White':
            return '♟'
        else:
            return '♙'

    def __repr__(self):
        return 'Pawn' + ' ' + str(self.cell.position())


class Bishop(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 3
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wB.png")
        else:
            self.image = QImage("Pictures/wikipedia/bB.png")

    def __str__(self):
        if self.color == 'White':
            return '♝'
        else:
            return '♗'

    def __repr__(self):
        return 'Bishop' + ' ' + str(self.cell.position())


class Knight(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 3
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wN.png")
        else:
            self.image = QImage("Pictures/wikipedia/bN.png")

    def __str__(self):
        if self.color == 'White':
            return '♞'
        else:
            return '♘'

    def __repr__(self):
        return 'Knight' + ' ' + str(self.cell.position())


class Rook(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 5
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wR.png")
        else:
            self.image = QImage("Pictures/wikipedia/bR.png")

    def __str__(self):
        if self.color == 'White':
            return '♜'
        else:
            return '♖'

    def __repr__(self):
        return 'Rook' + ' ' + str(self.cell.position())


class Queen(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 9
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wQ.png")
        else:
            self.image = QImage("Pictures/wikipedia/bQ.png")

    def __str__(self):
        if self.color == 'White':
            return '♛'
        else:
            return '♕'

    def __repr__(self):
        return 'Queen' + ' ' + str(self.cell.position())


class King(Piece):
    def __init__(self, board, cell, color):
        super().__init__(board, cell, color)
        self.weight = 0
        self.in_check = False
        if self.color == 'White':
            self.image = QImage("Pictures/wikipedia/wK.png")
        else:
            self.image = QImage("Pictures/wikipedia/bK.png")

    def __str__(self):
        if self.color == 'White':
            return '♚'
        else:
            return '♔'

    def __repr__(self):
        return 'King' + ' ' + str(self.cell.position())

    def check_by(self, checking_piece):
        self.in_check = checking_piece
        self.board.someone_in_check = self
        return True


'''
class VoidPiece(Piece):
    def __init__(self, board, cell):
        super().__init__(board, cell)
        self.color = None
'''


if __name__ == '__main__':
    print(Piece.__doc__)
    print(Piece.__dict__['__dict__'])
    print(Pawn.__dict__)
