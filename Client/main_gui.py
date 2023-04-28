import sys
import datetime
from ui import Ui_MainWindow
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
        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self)
        self.local_tracker = tracker
        self.file_name = ""
        self.ui_main.home_button.clicked.connect(lambda x:self.click_button('Home'))
        self.ui_main.pushButton_BtnServico.clicked.connect(lambda x:self.click_button('Swarms'))
        self.ui_main.pushButton_BtnAssuntos.clicked.connect(lambda x:self.click_button('Banned IPs'))
        self.ui_main.pushButton_BtnAcessoInfo.clicked.connect(lambda x:self.click_button('Log'))

        self._add_action = self.ui_main.toolbar.addAction('Add')
        # self._add_action.triggered.connect(self._add_torrents_triggered)

        self._pause_action = self.ui_main.toolbar.addAction('Pause')
        self._pause_action.setEnabled(False)
        # self._pause_action.triggered.connect(partial(self._control_action_triggered, control.pause))

        self._resume_action = self.ui_main.toolbar.addAction('Resume')
        self._resume_action.setEnabled(False)
        # self._resume_action.triggered.connect(partial(self._control_action_triggered, control.resume))

        self._remove_action = self.ui_main.toolbar.addAction('Remove')
        self._remove_action.setEnabled(False)
        # self._remove_action.triggered.connect(partial(self._control_action_triggered, control.remove))

        self._about_action = self.ui_main.toolbar.addAction('About')
        # self._about_action.triggered.connect(self._show_about)

        # self.ui_main.logWidget.setText(log_data)

        # self.ui_main.pushButton_BtnConfiguracao.clicked.connect(lambda x:self.click_button('CONFIGURAÇÃO'))
        self.hidden = False
        self.sock = init_udp_sock()

        redis_host = "localhost"
        redis_port = 6379
        self.r = redis.StrictRedis(host=redis_host, port=redis_port)

        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.settimeout(5)
        self.tcp_sock = ssl.wrap_socket(self.tcp_sock, server_side=False, keyfile='private-key.pem',
                                        certfile='cert.pem')
        self.tcp_sock.connect((self.local_tracker[0], 55556))

        self.set_dash_value()
        self.show()

    def menu_event(self, obj, event):
        menu = QMenu()
        point = event.pos()
        point.setX(0)
        index = obj.indexAt(point)
        if index.isValid():
            kick = menu.addAction('Kick Peer')  # index.data()
            ban = menu.addAction('Ban Peer')
        else: return

        res = menu.exec_(event.globalPos())
        ip = index.data().split(':')[0], int(index.data().split(':')[1])

        raw_addr = pickle.dumps(ip)
        print(ip)
        if res == kick:
            print("kicked")
            # print(self.file_name, raw_addr)
            print(self.r.lrem(self.file_name, 0, raw_addr))
            print(self.r.delete(raw_addr))
            self.add_to_log(f"Kicked {ip} as prompted")

            self.tcp_sock.send(b"UPDATE_FILES")
            try:
                data = self.tcp_sock.recv(1024)
                if data == b"FLOW":
                    self.tcp_sock.send(pickle.dumps([(raw_addr, self.file_name.encode())]))
            except Exception as e:
                print(e)
                pass

            self.swarms(self.file_name)

            # update table now
        elif res == ban and ip[0] != self.sock.getsockname()[0]:  # ban only if ip is not admin's ip
            print("banned")
            print(self.r.lrem(self.file_name, 0, raw_addr))
            print(self.r.delete(raw_addr))

            self.tcp_sock.send(b"UPDATE_FILES")
            try:
                data = self.tcp_sock.recv(1024)
                if data == b"FLOW":
                    self.tcp_sock.send(pickle.dumps([(raw_addr, self.file_name.encode())]))
            except Exception as e:
                print(e)
                pass

            self.add_to_log(f"Banned {ip[0]} as prompted")
            self.tcp_sock.send(f"BAN_IP {ip[0]}".encode())
            self.swarms(self.file_name)
            # update table now

    def menu_event2(self, obj, event):
        menu = QMenu()
        index = obj.indexAt(event.pos())
        remove = menu.addAction('')
        if index.isValid():
            remove.setText('Remove')  # index.data()
        else:
            remove.setText('No selection')
            remove.setEnabled(False)

        res = menu.exec_(event.globalPos())
        if res == remove:
            self.r.lrem("banned", 0, index.data())
            print("removed")
            banned_ips = self.r.lrange("banned", 0, -1)

            # update table now
    def set_dash_value(self):
        self.ui_main.label_TxtTopDataUserType.setText("Peer")
        self.ui_main.date_widget.setText(self.date_now())

    # Clicked buttons




    # Get date formatted
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
