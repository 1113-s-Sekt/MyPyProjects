import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ChessBoard import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.state = 0
        self.Board = Board('Classic')
        self.Board.look_for_cells_are_attacked()
        self.Board.move_creator()
        self.cell_active = 0
        self.cells_to_move = []
        self.cells_to_passant = []
        self.cells_to_rocky = []
        self.change = 0
        self.imgEnt = QImage("Pictures/EnterFigure.png")
        self.imgMove = QImage("Pictures/MoveAvailable.png")
        self.imgAttack = QImage("Pictures/Attack.png")

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.state == 1:
            if self.change != 0:
                painter.drawImage(QRect(0, 0, 600, 600), chess[0])
                for cell in self.Board.cells:
                    if cell.occupied != 0:
                        painter.drawImage(QRect(cell.pos()[0]*72+20, (7-cell.pos()[1])*70+10, 72, 72), cell.occupied.image)
                    if cell == self.cell_active:
                        painter.drawImage(QRect(cell.pos()[0] * 72 + 20, (7 - cell.pos()[1]) * 70 + 10, 72, 72),
                                          self.imgEnt)
                    elif cell in self.cells_to_move:
                        if cell.occupied == 0:
                            painter.drawImage(QRect(cell.pos()[0] * 72 + 20, (7 - cell.pos()[1]) * 70 + 10, 72, 72),
                                              self.imgMove)
                        else:
                            painter.drawImage(QRect(cell.pos()[0] * 72 + 20, (7 - cell.pos()[1]) * 70 + 10, 72, 72),
                                              self.imgAttack)
                    elif cell in self.cells_to_passant:
                        painter.drawImage(QRect(cell.pos()[0] * 72 + 20, (7 - cell.pos()[1]) * 70 + 10, 72, 72),
                                          self.imgAttack)
                    elif cell in self.cells_to_rocky:
                        painter.drawImage(QRect(cell.pos()[0] * 72 + 20, (7 - cell.pos()[1]) * 70 + 10, 72, 72),
                                          self.imgMove)
                if self.Board.someone_in_check:
                    for piece in self.Board.players[['White', 'Black'][self.Board.turn % 2]].pieces:
                        if str(piece) in ['♔', '♚']:
                            painter.drawImage(QRect(piece.cell.pos()[0] * 72 + 20, (7 - piece.cell.pos()[1]) * 70 + 10, 72, 72),
                                              self.imgAttack)
                self.change = 0
                print("End of update")

    def mousePressEvent(self, event):
        if self.state == 0:
            return None
        print(event)
        px, py = event.pos().x(), event.pos().y()
        if px in range(20, 596) and py in range(10, 570):
            x = (px-20)//72
            y = (py-10)//70
            print(x, y)
            cellEnt = self.Board.get_cell_by_notation("abcdefgh"[x] + "12345678"[7-y])
            self.change = 1
            print(cellEnt.position())
            print(cellEnt.occupied)
            if self.cell_active == 0:
                if cellEnt.occupied != 0 and cellEnt.occupied.color == ['White', 'Black'][self.Board.turn % 2]:
                    self.cell_active = cellEnt
                    self.cells_to_move = []
                    self.cells_to_passant = []
                    self.cells_to_rocky = []
                    print(self.cell_active)
                    for move in self.Board.players[['White', 'Black'][self.Board.turn % 2]].possible_moves:
                        print(move)
                        if cellEnt.position() == move[0]:
                            cell2 = self.Board.get_cell_by_notation(move[1])
                            if len(move) == 3 and move[2] == 'passant' and str(cellEnt) in ['♟', '♙']:
                                self.cells_to_passant.append(cell2)
                            else:
                                self.cells_to_move.append(cell2)
                        if move[0] == "0-0" and str(cellEnt) in ['♔', '♚']:
                            if self.Board.turn % 2 == 0:
                                self.cells_to_rocky.append(self.Board.get_cell_by_notation("g1"))
                            else:
                                self.cells_to_rocky.append(self.Board.get_cell_by_notation("g8"))
                        if move[0] == "0-0-0" and str(cellEnt) in ['♔', '♚']:
                            if self.Board.turn % 2 == 0:
                                self.cells_to_rocky.append(self.Board.get_cell_by_notation("c1"))
                            else:
                                self.cells_to_rocky.append(self.Board.get_cell_by_notation("c8"))
                    print(self.cells_to_move)
                else:
                    self.cells_to_move = []
                    self.cells_to_passant = []
                    self.cells_to_rocky = []
            else:
                if cellEnt in self.cells_to_move:
                    if cellEnt.occupied == 0:
                        self.Board.move([self.cell_active.position(), cellEnt.position()])
                        self.Board.look_for_cells_are_attacked()
                        self.Board.move_creator()
                    elif cellEnt.occupied.color == ['White', 'Black'][(self.Board.turn+1) % 2]:
                        self.Board.move([self.cell_active.position(), cellEnt.position(), 'x'])
                        self.Board.look_for_cells_are_attacked()
                        self.Board.move_creator()
                    self.cell_active = 0
                    self.cells_to_move = []
                    self.cells_to_passant = []
                    self.cells_to_rocky = []
                    if len(self.Board.players[['White', 'Black'][self.Board.turn % 2]].possible_moves) == 0:
                        congrats(self.Board.players[['White', 'Black'][(self.Board.turn+1) % 2]])
                elif cellEnt in self.cells_to_passant:
                    self.Board.move([self.cell_active.position(), cellEnt.position(), "passant"])
                    self.Board.look_for_cells_are_attacked()
                    self.Board.move_creator()
                    self.cell_active = 0
                    self.cells_to_move = []
                    self.cells_to_passant = []
                    self.cells_to_rocky = []
                    if len(self.Board.players[['White', 'Black'][self.Board.turn % 2]].possible_moves) == 0:
                        congrats(self.Board.players[['White', 'Black'][(self.Board.turn+1) % 2]])
                elif cellEnt in self.cells_to_rocky:
                    if cellEnt.position() in ["g1", "g8"]:
                        self.Board.move(["0-0"])
                    else:
                        self.Board.move(["0-0-0"])
                    self.Board.look_for_cells_are_attacked()
                    self.Board.move_creator()
                    self.cell_active = 0
                    self.cells_to_move = []
                    self.cells_to_passant = []
                    self.cells_to_rocky = []
                    if len(self.Board.players[['White', 'Black'][self.Board.turn % 2]].possible_moves) == 0:
                        congrats(self.Board.players[['White', 'Black'][(self.Board.turn+1) % 2]])
                else:
                    if cellEnt.occupied != 0 and cellEnt.occupied.color == ['White', 'Black'][self.Board.turn % 2]:
                        self.cell_active = cellEnt
                        self.cells_to_move = []
                        self.cells_to_passant = []
                        self.cells_to_rocky = []
                        for move in self.Board.players[['White', 'Black'][self.Board.turn % 2]].possible_moves:
                            if cellEnt.position() == move[0]:
                                cell2 = self.Board.get_cell_by_notation(move[1])
                                if len(move) == 3 and move[2] == 'passant' and str(cellEnt) in ['♟', '♙']:
                                    self.cells_to_passant.append(cell2)
                                else:
                                    self.cells_to_move.append(cell2)
                            if move[0] == "0-0" and str(cellEnt) in ['♔', '♚']:
                                if self.Board.turn % 2 == 0:
                                    self.cells_to_rocky.append(self.Board.get_cell_by_notation("g1"))
                                else:
                                    self.cells_to_rocky.append(self.Board.get_cell_by_notation("g8"))
                            if move[0] == "0-0-0" and str(cellEnt) in ['♔', '♚']:
                                if self.Board.turn % 2 == 0:
                                    self.cells_to_rocky.append(self.Board.get_cell_by_notation("c1"))
                                else:
                                    self.cells_to_rocky.append(self.Board.get_cell_by_notation("c8"))
                    else:
                        self.cells_to_move = []
                        self.cells_to_passant = []
                        self.cells_to_rocky = []
                        self.cell_active = 0
        self.update()


app = QApplication(sys.argv)
mainW = MainWindow()


def new_game():
    mainW.state = 1
    mainW.change = 1
    mainW.Board = Board('Classic')
    mainW.Board.look_for_cells_are_attacked()
    mainW.Board.move_creator()
    btn1.hide()
    mainW.update()


def main_menu():
    mainW.state = 0
    btn1.show()


def congrats(player):
    r = QMessageBox.question(mainW, "Congrats", str(player)+' won the Game, congratulations!', QMessageBox.Ok, QMessageBox.Ok)
    if r == QMessageBox.Ok:
        main_menu()


mainW.resize(600, 600)
mainW.setWindowTitle("Chess")
# r = QMessageBox.question(mainW, "Congrats", ' won the Game, congratulations!', QMessageBox.Ok, QMessageBox.Ok)

chess = [QImage("Pictures/ChessBoard.png")]
print(chess)
btn1 = QPushButton(mainW)
print(1)
btn1.move(200, 100)
print(2)
btn1.setText("New Game")
print(3)
btn1.clicked.connect(new_game)
print(4)
btn1.show()
print(5)
mainW.show()
sys.exit(app.exec_())
