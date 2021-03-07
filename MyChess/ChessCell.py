

class Cell:
    def __init__(self, board, num):
        w = board.width()
        self.__num = num
        self.occupied = 0
        self.color = ['Black', 'White'][(num // w + num % w) % 2]
        self.__position = 'abcdefgh'[num % w] + '12345678'[num // w]
        self.attacked = [0, 0]
        if num % 2 == 0:
            self.image = Images['BlackCell']
        else:
            self.image = Images['WhiteCell']

    def __repr__(self):
        return self.__position

    def __str__(self):
        if self.occupied:
            return str(self.occupied)
        else:
            return {'Black': '⬜', 'White': '⬛'}[self.color]

    def occupy(self, piece):
        self.occupied = piece

    def index(self):
        return self.__num

    def position(self):
        return self.__position

    def pos(self):
        return [Notation[self.__position[0]], int(self.__position[1])-1]


# _____________________________________________________________________________________________________________________
# _____________________________________________________________________________________________________________________
