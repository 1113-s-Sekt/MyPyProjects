

class Player:
    def __init__(self, board, color):
        self.color = color
        self.pieces = []
        for i in range(len(board.cells)):
            if board.cells[i].occupied == 0:
                continue
            if board.cells[i].occupied.color == str(self.color):
                self.pieces.append(board.cells[i].occupied)
        self.pieces = set(self.pieces)
        self.possible_moves = []

    def __repr__(self):
        return self.color

    def add_piece(self, piece):
        if piece == 0:
            print('The piece is not existing')
            return False
        if piece.color != self.color:
            print('Not the same color')
            return False
        self.pieces.add(piece)
        return self.pieces

    def remove_piece(self, piece):
        try:
            self.pieces.remove(piece)
            return self.pieces
        except ValueError:
            raise ValueError(print('Impossible to remove a non-existing piece'))

    def reset_possible_moves(self):
        self.possible_moves = []
        return True

    def add_possible_moves(self, move):
        self.possible_moves.append(move)
        return True

    def print_possible_moves(self):
        self.possible_moves.sort()
        if len(self.possible_moves) == 0:
            print('There are no possible moves, seems like checkmate :(')
            return False
        print('Possible moves are:')
        i = 0
        for move in self.possible_moves:
            i += 1
            print(move, end='   ')
            if i % 5 == 0:
                print()
        print()
        return True

    '''def search_for_possible_moves(self):
        pass

        for figure in self.pieces:
            for cell in figure.available_cells:
                if figure.cell == cell:
                    continue
                if cell.occupied != 0:
                    self.possible_moves.append([, ])
        '''

# _____________________________________________________________________________________________________________________
# _____________________________________________________________________________________________________________________