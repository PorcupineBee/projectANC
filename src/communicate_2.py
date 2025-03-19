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

class AudioSender(QThread):
    update_status = pyqtSignal(str)

    def __init__(self, server_ip):
        super().__init__()
        self.client = None
        self.running = True
        self.server_ip = server_ip

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.server_ip, 5000))
            self.update_status.emit("Connected")
        except:
            self.update_status.emit("Failed to Connect")
            return

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        while self.running:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                self.client.sendall(data)
            except:
                break

        self.client.close()
        self.update_status.emit("Disconnected")

    def stop(self):
        self.running = False
        if self.client:
            self.client.close()

class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Client")
        self.setGeometry(200, 200, 300, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("Status: Disconnected")
        self.start_button = QPushButton("Start Client")
        self.stop_button = QPushButton("Stop Client")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

        self.audio_thread = None

        self.start_button.clicked.connect(self.start_client)
        self.stop_button.clicked.connect(self.stop_client)

    def start_client(self):
        server_ip = "192.168.1.100"  # Change to your server's IP
        self.audio_thread = AudioSender(server_ip)
        self.audio_thread.update_status.connect(self.update_status)
        self.audio_thread.start()

    def stop_client(self):
        if self.audio_thread:
            self.audio_thread.stop()
        self.label.setText("Status: Stopped")

    def update_status(self, status):
        self.label.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientGUI()
    window.show()
    sys.exit(app.exec())
