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
def mousePressEvent(obj, event):
    obj.oldPos = event.globalPos()


def mouseMoveEvent(obj, event):
    delta = QPoint (event.globalPos() - obj.oldPos)
    obj.move(obj.x() + delta.x(), obj.y() + delta.y())
    obj.oldPos = event.globalPos()


class MainWindow(QMainWindow):
    def __init__(self, tracker, username):
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

        with open("log.log", "r") as log:
            log_data = log.read()

        self.ui_main.logWidget.setText(log_data)
        self.ui_main.logWidget.moveCursor(QTextCursor.End)

        # self.ui_main.pushButton_BtnConfiguracao.clicked.connect(lambda x:self.click_button('CONFIGURAÇÃO'))
        self.hidden = False
        self.sock = init_udp_sock()

        redis_host = "localhost"
        redis_port = 6379
        self.r = redis.StrictRedis(host=redis_host, port=redis_port)
        try:
            self.r.ping()
        except redis.ConnectionError:
            self.error_handler("Could not connect to database")

        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.settimeout(5)
        self.tcp_sock = ssl.wrap_socket(self.tcp_sock, server_side=False, keyfile='private-key.pem',
                                        certfile='cert.pem')
        self.tcp_sock.connect((self.local_tracker[0], 55556))

        self.set_dash_value(username)
        # threading.Thread(target=self.deleter_timer).start()

        self.fetch_requests()
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.update_widgets)
        self.timer.start()

        self.show()

    def error_handler(self, msg, close_program=True):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error")
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
        self.sock.sendto(b"DONE_ADMIN_OPERATION", self.local_tracker)

        if close_program:
            sys.exit(error_dialog.exec_())
        else:
            error_dialog.exec_()

    def remove_from_database(self, ip):
        all_keys = self.r.keys("*")
        for key in all_keys:
            print(key)
            if b".torrent" in key:
                file_name = key
                records = self.r.lrange(file_name, 0, -1)
                for record in records:
                    created_ip = pickle.loads(record)
                    if created_ip[0] == ip:
                        self.r.lrem(file_name, 0, record)
                        print(f"removed {ip} from {file_name.decode()}")

            elif key != b"banned" and key != b"admin_ip":
                created_ip = pickle.loads(key)
                if ip == created_ip[0]:
                    self.r.delete(key)
                    print("deleted", created_ip)

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
            print("Kicked")
            self.r.lrem(self.file_name, 0, raw_addr)
            self.r.delete(raw_addr)
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
            print("Banned")
            # self.remove_from_database(ip[0])

            # self.tcp_sock.send(b"UPDATE_FILES")
            # try:
            #     data = self.tcp_sock.recv(1024)
            #     if data == b"FLOW":
            #         self.tcp_sock.send(pickle.dumps([(raw_addr, self.file_name.encode())]))
            # except Exception as e:
            #     print(e)
            #     pass

            self.swarms(self.file_name, ban_ip=ip[0])
            self.add_to_log(f"Banned {ip[0]} as prompted")
            self.tcp_sock.send(f"BAN_IP {ip[0]}".encode())
            # update table now
        elif ip[0] == self.sock.getsockname()[0]:
            print("could not ban because the IP is of this Admin")

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
    def update_widgets(self):
        with open("log.log", "r") as log:
            log_data = log.read()
        self.ui_main.logWidget.setText(log_data)
        self.ui_main.logWidget.moveCursor(QTextCursor.End)
        if np.nan in self.ui_main.y:
            requests_data = self.fetch_requests()
            num_of_requests = requests_data[0] - 1
            # requests_per_ip = requests_data[1]
            self.ui_main.y[self.ui_main.y.index(np.nan)] = num_of_requests
        else:
            self.ui_main.x = self.ui_main.x[1:]  # Remove the first y element.
            self.ui_main.x.append(self.ui_main.x[-1] + 5)  # Add a new value 1 higher than the last.

            self.ui_main.y = self.ui_main.y[1:]  # Remove the first

            requests_data = self.fetch_requests()
            num_of_requests = requests_data[0] - 1
            # requests_per_ip = requests_data[1]
            self.ui_main.y.append(num_of_requests)  # Add a new random value.

        # for ip in requests_per_ip:
        #     requests_ip = requests_per_ip[ip]
        #     # print(ip, "-> requests:", requests_ip)
        #     if requests_ip >= 10:  # more than 10 requests in 5 seconds, Ban
        #         self.add_to_log(f"Banned {ip} due to over requesting")
        #         self.remove_from_database(ip)
        #         self.tcp_sock.send(f"BAN_IP {ip}".encode())

        self.ui_main.data_line.setData(self.ui_main.x, self.ui_main.y)  # Update the data.
        self.ui_main.graphWidget.clear()
        for i in range(len(self.ui_main.x)):
            self.ui_main.graphWidget.plot((self.ui_main.x[i], self.ui_main.x[i]), (0, self.ui_main.y[i]), pen=self.ui_main.line_pen)

    def add_to_log(self, msg):
        with open("log.log", "a") as f:
            f.write(f"\n\n> {msg} [{time.strftime('%H:%M:%S %d-%m-%Y', time.gmtime())}]")

    # Set values in Dash
    def deleter_timer(self):
        """
        removes ip after an hour (according to protocol)
        :return: None
        """
        timer = 300  # 300
        try:
            self.r.ping()
            while 1:
                ip_files = []
                table_names = self.r.keys("*.torrent*")
                for file_name in table_names:
                    records = self.r.lrange(file_name, 0, -1)

                    for raw_addr in records:
                        time_added = self.r.get(raw_addr)
                        print(pickle.loads(raw_addr),time_added)
                        if time.time() - float(time_added) >= timer:
                            self.r.lrem(file_name, 0, raw_addr)
                            self.r.delete(raw_addr)
                            ip_files.append((raw_addr, file_name))
                            self.add_to_log(f"Kicked {pickle.loads(raw_addr)} due to inactivity")
                if ip_files:
                    self.tcp_sock.send(b"UPDATE_FILES")
                    try:
                        data = self.tcp_sock.recv(1024)
                        if data == b"FLOW":
                            self.tcp_sock.send(pickle.dumps(ip_files))
                    except Exception as e:
                        print(e)
                        pass
                time.sleep(1)
        except Exception as e:
            print(e)
            pass

    def set_dash_value(self, username):
        self.ui_main.label_TxtTopDataUser.setText(username)
        self.ui_main.label_TxtTopDataUserType.setText("Admin")
        # self.ui_main.label_TxtValorRestituicao.setText("R$"+data_dict.get('receita_value'))
        # self.ui_main.pushButton_TopAlert.setText(data_dict.get('notification'))
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
        elif value == "Clear":
            with open("log.log", "w") as f:
                f.write("")
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.clear.hide()
            self.ui_main.logWidget.setText("")
            self.ui_main.logWidget.hide()
            self.ui_main.label_SubTitleDash.setText("Log is empty")

    def swarms(self, item, ban_ip=""):
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
            if ban_ip:
                for peer in peers:
                    peer_ip = pickle.loads(peer)[0]
                    if peer_ip == ban_ip:
                        peers.remove(peer)
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
                self.ui_main.label_SubTitleDash.setText("Sorry, no peers are available")

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
