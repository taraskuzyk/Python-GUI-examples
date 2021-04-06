from PyQt5 import QtGui, QtCore
import sys

# import ui_main
# import main_ui_test as ui_main
import ui_main_2 as ui_main

import numpy as np
import pyqtgraph
import SWHear


class ExampleApp(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self, parent=None):
        pyqtgraph.setConfigOption('background', 'w')  # before loading widget
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.grFFT.plotItem.showGrid(True, True, 0.7)
        self.grPCM.plotItem.showGrid(True, True, 0.7)
        self.maxFFT = 0
        self.maxPCM = 0

        self.min_freq.setText("0")
        self.max_freq.setText("50000")
        self.max_ampl.setText("500000")
        self.x_min_FFT = 0
        self.x_max_FFT = 50000
        self.x_max_ampl = 50000

        self.button_fft_apply.clicked.connect(self.on_fft_update)

        self.ear = SWHear.SWHear(rate=100000, updatesPerSecond=30)
        self.ear.stream_start()

    def update(self):
        if not self.ear.data is None and not self.ear.fft is None:
            pcmMax = np.max(np.abs(self.ear.data))

            # Making sure that FFT will never go further than to 1.0
            if np.max(self.ear.fft) > self.maxFFT:
                self.maxFFT = np.max(np.abs(self.ear.fft))
                # self.grFFT.plotItem.setRange(yRange=[0,self.maxFFT])
                self.grFFT.plotItem.setRange(yRange=[0, 1])
                print("maxFFT " + str(self.maxFFT))

            if pcmMax > self.maxPCM:
                self.maxPCM = pcmMax
                self.grPCM.plotItem.setRange(yRange=[-pcmMax, pcmMax])

            pen = pyqtgraph.mkPen(color='b')

            self.grPCM.plot(self.ear.datax, self.ear.data, pen=pen, clear=True)
            pen = pyqtgraph.mkPen(color='r')
            self.grFFT.plot(self.ear.fftx, self.ear.fft / self.x_max_ampl, pen=pen, clear=True)
            # self.grFFT.plot(self.ear.fftx, self.ear.fft, pen=pen, clear=True)
        QtCore.QTimer.singleShot(1, self.update)  # QUICKLY repeat

    @QtCore.pyqtSlot()
    def on_fft_update(self):
        print("min_freq" + str(self.min_freq.displayText()))
        print("max_freq" + str(self.max_freq.displayText()))
        if self.x_min_FFT != int(self.min_freq.displayText()) or self.x_max_FFT != int(self.max_freq.displayText()):
            self.x_min_FFT = int(self.min_freq.displayText())
            self.x_max_FFT = int(self.max_freq.displayText())
            self.grFFT.plotItem.setRange(xRange=[self.x_min_FFT, self.x_max_FFT])
        if self.x_max_ampl != int(self.x_max_ampl.displayText())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
