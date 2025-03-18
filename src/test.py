import numpy as np
import pyaudio

class AudioPlayer:
    def __init__(self, frequency=375, sample_rate=48000, chunk_size=512):
        self.p = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.current_frame = 0

        # Generate audio signal
        self.t = np.arange(0, chunk_size) / sample_rate
        self.wave = np.sin(2 * np.pi * frequency * self.t).astype(np.float32)

        # Open a callback-based stream
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=sample_rate,
                                  output=True,
                                  stream_callback=self.callback)

    def callback(self, in_data, frame_count, time_info, status):
        """ PyAudio callback function for non-blocking streaming. """
        self.current_frame += frame_count
        print(f"Current Frame: {self.current_frame}")
        return (self.wave.tobytes(), pyaudio.paContinue)

    def play(self):
        self.stream.start_stream()
        while self.stream.is_active():
            pass  # Keep running
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# Run the audio player
player = AudioPlayer()
player.play()
