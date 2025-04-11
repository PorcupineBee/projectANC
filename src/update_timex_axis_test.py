import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

class RealTimeSpectrogram(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup pyqtgraph image view
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.img_item = pg.ImageItem()
        self.img_item.setLevels([-1, 1])
        self.plot_widget.addItem(self.img_item)
        # self.plot_widget.setLabel('bottom', 'Time', 's')
        # self.plot_widget.setLabel('left', 'Frequency', 'Hz')

        # Simulation parameters
        self.fs = 16000  # Sample rate
        self.chunk_size = 512  # Samples per frame
        self.update_interval = 32  # milliseconds
        self.freq_bins = 256  # Simulate 256 frequency bins
        self.sec_per_chunk = self.chunk_size / self.fs
        
        # Time axis (will shift as data grows)
        self.time_window_secs = 5  # initial view of 5 seconds
        self.current_time = 0
        self.max_cols = int(self.fs * self.time_window_secs)

        # Initialize data matrix (frequency x time)
        # self.data = np.random.normal(0, 1, size=(self.freq_bins, self.max_cols))
        self.data = np.array([])

        # Set colormap (optional)
        self.img_item.setLookupTable(pg.colormap.get('inferno').getLookupTable())

        # Set image scale: x = time, y = frequency
        # self.img_item.scale(1 / (self.fs / self.chunk_size), 1)  # x scale = seconds per chunk

        # Timer to simulate new data every 32 ms
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(self.update_interval)
        

    def update_image(self):
        # Simulate new spectrogram column (replace this with real FFT data)
        # new_columns = np.random.normal(1, 1, size=(self.freq_bins, self.chunk_size))
        new_columns = np.ones((self.freq_bins, self.chunk_size))

        # Append and maintain rolling window
        if len(self.data) == 0:
            self.data = np.zeros((self.freq_bins, self.chunk_size))
        else:
            self.data = np.hstack((self.data, new_columns))
        # if self.data.shape[1] > self.max_cols:
        #     self.data = self.data[:, -self.max_cols:]

        # Update image
        self.img_item.setImage(self.data.T, autoLevels=False)
        # self.img_item.setImage(self.data/np.abs(self.data).max(), autoLevels=False)

        # Optionally update x-range
        print(self.data.shape)
        self.current_time += self.sec_per_chunk
        
        tr = QtGui.QTransform()
        tr.scale(self.current_time/self.data.shape[1], 20000/self.data.shape[0])
        self.img_item.setTransform(tr)
        self.plot_widget.setXRange(self.current_time-self.time_window_secs, self.current_time)
        self.plot_widget.setYRange(20, 20000)  #
        # self.img_item.setRect(QtCore.QRectF(current_time - self.time_window_secs, 0,
        #                                     self.time_window_secs, self.freq_bins))
        if self.current_time >= self.time_window_secs * 2:
            self.timer.stop()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimeSpectrogram()
    window.show()
    sys.exit(app.exec_())
