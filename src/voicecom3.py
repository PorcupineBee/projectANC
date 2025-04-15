import socket
import threading
import pyaudio
import numpy as np
import re
from PyQt5.QtCore import QThread, pyqtSignal
import debugpy
import time
import wave

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
DEFAULT_CHUNK = 512
DEFAULT_RATE = 16000
SERVER_PORT_FILE = "src/serverport.txt"

# Server thread class
class ServerAudioThread(QThread):
    debugpy.debug_this_thread()
    connection_established = pyqtSignal()
    recorded_chunk = pyqtSignal(np.ndarray, int)
    def __init__(self, chunk=DEFAULT_CHUNK, sampling_rate=DEFAULT_RATE, parent=None):
        super().__init__(parent)
        self.host = "0.0.0.0"
        self.RATE = sampling_rate
        self.CHUNK = chunk
        self.running = False
        self.conn = None
        self.server = None
        self._port = self._read_port_from_file()
        
        self._go = True
        self.start_stream = False
        self.connection_status = False 
        
    def _read_port_from_file(self):
        try:
            with open(SERVER_PORT_FILE, "r") as f:
                port_id = f.read().strip()
            
            if bool(re.fullmatch(r"\d+", port_id)):
                return int(port_id)
            else:
                raise ValueError("Invalid port id")
        except Exception as e:
            print(f"Error reading port: {e}")
            return None
    
    def trun_on_streaming(self):
        self.start_stream = True
        self.send_one_time = True  # make it outside
        
    def trun_off_streaming(self):
        self.start_stream = False
        
        
    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self._port))
        self.server.listen(5)
        
        print(f"Server listening on port {self._port}")
        self.conn, self.address = self.server.accept()
        print(f"Connection from {self.address}")
        
       
        
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, 
                            rate=self.RATE, input=True, 
                            frames_per_buffer=self.CHUNK)
        # try:
        while self._go:
            if not self.connection_status:
                response = self.conn.recv(self.CHUNK)
                if response and response.decode() == "1":
                    print("Connection established, ready to stream")
                    self.connection_established.emit()
                self.connection_status = True
            
            
            if self.start_stream:
                if self.send_one_time:
                    self.conn.sendall("ACK".encode('utf-8'))
                    self.send_one_time = False
                    # print("ACK send")
                if self.conn:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    _data = self.recorded_chunk(data, self.RATE)
                    self.conn.sendall(_data)
                    
        stream.stop_stream()
        stream.close()
        audio.terminate()
    
    def stop(self):
        """Stop streaming and close connections"""
        # self.running = False
        self._go = False
        self.start_stream = False
        self.connection_status = False 
        
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        self.conn = None
        self.server = None
        
        
class ClientAudioThread(QThread):
    connection_established = pyqtSignal()
    audio_received = pyqtSignal(np.ndarray)
    
    def __init__(self, chunk=DEFAULT_CHUNK, sampling_rate=DEFAULT_RATE, parent=None):
        super().__init__(parent)
        self.host = "0.tcp.in.ngrok.io"
        self.RATE = sampling_rate
        self.CHUNK = chunk
        self.running = False
        self.client = None
        self.audio_buffer = bytearray()
        
        self._go = True
        self.connection_status = False
        self.streaming_started = False
        
    
    def setPort(self, port):
        self._port = port
    
    def run(self):
        """Receive and process audio stream from server"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self._port))
        print(f"Connected to server at {self.host}:{self._port}")
        
        wf = wave.open("received_audio.wav", "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(self.RATE)

        while self._go:
            # Send confirmation code
            if not self.connection_status :
                self.client.send("1".encode('utf-8'))
                self.connection_status = True
            
            data = self.client.recv(self.CHUNK)
                
            if data != "ACK".encode("utf-8") and self.streaming_started:
                if not data:
                    break
                
                wf.writeframes(data)
                
                self.audio_received.emit(data)
            else:
                self.connection_established.emit()
                self.streaming_started = True     
        wf.close()
        print("Thread terminated")

    
    def stop(self):
        """Stop receiving and close connection"""
        self._go = False
        self.connection_status = False
        self.streaming_started = False
        if self.client:
            try:
                self.client.close()
            except:
                pass