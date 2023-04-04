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
import bencode
import os
import sqlite3
import atexit
import signal

from customized import PasswordEdit


# ========= BAN IP =========
# self.sock.sendto(f"BAN_IP {addr[0]}".encode(), self.local_tracker)

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
        global tracker
        self.app = QApplication(sys.argv)
        self.AdminLoginWindow = AdminLoginGui()
        self.AdminLoginWindow.show()
        self.app.exec_()
        tracker = self.AdminLoginWindow.local_tracker

        if tracker:  # resets values on tracker side once done
            sock = init_udp_sock()
            sock.sendto(b"DONE_ADMIN_OPERATION", tracker)


class AdminLoginGui(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_tracker = self.find_local_tracker()

        if self.local_tracker:
            self.setup_ui()

    def setup_ui(self):
        """Setup the login form.
        """
        self.resize(480, 625)
        # remove the title bar

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setStyleSheet(
            """
            QPushButton {
                border-style: outset;
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
            """
        )

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_3 = QHBoxLayout()

        self.widget = QWidget(self)
        self.widget.setMaximumSize(QSize(16777215, 16777215))
        self.widget.setStyleSheet(".QWidget{background-color: rgb(20, 20, 40);}")

        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(9, 0, 0, 0)

        self.pushButton_3 = QPushButton(self.widget)
        self.pushButton_3.setMinimumSize(QSize(35, 25))
        self.pushButton_3.setMaximumSize(QSize(35, 25))

        self.pushButton_3.setStyleSheet("color: white;\n"
                                        "font: 13pt \"Verdana\";\n"
                                        "border-radius: 1px;\n"
                                        "opacity: 200;\n")
        self.pushButton_3.clicked.connect(self.close)

        self.verticalLayout_2.addWidget(self.pushButton_3, 0, Qt.AlignRight)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, 15, -1, -1)

        self.label = QLabel(self.widget)
        self.label.setMinimumSize(QSize(100, 150))
        self.label.setMaximumSize(QSize(150, 150))
        self.label.setStyleSheet("image: url(icons/logo.png);")
        self.verticalLayout_3.addWidget(self.label, 0, Qt.AlignHCenter)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setContentsMargins(50, 35, 59, -1)

        self.label_2 = QLabel(self.widget)
        self.label_2.setStyleSheet("color: rgb(231, 231, 231);\n"
                                   "font: 15pt \"Verdana\";")
        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setMinimumSize(QSize(0, 40))
        self.lineEdit.setStyleSheet("QLineEdit {\n"
                                    "color: rgb(231, 231, 231);\n"
                                    "font: 15pt \"Verdana\";\n"
                                    "border: None;\n"
                                    "border-bottom-color: white;\n"
                                    "border-radius: 10px;\n"
                                    "padding: 0 8px;\n"
                                    "background: rgb(20, 20, 40);\n"
                                    "selection-background-color: darkgray;\n"
                                    "}")
        self.lineEdit.setFocus(True)
        self.lineEdit.setPlaceholderText("Username")
        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.lineEdit)

        # self.label_4 = QLabel(self.widget)
        # self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.label_3 = QLabel(self.widget)
        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_3)

        # self.lineEdit_3 = QLineEdit(self.widget)
        # self.lineEdit_3.setMinimumSize(QSize(0, 40))
        # self.lineEdit_3.setStyleSheet("QLineEdit {\n"
        #                               "color: rgb(231, 231, 231);\n"
        #                               "font: 15pt \"Verdana\";\n"
        #                               "border: None;\n"
        #                               "border-bottom-color: white;\n"
        #                               "border-radius: 10px;\n"
        #                               "padding: 0 8px;\n"
        #                               "background: rgb(20, 20, 40);\n"
        #                               "selection-background-color: darkgray;\n"
        #                               "}")
        # self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3)

        self.lineEdit_2 = PasswordEdit(self.widget)
        self.lineEdit_2.setMinimumSize(QSize(0, 40))
        self.lineEdit_2.setStyleSheet("QLineEdit {\n"
                                      "color: #0080FB;\n"
                                      "font: 15pt \"Verdana\";\n"
                                      "border: None;\n"
                                      "border-bottom-color: white;\n"
                                      "border-radius: 10px;\n"
                                      "padding: 0 8px;\n"
                                      "background: rgb(20, 20, 40);\n"
                                      "selection-background-color: darkgray;\n"
                                      "}")
        self.lineEdit_2.setPlaceholderText("Password")
        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.lineEdit_2)
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

        # self.line = QFrame(self.widget)
        # self.line.setStyleSheet("border: 2px solid white;")
        # self.line.setFrameShape(QFrame.HLine)
        # self.line.setFrameShadow(QFrame.Sunken)
        # self.formLayout_2.setWidget(1, QFormLayout.SpanningRole, self.line)

        self.line_3 = QFrame(self.widget)
        self.line_3.setStyleSheet("border: 2px solid white;")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.formLayout_2.setWidget(3, QFormLayout.SpanningRole, self.line_3)

        self.line_2 = QFrame(self.widget)
        self.line_2.setStyleSheet("border: 2px solid #0080FB;")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.formLayout_2.setWidget(5, QFormLayout.SpanningRole, self.line_2)

        self.pushButton = QPushButton(self.widget)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())

        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QSize(0, 60))
        self.pushButton.setAutoFillBackground(False)
        self.pushButton.setStyleSheet("color: rgb(231, 231, 231);\n"
                                      "font: 17pt \"Verdana\";\n"
                                      "border: 2px solid #0080FB;\n"
                                      "padding: 5px;\n"
                                      "border-radius: 3px;\n"
                                      "opacity: 200;\n"
                                      "")
        self.pushButton.setAutoDefault(True)
        self.pushButton.setShortcut("Return")
        self.formLayout_2.setWidget(7, QFormLayout.SpanningRole, self.pushButton)

        # self.pushButton_2 = QPushButton(self.widget)
        # self.pushButton_2.setMinimumSize(QSize(0, 60))
        # self.pushButton_2.setStyleSheet("color: rgb(231, 231, 231);\n"
        #                                 "font: 17pt \"Verdana\";\n"
        #                                 "border: 2px solid #0080FB;\n"
        #                                 "padding: 5px;\n"
        #                                 "border-radius: 3px;\n"
        #                                 "opacity: 200;\n"
        #                                 "")
        # self.pushButton_2.setDefault(False)
        # self.pushButton_2.setFlat(False)
        # self.formLayout_2.setWidget(8, QFormLayout.SpanningRole, self.pushButton_2)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                           QSizePolicy.Expanding)
        self.formLayout_2.setItem(6, QFormLayout.SpanningRole, spacerItem)
        self.verticalLayout_3.addLayout(self.formLayout_2)

        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                            QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalLayout_3.addWidget(self.widget)
        self.horizontalLayout_3.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_3.setText(_translate("Form", "X"))
        self.label_2.setText(_translate(
            "Form",
            "<html><head/><body><p><img src=\"icons/user_32x32.png\"/></p></body></html>"))
        self.label_3.setText(_translate(
            "Form",
            "<html><head/><body><p><img src=\"icons/lock_32x32.png\"/></p></body></html>"))
        # self.label_4.setText(_translate(
        #     "Form",
        #     "<html><head/><body><p><img src=\"icons/mail_32x32.png\"/></p></body></html>"))
        self.pushButton.setText(_translate("Form", "Sign In"))
        self.pushButton.clicked.connect(self.pass_password)

        # self.pushButton_2.setText(_translate("Form", "Register"))
    def pass_password(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        self.sock.connect((self.local_tracker[0], 55556))
        print("user:", self.lineEdit.text(), "password:", self.lineEdit_2.text())
        self.sock.send(f"USER_PASSWORD {self.lineEdit.text()} {self.lineEdit_2.text()}".encode())
        data = self.sock.recv(1024)
        if data == b"SUCCESS":
            self.close()
            self.sock.close()
            self.MainWindow = AdminGui(self.local_tracker)
            self.MainWindow.show()
            # continue to main window
        elif b"DENIED" in data:
            self.error_handler(data[7:].decode(), close_program=False)

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
        error_dialog.setText(msg)
        error_dialog.setIcon(QMessageBox.Critical)
        if close_program:
            sys.exit(error_dialog.exec_())
        else:
            error_dialog.exec_()


class AdminGui(QMainWindow):
    def __init__(self, local_tracker):
        super(AdminGui, self).__init__()
        self.local_tracker = local_tracker
        self.setWindowTitle("exTor")
        self.setGeometry(100, 100, 680, 500)
        self.create_graph()
        if not os.path.exists("databases"):
            os.makedirs("databases")
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.settimeout(5)
        self.tcp_sock = ssl.wrap_socket(self.tcp_sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        self.tcp_sock.connect((self.local_tracker[0], 55556))

        self.__BUF = 1024

        self.db_lock = threading.Lock()
        threading.Thread(target=self.deleter_timer).start()

        self.sock = init_udp_sock()
        # self.update_plot_data()
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    @errormng
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

    def deleter_timer(self):
        """
        removes ip after an hour (according to protocol)
        :return: None
        """
        timer = 20
        while 1:
            queries = []
            recv_db_status = self.recv_db()
            if recv_db_status != "success":  # error along the way
                print(recv_db_status)
                break
            else:
                print("SUCCESS UPDATE.")
            self.db_lock.acquire()  # acquire lock for db data to not change during operation

            conn = sqlite3.connect("databases\\swarms_data.db")
            curr = conn.cursor()
            # adds all ips-times into one list
            curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='BannedIPs';")
            table_names = curr.fetchall()
            print(table_names)
            for file_name in table_names:
                curr.execute(f"""SELECT * FROM "{file_name[0]}" """)
                records = curr.fetchall()

                for raw_addr, time_added, _ in records:
                    addr = pickle.loads(raw_addr)
                    if time.time() - time_added >= timer:
                        query = f"""DELETE FROM "{file_name[0]}" WHERE address=?"""
                        queries.append((query, raw_addr, file_name[0]))

                        curr.execute(query, (raw_addr,))
                        conn.commit()
                        # self.sock.sendto(f"BAN_IP {addr[0]}".encode(), self.local_tracker)

            conn.close()
            print(queries)
            if queries:
                self.tcp_sock.send(b"QUERIES")
                try:
                    data = self.tcp_sock.recv(self.__BUF)
                    if data == b"FLOW":
                        self.tcp_sock.send(pickle.dumps(queries))
                except:
                    pass

            self.db_lock.release()  # release lock so database can be used again

            time.sleep(20)

    # def get_db_data(self):

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

    def recv_db(self):
        """

        :return: success if passed, [error] if error
        """
        print("db download started")
        self.tcp_sock.send(b"REQUEST_DB")

        db_name = "swarms_data.db"
        if db_name[-3:] != ".db":
            return "file is not database"
        self.db_lock.acquire()
        f = open(f"databases\\{db_name}", "w")
        f.close()
        try:
            self.tcp_sock.send("FLOW".encode())
            s = 0
            length = int(pickle.loads(self.tcp_sock.recv(self.__BUF)))  # awaiting client to send the file's length
            print(f"torrent swarms db download has started ({length} bytes)")
            while s != length:
                data = self.tcp_sock.recv(self.__BUF)
                s += len(data)
                with open(f"databases\\{db_name}", "ab") as f:
                    f.write(data)
                if length != s:
                    self.tcp_sock.send("FLOW".encode())
            print(f"done downloading {db_name}")
            self.tcp_sock.send(b"DONE")
            self.db_lock.release()  # release lock so database can be used again

            return "success"

        except Exception as e:
            return e




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
    os._exit(0)
