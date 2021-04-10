from PyQt5 import QtGui, QtCore
import sys

# import ui_main
# import main_ui_test as ui_main
import ui_main_2 as ui_main
import random
import numpy as np
import pyqtgraph
from scipy import signal as sig
from serial_reader import SpoofSerial
from threading import Thread


def get_fft(data, sampling_freq):
    """Given some data and cycles per second, returns FFTfreq and FFT"""
    # data = data * np.hamming(len(data))

    fft = np.abs(np.fft.fft(data))
    # fft=10*np.log10(fft)
    freq = np.fft.fftfreq(len(fft), 1.0/sampling_freq)

    return freq, fft


class ExampleApp(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self, src=None, parent=None):
        if src is None:
            exit("src not provided to the app")
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

        self.sampling_freq = 1000
        self.seconds_to_show = 2

        self.button_fft_apply.clicked.connect(self.on_fft_update)

        self.signal = src

    def update(self):
        """Runs updates on graphs points infinitely"""

        # effectively this is
        # "while True:"
        # due to the end of the function

        if not self.signal.reassignment_in_progress :

            display_x = self.signal.x[-self.sampling_freq * self.seconds_to_show:]
            display_y = self.signal.y[-self.sampling_freq * self.seconds_to_show:]

            # print(sig.find_peaks(list(self.signal.x)))
            fft_x, fft_y = get_fft(display_y, self.sampling_freq)

            # Making sure that FFT will never go further than to 1.0
            fft_y_max = np.max(fft_y)
            if fft_y_max > self.maxFFT:
                self.maxFFT = fft_y_max
                print("maxFFT " + str(self.maxFFT))

            blue_pen = pyqtgraph.mkPen(color='b')
            self.grPCM.plot(
                display_x,
                display_y,
                pen=blue_pen,
                clear=True
            )

            red_pen = pyqtgraph.mkPen(color='r')
            self.grFFT.plot(
                fft_x,
                fft_y / self.maxFFT,
                pen=red_pen,
                clear=True
            )

        QtCore.QTimer.singleShot(1, self.update)  # QUICKLY repeat
        # doing this instead of while loop to stay on this thread in the infinite loop
        # PyQT doesn't allow it's GUI to be used across a few threads

    @QtCore.pyqtSlot()
    def on_fft_update(self):
        print("min_freq" + str(self.min_freq.displayText()))
        print("max_freq" + str(self.max_freq.displayText()))
        if self.x_min_FFT != int(self.min_freq.displayText()) or self.x_max_FFT != int(self.max_freq.displayText()):
            self.x_min_FFT = int(self.min_freq.displayText())
            self.x_max_FFT = int(self.max_freq.displayText())
            self.grFFT.plotItem.setRange(xRange=[self.x_min_FFT, self.x_max_FFT])
        if self.x_max_ampl != int(self.max_ampl.displayText()):
            self.x_max_ampl = int(self.max_ampl.displayText())


if __name__ == "__main__":
    try:
        app = QtGui.QApplication(sys.argv)

        signal = SpoofSerial()
        signal.start()
        form = ExampleApp(src=signal)
        form.show()
        # update_thread = Thread(target=form.update_infinitely)
        # update_thread.start()
        form.update()
        app.exec_()
        print("DONE")
    except KeyboardInterrupt:
        exit()
