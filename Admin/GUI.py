from PyQt5.QtWidgets import *
from PyQt5 import uic


class AdminGui(QMainWindow):
    def __init__(self):
        super(AdminGui, self).__init__()
        uic.loadUi("mygui.ui", self)
        self.show()


def main():
    app = QApplication([])
    window = AdminGui()
    app.exec_()


if __name__ == '__main__':
    main()