from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import math
import datetime
import numpy as np


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
        self.home_button.setMinimumSize(QtCore.QSize(0, 50))
        self.home_button.setMaximumSize(QtCore.QSize(140, 50))
        self.home_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.home_button.setStyleSheet("QPushButton{\n"
"    color:#E7E7E7;\n"
"    border:0px;\n"
"    border-radius:25px;\n"
"    font-size:20px;\n"
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
        icon3.addPixmap(QtGui.QPixmap("assets/img/home.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_button.setIcon(icon3)
        self.home_button.setIconSize(QtCore.QSize(40, 40))
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
        icon6.addPixmap(QtGui.QPixmap("assets/img/users.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem)
        self.pushButton_BtnAssuntos = QtWidgets.QPushButton(self.frame_7)
        self.pushButton_BtnAssuntos.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_BtnAssuntos.setStyleSheet("QPushButton{\n"
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
"}")
        self.pushButton_BtnAssuntos.setObjectName("pushButton_BtnAssuntos")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("assets/img/slash.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_BtnAssuntos.setIcon(icon7)
        self.pushButton_BtnAssuntos.setIconSize(QtCore.QSize(24, 24))
        self.verticalLayout_6.addWidget(self.pushButton_BtnAssuntos)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem1)
        self.pushButton_BtnAcessoInfo = QtWidgets.QPushButton(self.frame_7)
        self.pushButton_BtnAcessoInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_BtnAcessoInfo.setStyleSheet("QPushButton{\n"
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
"}")
        self.pushButton_BtnAcessoInfo.setObjectName("pushButton_BtnAcessoInfo")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("assets/img/file-text.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_BtnAcessoInfo.setIcon(icon8)
        self.pushButton_BtnAcessoInfo.setIconSize(QtCore.QSize(24, 24))
        self.verticalLayout_6.addWidget(self.pushButton_BtnAcessoInfo)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem2)
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

        self.date_widget = QtWidgets.QLineEdit(self.frame_5)
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
        self.date_widget.setEnabled(False)
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
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 101))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_TitleDash = QtWidgets.QLabel(self.frame_2)
        self.label_TitleDash.setMaximumSize(QtCore.QSize(16777215, 50))
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
        self.verticalLayout_9.addWidget(self.label_SubTitleDash)

        self.clear = QtWidgets.QPushButton(self.frame_2)
        self.clear.setMinimumSize(QtCore.QSize(0, 25))
        self.clear.setMaximumSize(QtCore.QSize(100, 50))
        self.clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.clear.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.clear.setStyleSheet("QPushButton{\n"
                                       "    text-align:left;\n"
                                       "    color:#E7E7E7;\n"
                                       "    border:0px;\n"
                                       "    border-radius:12px;\n"
                                       "    font-size:20px;\n"
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
        icon3.addPixmap(QtGui.QPixmap("assets/img/trash-2.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clear.setIcon(icon3)
        self.clear.setIconSize(QtCore.QSize(40, 40))
        self.clear.hide()

        self.verticalLayout_9.addWidget(self.clear)
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem11)

        self.verticalLayout_8.addWidget(self.frame_2)

        self.logWidget = QtWidgets.QTextEdit(self.frame_DashCentral)
        self.logWidget.setReadOnly(True)

        self.logWidget.hide()
        pg.setConfigOptions(antialias=True, background="#29283E")

        self.graphWidget = pg.PlotWidget(self.frame_DashCentral, title="")
        axis = pg.DateAxisItem()
        self.graphWidget.setAxisItems({'bottom': axis})
        self.graphWidget.setLabel('left', 'Requests')
        self.graphWidget.setLabel('bottom', 'Time')
        self.graphWidget.setLimits(yMin=0)

        date_list = [math.floor((datetime.datetime.today() + datetime.timedelta(seconds=i)).timestamp()) for i in
                     range(5, 51, 5)]
        self.x = sorted(date_list, reverse=False)  # 100 time points
        self.y = [np.nan for _ in range(10)]  # 100 data points

        pen = pg.mkPen(width=-1)
        self.line_pen = pg.mkPen(width=15, color="#0668E1")

        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.table = QtWidgets.QTableWidget(self.frame_DashCentral)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.hide()

        self.verticalLayout_8.addWidget(self.table)
        self.verticalLayout_8.addWidget(self.graphWidget)
        self.verticalLayout_8.addWidget(self.logWidget)

        self.verticalLayout_3.addWidget(self.frame_DashCentral)
        self.horizontalLayout_6.addWidget(self.frame_ColumnCenter)

        self.verticalLayout.addWidget(self.frame_Central)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "exTor Admin"))
        self.pushButton_LogoReceitaFederal.setText(_translate("MainWindow", "exTor"))
        self.label_TxtTopDataUser.setText(_translate("MainWindow", "{USER}"))
        self.label_TxtTopDataUserType.setText(_translate("MainWindow", "{PROFILE_TYPE}"))
        self.home_button.setText(_translate("MainWindow", " Home"))
        self.pushButton_BtnServico.setText(_translate("MainWindow", "Swarms"))
        self.pushButton_BtnAssuntos.setText(_translate("MainWindow", "Banned IPs"))
        self.pushButton_BtnAcessoInfo.setText(_translate("MainWindow", "Log"))
        self.clear.setText(_translate("MainWindow", "Clear"))
        self.date_widget.setText(_translate("MainWindow", "{weekday} 00/00/0000"))
        self.label_TitleDash.setText("Requests on Tracker")
        self.label_SubTitleDash.setText("UDP tracker requests")



