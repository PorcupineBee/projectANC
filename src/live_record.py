import sounddevice as sd
import soundfile as sf
import numpy as np

class RealTimeProcessor:
    def __init__(self,
                 filename_original="original.wav", 
                 filename_modified="modified.wav",
                 samplerate=16000,
                 input_spectrum_appender=None, 
                 output_spectrum_appender=None, 
                 channels=1, blocksize=512):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.filename_original = filename_original
        self.filename_modified = filename_modified
        self.original_buffer = []
        self.modified_buffer = []
        self.stream = None
        self.is_recording = False
        self.input_spectrum_appender =  input_spectrum_appender
        self.output_spectrum_appender = output_spectrum_appender

    def processing_function(self, chunk):
        # Example: apply a simple gain + clipping
        # processed = chunk * 2.0 +  0.25 * np.random.rand(len(chunk))
        noise_level = 0.02  # Change this for stronger/weaker noise
        noise = np.random.normal(0, noise_level, chunk.shape)
        processed = chunk/np.abs(chunk).max() + noise
        return np.clip(processed, -1.0, 1.0)
    
    def _callback(self, 
                  indata, 
                  frames, 
                  time, 
                  status):
        if status:
            print(f"Status: {status}")
        if self.is_recording:
            chunk = indata.copy()
            self.original_buffer.append(chunk)
            self.input_spectrum_appender(chunk, self.samplerate)
            modified_chunk = self.processing_function(chunk)
            self.modified_buffer.append(modified_chunk)
            self.output_spectrum_appender(modified_chunk, self.samplerate)
            

    def start_recording(self):
        self.original_buffer = []
        self.modified_buffer = []
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=self.channels,
            callback=self._callback
        )
        self.stream.start()
        print("Recording started...")

    def stop_and_save(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        # Stack chunks to form full audio arrays
        original_audio = np.concatenate(self.original_buffer, axis=0)
        modified_audio = np.concatenate(self.modified_buffer, axis=0)

        # Save both versions
        sf.write(self.filename_original, original_audio/np.abs(original_audio).max(), self.samplerate)
        sf.write(self.filename_modified, modified_audio, self.samplerate)

        print(f"Recording stopped.\nOriginal saved to: {self.filename_original}\nModified saved to: {self.filename_modified}")

import sys
import queue
import numpy as np
import sounddevice as sd
import torchaudio
import torch
from PyQt5 import QtCore


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
    noise_ready = QtCore.pyqtSignal(np.ndarray)   # this will send the noise block to the process thread
    # register_noise_signal = QtCore.pyqtSignal(np.ndarray, float)
    
    def __init__(self, sample_rate=44100, blocksize=512):
        super().__init__()
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.running = False
        self.noise_active = False
        self.noise_data = None
        self.noise_position = 0
        
    def load_noise_file(self, file_path):
        """Load a noise file using torchaudio
        returns offset"""
        try:
            waveform, sr = torchaudio.load(file_path)
            # Convert to mono if it's not
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample if needed
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
            
            # self.register_noise_signal.emit(waveform, self.noise_position)
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
                        self.plot_ready.emit(merged_data, processed_data)
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


# Example usage
if __name__ == "__main__":
    processor = RealTimeProcessor()
    input("Press Enter to start recording...")
    processor.start_recording()
    input("Press Enter to stop and save recordings...")
    processor.stop_and_save()
