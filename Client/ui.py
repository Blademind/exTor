from PyQt5 import QtCore, QtGui, QtWidgets
import datetime


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("QWidget{\n"
"    background-color: #29283E;\n"
"}")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 1, 0, 0)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_Top = QtWidgets.QFrame(self.centralwidget)
        self.frame_Top.setMaximumSize(QtCore.QSize(16777215, 80))
        self.frame_Top.setStyleSheet("QFrame{\n"
"\n"
"    background-color: #141428;\n"
"    border:0px;\n"
"}")
        self.frame_Top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Top.setObjectName("frame_Top")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_Top)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_TopLeft = QtWidgets.QFrame(self.frame_Top)
        self.frame_TopLeft.setMinimumSize(QtCore.QSize(282, 0))
        self.frame_TopLeft.setMaximumSize(QtCore.QSize(282, 16777215))
        self.frame_TopLeft.setStyleSheet("QFrame{\n"
"border:0px;\n"
"\n"
"}")
        self.frame_TopLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopLeft.setObjectName("frame_TopLeft")
        self.verticalLayout_21 = QtWidgets.QVBoxLayout(self.frame_TopLeft)
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_21.setSpacing(0)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.pushButton_LogoReceitaFederal = QtWidgets.QPushButton(self.frame_TopLeft)
        self.pushButton_LogoReceitaFederal.setMinimumSize(QtCore.QSize(50, 60))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_LogoReceitaFederal.setFont(font)
        self.pushButton_LogoReceitaFederal.setAutoFillBackground(False)
        self.pushButton_LogoReceitaFederal.setStyleSheet("QPushButton{\n"
"\n"
"color:#E7E7E7;\n"
"font-weight: bold;\n"
"background-color:transparent;\n"
"font-size:26px;\n"
"border:0px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/img/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_LogoReceitaFederal.setIcon(icon)
        self.pushButton_LogoReceitaFederal.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_LogoReceitaFederal.setObjectName("pushButton_LogoReceitaFederal")
        self.verticalLayout_21.addWidget(self.pushButton_LogoReceitaFederal)
        self.horizontalLayout.addWidget(self.frame_TopLeft)
        self.frame_TopCenter = QtWidgets.QFrame(self.frame_Top)
        self.frame_TopCenter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopCenter.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopCenter.setObjectName("frame_TopCenter")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_TopCenter)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textEdit_TxtTopSearch = QtWidgets.QLineEdit(self.frame_TopCenter)
        self.textEdit_TxtTopSearch.setClearButtonEnabled(True)
        icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight)
        self.action = self.textEdit_TxtTopSearch.addAction(icon, self.textEdit_TxtTopSearch.TrailingPosition)
        font = QtGui.QFont()
        font.setPointSize(1)
        self.textEdit_TxtTopSearch.setFont(font)
        self.textEdit_TxtTopSearch.setAcceptDrops(False)
        self.textEdit_TxtTopSearch.setToolTip("")
        self.textEdit_TxtTopSearch.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.textEdit_TxtTopSearch.setStyleSheet("QLineEdit{\n"
"border-radius:5px;\n"
"background-color: #f2f2f2;\n"
"text-align: center;\n"
"font-size:30px;\n"
"color:#141428;\n"
"}")
        self.textEdit_TxtTopSearch.setReadOnly(False)
        self.textEdit_TxtTopSearch.setObjectName("textEdit_TxtTopSearch")

        self.horizontalLayout_2.addWidget(self.textEdit_TxtTopSearch)
        self.horizontalLayout.addWidget(self.frame_TopCenter)
        self.frame_TopRight = QtWidgets.QFrame(self.frame_Top)
        self.frame_TopRight.setMinimumSize(QtCore.QSize(350, 0))
        self.frame_TopRight.setMaximumSize(QtCore.QSize(350, 16777215))
        self.frame_TopRight.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopRight.setObjectName("frame_TopRight")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_TopRight)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_TopAlert = QtWidgets.QFrame(self.frame_TopRight)
        self.frame_TopAlert.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopAlert.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopAlert.setObjectName("frame_TopAlert")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_TopAlert)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_TopAlert = QtWidgets.QPushButton(self.frame_TopAlert)
        self.pushButton_TopAlert.setStyleSheet("QPushButton{\n"
"color:#E7E7E7;\n"
"font-weight: bold;\n"
"background-color:transparent;\n"
"font-size:15px;\n"
"border:0px;\n"
"}")
        self.frame_TopProfile = QtWidgets.QFrame(self.frame_TopRight)
        self.frame_TopProfile.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopProfile.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopProfile.setObjectName("frame_TopProfile")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_TopProfile)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_ImgTopProfile = QtWidgets.QPushButton(self.frame_TopProfile)
        self.pushButton_ImgTopProfile.setStyleSheet("QPushButton{\n"
"color:#E7E7E7;\n"
"font-weight: bold;\n"
"background-color:transparent;\n"
"font-size:15px;\n"
"border:0px;\n"
"}")
        self.pushButton_ImgTopProfile.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("assets/img/profile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_ImgTopProfile.setIcon(icon2)
        self.pushButton_ImgTopProfile.setIconSize(QtCore.QSize(34, 34))
        self.pushButton_ImgTopProfile.setObjectName("pushButton_ImgTopProfile")
        self.horizontalLayout_5.addWidget(self.pushButton_ImgTopProfile)
        self.horizontalLayout_3.addWidget(self.frame_TopProfile)
        self.frame_TopDataUser = QtWidgets.QFrame(self.frame_TopRight)
        self.frame_TopDataUser.setMinimumSize(QtCore.QSize(150, 0))
        self.frame_TopDataUser.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_TopDataUser.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_TopDataUser.setObjectName("frame_TopDataUser")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_TopDataUser)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_TxtTopDataUser = QtWidgets.QLabel(self.frame_TopDataUser)
        self.label_TxtTopDataUser.setStyleSheet("QLabel{\n"
"\n"
"color:#E7E7E7;\n"
"\n"
"}")
        self.label_TxtTopDataUser.setObjectName("label_TxtTopDataUser")
        self.verticalLayout_2.addWidget(self.label_TxtTopDataUser)
        self.label_TxtTopDataUserType = QtWidgets.QLabel(self.frame_TopDataUser)
        self.label_TxtTopDataUserType.setMinimumSize(QtCore.QSize(0, 19))
        self.label_TxtTopDataUserType.setStyleSheet("QLabel{\n"
"color:#0080FB;\n"
"}")
        self.label_TxtTopDataUserType.setObjectName("label_TxtTopDataUserType")
        self.horizontalLayout_3.addWidget(self.frame_TopDataUser)
        self.horizontalLayout.addWidget(self.frame_TopRight)
        self.verticalLayout.addWidget(self.frame_Top)
        self.frame_Central = QtWidgets.QFrame(self.centralwidget)
        self.frame_Central.setStyleSheet("QFrame{\n"
"\n"
"    border:0px;\n"
"}")
        self.frame_Central.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Central.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Central.setObjectName("frame_Central")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_Central)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.frame_ColumnLeft = QtWidgets.QFrame(self.frame_Central)
        self.frame_ColumnLeft.setMaximumSize(QtCore.QSize(225, 16777215))
        self.frame_ColumnLeft.setStyleSheet("")
        self.frame_ColumnLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_ColumnLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_ColumnLeft.setObjectName("frame_ColumnLeft")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_ColumnLeft)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_4 = QtWidgets.QFrame(self.frame_ColumnLeft)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 80))
        self.frame_4.setMaximumSize(QtCore.QSize(16777215, 80))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.home_button = QtWidgets.QPushButton(self.frame_4)
        self.home_button.setLayout(QtWidgets.QGridLayout())
        self.home_button.setMinimumSize(QtCore.QSize(0, 50))
        self.home_button.setMaximumSize(QtCore.QSize(140, 50))
        self.home_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.home_button.setStyleSheet("QPushButton{\n"
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

        self.home_button.setIcon(icon3)
        self.home_button.setIconSize(QtCore.QSize(32, 32))
        self.home_button.setObjectName("pushButton_BtnDeclarar")
        self.verticalLayout_7.addWidget(self.home_button)
        self.verticalLayout_4.addWidget(self.frame_4)
        self.frame_7 = QtWidgets.QFrame(self.frame_ColumnLeft)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.pushButton_BtnServico = QtWidgets.QPushButton(self.frame_7)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("assets/img/upload.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_BtnServico.setIcon(icon6)
        self.pushButton_BtnServico.setIconSize(QtCore.QSize(24, 24))

        self.pushButton_BtnServico.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton_BtnServico.setMaximumSize(QtCore.QSize(16777215, 30))
        self.pushButton_BtnServico.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_BtnServico.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_BtnServico.setStyleSheet("QPushButton{\n"
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
        self.pushButton_BtnServico.setObjectName("pushButton_BtnServico")
        self.verticalLayout_6.addWidget(self.pushButton_BtnServico)
        spacerItem = QtWidgets.QSpacerItem(40, 200, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem)

        self.frame = QtWidgets.QFrame(self.frame_7)
        self.frame.setMinimumSize(QtCore.QSize(0, 2))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 2))
        self.frame.setStyleSheet("QFrame{\n"
"    background-color: #e9e9ee;\n"
"    border:0px;\n"
"}")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_6.addWidget(self.frame)

        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem10)
        self.pushButton_ImgLogoGovbr = QtWidgets.QPushButton(self.frame_7)
        self.pushButton_ImgLogoGovbr.setStyleSheet("QPushButton{\n"
"    border:0px;\n"
"}\n"
"    ")
        self.pushButton_ImgLogoGovbr.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("assets/img/logo_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_ImgLogoGovbr.setIcon(icon5)
        self.pushButton_ImgLogoGovbr.setIconSize(QtCore.QSize(300, 60))
        self.pushButton_ImgLogoGovbr.setObjectName("pushButton_ImgLogoGovbr")
        self.verticalLayout_6.addWidget(self.pushButton_ImgLogoGovbr)
        self.verticalLayout_4.addWidget(self.frame_7)
        self.horizontalLayout_6.addWidget(self.frame_ColumnLeft)

        self.frame_ColumnCenter = QtWidgets.QFrame(self.frame_Central)
        self.frame_ColumnCenter.setStyleSheet("")
        self.frame_ColumnCenter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_ColumnCenter.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_ColumnCenter.setObjectName("frame_ColumnCenter")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_ColumnCenter)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.frame_5 = QtWidgets.QFrame(self.frame_ColumnCenter)
        self.frame_5.setMinimumSize(QtCore.QSize(0, 80))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_5)
        self.date_widget = QtWidgets.QLineEdit()
        self.date_widget.setEnabled(False)
        self.date_widget.setGeometry(QtCore.QRect(10, 15, 190, 50))
        self.date_widget.setMinimumSize(QtCore.QSize(190, 50))
        self.date_widget.setMaximumSize(QtCore.QSize(190, 50))
        self.date_widget.setStyleSheet("QLineEdit{\n"
"border-radius:15px;\n"
"background-color: #fff;\n"
"text-align: center;\n"
"font-size:15px;\n"
"color:#141428;\n"
"border:1px solid #e1e4ed;\n"
"text-aling:center;\n"
"}")
        self.date_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_7.addWidget(self.date_widget)

        self.notification = Notification()
        self.horizontalLayout_7.addWidget(self.notification)
        
        spacerItem = QtWidgets.QSpacerItem(1000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_7.addItem(spacerItem)
        
        self.verticalLayout_3.addWidget(self.frame_5)
        self.frame_DashCentral = QtWidgets.QFrame(self.frame_ColumnCenter)
        self.frame_DashCentral.setStyleSheet("QFrame{\n"
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
        self.frame_DashCentral.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_DashCentral.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_DashCentral.setObjectName("frame_DashCentral")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_DashCentral)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.frame_2 = QtWidgets.QFrame(self.frame_DashCentral)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_TitleDash = QtWidgets.QLabel(self.frame_2)
        self.label_TitleDash.setStyleSheet("QLabel{\n"
"\n"
"color:#E7E7E7;\n"
"border:0px;\n"
"font-size:30px;\n"
"font-weight: bold;\n"
"}")
        self.label_TitleDash.setObjectName("label_TitleDash")
        self.verticalLayout_9.addWidget(self.label_TitleDash)

        self.label_SubTitleDash = QtWidgets.QLabel(self.frame_2)
        self.label_SubTitleDash.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_SubTitleDash.setStyleSheet("QLabel{\n"
                                              "\n"
                                              "color:#E7E7E7;\n"
                                              "border:0px;\n"
                                              "font-size:15px;\n"
                                              "}")
        self.label_SubTitleDash.setObjectName("label_SubTitleDash")
        self.label_SubTitleDash.hide()
        self.verticalLayout_9.addWidget(self.label_SubTitleDash)

        self.download_list = QtWidgets.QListWidget(self.frame_2)
        self.download_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.download_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.download_list.setAcceptDrops(True)

        self.folder_button = QtWidgets.QPushButton(self.frame_2)
        self.folder_button.setStyleSheet("QPushButton{\n"
"\n"
"color:#E7E7E7;\n"
"font-weight: bold;\n"
"font-size:26px;\n"

"}")
        self.folder_button.hide()
        self.verticalLayout_9.addWidget(self.download_list)

        self.verticalLayout_9.addWidget(self.folder_button)

        self.verticalLayout_8.addWidget(self.frame_2)
        self.verticalLayout_3.addWidget(self.frame_DashCentral)
        self.horizontalLayout_6.addWidget(self.frame_ColumnCenter)

        self.verticalLayout.addWidget(self.frame_Central)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "exTor User"))
        self.pushButton_LogoReceitaFederal.setText(_translate("MainWindow", "exTor"))
        self.label_TxtTopDataUser.setText(_translate("MainWindow", "{USER}"))
        self.label_TxtTopDataUserType.setText(_translate("MainWindow", "{PROFILE_TYPE}"))
        self.home_button.setText(_translate("MainWindow", " Home"))

        self.pushButton_BtnServico.setText(_translate("MainWindow", "Upload"))
        self.date_widget.setText(_translate("MainWindow", "{weekday} 00/00/0000"))

        self.label_TitleDash.setText("Download")
        self.label_SubTitleDash.setText("Upload your desired files to the LAN to share with others")
        self.folder_button.setText("Select Folder")


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

        self.buttonClose = QtWidgets.QPushButton(self)
        self.buttonClose.setStyleSheet("border-radius: 15px;")
        self.buttonClose.setIcon(QtGui.QIcon("assets/img/arrow-right-circle.svg"))  # icon
        self.buttonClose.setFixedSize(18, 18)

        self.layout().addWidget(self.titleLabel, 0, 0)
        self.layout().addWidget(self.messageLabel, 1, 0)
        self.layout().addWidget(self.timeLabel, 2, 0)
        self.layout().addWidget(self.buttonClose, 0, 1, 2, 1)


class Notification(QtWidgets.QWidget):
    signNotifyClose = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(QtWidgets.QWidget, self).__init__(parent)
        self.notification_queue = []
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.nMessages = 0
        self.mainLayout = QtWidgets.QHBoxLayout(self)

    def setNotify(self, title, message):
        if self.nMessages == 0:  # can be set to whatever number of notifications wished
                m = Message(title, message, parent=self)
                self.mainLayout.addWidget(m)
                m.buttonClose.clicked.connect(self.onClicked)
                self.nMessages += 1
                self.show()

        else:
                m = Message(title, message, parent=self)
                self.notification_queue.append(m)

    def onClicked(self):
        self.mainLayout.removeWidget(self.sender().parent())
        self.nMessages -= 1
        self.adjustSize()

        while self.notification_queue and self.nMessages == 0:  # can be set to whatever number of notifications wished
                m = self.notification_queue.pop(0)
                self.mainLayout.addWidget(m)
                m.buttonClose.clicked.connect(self.onClicked)
                self.nMessages += 1
                self.show()

        if self.nMessages == 0:
            self.close()


# region TRASH
        # self.toolbar = QtWidgets.QToolBar(self.frame_2)
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        # self.toolbar.setMovable(False)
        # self.toolbar.hide()
        # self.verticalLayout_9.addWidget(self.toolbar)
# endregion