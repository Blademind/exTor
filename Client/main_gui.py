import sys
import datetime
import ui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import warnings
import time
import redis
import numpy as np
import threading
import pickle
from socket import *
import ssl
from main import Handler
from multiprocessing import Process

def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            print(e)
    return wrapper


class MainWindow(QMainWindow):
    def __init__(self, tracker):
        QMainWindow.__init__(self)

        ui.init_win()
        self.ui_main = ui.ui_main
        print(self.ui_main)
        self.ui_main.setupUi(self)
        self.local_tracker = tracker
        self.file_name = ""
        # self.ui_main.home_button.clicked.connect(lambda x:self.click_button('Home'))
        # self.ui_main.pushButton_BtnServico.clicked.connect(lambda x:self.click_button('Swarms'))
        # self.ui_main.pushButton_BtnAssuntos.clicked.connect(lambda x:self.click_button('Banned IPs'))
        # self.ui_main.pushButton_BtnAcessoInfo.clicked.connect(lambda x:self.click_button('Log'))

        self.ui_main.textEdit_TxtTopSearch.returnPressed.connect(
            lambda: self.torrent_triggered(query=self.ui_main.textEdit_TxtTopSearch.text()))

        self._add_action = self.ui_main.toolbar.addAction('Add')
        self._add_action.triggered.connect(self.torrent_triggered)

        self._pause_action = self.ui_main.toolbar.addAction('Pause')
        self._pause_action.setEnabled(False)
        # self._pause_action.triggered.connect(partial(self._control_action_triggered, control.pause))

        self._resume_action = self.ui_main.toolbar.addAction('Resume')
        self._resume_action.setEnabled(False)
        # self._resume_action.triggered.connect(partial(self._control_action_triggered, control.resume))

        self._remove_action = self.ui_main.toolbar.addAction('Remove')
        self._remove_action.setEnabled(False)
        # self._remove_action.triggered.connect(partial(self._control_action_triggered, control.remove))

        # self.ui_main.logWidget.setText(log_data)

        # self.ui_main.pushButton_BtnConfiguracao.clicked.connect(lambda x:self.click_button('CONFIGURAÇÃO'))
        self.hidden = False
        # self.sock = init_udp_sock()

        # self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        # self.tcp_sock.settimeout(5)
        # self.tcp_sock = ssl.wrap_socket(self.tcp_sock, server_side=False, keyfile='private-key.pem',
        #                                 certfile='cert.pem')
        # self.tcp_sock.connect((self.local_tracker[0], 55556))
        # self.threads = []
        self.set_dash_value()
        self.show()

    def torrent_triggered(self, query=None):
        if query:
            print(query)
            vbox = QVBoxLayout(self.ui_main.frame_2)

            self.ui_main._name_label = QLabel()
            # self._name_label.setFont(TorrentListWidgetItem._name_font)
            vbox.addWidget(self.ui_main._name_label)

            self.ui_main._upper_status_label = QLabel()
            # self._upper_status_label.setFont(TorrentListWidgetItem._stats_font)
            vbox.addWidget(self.ui_main._upper_status_label)

            self.ui_main._progress_bar = QProgressBar()
            self.ui_main._progress_bar.setFixedHeight(15)
            self.ui_main._progress_bar.setMaximum(1000)
            vbox.addWidget(self.ui_main._progress_bar)

            self.ui_main._lower_status_label = QLabel()
            # self._lower_status_label.setFont(TorrentListWidgetItem._stats_font)
            vbox.addWidget(self.ui_main._lower_status_label)

            p = Process(target=Handler, args=(None, None, None, query))
            p.start()

    def set_dash_value(self):
        self.ui_main.label_TxtTopDataUserType.setText("User")
        self.ui_main.date_widget.setText(self.date_now())

    def date_now(self):
        now = datetime.datetime.now()
        return str(now.strftime("%A %d/%m/%Y")).capitalize()

@errormng
def init_udp_sock():
    """
    Creates a udp sock listening on given port
    :param port: port of the socket
    :return: the end created socket
    """

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(1)

    sock.bind((get_ip_addr(), 0))
    return sock


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip
    return sock


if __name__ == "__main__":
    warnings.simplefilter("ignore", category=RuntimeWarning)

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass
