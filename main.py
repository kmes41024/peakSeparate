from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor
from scipy.optimize import curve_fit
import numpy as np
from openpyxl import Workbook
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget, QLabel, QTableWidget, \
    QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from peakSeparate import peakSeparate

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)         # 新建一個figure
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #定義FigureCanvas的尺寸，設置FigureCanvas，使其盡可能的向外填充空間
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def start_static_plot(self, peak, savePath, fileName):
        self.fig.suptitle(fileName)
        self.axes.cla()

        color = ["#FFD9EC", "#A6FFA6", "#ACD6FF", "#E3E3E3", "#DEDEBE", "#FFFF82", "#80FFFF", "#C7C7E2", "#FFFFD4",
                 "#ffc1b3", "#deffb3", "#b3ffe7", "#ffdaa3", "#ffa3fd", "#FF8282", "#F0F000"]

        for k in range(1, len(peak.allSeparatedPeak)):
            c = 0
            for n, i in enumerate(peak.allSeparatedPeak[k][2]):
                i = np.array(i)
                i = np.where(i < 0.0, 0.0, i)
                maxV = np.max(i)
                index = peak.allSeparatedPeak[k][0][i.tolist().index(maxV)]
                if maxV != 0:
                    self.axes.fill_between(peak.allSeparatedPeak[k][0], i, peak.allSeparatedPeak[k][1], facecolor=color[c], alpha=0.6)
                    self.axes.annotate(index, xy=(index, maxV), xytext=(index + 1, maxV), size=6)

                if c + 1 == len(color):
                    c = -1
                c += 1

            self.axes.scatter([i[0] for i in peak.allSeparatedPeak[k][3]], [i[1] for i in peak.allSeparatedPeak[k][3]], s=10, c='black')

        for i in range(len(peak.rawDataX)):
            if peak.rawDataX[i] >= 300:
                x_300 = i
                break

        self.axes.plot(peak.rawDataX[x_300:-1], peak.rawDataY[x_300:-1], '-b', label='data', lw=1)
        self.axes.plot(peak.rawDataX[x_300:-1], peak.drawY[x_300:-1], ':', c='red', label='data', lw=1)
        
        self.axes.grid(True)
        self.draw()


class Ui_Form(object):
    savePath = ""
    lastOpenPath = "C:/"        

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1355, 887)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        Form.setFont(font)
        self.userMessage = QLabel(Form)
        self.userMessage.setGeometry(QtCore.QRect(1180, 620, 151, 41))
        self.userMessage.setObjectName("userMessage")
        self.userMessage.setAlignment(Qt.AlignRight)
        self.widgetImage = QWidget(Form)
        self.widgetImage.setGeometry(QtCore.QRect(20, 20, 1321, 521))
        self.widgetImage.setObjectName("widgetImage")
        self.tableResult = QTableWidget(Form)
        self.tableResult.setGeometry(QtCore.QRect(20, 550, 1031, 321))
        self.tableResult.setObjectName("tableResult")
        self.tableResult.setColumnCount(3)
        self.tableResult.setRowCount(0)
        self.tableResult.setHorizontalHeaderLabels(['X', 'Fit_Y', 'Orig_Y'])
        self.tableResult.setShowGrid(True)
        self.tableResult.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableResult.setEditTriggers(QAbstractItemView.NoEditTriggers)          # 禁止編輯
        self.tableResult.setSelectionBehavior(self.tableResult.SelectRows)          # 選中整列
        self.tableResult.verticalHeader().setVisible(False)                         # 不顯示左側表頭
        self.pushButtonFile = QPushButton(Form)
        self.pushButtonFile.setGeometry(QtCore.QRect(1210, 570, 121, 41))
        self.pushButtonFile.setObjectName("pushButtonFile")
        self.pushButtonFile.clicked.connect(self.getFile)
        self.pathMessage = QLabel(Form)
        self.pathMessage.setGeometry(QtCore.QRect(1055, 800, 276, 41))
        self.pathMessage.setObjectName("pathMessage")
        self.pathMessage.setAlignment(Qt.AlignRight)
        self.saveButtonFile = QPushButton(Form)
        self.saveButtonFile.setGeometry(QtCore.QRect(1150, 830, 181, 41))
        self.saveButtonFile.setObjectName("saveButtonFile")
        self.saveButtonFile.clicked.connect(self.saveFile)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=12, height=4, dpi=100)
        self.mpl_ntb = NavigationToolbar(self.mpl, self)             # 添加完整的 toolbar
        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)
        self.widgetImage.setLayout(self.layout)

    def getFile(self):
        self.userMessage.setText("loading...")
        txtFileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "open txt", self.lastOpenPath, "Normal text file (*.txt)")

        if txtFileName != "":
            name = txtFileName.split("/")[:-1]
            if self.savePath == "":
                self.savePath = "/".join(name) + "/"
                self.pathMessage.setText(self.savePath)
            fileName = (txtFileName.split("/")[-1]).split(".")[0]
            self.lastOpenPath = "/".join(name) + "/"

            newPeak = peakSeparate(self.savePath, txtFileName)

            self.mpl.start_static_plot(newPeak, self.savePath, fileName)

            if "" in newPeak.topX:
                spaceIndex = newPeak.topX.index("") + 1
            else:
                spaceIndex = 0

            col = 0
            self.tableResult.setRowCount(len(newPeak.topX) - spaceIndex - 1)
            for i in range(spaceIndex, len(newPeak.topX)):
                if str(newPeak.topX[i]) != "":
                    newItem = QTableWidgetItem(str(newPeak.topX[i]))
                    self.tableResult.setItem(col, 0, newItem)
                    newItem = QTableWidgetItem(str(round(newPeak.topY_fit[i], 2)))
                    self.tableResult.setItem(col, 1, newItem)
                    newItem = QTableWidgetItem(str(round(newPeak.topY_actual[i], 2)))
                    self.tableResult.setItem(col, 2, newItem)
                    col += 1

            self.userMessage.setText("")
        else:
            self.userMessage.setText("")

    def saveFile(self):
        self.savePath = QtWidgets.QFileDialog.getExistingDirectory(self, "save dir", "C:/")
        self.pathMessage.setText(self.savePath)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "重疊峰分峰"))
        self.pushButtonFile.setText(_translate("Form", "選擇檔案"))
        self.saveButtonFile.setText(_translate("Form", "選擇儲存資料夾..."))


class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec())
