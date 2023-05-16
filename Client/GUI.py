__author__ = "Alon Levy"
__nick__ = "Blademind"
__email__ = "alonlevy2005@gmail.com"


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from socket import *
import pickle
import warnings
import os
from main import MainWindow
import signal

def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            print(e)
    return wrapper


def mousePressEvent(obj, event):
    obj.oldPos = event.globalPos()


def mouseMoveEvent(obj, event):
    delta = QPoint (event.globalPos() - obj.oldPos)
    obj.move(obj.x() + delta.x(), obj.y() + delta.y())
    obj.oldPos = event.globalPos()


class UI:
    def __init__(self):
        global tracker
        self.app = QApplication(sys.argv)
        self.tracker = self.find_local_tracker()
        if self.tracker:
            self.MainWindow = MainWindow(self.tracker)
            self.MainWindow.show()
            self.app.exec_()
        else:
            print("IT CANNOT GET HERE!!!! WTF!!!!!")

    def find_local_tracker(self):
        sock = init_udp_sock()
        msg = b'FIND_LOCAL_TRACKER'
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

    def error_handler(self, msg, close_program=True):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error")
        # error_dialog.setWindowFlags(Qt.FramelessWindowHint)
        error_dialog.setStyleSheet(
            """
            QPushButton {
                border-style: outset;
                color: white;
                border-radius: 0px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0080FB;
                border-style: inset;
            }
            QPushButton:pressed {
                background-color: #43A6C6;
                border-style: inset;
            }
            QMessageBox{
                background-color: rgb(20, 20, 40);
                font: 13pt "Verdana";
                padding: 5px;
                border-radius: 3px;
                opacity: 200;
                }
            QMessageBox QLabel{
                color: white;
                }
            """

        )
        error_dialog.mouseMoveEvent = lambda event: mouseMoveEvent(error_dialog, event)
        error_dialog.mousePressEvent = lambda event: mousePressEvent(error_dialog, event)

        error_dialog.setText(msg)
        error_dialog.setIcon(QMessageBox.Critical)
        if close_program:
            sys.exit(error_dialog.exec_())
        else:
            error_dialog.exec_()

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


def exit_function():
    print("\nprogram ended")
    ui.MainWindow.interrupt_event.set()
    # for pr in ui.MainWindow.processes:
    #     os.kill(pr.pid, signal.SIGTERM)
    #     # pr.kill()
    os._exit(0)


if __name__ == '__main__':
    warnings.simplefilter("ignore", category=RuntimeWarning)
    ui = UI()
    exit_function()
