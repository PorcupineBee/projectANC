import sys
import socket
import threading
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class AudioReceiver(QThread):
    update_status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.server = None
        self.conn = None
        self.running = True

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 5000))
        self.server.listen(1)
        self.conn, _ = self.server.accept()
        self.update_status.emit("Connected")

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

        while self.running:
            try:
                data = self.conn.recv(CHUNK)
                if not data:
                    break
                stream.write(data)
            except:
                break

        self.conn.close()
        self.server.close()
        self.update_status.emit("Disconnected")

    def stop(self):
        self.running = False
        if self.conn:
            self.conn.close()

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Server")
        self.setGeometry(200, 200, 300, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("Status: Disconnected")
        self.start_button = QPushButton("Start Server")
        self.stop_button = QPushButton("Stop Server")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

        self.audio_thread = AudioReceiver()
        self.audio_thread.update_status.connect(self.update_status)
        
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

    def start_server(self):
        self.audio_thread.start()

    def stop_server(self):
        self.audio_thread.stop()
        self.label.setText("Status: Stopped")

    def update_status(self, status):
        self.label.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    sys.exit(app.exec())
