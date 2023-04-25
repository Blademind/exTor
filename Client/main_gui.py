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
        self.ui_main.clear.clicked.connect(lambda x: self.click_button('Clear'))

        # self.ui_main.logWidget.setText(log_data)
        self.ui_main.logWidget.moveCursor(QTextCursor.End)

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
            if banned_ips:
                self.ui_main.table.setColumnCount(1)
                self.ui_main.table.setRowCount(len(banned_ips))
                self.ui_main.table.setHorizontalHeaderLabels(['IP'])
                for i, ip in enumerate(banned_ips):
                    self.ui_main.table.setItem(i, 0, QTableWidgetItem(ip.decode()))
                    self.ui_main.table.item(i, 0).setBackground(QColor(41, 40, 62))
                    self.ui_main.table.item(i, 0).setForeground(QColor("white"))
                self.ui_main.table.show()
            else:
                self.ui_main.table.hide()
                self.ui_main.label_SubTitleDash.setText("No Banned IPs, Yet.")

            # update table now
    def set_dash_value(self):
        self.ui_main.label_TxtTopDataUserType.setText("Peer")
        self.ui_main.date_widget.setText(self.date_now())

    # Clicked buttons
    def click_button(self,value):
        # print("CLICKED", value)
        if value == "Home":
            # Object hide before showing graph, change text as well
            self.ui_main.table.hide()
            self.ui_main.logWidget.hide()
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.clear.hide()
            self.ui_main.label_TitleDash.setText("Requests on Tracker")
            self.ui_main.label_SubTitleDash.setText("UDP tracker requests")
            self.ui_main.graphWidget.show()
        elif value == "Swarms":
            try:
                self.ui_main.table.doubleClicked.disconnect()
            except: pass
            self.ui_main.table.contextMenuEvent = lambda event: None
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.clear.hide()
            self.ui_main.table.hide()
            self.ui_main.logWidget.hide()
            self.ui_main.graphWidget.hide()
            self.ui_main.table.doubleClicked.connect(self.swarms)
            self.ui_main.label_TitleDash.setText("Swarms")
            self.ui_main.label_SubTitleDash.setText("Group of Peers per local file")
            files = self.r.keys("*.torrent*")
            # print(files)
            if files:
                self.ui_main.table.clear()
                self.ui_main.table.setColumnCount(1)
                self.ui_main.table.setRowCount(len(files))
                self.ui_main.table.setHorizontalHeaderLabels(['File Name'])
                for i, file in enumerate(files):
                    self.ui_main.table.setItem(i, 0, QTableWidgetItem(file.decode()))
                    self.ui_main.table.item(i, 0).setBackground(QColor(41, 40, 62))
                    self.ui_main.table.item(i, 0).setForeground(QColor("white"))
                self.ui_main.table.show()
            else:
                self.ui_main.label_SubTitleDash.setText("Sorry, no groups are available")
        elif value == "Banned IPs":
            try:
                self.ui_main.table.doubleClicked.disconnect()
            except: pass
            self.ui_main.table.contextMenuEvent = lambda event: self.menu_event2(self.ui_main.table, event)
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.clear.hide()
            self.ui_main.table.hide()
            self.ui_main.logWidget.hide()
            self.ui_main.graphWidget.hide()
            self.ui_main.label_TitleDash.setText("Banned IPs")
            self.ui_main.label_SubTitleDash.setText("IPs which are not allowed to contact tracker")
            self.ui_main.table.clear()
            banned_ips = self.r.lrange("banned", 0, -1)
            if banned_ips:
                self.ui_main.table.setColumnCount(1)
                self.ui_main.table.setRowCount(len(banned_ips))
                self.ui_main.table.setHorizontalHeaderLabels(['IP'])
                for i, ip in enumerate(banned_ips):
                    self.ui_main.table.setItem(i, 0, QTableWidgetItem(ip.decode()))
                    self.ui_main.table.item(i, 0).setBackground(QColor(41, 40, 62))
                    self.ui_main.table.item(i, 0).setForeground(QColor("white"))
                self.ui_main.table.show()

            else:
                self.ui_main.label_SubTitleDash.setText("No Banned IPs, Yet.")
        elif value == "Log":
            try:
                self.ui_main.table.doubleClicked.disconnect()
            except: pass
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.clear.hide()
            self.ui_main.table.hide()
            self.ui_main.graphWidget.hide()
            self.ui_main.label_TitleDash.setText("Log")
            # self.ui_main.label_SubTitleDash.hide()
            # self.ui_main.label_SubTitleDash.setText("Log of this admin")

            if not self.ui_main.logWidget.document().isEmpty():
                self.ui_main.label_SubTitleDash.hide()
                self.ui_main.clear.show()
                self.ui_main.logWidget.moveCursor(QTextCursor.End)
                self.ui_main.logWidget.show()
            else:
                self.ui_main.label_SubTitleDash.setText("Log is empty")

    def swarms(self, item):
        try:
            self.ui_main.table.doubleClicked.disconnect()
        except: pass
        try:
            try:
                file = item.data()
                self.file_name = file
            except:
                file = item
            peers = self.r.lrange(file, 0, -1)
            if peers:
                self.ui_main.table.setColumnCount(2)
                self.ui_main.table.setHorizontalHeaderLabels(['IP:PORT','Time Added'])

                self.ui_main.table.contextMenuEvent = lambda event: self.menu_event(self.ui_main.table, event)

                # print("file:",file)
                # print(peers)
                self.ui_main.table.setRowCount(len(peers))
                for i, peer_raw in enumerate(peers):
                    peer = pickle.loads(peer_raw)
                    ip = f"{peer[0]}:{peer[1]}"
                    time_added = time.asctime(time.localtime(time.time()))

                    self.ui_main.table.setItem(i, 0, QTableWidgetItem(ip))
                    self.ui_main.table.item(i, 0).setBackground(QColor(41, 40, 62))
                    self.ui_main.table.item(i, 0).setForeground(QColor("white"))
                    self.ui_main.table.setItem(i, 1, QTableWidgetItem(time_added))
                    self.ui_main.table.item(i, 1).setBackground(QColor(41, 40, 62))
                    self.ui_main.table.item(i, 1).setForeground(QColor("white"))
            else:
                self.ui_main.table.hide()
                self.ui_main.label_SubTitleDash.setText("Sorry, no groups are available")

        except: pass



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
