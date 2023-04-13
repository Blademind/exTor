__author__ = "Alon Levy"
__nick__ = "Blademind"
__email__ = "alonlevy2005@gmail.com"


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from socket import *
import pickle
import ssl
import warnings
import os
from customized import PasswordEdit
from main import MainWindow


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
                background-color: #0668E1;
                border-style: inset;
            }
            QPushButton:pressed {
                background-color: #0080FB;
                border-style: inset;
            }
            """
        )

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_3 = QHBoxLayout()

        self.widget = QWidget(self)
        self.widget.setMaximumSize(QSize(16777215, 16777215))
        self.widget.setStyleSheet(".QWidget{background-color: #141428;}")

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
        self.label_2.setStyleSheet("color: #E7E7E7;\n"
                                   "font: 15pt \"Verdana\";")
        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setMinimumSize(QSize(0, 40))
        self.lineEdit.setStyleSheet("QLineEdit {\n"
                                    "color: #E7E7E7;\n"
                                    "font: 15pt \"Verdana\";\n"
                                    "border: None;\n"
                                    "border-bottom-color: white;\n"
                                    "border-radius: 10px;\n"
                                    "padding: 0 8px;\n"
                                    "background: #141428;\n"
                                    "selection-background-color: darkgray;\n"
                                    "}")
        self.lineEdit.setFocus(True)
        self.lineEdit.setPlaceholderText("Username")
        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.lineEdit)

        self.label_3 = QLabel(self.widget)
        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_3)

        self.lineEdit_2 = PasswordEdit(self.widget)
        self.lineEdit_2.setMinimumSize(QSize(0, 40))
        self.lineEdit_2.setStyleSheet("QLineEdit {\n"
                                      "color: #0080FB;\n"
                                      "font: 15pt \"Verdana\";\n"
                                      "border: None;\n"
                                      "border-bottom-color: white;\n"
                                      "border-radius: 10px;\n"
                                      "padding: 0 8px;\n"
                                      "background: #141428;\n"
                                      "selection-background-color: darkgray;\n"
                                      "}")
        self.lineEdit_2.setPlaceholderText("Password")
        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.lineEdit_2)
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

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
        self.pushButton.setStyleSheet("color: #0080FB;\n"
                                      "font: 17pt \"Verdana\";\n"
                                      "border: 2px solid #0080FB;\n"
                                      "padding: 5px;\n"
                                      "border-radius: 3px;\n"
                                      "opacity: 200;\n"
                                      "")
        self.pushButton.setAutoDefault(True)
        self.pushButton.setShortcut("Return")
        self.formLayout_2.setWidget(7, QFormLayout.SpanningRole, self.pushButton)

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

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_3.setText(_translate("Form", "X"))
        self.label_2.setText(_translate(
            "Form",
            "<html><head/><body><p><img src=\"icons/user.svg\"/></p></body></html>"))
        self.label_3.setText(_translate(
            "Form",
            "<html><head/><body><p><img src=\"icons/lock.svg\"/></p></body></html>"))
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
        username = self.lineEdit.text()
        self.sock.send(f"USER_PASSWORD {self.lineEdit.text()} {self.lineEdit_2.text()}".encode())
        data = self.sock.recv(1024)
        if data == b"SUCCESS":
            self.close()
            self.sock.close()

            self.MainWindow = MainWindow(self.local_tracker, username)
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


if __name__ == '__main__':
    warnings.simplefilter("ignore", category=RuntimeWarning)
    UI()
    os._exit(0)
