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
from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio, time

class TimeFrequencyWidget(QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        chunk_size = kwargs.get("chunk_size", 512)
        self.spectogramWidget = SpectrogramWidget()
        self.initUI()
        
        # some flags
        self.audio_running = False
        self.Audio_thread = AudioPLayThread(chunk_size=chunk_size)
        self.Audio_thread.stopProcess.connect(self.stopProcess)
        self.Audio_thread.restartProcess.connect(self.restartProcess)
        self.barmoveThread = BarMovementThread(chunk_size=chunk_size)
        self.barmoveThread.movebar.connect(self.spectogramWidget.move_inf_line)
        
        
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
    padding: 2px 15px;
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
    image: url(UI/icons/up_arrow.png); /* Use a custom icon or remove */
    width: 5px;
    height: 5px;
}

QSpinBox::down-arrow {
    image: url(UI/icons/down_arrow.png);
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
QPushButton{
    padding:6px 20px; 
    font-size:10px;
    font-weight:normal;
}
""")    
        
        self.control_layout = QHBoxLayout()
        
        # Play/Pause Button
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        # self.play_pause_btn.setStyleSheet()
        self.control_layout.addWidget(self.play_pause_btn)
        
        # Spinbox for time window size
        label = QLabel(self)
        label.setText("Window size")
        self.control_layout.addWidget(label)
        
        self.time_window_spinbox = QSpinBox()
        self.time_window_spinbox.setRange(100, 5000)  # Set limits
        self.time_window_spinbox.setValue(1000)  # Default value (ms)
        self.control_layout.addWidget(self.time_window_spinbox)
        
        self.showSpectogram = QRadioButton(self)
        self.showSpectogram.setText("Show Spectogram")
        self.showSpectogram.setChecked(True)
        self.showSpectogram.toggled.connect(self.spectogramWidget.showSpectrum)
        self.control_layout.addWidget(self.showSpectogram)
        
        hspecer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.control_layout.addItem(hspecer)
        
        self.control_layout.setContentsMargins(10, 5, 0, 0)
        self.control_layout.setSpacing(10)
        top_frame.setLayout(self.control_layout)
        main_layout.addWidget(top_frame)
        
        # endregion
        # PyQtGraph Plot Widget
        plot_frame = QFrame()
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.spectogramWidget)
        plot_layout.setContentsMargins(0, 5, 0, 0)
        plot_frame.setLayout(plot_layout)
                
        main_layout.addWidget(plot_frame)
        
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # region Not needed
        # self.setWindowTitle("Time-Frequency Spectrum Viewer")
        # self.setGeometry(100, 100, 800, 500)
        
        # # Data for simulation
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_progress)
        self.is_playing = False # ensures audio is not playing at initialization
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
        
    
    def toggle_playback(self):
        if self.is_playing:
            # 
            self.play_pause_btn.setText("Play")
            self.barmoveThread.pause()
            self.Audio_thread.pause()
        else:
            # turned on play of Audio and bar movement 
            self.play_pause_btn.setText("Pause")
            self.Audio_thread.s =  self.spectogramWidget.getframelocation()
            self.barmoveThread.start()
            self.Audio_thread.start()    
        self.is_playing = not self.is_playing
    
    def updateAudio(self, audio_data, fs):
        if self.audio_running:
            self.stopAudio()
        # update audio for the thread
        self.Audio_thread.update_Audio(audio_data, fs)
        # update spectogram data
        self.barmoveThread.dt = fs
        self.spectogramWidget.update_spectrogram(audio_data, fs)
        
        
    def playAudio(self):
        #===== start audio playing and spectogram inf bar animation thread
        
        self.Audio_thread.start()
        self.audio_running = True
        self.play_pause_btn.setText("Pause")
        
    def stopAudio(self):
        #===== stop audio playing and spectogram inf bar animation thread
        self.Audio_thread.pause()
        self.audio_running = False
        self.play_pause_btn.setText("Play")
        
    def restartProcess(self):
        self.spectogramWidget.inf_bar.setPos(0)
        
    
    def stopProcess(self):
        # if self.pplay
        self.barmoveThread.pause()
        self.play_pause_btn.setText("Play")
        self.spectogramWidget.inf_bar.setPos(0)
        self.is_playing = False
        
    
    #region LIVE rEC releted
    def live_rec_widget_stateStatus(self, flag):
        self.play_pause_btn.setEnabled(flag)
        self.time_window_spinbox.setEnabled(flag)
        self.showSpectogram.setEnabled(flag)
        if flag:
            self.spectogramWidget.livedata = np.array([])
            self.spectogramWidget.timeline = np.array([])
        else:
            self.spectogramWidget.inf_bar.setPos(0)
            self.spectogramWidget.plot_item.autoRange()
    
    def liverec_update(self, data_chunk, sr):
        self.spectogramWidget.live_update_spectrum(data_chunk, sr)
        
    #endregion L
        
class SpectrogramWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(SpectrogramWidget, self).__init__(parent)
        
        # Set up the layout
        self.plot_item = self.addPlot()
        self.plot_item.setLabel('bottom', 'Time', units='s')
        
        self.showSpectrum(True)
        self._audio_data = None
        self._fs = 0
        self.inf_bar = pg.InfiniteLine(0, movable=True, angle=90, bounds=[0, 1000])
        self.plot_item.addItem(self.inf_bar)
        self.inf_bar.setZValue(100)
        
        self.livedata = np.array([])
        self.chunk_size = 512
        self.time_window_secs = 5  # initial view of 5 seconds
        self.current_time = 0
        self.timeline = np.array([])
        

    def live_update_spectrum(self, data:np.ndarray, fs:float):
        """_summary_

        Args:
            data (np.ndarray): a block of size (BLOCK_SIZE, 1) (BLOCK_SIZE:  512 usually)
            fs (float): _description_

        Raises:
            NotImplemented: _description_
        """
        data = data.flatten()
        if self.show_spectrum_flag:        
            f, _t, chunk = scipy.signal.spectrogram(data, 
                                                    fs=self._fs, 
                                                    nperseg=512, #2048, 
                                                    noverlap=0, #0.75, 
                                                    window='hamming', 
                                                    scaling='density', 
                                                    mode='psd')
            chunk = 10 * np.log10(chunk + 1e-10)  # Add small value to avoid log(0)
            self.current_time += _t[-1] #self.chunk_size / self._fs
        else:
            chunk = data
            self.timeline = np.append(self.timeline, np.arange(len(data))/self._fs)
        
        if len(self.livedata)==0:
            self.livedata = chunk
        else:
            self.livedata = np.hstack((self.livedata, chunk))
            
        if self.show_spectrum_flag:        
            # Update image and scale
            self.img.setImage(self.livedata.T)
            tr = QtGui.QTransform()
            tr.scale(self.current_time/self.livedata.shape[1], (f[-1]-f[0])/self.livedata.shape[0])
            self.img.setTransform(tr)
            self.plot_item.setYRange(f[0], f[-1])        
            self.inf_bar.setPos(self.current_time)
        else:
            self.curve= self.plot_item.plot(self.timeline, self.livedata, 
                                             pen=pg.mkPen(color='r', width=1))
            self.inf_bar.setPos(self.current_time)
            raise NotImplemented("Not implemented yet0")
        self.plot_item.setXRange(self.current_time-self.time_window_secs, self.current_time)
            
        
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
                self.plot_item.removeItem(self.curve)
            self.img = pg.ImageItem()
            self.plot_item.addItem(self.img)
            
            # Add colorbar
            if not hasattr(self, "colorbar"):
                self.colorbar = pg.ColorBarItem(
                    values=(0, 1), 
                    colorMap=pg.colormap.getFromMatplotlib('inferno'),
                    label='Power (dB)',
                    width=10
                )
                self.addItem(self.colorbar)
            self.colorbar.setVisible(True)
            self.colorbar.setImageItem(self.img)            
        else:
            # keep curve item remove image item
            self.plot_item.setLabel('left', 'Amplitude')
            if hasattr(self, "img"):
                self.colorbar.setVisible(False)
                self.plot_item.removeItem(self.img)
        
        if hasattr(self,"_audio_data") and (self._audio_data is not None):
            self.update_spectrogram(self._audio_data, self._fs)
            
    def update_spectrogram(self, data, fs):
        """
        Update the spectrogram with new data
        
        Args:
            data: The signal data (1D numpy array)
            fs: Sampling frequency in Hz
        """
        self._audio_data = data
        self._fs = fs
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
            self.curve = self.plot_item.plot(TimeStamp[::5], data[::5], 
                                             pen=pg.mkPen(color='r', width=1))
        
        self.plot_item.autoRange()
            
        
    def move_inf_line(self, dt):
        next_step = self.inf_bar.value() + dt
        self.inf_bar.setPos(next_step)

    def getframelocation(self):
        position = self.inf_bar.getPos()[0]
        s = int(position * self._fs)
        return s
        

class AudioPLayThread(QThread):
    stopProcess = pyqtSignal()
    restartProcess = pyqtSignal()
    def __init__(self, chunk_size=512):
        """THis thread will play the total
        input audio.

        Args:
            chunk_size (int, optional): sample delay for process. Defaults to 512.
        """
        super().__init__()
        self.running = False
        self.process_paused = False

        self.stream = None
        # self.sample_rate = int(1/time_interval)
        # self.dt = time_interval
        self.chunk_size = chunk_size
        
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
    
    def update_Audio(self, audio_data, fs):
        """_summary_

        Args:
            audio_data (_type_): _description_
            fs (_type_, optional): _description_. Defaults to None.
        """
        self.music = audio_data.astype(np.float32)
        self.sample_rate = fs
    
    def pause(self):
        self.running = False
        self.process_paused = True
        
    def close(self):
        self.running = False
        self.quit()
        self.wait() 
 
class BarMovementThread(QThread):
    movebar = pyqtSignal(float)
    def __init__(self, chunk_size):
        super().__init__()
        self._go = False
        self.chunk_size = chunk_size
        self._dt = None # round(time_interval * chunk_size, 4)
    
    @property
    def dt(self):
        if self._dt is not None:
            return self._dt
        else:
            raise ValueError("Time interval self._dt is not set yet")
    
    @dt.setter
    def dt(self, fs):
        self._dt= round(self.chunk_size/ fs, 4)
                       
    def run(self):     
        self._go = True
        while self._go:
            self.movebar.emit(self.dt)
            time.sleep(self.dt)
            
    def pause(self):
        self._go = False

    def close(self):
        self.stop()
        self.quit()
        self.wait()
 

class EnhancedTimeFrequencyWidget(TimeFrequencyWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.denoise_btn = QPushButton(self, text="Enhance Audio")
        self.denoise_btn.clicked.connect(self.start_denoising_task)
        self.control_layout.addWidget(self.denoise_btn)
        
        self.EnhancerThread = AudioEnhancingThread()
        self.EnhancerThread.enhanceSignal.connect(self.NoiseEleminationProcess)
    
    def start_denoising_task(self):
        self.EnhancerThread.start()
        
    def EnhanceThisAudio(self, audio, sr):
        paudio = audio + np.random.normal(0, 0.02, size=audio.shape)
        self.updateAudio(paudio, sr)
        
    def NoiseEleminationProcess(self):
        ...
        
        
class AudioEnhancingThread(QThread):
    enhanceSignal = pyqtSignal() 
    def __init__(self):
        super().__init__()
        
    def run(self):
        if self._go:
            self.enhanceSignal.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeFrequencyWidget()
    window.show()
    sys.exit(app.exec_())
