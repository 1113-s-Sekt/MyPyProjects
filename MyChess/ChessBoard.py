from ChessPlayer import *


from random import randint, choice

Images = {'WhiteCell': 0, 'BlackCell': 0, 'Board': 0, 'Numbers': 0, 'Symbols': 0, 'Clocks': 0}
Colors = ('White', 'Black')

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


class Board(object):

    width = NonDataDescriptor()
    height = NonDataDescriptor()
    turn = IntDescriptor()
    half_turn = IntDescriptor()
    someone_in_check = ChessDescriptor(King)
    permutation = BoolDescriptor()
    move_list = ChessDescriptor(Move)
    cells = ChessDescriptor(Cell)
    player_white = ChessDescriptor(Player)
    player_black = ChessDescriptor(Player)

    def __init__(self, game_mode):
        self.width = 8
        self.height = 8
        self.turn = 0
        self.half_turn = 0       # Полуходы - ходы без движения пешек и взятия фигур. Если >=50 то объявляется НИЧЬЯ
        self.mode = game_mode
        self.castles = [False, False, False, False]     # флажки [б.кор, б.длин, ч.кор, ч.длин] True\False
        self.someone_in_check = False   # флажок Piece\False
        self.permutation = False    # флажок True\False
        self.move_list = []         # в формате [ ['e2', 'e4'], ['d7', 'd5'], ['e4', 'd5', 'x', 'ссылка на фигуру']... ]
        self.cells = [Cell(i, self.width) for i in range(self.width * self.height)]
        self.player_white = Player([], Colors[0])
        self.player_black = Player([], Colors[1])
        self.fill_board(self.mode)
        self.players = {Colors[0]: self.player_white, Colors[1]: self.player_black}

    def __call__(self, position=None):
        if position is None:
            return None
        else:
            try:
                if isinstance(position, list):
                    return self.cells[self.xy_to_index(position)]
                return self.get_cell(position)
            finally:
                raise ValueError('Position should be in Notation or [x, y]] form')
            # должен возвращать по позиции 'e4' или по координатам клетку если она существует, иначе None

    def __repr__(self):
        temp = ''
        for i in range(self.height - 1, -1, -1):
            temp += str(i + 1) + ' ' + \
                    ' '.join([str(self.cells[i * self.width + j]) for j in range(self.width)]) + '\n'
        temp += '  ' + 'a  b c  d  e f  g  h ' + '\n'
        return temp

    def encryption_forsyth_edwards(self) -> str:
        """Зашифровывает текущую доску в нотацию Форсайта-Эдвардса"""
        dict_white = {Rook: 'R', Bishop: 'B', Knight: 'N', Queen: 'Q', King: 'K', Pawn: 'P'}
        dict_black = {Rook: 'r', Bishop: 'b', Knight: 'n', Queen: 'q', King: 'k', Pawn: 'p'}
        dict_ = {Colors[0]: dict_white, Colors[1]: dict_black}
        code = []
        w = self.width
        h = self.height
        for y in range(h - 1, -1, -1):
            j = 0
            for x in range(w):
                cell = self.cells[y * w + x]
                dude = cell.piece
                if bool(dude):
                    if bool(j):
                        code.append(str(j))
                        j = 0
                    code.append(dict_[dude.color][dude.__class__])
                else:
                    j += 1
                    continue
            if bool(j):
                code.append(str(j))
            code.append('/')
        code.pop()
        code.append({0: ' w ', 1: ' b '}[self.turn % 2])
                                                                                             # Здесь, кажется, проверять всё излишне. Достаточно посмотреть флаги self.castles
        for player in (self.player_white, self.player_black):
            king = player.king
            if king.turn != 0:
                code.append('--')
            else:
                clr = player.color
                ind1 = self.notation_to_index(king.position)
                ind2 = {Colors[0]: 8, Colors[1]: 64}[clr]
                flag = False
                for i in range(ind1 + 1, ind2):
                    dude = self.cells[i].piece
                    if isinstance(dude, Rook):
                        if dude.turn == 0 and dude.color == clr:
                            flag = True
                code.append({Colors[0]: 'S', Colors[1]: 's'}[clr] * int(flag) + '-' * int(flag))
                ind2 = {Colors[0]: 0, Colors[1]: 56}[clr]
                flag = False
                for i in range(ind2, ind1):
                    dude = self.cells[i].piece              # l means "long", s means "short" castles
                    if isinstance(dude, Rook):
                        if dude.turn == 0 and dude.color == clr:
                            flag = True
                code.append({Colors[0]: 'L', Colors[1]: 'l'}[clr] * int(flag) + '-' * int(flag))
                                                                                            # =======================================================================
        if len(self.move_list) > 0:
            lmv = self.move_list[-1]            # if: 'en passant' possible - there
            cell2 = self.get_cell(lmv[1])       # ____ is a cell to attack like 'e3'
            if abs(int(lmv[0][1]) - int(lmv[1][1])) == 2 and isinstance(cell2.piece, Pawn):
                cll = ' ' + lmv[0][0] + str((int(lmv[0][1]) + int(lmv[1][1])) // 2)
                code.append(cll)
            else:                               # else: '..'
                code.append(' ..')
        else:
            code.append(' ..')
        code.append(f' {self.half_turn} {self.turn // 2 + 1}')
        code = ''.join(code)
        return code

    def decryption_forsyth_edwards(self, code: str):
        """Заполняет нашу доску в соответствии с нотацией Форсайда-Эдвардса"""
        piece_dict = {
            'r': Rook, 'R': Rook,
            'n': Knight, 'N': Knight,
            'b': Bishop, 'B': Bishop,
            'q': Queen, 'Q': Queen,
            'k': King, 'K': King,
            'p': Pawn, 'P': Pawn
        }
        nums = ('1', '2', '3', '4', '5', '6', '7', '8')
        index = 56  # Индекс клетки, а не итерации по строке code
        j = 0
        castles = []
        while code[j] != ' ':
            if code[j] == '/':
                index -= 16
                j += 1
                continue
            elif code[j] in nums:
                index += int(code[j])
            else:
                clr = {True: Colors[0], False: Colors[1]}[code[j].upper() == code[j]]
                self.cells[index].piece = piece_dict[code[j]](clr, self.cells[index].position)
                index += 1
                if isinstance(self.cells[index].piece, Rook):
                    castles.append(self.cells[index].piece)
            j += 1
        self.turn = (int(code[-1]) - 1) * 2 + {'w': 0, 'b': 1}[code[-13]]
        self.half_turn = int(code[-3])
        for j in range(4):
            if code[-8 - j] == '-':
                self.castles[-j - 1] = castles[j]
        return True

    def clear_board(self):
        """Очищает доску: стирает все ходы, обновляет счётчики и флаги, стирает игроков"""
        self.move_list = []
        for cell in self.cells:
            cell.piece = False
        for player in self.players:
            player.pieces = set()
        self.turn = 0
        self.half_turn = 0
        self.someone_in_check = False
        self.castles = [False, False, False, False]
        self.player_white = None
        self.player_black = None
        return True

    def fill_board(self, mode):
        """Заполняет доску в соот-вии с текущим режимом игры, создаёт игроков и даёт им в руки фигуры"""
        code = 0
        if mode == game_mode_classic:
            code = game_mode_classic_fe_notation
        elif mode == game_mode_fisher:
            code = create_fisher_pos()
        elif mode == game_mode_continue:
            code = open(save_file).read()
        elif mode == game_mode_custom:
            pass
        self.player_white = Player([], Colors[0])
        self.player_black = Player([], Colors[1])
        self.decryption_forsyth_edwards(code)
        for player in (self.players[Colors[0]], self.players[Colors[1]]):
            for cell in self.cells:
                dude = cell.piece
                if not dude:
                    continue
                else:
                    if dude.color == player.color:
                        player.add_piece(dude)
                        if isinstance(dude, King):
                            player.king = dude
        return True

    def refill_boar(self):
        """Перезаполняет доску с текущим game-mode"""
        self.clear_board()
        self.fill_board(self.mode)
        return True

    def notation_to_index(self, position): return Notation[position[0]] + (int(position[1]) - 1) * self.width

    def xy_to_index(self, xy): return self.width * xy[1] + xy[0]

    def get_cell(self, position): return self.cells[self.notation_to_index(position)]

    def __step(self, move_):
        """Механизм передвижения фигуры (перепривязка её местоположения)"""
        if (move_(0) not in self.cells) or (move_(1) not in self.cells):
            raise AttributeError('move contains reference to cell of another board')
        moving_piece = move_(0).piece
        move_(1).piece = moving_piece
        moving_piece.position = move_(1).position
        move_(0).piece = False
        return True

    def __capture(self, move_):
        """Механизм взятия вражеской фигуры"""
        if (move_(0) not in self.cells) or (move_(1) not in self.cells):
            raise AttributeError('move contains reference to cell of another board')
        if move_.capture():
            attacking_piece = move_(0).piece
            piece_under_attack = move_(1).piece      # Эта фигура помнит свою позицию и если что её можно легко
            move_.fig_taken = piece_under_attack     # восстановить. Ссыла на неё теперь содержится в этом ходу
            move_(1).piece = attacking_piece
            attacking_piece.position = move_(1).position
            move_(0).piece = False
        elif move_.passant():
            attacking_piece = move_(0).piece
            cell_under_attack = self.get_cell(move_[1][0] + move_[0][1])
            piece_under_attack = cell_under_attack.piece
            move_.fig_taken = piece_under_attack
            cell_under_attack.piece = False
            move_(1).piece = attacking_piece
            attacking_piece.position = move_(1).position
            move_(0).piece = False
        else:
            raise ValueError("It's not a capturing move")
        return True

    def pawn_permutation(self, to_whom):
        """Данный метод вызывается если поднят флаг Board.permutation; флаг поднимается только если какая-то из пешек
        на текущем ходу дошла до края доски, это проверяется в Board.move(Move). При поднятом флаге в интерфейсе
        срабатывает триггер, предлагающий игроку выбрать - в кого превратить пешку. Как только он выбирает - вызывается
        ЭТОТ метод - Board.pawn_permutation(to_whom)"""
        if to_whom not in ('Queen', 'Rook', 'Bishop', 'Knight'):
            raise ValueError('I do not understand to whom I should permute')
        move_ = self.move_list[-1]  # тут ошибки быть не может т.к. флаг permutation поднимается только после хода
        if move_.optional != 'permute':
            raise AttributeError('It is not a permutation move')
        if not isinstance(move_(1).piece, Pawn):
            raise ValueError('Last move was made not by Pawn')

        piece_dict = {
            'Queen': Queen, 'Rook': Rook, 'Bishop': Bishop, 'Knight': Knight
        }
        cell1 = move_(1)
        piece1 = cell1.piece
        color1 = piece1.color
        player = self.players[color1]

        move_.fig_pawn = piece1
        cell1.piece = piece_dict[to_whom](color1, cell1.position)   # Сразу смотрим в кого будем превращаться
        move_.fig_appeared = cell1.piece
        player.add_piece(cell1.piece)
        player.remove_piece(piece1)
        self.permutation = False
        return True

    def move(self, move_):
        """Не проверяет легитимность хода, просто аппарат его совершения"""
        color1 = Colors[self.turn % 2]
        player = {0: self.player_white, 1: self.player_black}[self.turn % 2]
        # нужно проверить равняется ли move_ хотя бы какому-то ходу в списке ходов игрока
        # ход будем сразу брать из available_moves, фильтровать ходы будем в интерфейсе
        if move_ not in player.possible_moves:
            raise ValueError('move_ not in player.possible_moves')
        else:
            if move_.castle_long():  # ход "длинная рокировка"
                if color1 == 'White':
                    self.__step(['??', 'c1'])
                    self.__step(['??', 'd1'])
                    self.get_cell('c1').occupied.turn += 1
                    # self.castles[:2] = False лучше будем проверять в move_creator один разок
                elif color1 == 'Black':
                    self.__step(['e8', 'c8'])
                    self.__step(['a8', 'd8'])
                    self.get_cell('c8').occupied.turn += 1
                    self.castles[2:] = False
                else:
                    return False
                self.turn += 1
                self.half_turn += 1
                self.move_list.append(move_)
                return True
            elif move_[0] == '0-0':  # ход "короткая рокировка"
                if color1 == 'White':
                    self.__step(['e1', 'g1'])
                    self.__step(['h1', 'f1'])
                    self.get_cell('g1').occupied.turn += 1
                    self.castles[:2] = False
                elif color1 == 'Black':
                    self.__step(['e8', 'g8'])
                    self.__step(['h8', 'f8'])
                    self.get_cell('g8').occupied.turn += 1
                    self.castles[2:] = False
                else:
                    return False
                self.turn += 1
                self.half_turn += 1
                self.move_list.append(move)
                return True
            cell1 = self.get_cell(move[0])
            piece1 = cell1.occupied
            if len(move) == 2:                                                      # обычный ход
                self.__step(move)
                self.half_turn += 1
                if isinstance(piece1, Pawn):
                    self.half_turn = 0
            elif move[-1] == 'x':                                                   # ход "взятие вражеской фигуры"
                cell2 = self.get_cell(move[1])
                move.append(cell2.occupied)
                self.players[cell2.occupied.color].remove_piece(cell2.occupied)
                self.__capture(move)
                self.half_turn = 0
            elif move[-1] == 'passant':                                             # ход "взятие на проходе"
                cell3 = self.get_cell(move[1][0] + move[0][1])
                move.append(cell3.occupied)
                self.players[cell3.occupied.color].remove_piece(cell3.occupied)
                self.__capture(move)
                self.half_turn = 0
            else:
                return False
            piece1.turn += 1
            self.turn += 1
            if isinstance(piece1, Pawn):  # Поднимаем флажок превращения пешки, потом по флажку обращаемся к интерфейсу
                if int(piece1.position[1]) == 1 or int(piece1.position[1]) == 8:
                    move_.optional = 'permutation'
                    self.permutation = True
            self.move_list.append(move_)

    def make_check(self, attacker_, king_):
        self.someone_in_check = king_
        king_.in_check = attacker_
        return True

    def reset_check(self):
        if bool(self.someone_in_check):
            self.someone_in_check.in_check = False
        self.someone_in_check = False
        return True

    def if_on_the_line(self, piece1, piece2):
        """Метод возвращает все клетки между 2мя фигурами (не включая сами фигуры).
        Наличие третьих фигур на этих клетках не проверяется"""
        xy1 = notation_to_xy(piece1.position)
        cells_between = []
        vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
        for vect in vector:
            i = 1               # i - это скаляр, на который умножается вектор. Изначально 1, в конце while -> i += 1
            temp = []
            while 0 <= xy1[0] + i * vect[0] <= 7 and 0 <= xy1[1] + i * vect[1] <= 7:
                cell = self.cells[self.xy_to_index([xy1[0] + i * vect[0], xy1[1] + i * vect[1]])]
                dude = cell.piece
                i += 1
                if dude == piece2:
                    cells_between = temp
                    return cells_between
                else:
                    temp.append(cell)
                    continue
        return cells_between

    def look_for_cells_are_attacked(self):      # смотрим какие клетки атакуются и какие клетки "атакуются"
        self.reset_check()
        for cell in self.cells:
            cell.attacked = [0, 0]
        for player in [self.player_white, self.player_black]:
            direction = {Colors[0]: 1, Colors[1]: -1}[player.color]
            ind = {Colors[0]: 0, Colors[1]: 1}[player.color]
            for figure in player.pieces:             # начинаем с фигур белых
                figure.reset_available_cells()
                piece_xy = notation_to_xy(figure.position)
                if isinstance(figure, Pawn):         # смотрим какие клетки атакует пешка
                    if piece_xy[0] > 0:
                        cell = self([piece_xy[0] - 1, piece_xy[1] + direction])
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = cell.piece
                        if isinstance(dude, King) and dude.color != figure.color:
                            self.make_check(figure, dude)
                    if piece_xy[0] < 7:
                        cell = self([piece_xy[0] + 1, piece_xy[1] + direction])
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = cell.piece
                        if isinstance(dude, King) and dude.color != figure.color:
                            self.make_check(figure, dude)
                    cell_to_move = self([piece_xy[0], piece_xy[1] + direction])
                    if not cell_to_move.piece:
                        figure.add_available_cells(cell_to_move)
                        if figure.turn == 0 and piece_xy[1] == {Colors[0]: 1, Colors[1]: 6}[figure.color]:
                            figure.add_available_cells(self([piece_xy[0], piece_xy[1] + 2 * direction]))
                    continue
                elif isinstance(figure, King):        # смотрим атаки короля по векторам
                    vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
                    for vect in vector:
                        if 0 <= piece_xy[0] + vect[0] <= 7 and 0 <= piece_xy[1] + vect[1] <= 7:
                            cell = self([piece_xy[0] + vect[0], piece_xy[1] + vect[1]])
                            cell.attacked[ind] += 1
                            figure.add_available_cells(cell)
                    continue
                elif isinstance(figure, Knight):      # смотрим атаки коня, пробегаем по всем возможным векторам
                    vector = [[1, 2], [2, 1], [-1, 2], [2, -1], [1, -2], [-2, 1], [-1, -2], [-2, -1]]
                    for vect in vector:
                        if 0 <= piece_xy[0] + vect[0] <= 7 and 0 <= piece_xy[1] + vect[1] <= 7:
                            cell = self([piece_xy[0] + vect[0], piece_xy[1] + vect[1]])
                            cell.attacked[ind] += 1
                            figure.add_available_cells(cell)
                            dude = cell.piece
                            if isinstance(dude, King) and dude.color != figure.color:
                                self.make_check(figure, dude)
                    continue
                vector = []
                if isinstance(figure, Rook):       # вектора для ладьи
                    vector = [[1, 0], [0, -1], [-1, 0], [0, 1]]
                elif isinstance(figure, Bishop):     # вектора для слона
                    vector = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
                elif isinstance(figure, Queen):     # вектора для ферзя
                    vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
                for vect in vector:
                    i = 1       # i - это скаляр, на который умножается вектор. Изначально 1, в конце while -> i += 1
                    while 0 <= piece_xy[0] + i * vect[0] <= 7 and 0 <= piece_xy[1] + i * vect[1] <= 7:
                        cell = self([piece_xy[0] + i * vect[0], piece_xy[1] + i * vect[1]])
                        cell.attacked[ind] += 1
                        figure.add_available_cells(cell)
                        dude = cell.piece
                        i += 1
                        if dude:
                            if isinstance(dude, King) and dude.color != figure.color:
                                self.make_check(figure, dude)
                            break

    def move_creator(self):
        dict_ = {0: self.player_white, 1: self.player_black}
        player = dict_[self.turn % 2]
        previous_player = dict_[(self.turn + 1) % 2]
        mvr_clr = player.color
        king = player.king
        king_xy = self(king.position)
        vector = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]
        attack = {Colors[0]: 1, Colors[1]: 0}[mvr_clr]

        previous_player.reset_possible_moves()      # сбрасываем все ходы предыдущего игрока, обнуляем его связки
        for p in previous_player.pieces:
            p.bounded = False

        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Сперва нужно сделать СВЯЗКИ

        for vect in vector:  # На данном этапе мы просто связываем фигуры, потом будем обрабатывать всё вместе.
            j = 1            # Будем смотреть связки начиная с короля во все стороны векторно. Если на пути встречается
            temp = False     # союзная фигура, а за ней вражеская нужного типа - то союзная привязывается.
            while 0 <= king_xy[0] + j * vect[0] <= 7 and 0 <= king_xy[1] + j * vect[1] <= 7:
                cell = self([king_xy[0] + j * vect[0], king_xy[1] + j * vect[1]])
                dude = cell.piece
                if not dude:
                    j += 1
                    continue
                if dude.color == king.color and not bool(temp):
                    temp = dude
                elif dude.color != king.color:
                    if isinstance(dude, King) or isinstance(dude, Pawn):   # Король и пешка связать никого не могут.
                        break                       # Конь должен отсекаться сам собой т.к. не лежит на линии при атаке.
                    if bool(temp) and self(temp.position) in dude.available_cells:
                        temp.bounded = dude     # Тут мы связываем фигуру только если сперва нашли союзную нам, и
                        if not isinstance(temp, Pawn):  # она атакована следующей несоюзной фигурой.
                            cells_to_stand_on = self.if_on_the_line(dude, king)
                            cells_to_stand_on.append(cell)  # Сразу на месте и ограничиваем доступные клетки фигуры,
                            cells_to_stand_on = set(cells_to_stand_on)
                            temp.available_cells = temp.available_cells.intersection(cells_to_stand_on)
                    break
                j += 1

        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Закончили СВЯЗКИ, пошли ШАХИ

        if self.someone_in_check:             # Рассмотрим сперва наличие шаха на доске
            if self.someone_in_check != player.king:
                raise ValueError('Fatal Error: king in check is not the player king')
            for cell in king.available_cells:  # 1. сперва смотрим ходы короля
                if cell.attacked[attack] == 0:
                    dude = cell.piece
                    if not dude:
                        player.add_possible_moves(Move(self(king.position), cell))
                    elif dude.color != king.color:
                        player.add_possible_moves(Move(self(king.position), cell, 'x'))
            attacker = king.in_check                          # если теперь шах одиночный, то:
            # _________________________________________________ 2,3. смотрим ходы перекрытия и съедения атакующей фигуры
            cells_we_can_stand_on = self.if_on_the_line(attacker, king)     # <- это клетки доступные для перекрытия
            cells_we_can_stand_on.append(self(attacker.position))      # добавляем клетку атакующего, её можно атаковать
            cells_we_can_stand_on = set(cells_we_can_stand_on)
            if self(king.position).attacked[attack] == 1:
                for figure in player.pieces:
                    if isinstance(figure, Pawn) or isinstance(figure, King):
                        continue                                # пешку рассматриваем отдельно (passant-check, etc.)
                    # далее из пересечения этих клеток и клеток, доступных нашей фигуре(K, Q, R, B, not P) делаем ходы
                    for cell in figure.available_cells.intersection(cells_we_can_stand_on):
                        dude = cell.piece
                        if not dude:
                            player.add_possible_moves(Move(self(figure.position), cell))
                        elif dude.color != figure.color:
                            player.add_possible_moves(Move(self(figure.position), cell, 'x'))
                for figure in player.pieces:    # а теперь начинает ебаный ад. Рассматриваем пешки....
                    if isinstance(figure, Pawn):
                        for cell in figure.available_cells.intersection(cells_we_can_stand_on):
                            if cell.position[0] != figure.position[0]:
                                dude = cell.piece
                                if dude == attacker:
                                    player.add_possible_moves(Move(self(figure.position), cell, 'x'))
                            else:
                                if not cell.piece:
                                    player.add_possible_moves(Move(self(figure.position), cell))
                        # А что если возможно взятие на проходе убивающее шахующую пешку????
                        if self.move_list[-1].optional:
                            continue
                        lmv = self.move_list[-1]
                        if isinstance(attacker, Pawn) and lmv[1].piece == attacker and attacker.turn == 1 and\
                                abs(int(lmv[0][1]) - int(lmv[1][1])) == 2 and\
                                attacker.position[0] == figure.position[0]:
                            for cell in figure.available_cells:
                                if cell.position[1] == attacker.position[1]:
                                    player.add_possible_moves(Move(self(figure.position), cell, 'passant'))
            return True

        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= ШАХИ закончили, начинаем обычные ходы

        # ОБЯЗАТЕЛЬНО НУЖНО ПРОВЕРИТЬ СВЯЗКИ ПЕШЕК ОТДЕЛЬНО - ЕСЛИ НА ПОСЛЕДНЕЙ ДОСТУПНОЙ КЛЕТКЕ ПО ДИАГОНАЛИ НЕТ СВЯЗЫВАЮЩЕЙ ФИГУРЫ ТО ГАВНОООО
        for i in range(4):
            if self.castles[i] and self.castles[i].turn > 0:
                self.castles[i] = False
        for figure in player.pieces:
            if isinstance(figure, King):
                for cell in figure.available_cells:
                    if cell.attacked[attack] == 0:
                        if not cell.piece:
                            player.add_possible_moves(Move(self(figure.position), cell))
                        elif cell.piece.color != figure.color:
                            player.add_possible_moves(Move(self(figure.position), cell, 'x'))
                clr = figure.color
                if clr == Colors[0]:
                    if figure.turn > 0:
                        self.castles[:2] = False
                    if self.castles[0]:
                        f = True
                        for cell in [self.cells[i] for i in range(self.notation_to_index(figure.position) + 1, 7)]:
                            dude = cell.piece
                            if cell.attacked[attack] > 0 or dude != self.castles[0]:
                                f = False
                                break
                        if f:
                            m = Move(self(figure.position), self('g1'), '0-0')
                            m.fig_appeared = self.castles[0]
                            player.add_possible_moves(m)
                            del m
                    if self.castles[1]:
                        f = True
                        for cell in [self.cells[i] for i in range(2, self.notation_to_index(figure.position))]:
                            dude = cell.piece
                            if cell.attacked[attack] > 0 or dude != self.castles[1]:
                                f = False
                                break
                        if f:
                            m = Move(self(figure.position), self('c1'), '0-0-0')
                            m.fig_appeared = self.castles[1]
                            player.add_possible_moves(m)
                            del m
                elif clr == Colors[1]:
                    if figure.turn > 0:
                        self.castles[2:] = False
                    if self.castles[2]:
                        f = True
                        for cell in [self.cells[i] for i in range(self.notation_to_index(figure.position) + 1, 63)]:
                            dude = cell.piece
                            if cell.attacked[attack] > 0 or dude != self.castles[2]:
                                f = False
                                break
                        if f:
                            m = Move(self(figure.position), self('g8'), '0-0')
                            m.fig_appeared = self.castles[2]
                            player.add_possible_moves(m)
                            del m
                    if self.castles[3]:
                        f = True
                        for cell in [self.cells[i] for i in range(58, self.notation_to_index(figure.position))]:
                            dude = cell.piece
                            if cell.attacked[attack] > 0 or dude != self.castles[3]:
                                f = False
                                break
                        if f:
                            m = Move(self(figure.position), self('c8'), '0-0-0')
                            m.fig_appeared = self.castles[3]
                            player.add_possible_moves(m)
                            del m
            elif isinstance(figure, Rook) or isinstance(figure, Knight) or isinstance(figure, Bishop) \
                    or isinstance(figure, Queen):
                '''if bool(figure.bounded):
                    if name == 'Knight':  # #
                        continue        # #
                    attacker = figure.bounded
                    cells_to_stand_on = self.if_on_the_line(attacker, king)
                    cells_to_stand_on.append(attacker.cell)
                    cells_to_stand_on = set(cells_to_stand_on)
                    for cell in figure.available_cells.intersection(cells_to_stand_on):
                        if cell != figure.cell:
                            if bool(cell.piece):
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                            else:
                                player.add_possible_moves([figure.cell.position(), cell.position()])'''
                for cell in figure.available_cells:
                    if not cell.piece:
                        player.add_possible_moves(Move(self(figure.position), cell))
                    elif bool(cell.piece) and cell.piece.color != mvr_clr:
                        player.add_possible_moves(Move(self(figure.position), cell, 'x'))
            elif isinstance(figure, Pawn):
                


                if bool(figure.bounded):
                    attacker = figure.bounded
                    if attacker.cell.position()[0] == figure.cell.position()[0]:
                        for cell in figure.available_cells:
                            if cell.position()[0] == figure.cell.position()[0] and cell != figure.cell:
                                if not cell.piece:
                                    player.add_possible_moves([figure.cell.position(), cell.position()])
                    else:
                        for cell in figure.available_cells:
                            if cell.position()[0] != figure.cell.position()[0] and cell.piece == attacker:
                                player.add_possible_moves([figure.cell.position(), cell.position(), 'x'])
                else:
                    for cell in figure.available_cells:
                        if cell.position()[0] == figure.cell.position()[0] and cell != figure.cell:
                            if not cell.piece:
                                player.add_possible_moves([figure.cell.position(), cell.position()])
                        if cell.position()[0] != figure.cell.position()[0]:
                            dude = cell.piece
                            if not dude:
                                if len(self.move_list) == 0 or len(self.move_list[-1]) < 2:
                                    continue
                                lmv = self.move_list[-1]
                                temp = self.get_cell(self.move_list[-1][1]).piece
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
                                                        {'White': 4, 'Black': 3}[king.color] * self.width + i]
                                                    if not cell.piece:
                                                        continue
                                                    nm = cll.piece.__class__.__name__
                                                    clr = cll.piece.color
                                                    if (nm == 'Rook' or nm == 'Queen') and clr != king.color:
                                                        kekw = 1
                                                    if kekw == 1 and (cll.piece == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 2
                                                    if kekw == 2 and (cll.piece == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 3
                                                if kekw == 3:
                                                    continue
                                                for i in range(7, king_xy[1] - 1, -1):
                                                    cll = self.cells[
                                                        {'White': 4, 'Black': 3}[king.color] * self.width + i]
                                                    if not cell.piece:
                                                        continue
                                                    nm = cll.piece.__class__.__name__
                                                    clr = cll.piece.color
                                                    if (nm == 'Rook' or nm == 'Queen') and clr != king.color:
                                                        kekw = 1
                                                    if kekw == 1 and (cll.piece == figure or
                                                                      cll.position() == lmv[1]):
                                                        kekw = 2
                                                    if kekw == 2 and (cll.piece == figure or
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


if __name__ == '__main__':
    pass
