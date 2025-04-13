import sys
import queue
import threading
import numpy as np
import sounddevice as sd
import torch
import torchaudio
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg

BLOCK_SIZE = 512
SAMPLE_RATE = 16000

class AudioRecorder(threading.Thread):
    def __init__(self, audio_queue):
        super().__init__()
        self.audio_queue = audio_queue
        self.stream = sd.InputStream(callback=self.callback, blocksize=BLOCK_SIZE, samplerate=SAMPLE_RATE, channels=1)
        self.running = False

    def callback(self, indata, frames, time, status):
        if self.running:
            self.audio_queue.put(indata[:, 0].copy())

    def run(self):
        self.running = True
        with self.stream:
            while self.running:
                sd.sleep(100)

    def stop(self):
        self.running = False

class NoiseEmitter(threading.Thread):
    def __init__(self, noise_queue, trigger_event):
        super().__init__()
        self.noise_queue = noise_queue
        self.trigger_event = trigger_event
        self.running = False
        self.noise_data = torch.zeros(0)
        self.idx = 0

    def load_noise(self, path):
        waveform, _ = torchaudio.load(path)
        self.noise_data = waveform[0]
        self.idx = 0
        self.trigger_event.set()

    def run(self):
        self.running = True
        while self.running:
            if self.trigger_event.is_set() and self.idx + BLOCK_SIZE < len(self.noise_data):
                block = self.noise_data[self.idx:self.idx+BLOCK_SIZE].numpy()
                self.idx += BLOCK_SIZE
            else:
                block = np.zeros(BLOCK_SIZE)
            self.noise_queue.put(block)
            sd.sleep(int(BLOCK_SIZE / SAMPLE_RATE * 1000))

    def stop(self):
        self.running = False

class MergerWorker(threading.Thread):
    def __init__(self, audio_queue, noise_queue, plot_widget):
        super().__init__()
        self.audio_queue = audio_queue
        self.noise_queue = noise_queue
        self.plot_widget = plot_widget
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                audio = self.audio_queue.get(timeout=1)
                noise = self.noise_queue.get(timeout=1)
                merged = audio + noise
                processed = self.process_data(merged)
                self.plot(processed)
            except queue.Empty:
                continue

    def process_data(self, data):
        return data  # placeholder for heavy processing

    def plot(self, data):
        self.plot_widget.plot(data, clear=True)

    def stop(self):
        self.running = False

class AudioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Multithread Audio Plotter')
        layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        self.button = QPushButton("Add Noise")
        self.button.clicked.connect(self.add_noise)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.audio_queue = queue.Queue()
        self.noise_queue = queue.Queue()
        self.trigger_event = threading.Event()

        self.recorder = AudioRecorder(self.audio_queue)
        self.emitter = NoiseEmitter(self.noise_queue, self.trigger_event)
        self.worker = MergerWorker(self.audio_queue, self.noise_queue, self.plot_widget)

        self.recorder.start()
        self.emitter.start()
        self.worker.start()

    def add_noise(self):
        self.emitter.load_noise('noise.wav')  # Add your file path

    def closeEvent(self, event):
        self.recorder.stop()
        self.emitter.stop()
        self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioApp()
    window.show()
    sys.exit(app.exec_())
