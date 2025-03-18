import sys
import numpy as np
import pyaudio, time
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

class NoisePlayerThread(QThread):
    # movesoundbar = pyqtSignal(float)
    stopProcess = pyqtSignal()
    restartProcess = pyqtSignal()
    def __init__(self, signal, time_interval, chunk_size=512):
        super().__init__()
        self.running = False
        self.process_paused = False

        self.stream = None
        self.sample_rate = int(1/time_interval)
        self.dt = time_interval
        self.chunk_size = chunk_size
        
        self.music =  signal.astype(np.float32)
        
        self.p = pyaudio.PyAudio()
        self.s = 0
    
    def run(self):
        self.running = True
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.sample_rate,
                                  output=True)
        while self.running:
            music = self.music[self.chunk_size * self.s:self.chunk_size*(self.s+1)]
            self.stream.write(music.tobytes())
            self.s+=1
            if self.s*self.chunk_size >= len(self.music):
                self.s=0
                self.restartProcess.emit()

        # if not self.process_paused:
        #     self.stopProcess.emit()
        #     self.s = 0
            
        self.stream.stop_stream()
        self.stream.close()
        self.quit()

    def pause(self):
        self.running = False
        self.process_paused = True
    # def _movebar(self):
    #     tstepsize = self.dt * 5
    #     self.movesoundbar.emit(tstepsize)
    #     time.sleep(tstepsize)
        
    def close(self):
        self.running = False
        self.quit()
        self.wait()
        
class BarMovementThread(QThread):
    movebar = pyqtSignal(float)
    def __init__(self, time_interval, chunk_size):
        super().__init__()
        self._go = False
        self.dt = round(time_interval * chunk_size, 4)
        
    def run(self):     
        while self._go:
            self.movebar.emit(self.dt)
            time.sleep(self.dt)
            
    def play(self):
        self._go = True
        
    def pause(self):
        self._go = False

    def close(self):
        self.stop()
        self.quit()
        self.wait()
    

class NoisePlayerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.thread = NoisePlayerThread()
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.toggle_button = QPushButton("Play Noise")
        self.toggle_button.clicked.connect(self.toggle_noise)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)

    def toggle_noise(self):
        if self.thread.isRunning():
            self.thread.toggle()
            self.toggle_button.setText("Play Noise")
        else:
            self.thread.start()
            self.toggle_button.setText("Pause Noise")

    def closeEvent(self, event):
        self.thread.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = NoisePlayerApp()
    mainWin.show()
    sys.exit(app.exec_())
