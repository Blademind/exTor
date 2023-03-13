from PyQt6.QtWidgets import *
from PyQt6 import uic


class AdminGui(QMainWindow):
    def __init__(self):
        super(MyGui, self).__init__()
        uic.loadUi("mygui.ui")