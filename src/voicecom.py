import sys, re
import socket
import threading
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

FORMAT = pyaudio.paInt16
CHANNELS = 1
SERVER_PORT_FILE = "src/serverport.txt"
# thread class for the server
class ServerElement(QThread):
     
    def __init__(self, 
                 CHUNK=512, 
                 sampling_rate=16000, 
                 parent=None):
            super().__init__(parent), 
            self.host = "0.0.0.0"
            self.RATE = sampling_rate
            self.CHUNK = CHUNK
            with open(SERVER_PORT_FILE, "r") as f:
                port_id = f.read().strip()
                f.close()
            if bool(re.fullmatch(r"\d+", port_id)):
                self._port = int(port_id)
            else:
                raise ValueError("Invalid port id ")      
                  
    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server.bind((self.host, self._port))
        
        self.server.listen(5)
        
        self.conn, self.add = self.server.accept()
        
        
        while True:
            response = self.conn.recv(self.CHUNK)            
            if not response:
                print("Connection closed")
                
            triger = response.decode()
            
            if triger:
                print("connection established, ready to stream")
                break
            
        self.running = True
        
        
    def run(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, 
                            rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
        while self.running:
            try: 
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.server.sendall(data)
                
            except Exception as e:
                break
        
        self.conn.close()
        self.server.close()
        
    def stop(self):
        self.running = False
        if self.conn:
            self.conn.close()
            

# tread class for the Client
class ClientElement(QThread):
     
    def __init__(self, 
                 CHUNK=512, 
                 sampling_rate=16000, 
                 parent=None):
        super().__init__(parent)
        self.host = "0.tcp.in.ngrok.io"
        self.RATE = sampling_rate
        self.CHUNK = CHUNK
        
    def connect_server(self, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client.connect((self.host, port))
            print("Connecttion with server established")
            self.client.send("1".encode('utf-8'))
            response = self.client.recv(self.CHUNK).decode('utf-8')
            if response:
                self.start()
        except Exception as e:
            print("Conne ction Failed")
        self.running = True
        
    def run(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, 
                            rate=self.RATE, output=True, 
                            frames_per_buffer=self.CHUNK)
        
        while self.running:
            try: 
                data = self.client.recv(self.CHUNK)
                if not data:
                    break
                stream.write(data)
                
            except Exception as e:
                break
            
        self.client.close()
        
    def stop(self):
        self.running = False
        if self.client:
            self.client.close()

