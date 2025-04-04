import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QSpinBox, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpacerItem, QSizePolicy, 
                             QFrame, QRadioButton)
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import scipy.signal

import numpy as np
import sounddevice as sd
from scipy.signal import spectrogram
from PyQt5.QtCore import QTimer
from UI.play_soundbox import NoisePlayerThread


class TimeFrequencyWidget(QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self.spectogramWidget = SpectrogramWidget()
        self.initUI()
        
        # some flags
        self.audio_running = False
        self.Audio_thread = AudioPLayThread()
        
        if (("audio_data" in kwargs.keys()) and 
            ("fs" in kwargs.keys())):
            audio_data = kwargs.pop("audio_data")
            fs = kwargs.pop("fs")
            self.updateAudio(audio_data=audio_data,
                             fs=fs)
        
    def initUI(self):
        # region UI part
        # Layouts
        main_layout = QVBoxLayout()
        top_frame = QFrame()
        top_frame.setStyleSheet("""QSpinBox {
    background-color: #333;
    color: #fff;
    font-size: 10px;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 2px;
    selection-background-color: #777;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #444;
    border: none;
    width: 16px;
    height: 12px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #666;
}

QSpinBox::up-arrow {
    image: url(icons/up_arrow.png); /* Use a custom icon or remove */
    width: 5px;
    height: 5px;
}

QSpinBox::down-arrow {
    image: url(icons/down_arrow.png);
    width: 5px;
    height: 5px;
}
QLabel {
    color:#f1f1f1;
}
QRadioButton{
    color:#f1f1f1;
    font-weight:bold;
}
""")    
        
        control_layout = QHBoxLayout()
        
        # Play/Pause Button
        self.play_pause_btn = QPushButton("play")
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_pause_btn)
        
        # Spinbox for time window size
        label = QLabel(self)
        label.setText("Window size")
        control_layout.addWidget(label)
        
        self.time_window_spinbox = QSpinBox()
        self.time_window_spinbox.setRange(100, 5000)  # Set limits
        self.time_window_spinbox.setValue(1000)  # Default value (ms)
        control_layout.addWidget(self.time_window_spinbox)
        
        self.showSpectogram = QRadioButton(self)
        self.showSpectogram.setText("Show Spectogram")
        self.showSpectogram.toggled.connect(self.spectogramWidget.showSpectrum)
        control_layout.addWidget(self.showSpectogram)
        
        hspecer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        control_layout.addItem(hspecer)
        
        control_layout.setContentsMargins(10, 5, 0, 0)
        control_layout.setSpacing(10)
        top_frame.setLayout(control_layout)
        main_layout.addWidget(top_frame)
        
        # endregion
        # PyQtGraph Plot Widget
        # plot_frame = QFrame()
        # plot_layout = QVBoxLayout()
        # plot_layout.addWidget(self.spectogramWidget)
        # plot_frame.setLayout(plot_layout)
                
        main_layout.addWidget(self.spectogramWidget)
        
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # region Not needed
        # self.setWindowTitle("Time-Frequency Spectrum Viewer")
        # self.setGeometry(100, 100, 800, 500)
        
        # # Data for simulation
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_progress)
        # self.is_playing = False
        # self.progress_line = pg.InfiniteLine(pos=0, angle=90, pen='r')
        # self.spectogramWidget.addItem(self.progress_line)
        
        # # Load example audio
        # self.audio_data, self.sample_rate = self.load_audio()
        # self.spectrogram_data, self.freqs, self.times = self.compute_spectrogram(self.audio_data, self.sample_rate)
        
        # # Plot spectrogram
        # self.img = pg.ImageItem()
        # self.spectogramWidget.addItem(self.img)
        # self.img.setImage(10 * np.log10(self.spectrogram_data + 1e-10))
        # self.img.scale(self.times[-1] / self.img.width(), self.freqs[-1] / self.img.height())
        # self.current_time_index = 0
        # endregion
        
    
    # def load_audio(self):
    #     duration = 5  # seconds
    #     sample_rate = 44100
    #     t = np.linspace(0, duration, duration * sample_rate, endpoint=False)
    #     audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # Example sine wave
    #     return audio_data, sample_rate
    
    # def compute_spectrogram(self, audio_data, sample_rate):
    #     f, t, Sxx = spectrogram(audio_data, fs=sample_rate, 
    #                             window='hamming',
    #                             noverlap=0.75,
    #                             detrend='constant',
    #                             scaling='density',
    #                             nperseg=None)
    #     return Sxx, f, t
    
    def toggle_playback(self):
        if self.is_playing:
            self.timer.stop()
            self.play_pause_btn.setText("Play")
        else:
            self.timer.start(50)  # Update every 50ms
            self.play_pause_btn.setText("Pause")
            sd.play(self.audio_data, samplerate=self.sample_rate)
        self.is_playing = not self.is_playing
    
    def update_progress(self):
        if self.current_time_index < len(self.times) - 1:
            self.current_time_index += 1
            self.progress_line.setPos(self.times[self.current_time_index])
        else:
            self.timer.stop()
            self.is_playing = False
            self.play_pause_btn.setText("Play")


            
    def updateAudio(self, audio_data, fs):
        if self.audio_running:
            self.stopAudio()
        # update audio for the thread
        self.Audio_thread.update_Audio(audio_data, fs)
        # update spectogram data
        self.spectogramWidget.update_spectrogram(audio_data, fs)
        
        
    def playAudio(self):
        #===== start audio playing and spectogram inf bar animation thread
        self.Audio_thread.start()
        self.audio_running = True
        self.play_pause_btn.setText("Pause")
        
    def stopAudio(self):
        #===== stop audio playing and spectogram inf bar animation thread
        self.Audio_thread.stop()
        self.audio_running = False
        self.play_pause_btn.setText("Play")
    

class SpectrogramWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(SpectrogramWidget, self).__init__(parent)
        
        # Set up the layout
        self.plot_item = self.addPlot()
        self.plot_item.setLabel('bottom', 'Time', units='s')
        
        self.showSpectrum(True)
        
        self.inf_bar = pg.InfiniteLine(0, movable=True, angle=90)
    
    def showSpectrum(self, flag):
        """
        Toggles the display of a spectrum visualization between an image-based 
        spectrogram and a curve-based plot, depending on the provided flag.
            flag (bool): If True, displays the spectrogram with a colorbar 
                         representing power in dB. If False, displays a curve 
                         plot representing amplitude.
        """
        self.show_spectrum_flag = flag
        if flag:
            # keep imag item remove curve item
            self.plot_item.setLabel('left', 'Frequency', units='Hz')
            if hasattr(self, "curve"):
                self.removeItem(self.curve)
            self.img = pg.ImageItem()
            self.plot_item.addItem(self.img)
            
            # Add colorbar
            cm = pg.colormap.getFromMatplotlib('inferno')
            if not hasattr(self, "colorbar"):
                self.colorbar = pg.ColorBarItem(
                    values=(0, 1), 
                    colorMap=cm,
                    label='Power (dB)'
                )
            self.colorbar.setImageItem(self.img)
            self.addItem(self.colorbar)
        else:
            # keep curve item remove image item
            self.plot_item.setLabel('left', 'Amplitude')
            if hasattr(self, "colorbar"):
                self.colorbar.setParent(None)
                self.removeItem(self.colorbar)
                self.removeItem(self.img)
                self.colorbar.deleteLater()
            self.curve = pg.PlotDataItem(
                pen=pg.mkPen(color='b', width=1)
            )
            self.addItem(self.curve)
            
    def update_spectrogram(self, data, fs):
        """
        Update the spectrogram with new data
        
        Args:
            data: The signal data (1D numpy array)
            fs: Sampling frequency in Hz
        """
        if self.show_spectrum_flag:
            # Compute the spectrogram with parameters optimized for audio
            f, t, Sxx = scipy.signal.spectrogram(data, 
                                                 fs=fs, 
                                                 nperseg=None, #2048, 
                                                 noverlap=0.75, 
                                                window='hamming', 
                                                scaling='density', 
                                                mode='psd')
            
            # Convert to dB scale
            Sxx_db = 10 * np.log10(Sxx.T + 1e-10)  # Add small value to avoid log(0)
            
            # Update image and scale
            self.img.setImage(Sxx_db)
            tr = QtGui.QTransform()
            tr.scale(t[-1]/Sxx_db.shape[0], f[-1]/Sxx_db.shape[1])
            self.img.setTransform(tr)
            self.plot_item.setXRange(t[0], t[-1])
            self.plot_item.setYRange(f[0], f[-1])  # Limit to 8kHz for speech/music focus
            
            self.colorbar.setLevels((Sxx_db.min(), Sxx_db.max()))
        else:
            TimeStamp = np.linspace(0, round(len(data) / fs, 5), len(data))
            self.curve.setData(X=TimeStamp, Y=data)
    
    def play(self):
        position = self.inf_bar.getPos()
        print(position)
        self.NP_thread.start()

from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio, time

class AudioPLayThread(QThread):
    stopProcess = pyqtSignal()
    restartProcess = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.running = False
        self.process_paused = False

        self.stream = None
        # self.sample_rate = int(1/time_interval)
        # self.dt = time_interval
        # self.chunk_size = chunk_size
        
        # self.music = signal.astype(np.float32)
        
        self.p = pyaudio.PyAudio()
        self.s = 0  # chunk index
    
    def run(self):
        self.running = True
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.sample_rate,
                                  output=True)
        while self.running:
            music = self.music[self.chunk_size * self.s : self.chunk_size*(self.s+1)]
            self.stream.write(music.tobytes())
            self.s+=1
            if self.s*self.chunk_size >= len(self.music):
                self.s=0
                self.restartProcess.emit()

        self.stream.stop_stream()
        self.stream.close()
        self.quit()

    def update_Audio(self, audio_data, fs=None):
        """_summary_

        Args:
            audio_data (_type_): _description_
            fs (_type_, optional): _description_. Defaults to None.
        """
        ...
    def pause(self):
        self.running = False
        self.process_paused = True
    def close(self):
        self.running = False
        self.quit()
        self.wait() 
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeFrequencyWidget()
    window.show()
    sys.exit(app.exec_())
