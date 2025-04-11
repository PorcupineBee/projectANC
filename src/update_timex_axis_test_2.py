import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui


class RealTimeSpectrogram(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup the plot
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.img_item = pg.ImageItem()
        self.plot_widget.addItem(self.img_item)

        self.fs = 16000               # Sampling rate
        self.chunk_size = 512         # Samples per update (32 ms at 16kHz)
        self.update_interval = 32     # ms
        self.freq_bins = 256          # Number of frequency bins
        self.sec_per_chunk = self.chunk_size / self.fs

        self.view_duration = 5        # Visible duration in seconds
        self.total_data = np.empty((self.freq_bins, 0))  # Growing data array
        self.current_time = 0         # Current time in seconds

        # Set colormap (optional)
        self.img_item.setLookupTable(pg.colormap.get('inferno').getLookupTable())

        # Scale image so that 1 column = 1 chunk (in time)
        tr = QtGui.QTransform()
        tr.scale(self.sec_per_chunk, 1)  # x = time, y = freq

        self.img_item.setTransform(tr)
        
        # Enable mouse-based panning/scrolling
        self.plot_widget.setMouseEnabled(x=True, y=False)
        # self.plot_widget.setLabel('bottom', 'Time', 's')
        # self.plot_widget.setLabel('left', 'Frequency', 'Hz')

        # Setup timer for real-time updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(self.update_interval)

    def update_image(self):
        # Simulate new column (replace with your real FFT data)
        new_column = np.random.rand(self.freq_bins, 1) * 100

        # Append new data
        self.total_data = np.hstack((self.total_data, new_column))
        self.current_time += self.sec_per_chunk

        # Update the image with full data
        self.img_item.setImage(self.total_data, autoLevels=False)

        # Compute new view range (last 5 seconds)
        visible_cols = int(self.view_duration / self.sec_per_chunk)
        max_cols = self.total_data.shape[1]
        right_time = max_cols * self.sec_per_chunk
        left_time = max(0, right_time - self.view_duration)

        # Adjust view to scroll automatically
        self.plot_widget.setXRange(left_time, right_time, padding=0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = RealTimeSpectrogram()
    win.resize(1000, 600)
    win.show()
    sys.exit(app.exec_())
