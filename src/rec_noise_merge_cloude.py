import sys
import queue
import numpy as np
import sounddevice as sd
import torchaudio
import torch
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


class AudioRecorderThread(QtCore.QThread):
    """Thread 1: Audio recorder that captures audio and emits data"""
    data_ready = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self, sample_rate=44100, channels=1, blocksize=512):
        super().__init__()
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.running = False
        
    def run(self):
        self.running = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            # Convert to numpy array and emit
            data = np.array(indata.copy())
            self.data_ready.emit(data)
        
        # Create the input stream
        with sd.InputStream(
            callback=audio_callback,
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.blocksize
        ):
            while self.running:
                sd.sleep(100)  # Sleep to prevent high CPU usage
    
    def stop(self):
        self.running = False
        self.wait()


class NoiseEmitterThread(QtCore.QThread):
    """Thread 2: Noise packet emitter that can add noise on demand"""
    noise_ready = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self, sample_rate=44100, blocksize=512):
        super().__init__()
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.running = False
        self.noise_active = False
        self.noise_data = None
        self.noise_position = 0
        
    def load_noise_file(self, file_path):
        """Load a noise file using torchaudio"""
        try:
            waveform, sr = torchaudio.load(file_path)
            # Convert to mono if it's not
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample if needed
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
                
            self.noise_data = waveform.numpy().flatten()
            self.noise_position = 0
            return True
        except Exception as e:
            print(f"Error loading noise file: {e}")
            return False
    
    def toggle_noise(self, active):
        self.noise_active = active
        if active:
            self.noise_position = 0  # Reset position when activated
    
    def run(self):
        self.running = True
        
        while self.running:
            if self.noise_active and self.noise_data is not None:
                # Get the next block of noise data
                if self.noise_position + self.blocksize <= len(self.noise_data):
                    noise_block = self.noise_data[self.noise_position:self.noise_position + self.blocksize]
                    self.noise_position += self.blocksize
                    
                    # Loop back to beginning if needed
                    if self.noise_position >= len(self.noise_data):
                        self.noise_position = 0
                else:
                    # Handle the edge case at the end of the file
                    remaining = len(self.noise_data) - self.noise_position
                    noise_block = np.zeros(self.blocksize)
                    noise_block[:remaining] = self.noise_data[self.noise_position:]
                    noise_block[remaining:] = self.noise_data[:self.blocksize - remaining]
                    self.noise_position = self.blocksize - remaining
            else:
                # Send zeros when noise is not active
                noise_block = np.zeros(self.blocksize)
                
            # Reshape to match audio format (samples, channels)
            noise_block = noise_block.reshape(-1, 1)
            self.noise_ready.emit(noise_block)
            
            # Emit at regular intervals to match audio callback rate
            QtCore.QThread.msleep(int(1000 * self.blocksize / self.sample_rate))
    
    def stop(self):
        self.running = False
        self.wait()


class AudioProcessorThread(QtCore.QThread):
    """Thread 3: Audio processor that merges audio and noise, processes, and plots"""
    plot_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    
    def __init__(self, blocksize=512, queue_size=100):
        super().__init__()
        self.blocksize = blocksize
        self.audio_queue = queue.Queue(maxsize=queue_size)
        self.noise_queue = queue.Queue(maxsize=queue_size)
        self.running = False
        
    def add_audio_data(self, audio_data):
        """Add audio data to queue"""
        try:
            self.audio_queue.put(audio_data, block=False)
        except queue.Full:
            print("Audio queue full, dropping oldest data")
            # Remove oldest item and add new one
            try:
                self.audio_queue.get(block=False)
                self.audio_queue.put(audio_data, block=False)
            except:
                pass
    
    def add_noise_data(self, noise_data):
        """Add noise data to queue"""
        try:
            self.noise_queue.put(noise_data, block=False)
        except queue.Full:
            print("Noise queue full, dropping oldest data")
            # Remove oldest item and add new one
            try:
                self.noise_queue.get(block=False)
                self.noise_queue.put(noise_data, block=False)
            except:
                pass
    
    def run(self):
        self.running = True
        
        while self.running:
            # Check if there's data in both queues
            if not self.audio_queue.empty() and not self.noise_queue.empty():
                try:
                    # Get data from queues
                    audio_data = self.audio_queue.get(timeout=0.5)
                    noise_data = self.noise_queue.get(timeout=0.5)
                    
                    # Process the data (merge audio and noise)
                    if audio_data.shape == noise_data.shape:
                        merged_data = audio_data + noise_data
                        
                        # Simulate time-consuming processing
                        processed_data = self.process_audio(merged_data)
                        
                        # Emit the processed data for plotting
                        self.plot_ready.emit(audio_data, noise_data, processed_data)
                    else:
                        print(f"Shape mismatch: audio {audio_data.shape}, noise {noise_data.shape}")
                except queue.Empty:
                    pass
            else:
                # Sleep if no data is available
                QtCore.QThread.msleep(10)
    
    def process_audio(self, data):
        """Process the merged audio data (simulating time-consuming operations)"""
        # Example processing: apply a simple filter
        # In a real application, this could be much more complex
        
        # Simulate processing time
        QtCore.QThread.msleep(20)
        
        # Example: apply a simple moving average filter
        window_size = 5
        processed = np.zeros_like(data)
        
        for i in range(data.shape[0]):
            start = max(0, i - window_size // 2)
            end = min(data.shape[0], i + window_size // 2 + 1)
            processed[i] = np.mean(data[start:end], axis=0)
        
        return processed
    
    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Processing System")
        self.setGeometry(100, 100, 1000, 600)
        
        # Set up the central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layouts
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        control_layout = QtWidgets.QHBoxLayout()
        
        # Create control buttons
        self.start_button = QtWidgets.QPushButton("Start Recording")
        self.stop_button = QtWidgets.QPushButton("Stop Recording")
        self.load_noise_button = QtWidgets.QPushButton("Load Noise File")
        self.toggle_noise_button = QtWidgets.QPushButton("Toggle Noise")
        
        # Add buttons to control layout
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.load_noise_button)
        control_layout.addWidget(self.toggle_noise_button)
        
        # Create plots
        self.plot_widget = pg.GraphicsLayoutWidget()
        
        # Add plots for audio, noise, and processed data
        self.audio_plot = self.plot_widget.addPlot(row=0, col=0, title="Audio Input")
        self.noise_plot = self.plot_widget.addPlot(row=1, col=0, title="Noise Input")
        self.processed_plot = self.plot_widget.addPlot(row=2, col=0, title="Processed Output")
        
        # Create plot items
        self.audio_curve = self.audio_plot.plot(pen='g')
        self.noise_curve = self.noise_plot.plot(pen='r')
        self.processed_curve = self.processed_plot.plot(pen='b')
        
        # Add layouts to main layout
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.plot_widget)
        
        # Set up threads
        self.audio_thread = AudioRecorderThread()
        self.noise_thread = NoiseEmitterThread()
        self.processor_thread = AudioProcessorThread()
        
        # Connect signals/slots
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.load_noise_button.clicked.connect(self.load_noise_file)
        self.toggle_noise_button.clicked.connect(self.toggle_noise)
        
        self.audio_thread.data_ready.connect(self.processor_thread.add_audio_data)
        self.noise_thread.noise_ready.connect(self.processor_thread.add_noise_data)
        self.processor_thread.plot_ready.connect(self.update_plots)
        
        # Initial state
        self.stop_button.setEnabled(False)
        self.toggle_noise_button.setEnabled(False)
        
        self.noise_active = False
        
    def start_recording(self):
        """Start all threads"""
        self.audio_thread.start()
        self.noise_thread.start()
        self.processor_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def stop_recording(self):
        """Stop all threads"""
        self.audio_thread.stop()
        self.noise_thread.stop()
        self.processor_thread.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def load_noise_file(self):
        """Open a file dialog to select a noise file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Noise File", "", "Audio Files (*.wav *.mp3 *.ogg)"
        )
        
        if file_path:
            success = self.noise_thread.load_noise_file(file_path)
            if success:
                self.toggle_noise_button.setEnabled(True)
                print(f"Loaded noise file: {file_path}")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Error", "Failed to load noise file."
                )
    
    def toggle_noise(self):
        """Toggle noise on/off"""
        self.noise_active = not self.noise_active
        self.noise_thread.toggle_noise(self.noise_active)
        
        if self.noise_active:
            self.toggle_noise_button.setText("Disable Noise")
        else:
            self.toggle_noise_button.setText("Enable Noise")
    
    @QtCore.pyqtSlot(np.ndarray, np.ndarray, np.ndarray)
    def update_plots(self, audio_data, noise_data, processed_data):
        """Update the plots with new data"""
        # Extract data for plotting (first channel only)
        audio_y = audio_data[:, 0]
        noise_y = noise_data[:, 0]
        processed_y = processed_data[:, 0]
        
        # Create x values
        x = np.arange(len(audio_y))
        
        # Update plots
        self.audio_curve.setData(x, audio_y)
        self.noise_curve.setData(x, noise_y)
        self.processed_curve.setData(x, processed_y)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_recording()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())