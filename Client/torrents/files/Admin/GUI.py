import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from socket import *
import pickle
import ssl

def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            print(e)
    return wrapper


class AdminLoginGui(QMainWindow):
    def __init__(self):
        super(AdminLoginGui, self).__init__()
        uic.loadUi("mygui.ui", self)
        # self.tracker_connection_window()
        self.local_tracker = self.find_local_tracker()

        if self.local_tracker:

            self.setWindowTitle("exTor")
            self.pushButton.clicked.connect(self.pass_password)
            # self.setFixedSize(1,1)
            self.show()

    def pass_password(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        self.sock.connect((self.local_tracker[0], 55556))
        self.sock.send(b"ADMIN")
        data = self.sock.recv(1024)
        print(data)
    def find_local_tracker(self):
        sock = init_udp_sock()
        msg = b'FIND LOCAL TRACKER'
        try:
            sock.sendto(msg, ("255.255.255.255", 12345))
        except Exception as e:
            print(e)
        try:
            data = sock.recv(1024)
            try:
                ip = pickle.loads(data)
                test_open = sock.connect_ex(ip)
                if test_open != 0:
                    self.error_handler("tracker is not connectable")

                print("found local tracker")
                return ip
            except KeyError:
                self.error_handler("fatal error while searching for local tracker")
        except:
            self.error_handler("no response from local tracker")

    # def tracker_connection_window(self):
    #     win = QMainWindow(self)
    #
    #     win.setWindowTitle("Trying connection")
    #     l1 = QLabel()
    #     l1.setText("ASDASDSA")
    #     l1.setAlignment(Qt.AlignCenter)
    #     win.show()
    #
    #     #
    #     # connection_dialog = QWidget()
    #     # connection_dialog.setWindowTitle("Trying connection")
    #     # connection_dialog.setText("Contacting Tracker...")
    #     # connection_dialog.setIcon(QMessageBox.Information)
    #     # sys.exit(connection_dialog.exec_())

    def error_handler(self, msg):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(msg)
        error_dialog.setIcon(QMessageBox.Critical)
        sys.exit(error_dialog.exec_())


@errormng
def init_udp_sock():
    """
    Creates a udp sock listening on given port
    :param port: port of the socket
    :return: the end created socket
    """

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(2)

    sock.bind((get_ip_addr(), 0))
    return sock


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip


def main():
    app = QApplication([])
    LoginWindow = AdminLoginGui()
    app.exec_()


if __name__ == '__main__':
    main()