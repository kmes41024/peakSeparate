from scipy.optimize import curve_fit
import numpy as np
from openpyxl import Workbook
import sys
import matplotlib.pyplot as plt

class peakSeparate:
    def __init__(self, savePath, filepath):
        self.rawDataX = []              # 記錄整個(原始)光譜的峰座標
        self.rawDataY = []
        
        self.splitPos = []              # 記錄各個重疊峰的start & end在rawData的index

        self.topX = []                  # 記錄所有峰頂座標
        self.topY_fit = []              # 記錄分峰頂峰的Y座標
        self.topY_actual = []           # 記錄分峰頂峰對應到fit Curve的Y座標

        self.fitCurveY = []             # 記錄重疊峰做curve_fit後的Y座標
        self.drawY = []                 # 串接所有重疊峰的fit curve

        self.allSeparatedPeak = []      # 記錄每個重疊峰的分峰

        self.readData(filepath)
        self.splitData()

        for i in range(len(self.splitPos)):
            self.sub_peakX = []
            self.sub_peakY = []

            self.guess_total = []
            self.width = 10

            startX = self.rawDataX[self.splitPos[i][0]]
            for s in range(10):
                self.sub_peakX.append(startX - 10 + s)
                self.sub_peakY.append(0.0)

            self.sub_peakX.extend(self.rawDataX[self.splitPos[i][0]:self.splitPos[i][1] + 1].tolist())
            self.sub_peakY.extend(self.rawDataY[self.splitPos[i][0]:self.splitPos[i][1] + 1].tolist())

            endX = self.rawDataX[self.splitPos[i][1]]
            for e in range(10):
                self.sub_peakX.append(endX + 1 + e)
                self.sub_peakY.append(0.0)

            self.sub_peakX = np.array(self.sub_peakX)
            self.sub_peakY = np.array(self.sub_peakY)

            if self.sub_peakY.max() >= 200 or i == 0:
                self.doneFit = False

                while not self.doneFit:
                    maxWidth = (self.sub_peakX[-1] - self.sub_peakX[0]) * 2 / 3

                    self.setPeak()
                    self.setSepratePeak()
                    if not self.doneFit:
                        self.width += 2
                    if self.width > maxWidth:
                        break
                
                if self.doneFit == False:
                    self.fitCurveY.append(self.sub_peakY[10: -10].tolist())
            else:
                self.fitCurveY.append(self.sub_peakY[10: -10].tolist())
            
        self.addAllCurveFit()
        self.saveTopToCsv(savePath, (filepath.split("/")[-1]).split(".")[0])

    ##讀txt檔
    def readData(self, path):
        f = open(path, 'r')

        data_x = []
        data_y = []

        lineCount = 0
        for line in f.readlines():
            tmp = line.split('\t')
            tmp[0] = int(tmp[0])
            tmp[1] = float(tmp[1])
            data_x.append(tmp[0])
            data_y.append(tmp[1])
            lineCount += 1
            if lineCount > 1413:
                break
        f.close()

        data_x.append(0)
        data_y.append(0)

        self.rawDataX = np.array(data_x)
        self.rawDataY = np.array(data_y)
        self.rawDataY = np.where(self.rawDataY <= 50.0, 0.0, self.rawDataY)

    def splitData(self):
        start = False
        startY_index = 0
        for i in range(len(self.rawDataY)):
            if self.rawDataY[i] != 0.0 and start != True:
                startY_index = i
                start = True
            elif self.rawDataY[i] == 0.0 and start == True:
                self.splitPos.append([startY_index, i - 1])
                start = False

        if start:
            self.splitPos.append([startY_index, i])
            start = False

    def func(self, x, *params):
        # 根據參數的長度確定要擬合的函數數量
        num_func = int(len(params) / 3)

        # 將每個參數插入一個高斯函數並添加到 y_list
        y_list = []
        for i in range(num_func):
            y = np.zeros_like(x)
            param_range = list(range(3 * i, 3 * (i + 1), 1))
            amp = params[int(param_range[0])]
            ctr = params[int(param_range[1])]
            wid = params[int(param_range[2])]
            y = y + amp * np.exp(-((x - ctr) / wid) ** 2)
            y_list.append(y)

        # 覆蓋 y_list 中的所有高斯函數
        y_sum = np.zeros_like(x)
        for i in y_list:
            y_sum = y_sum + i

        # 最後添加背景
        y_sum = y_sum + params[-1]
        return y_sum

    def fit_plot(self, x, *params):
        num_func = int(len(params) / 3)
        y_list = []
        for i in range(num_func):
            y = np.zeros_like(x)
            param_range = list(range(3 * i, 3 * (i + 1), 1))
            amp = params[int(param_range[0])]
            ctr = params[int(param_range[1])]
            wid = params[int(param_range[2])]
            y = y + amp * np.exp(-((x - ctr) / wid) ** 2) + params[-1]
            y_list.append(y)
        return y_list

    def gaussian(self, x, *param):
        return param[0] * np.exp(-np.power(x - param[2], 2.) / (2 * np.power(param[4], 2.))) + param[1] * np.exp(
            -np.power(x - param[3], 2.) / (2 * np.power(param[5], 2.)))

    def setPeak(self):
        guess = []

        startX = self.sub_peakX[0]
        endX = self.sub_peakX[len(self.sub_peakX) - 1]
        maxY = np.array(self.sub_peakY).max()
        highestX = self.sub_peakX[self.sub_peakY.tolist().index(maxY)]

        # ---最高峰的左邊----------------------------#
        minus = self.width
        w = int(minus / 2)
        nowX = highestX
        while nowX - minus >= startX:
            valueX = nowX - minus
            while valueX not in self.sub_peakX:
                valueX -= 1
            x_index = self.sub_peakX.tolist().index(valueX)
            nowhigh = self.sub_peakY[x_index]
            if nowhigh != 0:
                guess.append([0, valueX, w])
            nowX = nowX - minus

        # ---最高峰----------------------------------#
        guess.append([0, highestX, w])

        # ---最高峰的一右邊--------------------------#
        add = self.width
        w = int(add / 2)
        nowX = highestX

        while nowX + add <= endX:
            valueX = nowX + add
            while valueX not in self.sub_peakX:
                valueX -= 1
            x_index = self.sub_peakX.tolist().index(valueX)
            nowhigh = self.sub_peakY[x_index]
            if nowhigh != 0:
                guess.append([0, valueX, w])
            nowX = nowX + add

        # ---設定背景强度---------------------------#
        background = 10

        self.guess_total = []
        for i in guess:
            self.guess_total.extend(i)
        self.guess_total.append(background)

    ##計算重疊峰 fit後的峰 & 處理分峰
    def setSepratePeak(self):
        try:
            popt, pcov = curve_fit(self.func, self.sub_peakX, self.sub_peakY, p0=self.guess_total)
            self.doneFit = True
        except RuntimeError:
            self.doneFit = False

        if self.doneFit:
            fit = np.array(self.func(self.sub_peakX, *popt))
            fit = np.where(fit < 0, 0, fit)

            y_list = self.fit_plot(self.sub_peakX, *popt)
            baseline = np.zeros_like(self.sub_peakX)

            point = []  # 分峰的最高點

            # y_list: 記錄分峰的peak資料
            for n, i in enumerate(y_list):
                i = np.array(i)
                i = np.where(i < 0.0, 0.0, i)
                maxV = np.max(i)
                index = self.sub_peakX[i.tolist().index(maxV)]
                if maxV != 0:
                    point.append([index, maxV, round(self.sub_peakY[i.tolist().index(maxV)], 2)])

            point.sort()

            self.allSeparatedPeak.append([self.sub_peakX, baseline, y_list, point])

            self.topX.extend([i[0] for i in point])
            self.topY_fit.extend([i[1] for i in point])
            self.topY_actual.extend([i[2] for i in point])
            self.topX.append("")
            self.topY_fit.append("")
            self.topY_actual.append("")

            fitY = self.func(self.sub_peakX, *popt)
            self.fitCurveY.append(fitY[10: -10].tolist())

    #將每段重疊峰的fit Curve組合在一起
    def addAllCurveFit(self):
        self.drawY = self.rawDataY.copy()
        for i in range(len(self.splitPos)):  # 被切成幾個重疊峰
            count = 0
            for index in range(self.splitPos[i][0], (self.splitPos[i][1] + 1)):  # 每個重疊峰區段
                self.drawY[index] = self.fitCurveY[i][count]
                count += 1

    #儲存fit後的Curve
    def saveFitCurve(self, path, fileName): 
        for i in range(len(self.rawDataX)):
            if self.rawDataX[i] >= 300:
                x_300 = i
                break

        wb = Workbook()
        ws = wb.active

        ws.append(["X", "Y"])
        for i in range(x_300, len(self.rawDataX)):
            ws.append([self.rawDataX[i], self.drawY[i]])

        wb.save(path + "//" + fileName + '-fitCurve.xlsx')

    #儲存每個分峰的最高點對應到的x座標、y座標、最高點對應到fit Curve的值
    def saveTopToCsv(self, path, fileName):
        wb = Workbook()
        ws = wb.active

        spaceIndex = 0 
        ws.append(["X", "sub_curve Y", "actual Y"])
        for i in range(spaceIndex, len(self.topX)):
            ws.append([self.topX[i], self.topY_fit[i], self.topY_actual[i]])

        wb.save(path + "//" + fileName + '.xlsx')

