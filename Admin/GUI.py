import datetime
import random
import threading
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from socket import *
import pickle
import ssl
# from PyQt5.QtChart import QValueAxis,QChart, QChartView, QLineSeries
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np
import warnings
import math
def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            print(e)
    return wrapper


class UI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.LoginWindow = AdminLoginGui()
        self.LoginWindow.show()
        self.app.exec_()
        tracker = self.LoginWindow.local_tracker

        if tracker:  # resets values on tracker side once done
            sock = init_udp_sock()
            sock.sendto(b"DONE_ADMIN_OPERATION", tracker)


class AdminLoginGui(QMainWindow):
    def __init__(self):
        super(AdminLoginGui, self).__init__()
        uic.loadUi("mygui.ui", self)
        # self.tracker_connection_window()
        self.local_tracker = self.find_local_tracker()

        if self.local_tracker:

            self.setWindowTitle("exTor")
            self.pushButton.setShortcut("Return")
            self.pushButton.clicked.connect(self.pass_password)

            # self.setFixedSize(1,1)

    def pass_password(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        self.sock.connect((self.local_tracker[0], 55556))
        self.sock.send(f"USER_PASSWORD {self.user.text()} {self.password.text()}".encode())
        data = self.sock.recv(1024)
        if data == b"SUCCESS":
            self.close()
            self.sock.close()
            self.MainWindow = AdminGui(self.local_tracker)
            self.MainWindow.show()
            # continue to main window
        elif data == b"DENIED":
            self.error_handler("user or password incorrect", close_program=False)

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

    def error_handler(self, msg, close_program=True):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(msg)
        error_dialog.setIcon(QMessageBox.Critical)
        if close_program:
            sys.exit(error_dialog.exec_())
        else:
            error_dialog.exec_()


class AdminGui(QMainWindow):
    def __init__(self, local_tracker):
        super(AdminGui, self).__init__()
        # uic.loadUi("mygui.ui", self)
        self.local_tracker = local_tracker
        self.setWindowTitle("exTor")
        self.setGeometry(100, 100, 680, 500)
        self.create_graph()

        self.sock = init_udp_sock()
        # self.update_plot_data()
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        if np.nan in self.y:
            requests_data = self.fetch_requests()
            requests = requests_data[0]
            print(requests_data[1])

            if requests:
                self.y[self.y.index(np.nan)] = requests
            else:
                self.y[self.y.index(np.nan)] = 0
        else:
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 5)  # Add a new value 1 higher than the last.

            self.y = self.y[1:]  # Remove the first

            requests_data = self.fetch_requests()
            requests = requests_data[0]
            print(requests_data[1])
            if requests:
                self.y.append(requests)  # Add a new random value.
            else:
                self.y.append(0)

        self.data_line.setData(self.x, self.y)  # Update the data.

    def create_graph(self):
        pg.setConfigOptions(antialias=True)
        self.graphWidget = pg.PlotWidget(title="Requests on tracker")
        axis = pg.DateAxisItem()
        self.graphWidget.setAxisItems({'bottom': axis})
        self.graphWidget.setLabel('left', 'Requests')
        self.graphWidget.setLabel('bottom', 'Time')

        self.graphWidget.showGrid(x=True, y=True)

        date_list = [math.floor((datetime.datetime.today() + datetime.timedelta(seconds=i)).timestamp()) for i in range(5, 51, 5)]
        self.x = sorted(date_list, reverse=False)  # 100 time points
        # self.x = [_ for _ in range(5, 51, 5)]
        self.y = [np.nan for _ in range(10)]  # 100 data points

        self.setCentralWidget(self.graphWidget)

        # plot data: x, y values
        pen = pg.mkPen(width=5)
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen, symbol='o')

    def fetch_requests(self):
        try:
            self.sock.sendto(b"FETCH_REQUESTS", self.local_tracker)
            requests = pickle.loads(self.sock.recv(1024))
            return requests
        except Exception as e:
            print(e)
            return


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


if __name__ == '__main__':
    warnings.simplefilter("ignore", category=RuntimeWarning)
    UI()

