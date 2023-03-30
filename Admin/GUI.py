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
        elif b"DENIED" in data:
            self.error_handler(data[7:].decode(), close_program=False)

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
        timer = 60
        while 1:
            queries = []
            recv_db_status = self.recv_db()
            if recv_db_status != "success":  # error along the way
                print(recv_db_status)
                break
            else:
                print("SUCCESS UPDATE.")
            self.db_lock.acquire()  # acquire lock for db data to not change during operation

            conn = sqlite3.connect("databases\\torrent_swarms.db")
            curr = conn.cursor()
            # adds all ips-times into one list
            curr.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = curr.fetchall()
            for file_name in table_names:
                curr.execute(f"""SELECT * FROM "{file_name[0]}" """)
                records = curr.fetchall()
                for raw_addr, time_added, tokens in records:
                    # addr = pickle.loads(raw_addr)
                    if time.time() - time_added >= timer:
                        queries.append((f"""DELETE FROM "{file_name[0]}" WHERE address=?""", raw_addr, file_name[0]))

                        curr.execute(f"""DELETE FROM "{file_name[0]}" WHERE address=?""", (raw_addr,))
                        conn.commit()

                        # if os.path.exists(f"torrents\\{file_name[0]}"):
                        #     print(f"removed {addr} from {file_name[0]}")
                        #     with open(f"torrents\\{file_name[0]}", "rb") as f:
                        #         torrent_data = bencode.bdecode(f.read())
                        #
                        #     for i in torrent_data["announce-list"]:
                        #         if list(addr) == i:
                        #             torrent_data["announce-list"].remove(i)
                        #             break
                        #
                        #     with open(f"torrents\\{file_name[0]}", "wb") as f:
                        #         f.write(bencode.bencode(torrent_data))
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

        db_name = "torrent_swarms.db"
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

