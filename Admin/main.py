import sys
import json
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
    def __init__(self, tracker, username):
        QMainWindow.__init__(self)
        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self)
        self.local_tracker = tracker

        self.ui_main.pushButton_BtnDeclarar.clicked.connect(lambda x:self.click_button('Home'))
        self.ui_main.pushButton_BtnServico.clicked.connect(lambda x:self.click_button('Swarms'))
        self.ui_main.pushButton_BtnAssuntos.clicked.connect(lambda x:self.click_button('Banned IPs'))
        self.ui_main.pushButton_BtnAcessoInfo.clicked.connect(lambda x:self.click_button('Log'))

        self.ui_main.pushButton_BtnConfiguracao.clicked.connect(lambda x:self.click_button('CONFIGURAÇÃO'))
        self.hidden = False

        self.set_dash_value(username)
        threading.Thread(target=self.deleter_timer).start()
        self.sock = init_udp_sock()
        redis_host = "localhost"
        redis_port = 6379
        self.r = redis.StrictRedis(host=redis_host, port=redis_port)


        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.show()

    def fetch_requests(self):
        try:
            self.sock.sendto(b"FETCH_REQUESTS", self.local_tracker)
            requests = self.sock.recv(1024)
            requests = pickle.loads(requests)
            return requests
        except Exception as e:
            print(e)
            return

    @errormng
    def update_plot_data(self):

        if np.nan in self.ui_main.y:
            requests_data = self.fetch_requests()
            requests = requests_data[0]

            if requests:
                self.ui_main.y[self.ui_main.y.index(np.nan)] = requests
            else:
                self.ui_main.y[self.ui_main.y.index(np.nan)] = 0
        else:
            self.ui_main.x = self.ui_main.x[1:]  # Remove the first y element.
            self.ui_main.x.append(self.ui_main.x[-1] + 5)  # Add a new value 1 higher than the last.

            self.ui_main.y = self.ui_main.y[1:]  # Remove the first

            requests_data = self.fetch_requests()
            requests = requests_data[0]
            if requests:
                self.ui_main.y.append(requests)  # Add a new random value.
            else:
                self.ui_main.y.append(0)

        self.ui_main.data_line.setData(self.ui_main.x, self.ui_main.y)  # Update the data.

    # Set values in Dash
    def deleter_timer(self):
        """
        removes ip after an hour (according to protocol)
        :return: None
        """
        timer = 120
        tcp_sock = socket(AF_INET, SOCK_STREAM)
        tcp_sock.settimeout(5)
        tcp_sock = ssl.wrap_socket(tcp_sock, server_side=False, keyfile='private-key.pem',
                                        certfile='cert.pem')
        tcp_sock.connect((self.local_tracker[0], 55556))
        try:
            self.r.ping()
            while 1:
                ip_files = []
                table_names = self.r.keys("*.torrent*")
                for file_name in table_names:
                    records = self.r.lrange(file_name, 0, -1)

                    for raw_addr in records:
                        time_added = self.r.get(raw_addr)
                        if time.time() - float(time_added) >= timer:
                            self.r.lrem(file_name, 0, raw_addr)
                            self.r.delete(raw_addr)
                            ip_files.append((raw_addr, file_name))
                if ip_files:
                    tcp_sock.send(b"UPDATE_FILES")
                    try:
                        data = tcp_sock.recv(1024)
                        if data == b"FLOW":
                            tcp_sock.send(pickle.dumps(ip_files))
                    except Exception as e:
                        print(e)
                        pass
                time.sleep(1)
        except:
            pass

    def set_dash_value(self, username):
        self.ui_main.label_TxtTopDataUser.setText(username)
        self.ui_main.label_TxtTopDataUserType.setText("Admin")
        # self.ui_main.label_TxtValorRestituicao.setText("R$"+data_dict.get('receita_value'))
        # self.ui_main.pushButton_TopAlert.setText(data_dict.get('notification'))
        self.ui_main.lineEdit_TxtDataAtual.setText(self.date_now())

    # Clicked buttons
    def click_button(self,value):
        print("CLICKED", value)
        if value == "Home":
            # Object hide before showing graph, change text as well
            self.ui_main.table.hide()
            self.ui_main.label_TitleDash.setText("Requests on Tracker")
            self.ui_main.label_SubTitleDash.setText("UDP tracker requests")
            self.ui_main.graphWidget.show()
        elif value == "Swarms":
            self.ui_main.graphWidget.hide()
            self.ui_main.table.doubleClicked.connect(self.swarms)
            self.ui_main.label_TitleDash.setText("Swarms")
            self.ui_main.label_SubTitleDash.setText("Group of Peers per local file")
            files = self.r.keys("*.torrent*")
            if files:
                self.ui_main.table.setColumnCount(1)
                self.ui_main.table.setRowCount(len(files))
                self.ui_main.table.setHorizontalHeaderLabels(['File Name'])
                print(files)
                for i, file in enumerate(files):
                    self.ui_main.table.setItem(i, 0, QTableWidgetItem(file.decode()))
                    self.ui_main.table.item(i, 0).setBackground(QColor(41,40,62))
                    self.ui_main.table.item(i, 0).setForeground(QColor("white"))
                self.ui_main.table.show()
            else:
                self.ui_main.label_SubTitleDash.setText("Sorry, no groups are available")

    def swarms(self, item):
        self.ui_main.table.setColumnCount(2)
        file = item.data()

        peers = self.r.lrange(file, 0, -1)
        print(peers)
        self.ui_main.table.setRowCount(len(peers))
        for i, peer_raw in enumerate(peers):
            peer = pickle.loads(peer_raw)
            ip = f"{peer[0]}:{peer[1]}"
            time_added = str(datetime.timedelta(seconds=float(self.r.get(peer_raw))))
            self.ui_main.table.setItem(i, 0, QTableWidgetItem(ip))
            self.ui_main.table.item(i, 0).setBackground(QColor(41, 40, 62))
            self.ui_main.table.item(i, 0).setForeground(QColor("white"))
            self.ui_main.table.setItem(i, 1, QTableWidgetItem(time_added))
            self.ui_main.table.item(i, 1).setBackground(QColor(41, 40, 62))
            self.ui_main.table.item(i, 1).setForeground(QColor("white"))




    # Open File data.json

    def open_file_json(self, file_name_str, mode):
        try:
            data_file = open(
                file_name_str,
                mode=mode,
                encoding='utf-8',
                errors='ignore')
            data_file = json.load(data_file)
        except IOError as e:
            return str(e)
        else:
            return data_file

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
