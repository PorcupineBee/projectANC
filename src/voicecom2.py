import socket
import threading
import pyaudio
import numpy as np
import re
from PyQt5.QtCore import QThread, pyqtSignal
import debugpy
import time
# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
DEFAULT_CHUNK = 512
DEFAULT_RATE = 24000
SERVER_PORT_FILE = "src/serverport.txt"

# Server thread class
class ServerAudioThread(QThread):
    debugpy.debug_this_thread()
    connection_established = pyqtSignal()
    
    def __init__(self, chunk=DEFAULT_CHUNK, sampling_rate=DEFAULT_RATE, parent=None):
        super().__init__(parent)
        self.host = "0.0.0.0"
        self.RATE = sampling_rate
        self.CHUNK = chunk
        self.running = False
        self.conn = None
        self.server = None
        self._port = self._read_port_from_file()
    
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
    
    def start_server(self):
        """Initialize server socket and wait for client connection"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self._port))
            self.server.listen(5)
            
            print(f"Server listening on port {self._port}")
            self.conn, self.address = self.server.accept()
            print(f"Connection from {self.address}")
            
            # Wait for client's confirmation code
            response = self.conn.recv(self.CHUNK)
            if response and response.decode() == "1":
                print("Connection established, ready to stream")
                self.connection_established.emit()
                self.conn.sendall("ACK".encode('utf-8'))
                return True
            return False
        except Exception as e:
            print(f"Server error: {e}")
            return False
    
    def run(self):
        """Start streaming audio to client"""
        # try:
        for i in range(5):
            message = f"Hello from Colab! Message #{i+1}"
            print(f"Sending: {message}")
            self.conn.send(message.encode('utf-8'))
            
            # Receive response
            response = self.conn.recv(1024).decode('utf-8')
            print(f"Received: {response}")
            
            time.sleep(1)
            
        # audio = pyaudio.PyAudio()
        # stream = audio.open(format=FORMAT, channels=CHANNELS, 
        #                     rate=self.RATE, input=True, 
        #                     frames_per_buffer=self.CHUNK)
        
        # self.running = True
        # while self.running:
        #     data = stream.read(self.CHUNK, exception_on_overflow=False)
        #     if self.conn:
        #         self.conn.sendall(data)
        
        # Clean up
        # stream.stop_stream()
        # stream.close()
        # audio.terminate()
        # except Exception as e:
        #     print(f"Error in server audio streaming: {e}")
        # finally:
        #     self.stop()
    
    def stop(self):
        """Stop streaming and close connections"""
        self.running = False
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

# Client thread class
class ClientAudioThread(QThread):
    connection_established = pyqtSignal()
    audio_received = pyqtSignal(bytes)
    
    def __init__(self, chunk=DEFAULT_CHUNK, sampling_rate=DEFAULT_RATE, parent=None):
        super().__init__(parent)
        self.host = "0.tcp.in.ngrok.io"
        self.RATE = sampling_rate
        self.CHUNK = chunk
        self.running = False
        self.client = None
        self.audio_buffer = bytearray()
    
    def connect_to_server(self, port):
        """Connect to server and send confirmation code"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, port))
            print(f"Connected to server at {self.host}:{port}")
            
            # Send confirmation code
            self.client.send("1".encode('utf-8'))
            
            # Wait for acknowledgment
            response = self.client.recv(self.CHUNK).decode('utf-8')
            if response == "ACK":
                self.connection_established.emit()
                return True
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def run(self):
        """Receive and process audio stream from server"""
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS, 
                                rate=self.RATE, output=True, 
                                frames_per_buffer=self.CHUNK)
            
            self.running = True
            self.audio_buffer = bytearray()
            
            while self.running:
                data = self.client.recv(self.CHUNK)
                if not data:
                    break
                
                # Play the audio
                stream.write(data)
                
                # Store the audio data
                self.audio_buffer.extend(data)
                self.audio_received.emit(data)
            
            # Clean up
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception as e:
            print(f"Error in client audio reception: {e}")
        finally:
            self.stop()
    
    def save_audio(self, filename="received_audio.wav"):
        """Save received audio to a WAV file"""
        import wave
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(self.audio_buffer)
            print(f"Audio saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def stop(self):
        """Stop receiving and close connection"""
        self.running = False
        if self.client:
            try:
                self.client.close()
            except:
                pass