from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget
import sys
import pyqtgraph as pg
import math
import datetime
import numpy as np
import warnings
app = QApplication(sys.argv)

graphWidget = pg.PlotWidget(title="")
axis = pg.DateAxisItem()
graphWidget.setAxisItems({'bottom': axis})
graphWidget.setLabel('left', 'Requests')
graphWidget.setLabel('bottom', 'Time')


date_list = [math.floor((datetime.datetime.today() + datetime.timedelta(seconds=i)).timestamp()) for i in
             range(5, 51, 5)]
x = sorted(date_list, reverse=False)  # 100 time points
# self.x = [_ for _ in range(5, 51, 5)]
y = [1 for _ in range(10)]  # 100 data points


pen = pg.mkPen(width=-1)
pen2 = pg.mkPen(width=15, color="#0668E1")
# pen2.setStyle(QtCore.Qt.DashDotLine)
# pen2.setCapStyle(QtCore.Qt.RoundCap)
# pen2.setJoinStyle(QtCore.Qt.RoundJoin)
data_line = graphWidget.plot(x, y, pen=pen)

for i in range(len(x)):
    graphWidget.plot((x[i], x[i]), (0, y[i]), pen=pen2)
# graphWidget.clear()
# graphWidget.showGrid(x=True, y=True)

# data_line.addItem(line)

# graphWidget.show()
# app.exec_()

if __name__ == '__main__':
    warnings.simplefilter("ignore", category=RuntimeWarning)
    graphWidget.show()
    app.exec_()