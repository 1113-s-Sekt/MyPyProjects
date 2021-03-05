import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ChessBoard import *


def start():
    b = Board('Classic')
    no_checkmate = True
    white = b.player_white
    black = b.player_black
    while no_checkmate:
        player = {0: white, 1: black}[b.turn % 2]
        b.look_for_cells_are_attacked()
        b.move_creator()
        print(f'{player.color} to move')
        player.print_possible_moves()


class MyChessGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('My Chess')
        self.setWindowIcon(QIcon('images/MyChessIcon.png'))
        self.setGeometry(50, 50, 1250, 950)
        self.startButton = QPushButton(self)
        self.startButton.setText('START')
        self.startButton.move(400, 300)
        self.startButton.resize(300, 100)
        self.startButton.show()
        self.startButton.clicked.connect(start)



if __name__ == "__main__":
    gameApp = QApplication(sys.argv)
    gameWindows = MyChessGame()

    gameWindows.show()

    sys.exit(gameApp.exec_())
