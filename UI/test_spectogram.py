import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import scipy.signal
from matplotlib.pyplot import cm
from scipy.io import wavfile
import os
import sys

class SpectrogramWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(SpectrogramWidget, self).__init__(parent)
        
        # Set up the layout
        self.plot_item = self.addPlot()
        self.img = pg.ImageItem()
        self.plot_item.addItem(self.img)
        
        # Set labels
        self.plot_item.setLabel('left', 'Frequency', units='Hz')
        self.plot_item.setLabel('bottom', 'Time', units='s')
        
        # Setup inferno colormap (from matplotlib)
        inferno_colors = cm.get_cmap('inferno')
        positions = np.linspace(0, 1, 256)
        colors = [inferno_colors(i) for i in positions]
        colors = [(int(r*255), int(g*255), int(b*255), int(a*255)) for r, g, b, a in colors]
        color_map = pg.ColorMap(positions, colors)
        
        self.img.setColorMap(color_map)
        
        # Add colorbar
        self.colorbar = pg.ColorBarItem(
            values=(0, 1), 
            colorMap=color_map,
            label='Power (dB)'
        )
        self.colorbar.setImageItem(self.img)
        self.addItem(self.colorbar)
        
    def update_spectrogram(self, data, fs):
        """
        Update the spectrogram with new data
        
        Args:
            data: The signal data (1D numpy array)
            fs: Sampling frequency in Hz
        """
        # Compute the spectrogram with parameters optimized for audio
        f, t, Sxx = scipy.signal.spectrogram(data, fs=fs, nperseg=2048, noverlap=1536, 
                                            window='hann', scaling='density', mode='psd')
        
        # Convert to dB scale
        Sxx_db = 10 * np.log10(Sxx.T + 1e-10)  # Add small value to avoid log(0)
        
        # Normalize values for better visualization
        # vmin = np.max(Sxx_db) - 70  # 70dB dynamic range
        # vmax = np.max(Sxx_db)
        # norm_Sxx = np.clip((Sxx_db - vmin) / (vmax - vmin), 0, 1)
        
        # Update image and scale
        self.img.setImage(Sxx_db)
        tr = QtGui.QTransform()
        tr.scale(t[-1]/Sxx_db.shape[0], f[-1]/Sxx_db.shape[1])
        self.img.setTransform(tr)
        self.plot_item.setXRange(t[0], t[-1])
        self.plot_item.setYRange(f[0], f[-1])  # Limit to 8kHz for speech/music focus
        
        self.colorbar.setLevels((Sxx_db.min(), Sxx_db.max()))


class AudioSpectrogramApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(AudioSpectrogramApp, self).__init__()
        
        self.setWindowTitle('Audio Spectrogram with PyQtGraph')
        self.resize(1000, 700)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create file input section
        # file_layout = QtWidgets.QHBoxLayout()
        
        # file_layout.addWidget(self.file_path_input)
        # Create spectrogram widget
        self.spectrogram = SpectrogramWidget()
        
        # Add widgets to main layout
        main_layout.addWidget(self.spectrogram)
        
        # Status bar for messages
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.load_audio()
        
    def load_audio(self):
        file_path = "A:/gitclones/EEproject/raw_data/assets_noisy_snr0.wav" #self.file_path_input.text()
        if not file_path:
            self.status_bar.showMessage("Please enter a file path", 3000)
            return
        
        if not os.path.exists(file_path):
            self.status_bar.showMessage(f"File not found: {file_path}", 3000)
            return
        
        try:
            # Load the audio file
            fs, data = wavfile.read(file_path)
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Normalize audio to range [-1, 1]
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0
            elif data.dtype == np.int32:
                data = data.astype(np.float32) / 2147483648.0
            elif data.dtype == np.uint8:
                data = (data.astype(np.float32) - 128) / 128.0
            
            # Update the spectrogram
            self.spectrogram.update_spectrogram(data, fs)
            
            # Update status
            duration = len(data) / fs
            self.status_bar.showMessage(
                f"Loaded: {os.path.basename(file_path)} | Duration: {duration:.2f}s | Sample rate: {fs}Hz", 
                5000
            )
            
        except Exception as e:
            self.status_bar.showMessage(f"Error loading audio: {str(e)}", 5000)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = AudioSpectrogramApp()
    window.show()
    sys.exit(app.exec_())