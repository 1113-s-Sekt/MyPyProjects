from ChessPieces import *

Images = {'WhiteCell': 0, 'BlackCell': 0, 'Board': 0, 'Numbers': 0, 'Symbols': 0, 'Clocks': 0}
Notation = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10        # etc.
}


def notation_to_xy(position):
    return [Notation[position[0]], (int(position[1]) - 1)]

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
#


class Board:
    def __init__(self, game_mode):
        self.__name__ = 'Board'
        self.__width = 8
        self.__height = 8
        self.turn = 0
        self.mode = game_mode
        self.someone_in_check = False
        self.move_list = []         # в формате [ ['e2', 'e4'], ['d7', 'd5'], ['e4', 'd5', 'x', 'ссылка на фигуру']... ]
        self.cells = [Cell(self, i) for i in range(self.__width * self.__height)]
        if self.mode == 'Classic':
            for i in range(self.__width):
                self.cells[8 + i].occupy(Pawn(self, self.cells[8 + i], 'White'))
                self.cells[48 + i].occupy(Pawn(self, self.cells[48 + i], 'Black'))

            self.cells[0].occupy(Rook(self, self.cells[0], 'White'))
            self.cells[7].occupy(Rook(self, self.cells[7], 'White'))
            self.cells[1].occupy(Knight(self, self.cells[1], 'White'))
            self.cells[6].occupy(Knight(self, self.cells[6], 'White'))
            self.cells[2].occupy(Bishop(self, self.cells[2], 'White'))
            self.cells[5].occupy(Bishop(self, self.cells[5], 'White'))
            self.cells[3].occupy(Queen(self, self.cells[3], 'White'))
            self.cells[4].occupy(King(self, self.cells[4], 'White'))

            # self.cells[16].occupy(Pawn(self, self.cells[16], 'Black'))

            self.cells[56].occupy(Rook(self, self.cells[56], 'Black'))
            self.cells[63].occupy(Rook(self, self.cells[63], 'Black'))
            self.cells[57].occupy(Knight(self, self.cells[57], 'Black'))
            self.cells[62].occupy(Knight(self, self.cells[62], 'Black'))
            self.cells[58].occupy(Bishop(self, self.cells[58], 'Black'))
            self.cells[61].occupy(Bishop(self, self.cells[61], 'Black'))
            self.cells[59].occupy(Queen(self, self.cells[59], 'Black'))
            self.cells[60].occupy(King(self, self.cells[60], 'Black'))
        # elif self.mode.__name__ = 'Board':

        self.player_white = Player(self, 'White')
        self.player_black = Player(self, 'Black')
        self.players = {'White': self.player_white, 'Black': self.player_black}
        self.possible_moves = [self.player_white.possible_moves, self.player_black.possible_moves]    # ##############

    def encryptionForsythEdwards(self) -> str:
        code = ''
        return code

    def decryptionForsythEdwards(self, code: str):

        return True

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
            print("Board.capture(move) is available only for capturing move, which contains 'x' as third element.")

    def pawn_permutation(self, move):
        cell1 = self.get_cell_by_notation(move[0])
        cell2 = self.get_cell_by_notation(move[1])
        piece1 = cell1.occupied
        color1 = piece1.color
        if move[-1] == 'Queen':  # превращение пешки в ферзя
            self.__step(move)
            move.append(piece1)
            cell2.occupy(Queen(self, cell2, color1))
            move[2] = cell2.occupied
            self.players[color1].add_piece(cell2.occupied)
            self.players[color1].remove_piece(piece1)
        elif move[-1] == 'Rook':  # превращение пешки в ладью
            self.__step(move)
            move.append(piece1)
            cell2.occupy(Rook(self, cell2, color1))
            move[2] = cell2.occupied
            self.players[color1].add_piece(cell2.occupied)
            self.players[color1].remove_piece(piece1)
        elif move[-1] == 'Bishop':  # превращение пешки в слона
            self.__step(move)
            move.append(piece1)
            cell2.occupy(Bishop(self, cell2, color1))
            move[2] = cell2.occupied
            self.players[color1].add_piece(cell2.occupied)
            self.players[color1].remove_piece(piece1)
        elif move[-1] == 'Knight':  # превращение пешки в коня
            self.__step(move)
            move.append(piece1)
            cell2.occupy(Knight(self, cell2, color1))
            move[2] = cell2.occupied
            self.players[color1].add_piece(cell2.occupied)
            self.players[color1].remove_piece(piece1)
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
                self.move_list.append(move)
                return True
            cell1 = self.get_cell_by_notation(move[0])
            piece1 = cell1.occupied
            if len(move) == 2:                                                      # обычный ход
                self.__step(move)
            elif move[-1] == 'x':                                                   # ход "взятие вражеской фигуры"
                cell2 = self.get_cell_by_notation(move[1])
                self.players[cell2.occupied.color].remove_piece(cell2.occupied)
                self.__capture(move)
            elif move[-1] == 'passant':                                             # ход "взятие на проходе"
                cell3 = self.get_cell_by_notation(move[1][0] + move[0][1])
                self.players[cell3.occupied.color].remove_piece(cell3.occupied)
                self.__capture(move)
            elif piece1.__class__.__name__ == 'Pawn':                                                                             # это временное решение, для консоли
                if piece1.cell.position()[1] == 1 or piece1.cell.position()[1] == 8:
                    #print('Pawn to ...?')
                    #temp = input()
                    #while temp not in ['Queen', 'Rook', 'Knight', 'Bishop']:
                    #    print('Again pls, I dont understand')
                    #    temp = input()
                    #move.append(temp)
                    move = self.pawn_permutation(move)
                self.move_list.append(move)
            else:
                return False
            piece1.turn += 1
            self.turn += 1

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
        return None

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
                        if dude.__class__.__name__ == 'King' and dude.color != figure.color:
                            dude.check_by(figure)
                    if piece_xy[0] < 7:
                        cell = self.cells[self.xy_to_index([piece_xy[0] + 1, piece_xy[1] + direction])]
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = self.cells[self.xy_to_index([piece_xy[0] + 1, piece_xy[1] + direction])].occupied
                        if dude.__class__.__name__ == 'King' and dude.color != figure.color:
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
                            if dude.__class__.__name__ == 'King' and dude.color != figure.color:
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
                            continue
                        elif dude.__class__.__name__ == 'King' and dude.color != figure.color:
                            dude.check_by(figure)
                            continue
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
                    if figure.__class__.__name__ == 'Pawn' or figure.__class__.__name__ == 'King':
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
                    if figure.__class__.__name__ == 'Pawn':
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
                        if attacker.__class__.__name__ == 'Pawn' and self.move_list[-1][1] == attacker.cell.position():
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
            if figure.__class__.__name__ == 'King':
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
                            if dude.turn == 0 and dude.__class__.__name__ == 'Rook' and dude.color == clr:
                                if self.cells[1].attacked[attack] == 0 and not bool(self.cells[1].occupied) \
                                        and self.cells[2].attacked[attack] == 0 and not bool(self.cells[2].occupied)\
                                        and self.cells[3].attacked[attack] == 0 and not bool(self.cells[3].occupied):
                                    player.add_possible_moves(['0-0-0'])
                        dude = self.cells[7].occupied
                        if dude != 0:
                            if dude.turn == 0 and dude.__class__.__name__ == 'Rook' and dude.color == clr:
                                if self.cells[5].attacked[attack] == 0 and not bool(self.cells[5].occupied) \
                                        and self.cells[6].attacked[attack] == 0 and not bool(self.cells[6].occupied):
                                    player.add_possible_moves(['0-0'])
                    elif clr == 'Black':
                        dude = self.cells[56].occupied
                        if dude != 0:
                            if dude.turn == 0 and dude.__class__.__name__ == 'Rook' and dude.color == clr:
                                if self.cells[57].attacked[attack] == 0 and not bool(self.cells[57].occupied) \
                                        and self.cells[58].attacked[attack] == 0 and not bool(self.cells[58].occupied) \
                                        and self.cells[59].attacked[attack] == 0 and not bool(self.cells[59].occupied):
                                    player.add_possible_moves(['0-0-0'])
                        dude = self.cells[63].occupied
                        if dude != 0:
                            if dude.turn == 0 and dude.__class__.__name__ == 'Rook' and dude.color == clr:
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
                                if temp.__class__.__name__ == 'Pawn' and temp.cell.position()[0] == cell.position()[0]:
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

    def __history_back(self, move):
        pass

    def __history_forward(self, move):
        pass

# _____________________________________________________________________________________________________________________
# _____________________________________________________________________________________________________________________


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
            print('Impossible to remove a non-existing piece')

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


