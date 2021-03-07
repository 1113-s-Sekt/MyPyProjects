from ChessPieces import *
from ChessPlayer import *
from ChessCell import *
from random import randint, choice

Images = {'WhiteCell': 0, 'BlackCell': 0, 'Board': 0, 'Numbers': 0, 'Symbols': 0, 'Clocks': 0}
Notation = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10        # etc.
}

# Ходы записываются в формате:
# [ ['e2', 'e4'], ['d7', 'd5'], ['e4', 'd5', 'x', 'ссылка на фигуру']... ]
#
# ['e2', 'e4'] - простое передвижение фигуры,
#
# ['e4', 'd5', 'x', 'ссылка на съеденую фигуру']:   - простое взятие
#       на вход подаётся ход ['e4', 'd5', 'x'] - взятие фигуры,
#       потом в ход записывается ссылка на съеденную фигуру, остальные ссылки на неё удаляются,
#       ссылка хранится в истории для возврата хода
#
# ['d5', 'c6', 'passant', 'ссылка на съеденую фигуру']:   - взятие на проходе
#       на вход подаётся ход ['d5', 'c6', 'passant'] - взятие фигуры,
#       потом в ход записывается ссылка на съеденную фигуру, остальные ссылки на неё удаляются,
#       всё как в простом взятии, только другое обозначение
#
# ['e7', 'e8', 'ссылка на фигуру, которой пешка стала', 'ссылка на бывшую пешку']:  - превращение пешки
#       на вход подаётся ход в формате ['e7', 'e8', 'Queen']
#       потом в массив добавляется ссылка на бывшую пешку,
#       вместо 'Queen' встаёт ссылка на эту фигуру - опять же для истории,
#       при отматывании истории назад и при повторном движении вперёд создаваться новая фигура не будет,
#       просто будут удаляться все ссылки на неё кроме той, что в истории, в этом ходу
#
# ['0-0-0']:    - рокировка
#       длинная рокировка, ход подаётся в таком же формате
#       (аналогично с короткой рокировкой - '0-0')
#
# ['c4', 'd6', '+']:    - ход с шахом (в move подаётся просто как ['c4', 'd6'])
#       у короля должен быть флажок состояния "в шахе",
#       т.к. проверка ходов начинается с короля, то сперва проверяем короля на наличие шаха ему
#       если он есть, то допускаются только те ходы, которые ведут к его исчезновению, т.е.:
#               1. Король ходит на неатакованную клетку
#               2. Фигура закрывает короля от шаха
#               3. Союзная фигура убивает атакующую
#
#       при этом сперва нужно проверить - какие фигуры атакуют клетку с королём, если их больше одной,
#       то остаётся только первый пункт - ход королём. Т.е. если короля атакуют сразу две фигуры - остальные ходы
#       уже не нужно проверять, смотрим только то, куда может уйти король:
#
# ['c4', 'd6', '++']:    - ход с двойным шахом (в move подаётся просто как ['c4', 'd6'])
#
#       Если после шаха не существует легитимных ходов, то это мат
#       (т.е. после этого хода будет проверка всех ходов, если их нет - "флажок мата" поднимается, партия заканчивается,
#       после этого отображается история в интерфейсе. Т.е. если ход с шахом и ходов нет - то в нотацию записывается
#       "мат", если ходы есть, то "шах")
#
#       Почему для слова "клетка(поле)" используется слово "cell", а не "field" - ответа дать нельзя,
#       потом когда-нибудь поправлю везде это слово...
#
#   !!! Изменения в нотации Ф.-Э.:
#       'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w SLsl .. 0 0' - классическая партия
#       1) Рокировки обозначаются не KQkq а SLsl (SHORT, LONG, short, long)
#       2) Если прошлый ход не был двойной ход пешкой, то ставится не '-' а '..' для отличия от других символов в строке
#               и фиксированной длительности задней части строки
#
#


game_mode_classic = 0
game_mode_classic_fe_notation = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w SLsl .. 0 1'
game_mode_fisher = 1
game_mode_custom = 2
game_mode_continue = 3
save_file = 'saves/lastgame.txt'


def notation_to_xy(position):
    return [Notation[position[0]], (int(position[1]) - 1)]


def create_fisher_pos():
    k = randint(1, 6)
    posblack = ['' for i in range(8)]
    posblack[k] = 'k'                               # Поставили короля на случайное место [False, ..., 'k', ..., False]
    posblack[randint(0, k - 1)] = 'r'               # Поствили одна ладью слева, другую справа от короля рандомно
    posblack[randint(k + 1, 7)] = 'r'
    r = randint(0, 7)
    while bool(posblack[r]):                        # Поставили на первый пустой слот одного слона
        r = randint(0, 7)
    posblack[r] = 'b'
    while bool(posblack[k]) or not bool((k + r) % 2):
        k = randint(0, 7)                           # Ставим след. слона в пустой слот так, чтобы он был другой четности
    posblack[k] = 'b'                               # До слонов было заполнено только 3 клетки, так что 100% есть клетки
    free_pos = []                                   # пустые и разной чётности
    for kekw in range(8):                           # Ищем все пустые поля
        if not bool(posblack[kekw]):
            free_pos.append(kekw)
    k = choice(free_pos)
    posblack[k] = 'q'                               # Ставим в рандомное ферзя
    free_pos.remove(k)
    posblack[free_pos[0]] = 'n'                     # Оставшиеся два заполняем конями
    posblack[free_pos[1]] = 'n'
    posblack = ''.join(posblack)
    poswhite = posblack.upper()
    code = posblack + '/pppppppp/8/8/8/8/PPPPPPPP/' + poswhite + ' w SLsl .. 0 1'
    return code


class Board:

    def __init__(self, game_mode):
        self.__name__ = 'Board'
        self.__width = 8
        self.__height = 8
        self.turn = 0
        self.half_turn = 0       # Полуходы - ходы без движения пешек и взятия фигур. Если >=50 то объявляется НИЧЬЯ
        self.mode = game_mode
        self.someone_in_check = False
        self.permutation = False
        self.move_list = []         # в формате [ ['e2', 'e4'], ['d7', 'd5'], ['e4', 'd5', 'x', 'ссылка на фигуру']... ]
        self.cells = [Cell(self, i) for i in range(self.__width * self.__height)]
        self.fill_board(self.mode)
        self.players = {'White': self.player_white, 'Black': self.player_black}

    def encryption_forsyth_edwards(self) -> str:     # зашифровывает текущую доску в нотацию Форсайта-Эдвардса
        "Зашифровывает текущую доску в нотацию Форсайта-Эдвардса"
        dict = {Rook: 'r', Bishop: 'b', Knight: 'n', Queen: 'q', King: 'k', Pawn: 'p'}
        code = []
        w = self.__width
        h = self.__height
        for y in range(h - 1, -1, -1):
            j = 0
            for x in range(w):
                cell = self.cells[y * w + x]
                dude = cell.occupied
                if dude != 0:
                    if bool(j):
                        code.append(str(j))
                        j = 0
                    code.append(dict[dude.__class__])
                else:
                    j += 1
                    continue
                if dude.color == 'White':
                    code[-1] = code[-1].upper()
            if bool(j):
                code.append(str(j))
            code.append('/')
        code.pop()
        code.append({0: ' w ', 1: ' b '}[self.turn % 2])
        king = 0
        for player in [self.player_white, self.player_black]:
            clr = player.color
            for figure in player.pieces:
                if isinstance(figure, King):
                    king = figure
            if king.turn != 0:
                code.append('--')
            else:
                dude = self.cells[{'White': 7, 'Black': 63}[clr]].occupied
                if isinstance(dude, Rook) and not bool(dude.turn):
                    code.append('s')                                    # l means "long", s means "short" castles
                    if clr == 'White':
                        code[-1] = code[-1].upper()
                else:
                    code.append('-')
                dude = self.cells[{'White': 0, 'Black': 56}[clr]].occupied
                if isinstance(dude, Rook) and not bool(dude.turn):
                    code.append('l')
                    if clr == 'White':
                        code[-1] = code[-1].upper()
                else:
                    code.append('-')
        if len(self.move_list) > 0:
            lmv = self.move_list[-1]                        # if: 'en passant' possible - there
            cell2 = self.get_cell_by_notation(lmv[1])       # is a cell to attack like 'e3'
            if abs(int(lmv[0][1]) - int(lmv[1][1])) == 2 and isinstance(cell2.occupied, Pawn):
                cll = ' ' + lmv[0][0] + str((int(lmv[0][1]) + int(lmv[1][1])) // 2)
                code.append(cll)
            else:                                           # else: '..'
                code.append(' ..')
        else:
            code.append(' ..')
        code.append(f' {self.half_turn} {self.turn // 2 + 1}')
        code = ''.join(code)
        return code

    def decryption_forsyth_edwards(self, code: str):  # заполняет доску в соот-вии с ноатцией Ф.-Э.
        piece_dict = {
            'r': Rook, 'R': Rook,
            'n': Knight, 'N': Knight,
            'b': Bishop, 'B': Bishop,
            'q': Queen, 'Q': Queen,
            'k': King, 'K': King,
            'p': Pawn, 'P': Pawn
        }
        nums = ['1', '2', '3', '4', '5', '6', '7', '8']
        index = 56  # Индекс клетки, а не итерации по строке code
        j = 0
        while code[j] != ' ':
            if code[j] == '/':
                index -= 16
                j += 1
                continue
            elif code[j] in nums:
                index += int(code[j])
            else:
                clr = {True: 'White', False: 'Black'}[code[j].upper() == code[j]]
                self.cells[index].occupy(piece_dict[code[j]](self, self.cells[index], clr))
                index += 1
            j += 1
        self.turn = (int(code[-1]) - 1) * 2 + {'w': 0, 'b': 1}[code[-13]]
        self.half_turn = int(code[-3])
        castles = []
        for j in range(4):
            if code[-8 - j] != '-':
                castles.append(code[-8 - j])
        return castles

    def width(self):
        return self.__width

    def height(self):
        return self.__height

    def __repr__(self):
        temp = ''
        for i in range(self.__height - 1, -1, -1):
            temp += str(i + 1) + ' ' + \
                    ' '.join([str(self.cells[i * self.__width + j]) for j in range(self.__width)]) + '\n'
        temp += '  ' + 'a  b c  d  e f  g  h ' + '\n'
        return temp

    def notation_to_index(self, position):                                  # эти методы нужно вынести за класс Board,
        return Notation[position[0]] + (int(position[1]) - 1) * self.__width

    def xy_to_index(self, xy):
        return self.__width * xy[1] + xy[0]

    def get_cell_by_notation(self, position):
        return self.cells[self.notation_to_index(position)]

    def __step(self, move):                             # механизм передвижения фигуры (перепривязка её местоположения)
        cell1 = self.get_cell_by_notation(move[0])
        cell2 = self.get_cell_by_notation(move[1])
        cell2.occupy(cell1.occupied)
        cell2.occupied.bind_cell(cell2)
        cell1.occupy(0)
        return self

    def __capture(self, move):                          # механизм взятия вражеской фигуры (теперь move содержит ссылку
        try:                                            # на съеденную фигуру вместо 'x')
            if move[2] == 'x':
                attacking_piece = self.get_cell_by_notation(move[0]).occupied
                piece_under_attack = self.get_cell_by_notation(move[1]).occupied
                move.append(piece_under_attack)
                self.get_cell_by_notation(move[1]).occupy(attacking_piece)
                attacking_piece.bind_cell(self.get_cell_by_notation(move[1]))
                self.get_cell_by_notation(move[0]).occupy(0)
                return move
            elif move[2] == 'passant':
                attacking_piece = self.get_cell_by_notation(move[0]).occupied
                piece_under_attack = self.get_cell_by_notation(move[1][0] + move[0][1]).occupied
                move.append(piece_under_attack)
                self.get_cell_by_notation(move[1][0] + move[0][1]).occupy(0)
                self.get_cell_by_notation(move[1]).occupy(attacking_piece)
                attacking_piece.bind_cell(self.get_cell_by_notation(move[1]))
                self.get_cell_by_notation(move[0]).occupy(0)
            else:
                print("It's not a capturing move")
                return False
        except ValueError:
            raise ValueError(print("Board.capture(move) is available only for capturing move, "
                                   "which contains 'x' as third element."))

    def pawn_permutation(self, move, to_whom):
        move.append(to_whom)
        cell1 = self.get_cell_by_notation(move[1])  # ['e7', 'e8', 'Queen'] or:
        piece1 = cell1.occupied                     # ['e7', 'e8', 'x', <ссылка на съеденную фигуру>, 'Queen']
        color1 = piece1.color
        if move[-1] == 'Queen':  # превращение пешки в ферзя
            move.append(piece1)                        # ['e7', 'e8', 'Queen', <ссылка на пешку>] or:
            cell1.occupy(Queen(self, cell1, color1))   # ['e7', 'e8', 'x', <ссыл на съед ф>, 'Queen', <ссылка на пешку>]
            move.append(cell1.occupied)                # ['e7', 'e8', 'Queen', <ссылка на пешку>, <ссылка на ферзя>] or:
            self.players[color1].add_piece(cell1.occupied)  # ['e7', 'e8', 'x', <ссыл на съед ф>,
            self.players[color1].remove_piece(piece1)              # 'Queen', <ссылка на пешку>, <ссылка на ферзя>]
        elif move[-1] == 'Rook':  # превращение пешки в ладью
            move.append(piece1)
            cell1.occupy(Rook(self, cell1, color1))
            move.append(cell1.occupied)
            self.players[color1].add_piece(cell1.occupied)
            self.players[color1].remove_piece(piece1)
        elif move[-1] == 'Bishop':  # превращение пешки в слона
            move.append(piece1)
            cell1.occupy(Bishop(self, cell1, color1))
            move.append(cell1.occupied)
            self.players[color1].add_piece(cell1.occupied)
            self.players[color1].remove_piece(piece1)
        elif move[-1] == 'Knight':  # превращение пешки в коня
            move.append(piece1)
            cell1.occupy(Knight(self, cell1, color1))
            move.append(cell1.occupied)
            self.players[color1].add_piece(cell1.occupied)
            self.players[color1].remove_piece(piece1)
        else:
            return False
        self.move_list.append(move)
        self.permutation = False
        return move

    def move(self, move):                             # не проверяет легитимность хода, просто аппарат его совершения
        color1 = {0: 'White', 1: 'Black'}[self.turn % 2]
        player = {'White': self.player_white, 'Black': self.player_black}[color1]
        if move not in player.possible_moves:
            print('An impossible or incorrect move')
            return False
        else:
            if move[0] == '0-0-0':  # ход "длинная рокировка"
                if color1 == 'White':
                    self.__step(['e1', 'c1'])
                    self.__step(['a1', 'd1'])
                    self.get_cell_by_notation('c1').occupied.turn += 1
                elif color1 == 'Black':
                    self.__step(['e8', 'c8'])
                    self.__step(['a8', 'd8'])
                    self.get_cell_by_notation('c8').occupied.turn += 1
                else:
                    return False
                self.turn += 1
                self.half_turn += 1
                self.move_list.append(move)
                return True
            elif move[0] == '0-0':  # ход "короткая рокировка"
                if color1 == 'White':
                    self.__step(['e1', 'g1'])
                    self.__step(['h1', 'f1'])
                    self.get_cell_by_notation('g1').occupied.turn += 1
                elif color1 == 'Black':
                    self.__step(['e8', 'g8'])
                    self.__step(['h8', 'f8'])
                    self.get_cell_by_notation('g8').occupied.turn += 1
                else:
                    return False
                self.turn += 1
                self.half_turn += 1
                self.move_list.append(move)
                return True
            cell1 = self.get_cell_by_notation(move[0])
            piece1 = cell1.occupied
            if len(move) == 2:                                                      # обычный ход
                self.__step(move)
                self.half_turn += 1
                if isinstance(piece1, Pawn):
                    self.half_turn = 0
            elif move[-1] == 'x':                                                   # ход "взятие вражеской фигуры"
                cell2 = self.get_cell_by_notation(move[1])
                move.append(cell2.occupied)
                self.players[cell2.occupied.color].remove_piece(cell2.occupied)
                self.__capture(move)
                self.half_turn = 0
            elif move[-1] == 'passant':                                             # ход "взятие на проходе"
                cell3 = self.get_cell_by_notation(move[1][0] + move[0][1])
                move.append(cell3.occupied)
                self.players[cell3.occupied.color].remove_piece(cell3.occupied)
                self.__capture(move)
                self.half_turn = 0
            else:
                return False
            piece1.turn += 1
            self.turn += 1
            if isinstance(piece1, Pawn):  # Поднимаем флажок превращения пешки, потом по флажку обращаемся к интерфейсу
                if piece1.cell.position()[1] == 1 or piece1.cell.position()[1] == 8:
                    self.permutation = True
                    return True
            self.move_list.append(move)

    def reset_check(self):
        if self.someone_in_check:
            self.someone_in_check.in_check = False
        self.someone_in_check = False
        return True

    def if_on_the_line(self, piece1, piece2):                   # метод возвращает все клетки между 2мя фигурами
        xy1 = notation_to_xy(piece1.cell.position())            # (не включая сами фигуры). Наличие третьих фигур на
        cells_between = []                                      # этих клетках не проверяется (это tool)
        vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
        for vect in vector:
            i = 1  # i - это скаляр, на который умножается вектор. Изначально 1, в конце while -> i += 1
            temp = []
            while 0 <= xy1[0] + i * vect[0] <= 7 and 0 <= xy1[1] + i * vect[1] <= 7:
                cell = self.cells[
                    self.xy_to_index([xy1[0] + i * vect[0], xy1[1] + i * vect[1]])]
                dude = cell.occupied
                i += 1
                if dude != piece2:
                    temp.append(cell)
                    continue
                elif dude == piece2:
                    cells_between = temp
                    return cells_between
        return cells_between

    def look_for_cells_are_attacked(self):      # смотрим какие клетки атакуются и какие клетки "(псевдо)доступны"
        self.reset_check()
        for cell in self.cells:
            cell.attacked = [0, 0]
        for player in [self.player_white, self.player_black]:
            direction = {'White': 1, 'Black': -1}[player.color]
            ind = {'White': 0, 'Black': 1}[player.color]
            for figure in player.pieces:             # начинаем с фигур белых
                figure.reset_available_cells()
                piece_xy = notation_to_xy(figure.cell.position())
                piece_name = figure.__class__.__name__
                if piece_name == 'Pawn':         # смотрим какие клетки атакует пешка
                    if piece_xy[0] > 0:
                        cell = self.cells[self.xy_to_index([piece_xy[0] - 1, piece_xy[1] + direction])]
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = self.cells[self.xy_to_index([piece_xy[0] - 1, piece_xy[1] + direction])].occupied
                        if isinstance(dude, King) and dude.color != figure.color:
                            dude.check_by(figure)
                    if piece_xy[0] < 7:
                        cell = self.cells[self.xy_to_index([piece_xy[0] + 1, piece_xy[1] + direction])]
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = self.cells[self.xy_to_index([piece_xy[0] + 1, piece_xy[1] + direction])].occupied
                        if isinstance(dude, King) and dude.color != figure.color:
                            dude.check_by(figure)
                    if self.cells[self.xy_to_index([piece_xy[0], piece_xy[1] + direction])].occupied == 0:
                        figure.add_available_cells(self.cells[self.xy_to_index([piece_xy[0], piece_xy[1] + direction])])
                        if figure.turn == 0 and piece_xy[1] == {'White': 1, 'Black': 6}[figure.color]:
                            figure.add_available_cells(
                                self.cells[self.xy_to_index([piece_xy[0], piece_xy[1] + 2 * direction])])
                    continue
                elif piece_name == 'King':        # смотрим атаки короля по векторам
                    vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
                    for vect in vector:
                        if 0 <= piece_xy[0] + vect[0] <= 7 and 0 <= piece_xy[1] + vect[1] <= 7:
                            cell = self.cells[self.xy_to_index([piece_xy[0] + vect[0], piece_xy[1] + vect[1]])]
                            cell.attacked[ind] += 1
                            figure.add_available_cells(cell)
                    continue
                elif piece_name == 'Knight':      # смотрим атаки коня, пробегаем по всем возможным векторам
                    vector = [[1, 2], [2, 1], [-1, 2], [2, -1], [1, -2], [-2, 1], [-1, -2], [-2, -1]]
                    for vect in vector:
                        if 0 <= piece_xy[0] + vect[0] <= 7 and 0 <= piece_xy[1] + vect[1] <= 7:
                            cell = self.cells[self.xy_to_index([piece_xy[0] + vect[0], piece_xy[1] + vect[1]])]
                            cell.attacked[ind] += 1
                            figure.add_available_cells(cell)
                            dude = cell.occupied
                            if dude == 0:
                                pass
                            elif isinstance(dude, King) and dude.color != figure.color:
                                dude.check_by(figure)
                    continue
                vector = []
                if piece_name == 'Rook':       # вектора для ладьи
                    vector = [[1, 0], [0, -1], [-1, 0], [0, 1]]
                elif piece_name == 'Bishop':     # вектора для слона
                    vector = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
                elif piece_name == 'Queen':     # вектора для ферзя
                    vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
                for vect in vector:
                    i = 1       # i - это скаляр, на который умножается вектор. Изначально 1, в конце while -> i += 1
                    while 0 <= piece_xy[0] + i * vect[0] <= 7 and 0 <= piece_xy[1] + i * vect[1] <= 7:
                        cell = self.cells[
                            self.xy_to_index([piece_xy[0] + i * vect[0], piece_xy[1] + i * vect[1]])]
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = cell.occupied
                        i += 1
                        if dude == 0:
                            pass
                        elif isinstance(dude, King) and dude.color != figure.color:
                            dude.check_by(figure)
                        else:
                            break

    def move_creator(self):
        white = self.player_white
        black = self.player_black
        white.reset_possible_moves()
        black.reset_possible_moves()
        for player in [white, black]:
            for p in player.pieces:
                p.bounded = False
        if bool(self.someone_in_check):             # Рассмотрим сперва наличие шаха на доске
            king = self.someone_in_check            # если на доске шах, то ходит по-любому тот, кому шах
            player = {'White': white, 'Black': black}[king.color]
            king.available_cells.remove(king.cell)
            for cell in king.available_cells:  # 1. сперва смотрим ходы короля
                if cell.attacked[{'White': 1, 'Black': 0}[king.color]] == 0:
                    dude = cell.occupied
                    if dude == 0:
                        player.add_possible_moves([king.cell.position(), cell.position()])
                    elif dude.color == king.color:
                        continue
                    else:
                        player.add_possible_moves([king.cell.position(), cell.position(), 'x'])
            attacker = king.in_check                                    # если теперь шах одиночный, то:
            # 2,3. смотрим ходы перекрытия и съедения атакующей фигуры
            cells_we_can_stand_on = self.if_on_the_line(attacker, king)        # клетки доступные для перекрытия
            cells_we_can_stand_on.append(attacker.cell)
            cells_we_can_stand_on = set(cells_we_can_stand_on)        # добавляем клетку атакующего, её можно атаковать
            if king.cell.attacked[{'White': 1, 'Black': 0}[king.color]] == 1:
                for figure in player.pieces:
                    if isinstance(figure, Pawn) or isinstance(figure, King):
                        continue                                # пешку рассматриваем отдельно (passant-check, etc.)
                    figure.available_cells.remove(figure.cell)  # у наших фигур убираем клетки на которой они стоят
                    # далее из пересечения этих клеток и клеток, доступных нашей фигуре(K, Q, R, B, not P) делаем ходы
                    for cell in figure.available_cells.intersection(cells_we_can_stand_on):
                        dude = cell.occupied
                        if dude == 0:
                            player.add_possible_moves([figure.cell.position(), cell.position()])
                        elif dude.color == figure.color:
                            continue
                        else:
                            player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                for figure in player.pieces:    # а теперь начинает ебаный ад. Рассматриваем пешки....
                    if isinstance(figure, Pawn):
                        figure.available_cells.remove(figure.cell)
                        for cell in figure.available_cells.intersection(cells_we_can_stand_on):
                            if cell.position()[0] != figure.cell.position()[0]:
                                dude = cell.occupied
                                if dude == attacker:
                                    player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                            else:
                                if cell.occupied == 0:
                                        player.add_possible_moves([figure.cell.position(), cell.position()])
                        # а что если возможно взятие на проходе убивающее шахующую пешку????
                        # Это ужасно криво, но что поделать))00) Очень много обстоятельств должно сложиться
                        # В 99.9999% случаев не дойдёт даже до проверки 3го условия
                        if len(self.move_list[-1]) < 2:
                            continue
                        if isinstance(attacker, Pawn) and self.move_list[-1][1] == attacker.cell.position():
                            if attacker.turn == 1 and \
                                    abs(int(self.move_list[-1][0][1]) - int(self.move_list[-1][1][1])) == 2:
                                if attacker.cell.position()[0] == figure.cell.position()[0]:
                                    for cell in figure.available_cells:
                                        if cell.position()[1] == attacker.cell.position()[1]:
                                            player.add_possible_moves(
                                                [figure.cell.position(), cell.position(), 'passant'])
            return self.someone_in_check
        # Слава Господу мы закончили с шахами. Теперь связОчки и все остальные ходы)0)))))))))))))))
        player = {0: white, 1: black}[self.turn % 2]   # смотрим какой игрок ходит в общем случае
        mvr_clr = player.color                         # цвет запишем на всякий
        attack = {'White': 1, 'Black': 0}[mvr_clr]
        # будем смотреть связки начиная с короля во все стороны по очереди (векторно)
        # если на пути встречается союзная фигура, а за ней вражеская нужного типа - то союзная привязывается
        king = False    # для начала неплохо отыскать короля бы >_<
        for figure in player.pieces:    # в будущем неплохо бы сохранять ссылку на короля у самого игрока, или типо того
            if isinstance(figure, King):
                king = figure
        king_xy = notation_to_xy(king.cell.position())
        vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
        for vect in vector:     # на данном этапе мы просто связываем фигуры, потом будем обрабатывать всё вместе
            j = 1
            temp = False
            while 0 <= king_xy[0] + j * vect[0] <= 7 and 0 <= king_xy[1] + j * vect[1] <= 7:
                cell = self.cells[
                    self.xy_to_index([king_xy[0] + j * vect[0], king_xy[1] + j * vect[1]])]
                dude = cell.occupied
                if dude == 0:
                    j += 1
                    continue
                if dude.color == king.color and not bool(temp):
                    temp = dude
                elif dude.color != king.color:
                    n = dude.__class__.__name__
                    if n == 'King' or n == 'Pawn':  # будем честны, король и пешка связать не могут
                        break                       # конь должен отсекаться сам собой т.к. не лежит на линии при атаке
                    if bool(temp) and temp.cell in dude.available_cells:
                        temp.bounded = dude     # тут мы связываем фигуру только если сперва нашли союзную нам, и
                    break                       # она атакована следующей несоюзной фигурой
                j += 1
        # вроде связали, потом посмотрим как работает)))))))))))))))
        # теперь давайте наконец пробежимся по всем фигуркам, поимённо
        for figure in player.pieces:
            name = figure.__class__.__name__
            if name == 'King':
                for cell in figure.available_cells:
                    if cell != figure.cell:
                        if cell.attacked[attack] == 0:
                            if cell.occupied == 0:
                                player.add_possible_moves([figure.cell.position(), cell.position()])
                            elif cell.occupied.color != figure.color:
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                if figure.turn == 0:
                    clr = figure.color
                    if clr == 'White':
                        dude = self.cells[0].occupied
                        if dude != 0:
                            if dude.turn == 0 and isinstance(dude, Rook) and dude.color == clr:
                                if self.cells[1].attacked[attack] == 0 and not bool(self.cells[1].occupied) \
                                        and self.cells[2].attacked[attack] == 0 and not bool(self.cells[2].occupied)\
                                        and self.cells[3].attacked[attack] == 0 and not bool(self.cells[3].occupied):
                                    player.add_possible_moves(['0-0-0'])
                        dude = self.cells[7].occupied
                        if dude != 0:
                            if dude.turn == 0 and isinstance(dude, Rook) and dude.color == clr:
                                if self.cells[5].attacked[attack] == 0 and not bool(self.cells[5].occupied) \
                                        and self.cells[6].attacked[attack] == 0 and not bool(self.cells[6].occupied):
                                    player.add_possible_moves(['0-0'])
                    elif clr == 'Black':
                        dude = self.cells[56].occupied
                        if dude != 0:
                            if dude.turn == 0 and isinstance(dude, Rook) and dude.color == clr:
                                if self.cells[57].attacked[attack] == 0 and not bool(self.cells[57].occupied) \
                                        and self.cells[58].attacked[attack] == 0 and not bool(self.cells[58].occupied) \
                                        and self.cells[59].attacked[attack] == 0 and not bool(self.cells[59].occupied):
                                    player.add_possible_moves(['0-0-0'])
                        dude = self.cells[63].occupied
                        if dude != 0:
                            if dude.turn == 0 and isinstance(dude, Rook) and dude.color == clr:
                                if self.cells[61].attacked[attack] == 0 and not bool(self.cells[61].occupied) \
                                        and self.cells[62].attacked[attack] == 0 and not bool(self.cells[62].occupied):
                                    player.add_possible_moves(['0-0'])
            elif name == 'Bishop' or name == 'Queen' or name == 'Rook' or name == 'Knight':
                if bool(figure.bounded):
                    if name == 'Knight':  # #
                        continue        # #
                    attacker = figure.bounded
                    cells_to_stand_on = self.if_on_the_line(attacker, king)
                    cells_to_stand_on.append(attacker.cell)
                    cells_to_stand_on = set(cells_to_stand_on)
                    for cell in figure.available_cells.intersection(cells_to_stand_on):
                        if cell != figure.cell:
                            if bool(cell.occupied):
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                            else:
                                player.add_possible_moves([figure.cell.position(), cell.position()])
                else:
                    for cell in figure.available_cells:
                        if cell != figure.cell:
                            if bool(cell.occupied) and cell.occupied.color != mvr_clr:
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                            elif cell.occupied == 0:
                                player.add_possible_moves([figure.cell.position(), cell.position()])
            elif name == 'Pawn':
                if bool(figure.bounded):
                    attacker = figure.bounded
                    if attacker.cell.position()[0] == figure.cell.position()[0]:
                        for cell in figure.available_cells:
                            if cell.position()[0] == figure.cell.position()[0] and cell != figure.cell:
                                if cell.occupied == 0:
                                    player.add_possible_moves([figure.cell.position(), cell.position()])
                    else:
                        for cell in figure.available_cells:
                            if cell.position()[0] != figure.cell.position()[0] and cell.occupied == attacker:
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                else:
                    for cell in figure.available_cells:
                        if cell.position()[0] == figure.cell.position()[0] and cell != figure.cell:
                            if cell.occupied == 0:
                                player.add_possible_moves([figure.cell.position(), cell.position()])
                        if cell.position()[0] != figure.cell.position()[0]:
                            dude = cell.occupied
                            if dude == 0:
                                if len(self.move_list) == 0 or len(self.move_list[-1]) < 2:
                                    continue
                                lmv = self.move_list[-1]
                                temp = self.get_cell_by_notation(self.move_list[-1][1]).occupied
                                if isinstance(temp, Pawn) and temp.cell.position()[0] == cell.position()[0]:
                                    if temp.turn == 1 and abs(int(lmv[0][1]) - int(lmv[1][1])) == 2:
                                        if temp.cell.position()[1] == figure.cell.position()[1]:
                                            pos = lmv[0][0] + str((int(lmv[0][1]) + int(lmv[1][1])) // 2)
                                            # проверяем не откроем ли мы своего короля под шах таким ходом
                                            if (king_xy[1] == 5 and king.color == 'White') or \
                                                    (king_xy[1] == 4 and king.color == 'Black'):
                                                kekw = 0
                                                for i in range(king_xy[1]):
                                                    cll = self.cells[
                                                        {'White': 4, 'Black': 3}[king.color] * self.__width + i]
                                                    if cell.occupied == 0:
                                                        continue
                                                    nm = cll.occupied.__class__.__name__
                                                    clr = cll.occupied.color
                                                    if (nm == 'Rook' or nm == 'Queen') and clr != king.color:
                                                        kekw = 1
                                                    if kekw == 1 and (cll.occupied == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 2
                                                    if kekw == 2 and (cll.occupied == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 3
                                                if kekw == 3:
                                                    continue
                                                for i in range(7, king_xy[1] - 1, -1):
                                                    cll = self.cells[
                                                        {'White': 4, 'Black': 3}[king.color] * self.__width + i]
                                                    if cell.occupied == 0:
                                                        continue
                                                    nm = cll.occupied.__class__.__name__
                                                    clr = cll.occupied.color
                                                    if (nm == 'Rook' or nm == 'Queen') and clr != king.color:
                                                        kekw = 1
                                                    if kekw == 1 and (cll.occupied == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 2
                                                    if kekw == 2 and (cll.occupied == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 3
                                                if kekw == 3:
                                                    continue
                                            player.add_possible_moves([figure.cell.position(), pos, 'passant'])
                            elif dude.color != mvr_clr:
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])

    def clear_board(self):
        self.move_list = []
        for cell in self.cells:
            cell.occupied = 0
        for player in self.players:
            player.pieces = []
        self.turn = 0
        self.half_turn = 0
        self.someone_in_check = False
        self.player_white = 0
        self.player_black = 0

    def fill_board(self, mode):
        code = 0
        if mode == game_mode_classic:
            code = game_mode_classic_fe_notation
        elif mode == game_mode_fisher:
            code = create_fisher_pos()
        elif mode == game_mode_continue:
            code = open(save_file).read()
        elif mode == game_mode_custom:
            pass
        self.decryption_forsyth_edwards(code)
        self.player_white = Player(self, 'White')
        self.player_black = Player(self, 'Black')

    def __history_back(self, move):
        pass

    def __history_forward(self, move):
        pass

# _____________________________________________________________________________________________________________________
# _____________________________________________________________________________________________________________________


if __name__ == '__main__':
    pass