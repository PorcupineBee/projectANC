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
        self.input_spectrum_appender = input_spectrum_appender
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


# Example usage
if __name__ == "__main__":
    processor = RealTimeProcessor()
    input("Press Enter to start recording...")
    processor.start_recording()
    input("Press Enter to stop and save recordings...")
    processor.stop_and_save()
