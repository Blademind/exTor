from PyQt5 import QtCore, QtGui, QtWidgets
import datetime


class Ui_MainWindow(object):
    def setup_ui(self, main_window):
        main_window.resize(1280, 720)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setStyleSheet("QWidget{\n"
"    background-color: #29283E;\n"
"}")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setContentsMargins(0, 1, 0, 0)
        self.vertical_layout.setSpacing(1)
        self.frame_top = QtWidgets.QFrame(self.central_widget)
        self.frame_top.setMaximumSize(QtCore.QSize(16777215, 80))
        self.frame_top.setStyleSheet("QFrame{\n"
"\n"
"    background-color: #141428;\n"
"    border:0px;\n"
"}")
        self.frame_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.frame_top)
        self.frame_topLeft = QtWidgets.QFrame(self.frame_top)
        self.frame_topLeft.setMinimumSize(QtCore.QSize(282, 0))
        self.frame_topLeft.setMaximumSize(QtCore.QSize(282, 16777215))
        self.frame_topLeft.setStyleSheet("QFrame{\n"
"border:0px;\n"
"\n"
"}")
        self.frame_topLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_topLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_2 = QtWidgets.QVBoxLayout(self.frame_topLeft)
        self.vertical_layout_2.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout_2.setSpacing(0)
        self.logo_button = QtWidgets.QPushButton(self.frame_topLeft)
        self.logo_button.setMinimumSize(QtCore.QSize(50, 60))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.logo_button.setFont(font)
        self.logo_button.setAutoFillBackground(False)
        self.logo_button.setStyleSheet("QPushButton{\n"
"\n"
"color:#E7E7E7;\n"
"font-weight: bold;\n"
"background-color:transparent;\n"
"font-size:26px;\n"
"border:0px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/img/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logo_button.setIcon(icon)
        self.logo_button.setIconSize(QtCore.QSize(48, 48))
        self.vertical_layout_2.addWidget(self.logo_button)
        self.horizontal_layout.addWidget(self.frame_topLeft)
        self.frame_topCenter = QtWidgets.QFrame(self.frame_top)
        self.frame_topCenter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_topCenter.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout_2 = QtWidgets.QHBoxLayout(self.frame_topCenter)
        self.line_edit_search_top = QtWidgets.QLineEdit(self.frame_topCenter)
        self.line_edit_search_top.setClearButtonEnabled(True)
        icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight)
        self.action = self.line_edit_search_top.addAction(icon, self.line_edit_search_top.TrailingPosition)

        font = QtGui.QFont()
        font.setPointSize(1)
        self.line_edit_search_top.setFont(font)
        self.line_edit_search_top.setAcceptDrops(False)
        self.line_edit_search_top.setToolTip("")
        self.line_edit_search_top.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.line_edit_search_top.setStyleSheet("QLineEdit{\n"
                                               "border-radius:5px;\n"
                                               "background-color: #f2f2f2;\n"
                                               "text-align: center;\n"
                                               "font-size:30px;\n"
                                               "color:#141428;\n"
                                               "}")
        self.line_edit_search_top.setReadOnly(False)

        self.horizontal_layout_2.addWidget(self.line_edit_search_top)
        self.horizontal_layout.addWidget(self.frame_topCenter)
        self.frame_topRight = QtWidgets.QFrame(self.frame_top)
        self.frame_topRight.setMinimumSize(QtCore.QSize(350, 0))
        self.frame_topRight.setMaximumSize(QtCore.QSize(350, 16777215))
        self.frame_topRight.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_topRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout_3 = QtWidgets.QHBoxLayout(self.frame_topRight)
        self.frame_alert_top = QtWidgets.QFrame(self.frame_topRight)
        self.frame_alert_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_alert_top.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.horizontal_layout_4 = QtWidgets.QHBoxLayout(self.frame_alert_top)
        self.push_button_alert_top = QtWidgets.QPushButton(self.frame_alert_top)
        self.push_button_alert_top.setStyleSheet("QPushButton{\n"
                                               "color:#E7E7E7;\n"
                                               "font-weight: bold;\n"
                                               "background-color:transparent;\n"
                                               "font-size:15px;\n"
                                               "border:0px;\n"
                                               "}")
        self.frame_profile_top = QtWidgets.QFrame(self.frame_topRight)
        self.frame_profile_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_profile_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout_5 = QtWidgets.QHBoxLayout(self.frame_profile_top)
        self.horizontal_layout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_5.setSpacing(0)
        self.push_button_profileImg_top = QtWidgets.QPushButton(self.frame_profile_top)
        self.push_button_profileImg_top.setStyleSheet("QPushButton{\n"
                                                      "color:#E7E7E7;\n"
                                                      "font-weight: bold;\n"
                                                      "background-color:transparent;\n"
                                                      "font-size:15px;\n"
                                                      "border:0px;\n"
                                                      "}")
        self.push_button_profileImg_top.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("assets/img/profile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.push_button_profileImg_top.setIcon(icon2)
        self.push_button_profileImg_top.setIconSize(QtCore.QSize(34, 34))
        self.horizontal_layout_5.addWidget(self.push_button_profileImg_top)
        self.horizontal_layout_3.addWidget(self.frame_profile_top)
        self.frame_userData_top = QtWidgets.QFrame(self.frame_topRight)
        self.frame_userData_top.setMinimumSize(QtCore.QSize(150, 0))
        self.frame_userData_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_userData_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_3 = QtWidgets.QVBoxLayout(self.frame_userData_top)
        self.label_userData_top = QtWidgets.QLabel(self.frame_userData_top)
        self.label_userData_top.setStyleSheet("QLabel{\n"
                                              "\n"
                                              "color:#E7E7E7;\n"
                                              "\n"
                                              "}")
        self.vertical_layout_3.addWidget(self.label_userData_top)
        self.label_userDataType_top = QtWidgets.QLabel(self.frame_userData_top)
        self.label_userDataType_top.setMinimumSize(QtCore.QSize(0, 19))
        self.label_userDataType_top.setStyleSheet("QLabel{\n"
                                                  "color:#0080FB;\n"
                                                  "}")
        self.horizontal_layout_3.addWidget(self.frame_userData_top)
        self.horizontal_layout.addWidget(self.frame_topRight)
        self.vertical_layout.addWidget(self.frame_top)
        self.frame_central = QtWidgets.QFrame(self.central_widget)
        self.frame_central.setStyleSheet("QFrame{\n"
                                         "\n"
                                         "    border:0px;\n"
                                         "}")
        self.frame_central.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_central.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout_4 = QtWidgets.QHBoxLayout(self.frame_central)
        self.frame_column_left = QtWidgets.QFrame(self.frame_central)
        self.frame_column_left.setMaximumSize(QtCore.QSize(225, 16777215))
        self.frame_column_left.setStyleSheet("")
        self.frame_column_left.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_column_left.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_4 = QtWidgets.QVBoxLayout(self.frame_column_left)
        self.frame = QtWidgets.QFrame(self.frame_column_left)
        self.frame.setMinimumSize(QtCore.QSize(0, 80))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 80))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_5 = QtWidgets.QVBoxLayout(self.frame)
        self.push_button_home = QtWidgets.QPushButton(self.frame)
        self.push_button_home.setLayout(QtWidgets.QGridLayout())
        self.push_button_home.setMinimumSize(QtCore.QSize(0, 50))
        self.push_button_home.setMaximumSize(QtCore.QSize(140, 50))
        self.push_button_home.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.push_button_home.setStyleSheet("QPushButton{\n"
                                      "    color:#E7E7E7;\n"
                                      "    border:0px;\n"
                                      "    border-radius:25px;\n"
                                      "    font-size:18px;\n"
                                      "    cursor: pointer;\n"
                                      "    background-color:#538fff;\n"
                                      "}\n"
                                      "QPushButton:hover{\n"
                                      "background-color:#3668ff;\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("assets/img/home.svg"),)

        self.push_button_home.setIcon(icon3)
        self.push_button_home.setIconSize(QtCore.QSize(32, 32))
        self.vertical_layout_5.addWidget(self.push_button_home)
        self.vertical_layout_4.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.frame_column_left)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_6 = QtWidgets.QVBoxLayout(self.frame_2)
        self.upload_button = QtWidgets.QPushButton(self.frame_2)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("assets/img/upload.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.upload_button.setIcon(icon6)
        self.upload_button.setIconSize(QtCore.QSize(24, 24))

        self.upload_button.setMinimumSize(QtCore.QSize(0, 30))
        self.upload_button.setMaximumSize(QtCore.QSize(16777215, 30))
        self.upload_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_button.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.upload_button.setStyleSheet("QPushButton{\n"
                                        "    text-align:left;\n"
                                        "    color:#E7E7E7;\n"
                                        "    border:0px;\n"
                                        "    font-size:16px;\n"
                                        "    cursor: pointer;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "text-decoration: underline;\n"
                                        "font-weight: bold;\n"
                                        "}\n"
                                        "\n"
                                        "")
        self.vertical_layout_6.addWidget(self.upload_button)
        spacer_item = QtWidgets.QSpacerItem(40, 200, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.vertical_layout_6.addItem(spacer_item)

        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 2))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 2))
        self.frame_3.setStyleSheet("QFrame{\n"
                                 "    background-color: #e9e9ee;\n"
                                 "    border:0px;\n"
                                 "}")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_6.addWidget(self.frame_3)

        spacer_item2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.vertical_layout_6.addItem(spacer_item2)
        self.push_button_subLogo = QtWidgets.QPushButton(self.frame_2)
        self.push_button_subLogo.setStyleSheet("QPushButton{\n"
                                         "    border:0px;\n"
                                         "}\n"
                                         "    ")
        self.push_button_subLogo.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("assets/img/logo_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.push_button_subLogo.setIcon(icon5)
        self.push_button_subLogo.setIconSize(QtCore.QSize(300, 60))
        self.vertical_layout_6.addWidget(self.push_button_subLogo)
        self.vertical_layout_4.addWidget(self.frame_2)
        self.horizontal_layout_4.addWidget(self.frame_column_left)

        self.frame_column_center = QtWidgets.QFrame(self.frame_central)
        self.frame_column_center.setStyleSheet("")
        self.frame_column_center.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_column_center.setFrameShadow(QtWidgets.QFrame.Raised)

        self.vertical_layout_7 = QtWidgets.QVBoxLayout(self.frame_column_center)

        self.frame_4 = QtWidgets.QFrame(self.frame_column_center)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 80))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_layout_5 = QtWidgets.QHBoxLayout(self.frame_4)
        self.line_edit_date = QtWidgets.QLineEdit()
        self.line_edit_date.setEnabled(False)
        self.line_edit_date.setGeometry(QtCore.QRect(10, 15, 190, 50))
        self.line_edit_date.setMinimumSize(QtCore.QSize(190, 50))
        self.line_edit_date.setMaximumSize(QtCore.QSize(190, 50))
        self.line_edit_date.setStyleSheet("QLineEdit{\n"
                                       "border-radius:15px;\n"
                                       "background-color: #fff;\n"
                                       "text-align: center;\n"
                                       "font-size:15px;\n"
                                       "color:#141428;\n"
                                       "border:1px solid #e1e4ed;\n"
                                       "text-aling:center;\n"
                                       "}")
        self.line_edit_date.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontal_layout_5.addWidget(self.line_edit_date)

        self.notification = Notification()
        self.horizontal_layout_5.addWidget(self.notification)
        
        spacer_item = QtWidgets.QSpacerItem(1000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontal_layout_5.addItem(spacer_item)

        self.vertical_layout_7.addWidget(self.frame_4)
        self.frame_dash_central = QtWidgets.QFrame(self.frame_column_center)
        self.frame_dash_central.setStyleSheet("QFrame{\n"
                                             "    background-color: #141428;\n"
                                             "    border-radius:10px;\n"
                                             "border:0px;\n"
                                             "}"
                                             "QTextEdit{\n"
                                             "border-radius:15px;\n"
                                             "background-color: #f2f2f2;\n"
                                             "text-align: center;\n"
                                             "font-size:30px;\n"
                                             "}"
                                              )
        self.frame_dash_central.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_dash_central.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vertical_layout_8 = QtWidgets.QVBoxLayout(self.frame_dash_central)
        self.frame_5 = QtWidgets.QFrame(self.frame_dash_central)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)

        self.vertical_layout_9 = QtWidgets.QVBoxLayout(self.frame_5)
        self.label_title_dash = QtWidgets.QLabel(self.frame_5)
        self.label_title_dash.setStyleSheet("QLabel{\n"
                                           "\n"
                                           "color:#E7E7E7;\n"
                                           "border:0px;\n"
                                           "font-size:30px;\n"
                                           "font-weight: bold;\n"
                                           "}")
        self.vertical_layout_9.addWidget(self.label_title_dash)

        self.label_sub_title_dash = QtWidgets.QLabel(self.frame_5)
        self.label_sub_title_dash.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_sub_title_dash.setStyleSheet("QLabel{\n"
                                              "\n"
                                              "color:#E7E7E7;\n"
                                              "border:0px;\n"
                                              "font-size:15px;\n"
                                              "}")
        self.label_sub_title_dash.hide()
        self.vertical_layout_9.addWidget(self.label_sub_title_dash)

        self.list_download = QtWidgets.QListWidget(self.frame_5)
        self.list_download.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_download.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_download.setAcceptDrops(True)

        self.push_button_folder = QtWidgets.QPushButton(self.frame_5)
        self.push_button_folder.setStyleSheet("QPushButton{\n"
                                         "\n"
                                         "color:#E7E7E7;\n"
                                         "font-weight: bold;\n"
                                         "font-size:26px;\n"
                                         "}")
        self.push_button_folder.hide()

        self.vertical_layout.addWidget(self.frame_central)
        self.vertical_layout_7.addWidget(self.frame_dash_central)
        self.vertical_layout_8.addWidget(self.frame_5)
        self.vertical_layout_9.addWidget(self.list_download)
        self.vertical_layout_9.addWidget(self.push_button_folder)
        self.horizontal_layout_4.addWidget(self.frame_column_center)

        main_window.setCentralWidget(self.central_widget)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "exTor User"))
        self.logo_button.setText(_translate("MainWindow", "exTor"))
        self.label_userData_top.setText(_translate("MainWindow", "{USER}"))
        self.label_userDataType_top.setText(_translate("MainWindow", "{PROFILE_TYPE}"))
        self.push_button_home.setText(_translate("MainWindow", " Home"))

        self.upload_button.setText(_translate("MainWindow", "Upload"))
        self.line_edit_date.setText(_translate("MainWindow", "{weekday} 00/00/0000"))

        self.label_title_dash.setText("Activities")
        self.label_sub_title_dash.setText("Upload your desired files to the LAN to share with others")
        self.push_button_folder.setText("Select Folder")


class Message(QtWidgets.QWidget):
    def __init__(self, title, message, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.titleLabel = QtWidgets.QLabel(title, self)
        self.titleLabel.setStyleSheet(
            "font-family: 'Roboto', sans-serif; font-size: 15px; font-weight: bold; padding: 0;color:white;")
        self.messageLabel = QtWidgets.QLabel(message, self)
        self.messageLabel.setStyleSheet(
            "font-family: 'Roboto', sans-serif; font-size: 15px; font-weight: normal; padding: 0; color:white;")

        self.timeLabel = QtWidgets.QLabel(datetime.datetime.now().strftime("%H:%M:%S"), self)
        self.timeLabel.setStyleSheet(
            "font-family: 'Roboto', sans-serif; font-size: 12px; font-weight: normal; padding: 0; color:white;")

        self.push_button_close = QtWidgets.QPushButton(self)
        self.push_button_close.setStyleSheet("border-radius: 15px;")
        self.push_button_close.setIcon(QtGui.QIcon("assets/img/arrow-right-circle.svg"))  # icon
        self.push_button_close.setFixedSize(18, 18)

        self.layout().addWidget(self.titleLabel, 0, 0)
        self.layout().addWidget(self.messageLabel, 1, 0)
        self.layout().addWidget(self.timeLabel, 2, 0)
        self.layout().addWidget(self.push_button_close, 0, 1, 2, 1)


class Notification(QtWidgets.QWidget):
    signNotifyClose = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.notification_queue = []
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.number_of_messages = 0
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def set_notify(self, title, message):
        if self.number_of_messages == 0:  # can be set to whatever number of notifications wished
                m = Message(title, message, parent=self)
                self.main_layout.addWidget(m)
                m.push_button_close.clicked.connect(self.on_clicked)
                self.number_of_messages += 1
                self.show()

        else:
                m = Message(title, message, parent=self)
                self.notification_queue.append(m)

    def on_clicked(self):
        self.main_layout.removeWidget(self.sender().parent())
        self.number_of_messages -= 1
        self.adjustSize()

        while self.notification_queue and self.number_of_messages == 0:  # can be set to whatever number of notifications wished
                m = self.notification_queue.pop(0)
                self.main_layout.addWidget(m)
                m.push_button_close.clicked.connect(self.on_clicked)
                self.number_of_messages += 1
                self.show()

        if self.number_of_messages == 0:
            self.close()
