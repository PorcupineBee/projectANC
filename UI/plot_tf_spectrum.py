import sys
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from scipy.signal import spectrogram

class TimeFreqContourWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        layout = QVBoxLayout(self)

        # Add Play Button
        self.play_button = QPushButton("Play")
        layout.addWidget(self.play_button)

        # Create Graphics Layout Widget (instead of ImageView)
        self.plot_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.plot_widget)

        # Create a plot and image item
        self.plot = self.plot_widget.addPlot()
        self.img_item = pg.ImageItem()
        self.plot.addItem(self.img_item)

        # Set axis labels
        self.plot.setLabel("bottom", "Time (s)")
        self.plot.setLabel("left", "Frequency (Hz)")

        # Generate sample time-frequency power spectrum
        self.time, self.freqs, self.power_spectrum = self.generate_synthetic_spectrogram()

        # Create inferno colormap
        self.lut = self.create_inferno_colormap()

        # Display the initial power spectrum with colormap
        self.update_plot()

        # Connect button to start animation
        self.play_button.clicked.connect(self.start_animation)

        # Animation parameters
        self.current_frame = 0
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.animate)

    def generate_synthetic_spectrogram(self):
        """Generate a synthetic time-frequency power spectrum using a test signal."""
        fs = 48000  # Sampling frequency
        # N = 800000
        t = np.arange(0, 5, 1/fs)  # 5 seconds of data
        signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 40 * t)  # Two-frequency signal

        # Compute spectrogram
        f, t_spec, Sxx = spectrogram(signal, fs, nperseg=256, noverlap=200)

        # Normalize Sxx for visualization
        Sxx = 10 * np.log10(Sxx + 1e-10)  # Convert to dB scale
        
        return t_spec, f, Sxx

    def create_inferno_colormap(self):
        """Create a lookup table (LUT) for the inferno colormap from Matplotlib."""
        colormap = plt.get_cmap("inferno")  # Get inferno colormap
        colors = colormap(np.linspace(0, 1, 256))[:, :3] * 255  # Convert to 8-bit RGB
        return colors.astype(np.uint8)

    def update_plot(self):
        """Update the power spectrum plot with inferno colormap using ImageItem."""
        self.img_item.setImage(self.power_spectrum)  # Transpose to match PyQtGraph orientation
        self.img_item.setLookupTable(self.lut)  # Apply inferno colormap
        self.img_item.setLevels([np.min(self.power_spectrum), np.max(self.power_spectrum)])

        # Set correct scaling
        # self.img_item.setScale(self.time[1] - self.time[0], self.freqs[1] - self.freqs[0])
        self.img_item.setPos(self.time[0], self.freqs[0])

    def start_animation(self):
        """Start animation for dynamic effect."""
        self.current_frame = 0
        self.timer.start(100)  # Update every 100ms

    def animate(self):
        """Update plot dynamically to create an animation effect."""
        if self.current_frame < self.power_spectrum.shape[1]:
            self.img_item.setImage(self.power_spectrum[:, :self.current_frame])  # Transpose for correct orientation
            self.img_item.setLookupTable(self.lut)  # Apply LUT to each frame
            self.current_frame += 1
        else:
            self.timer.stop()  # Stop animation when finished

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeFreqContourWidget()
    window.show()
    sys.exit(app.exec_())
