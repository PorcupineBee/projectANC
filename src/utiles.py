import torchaudio as ta
import numpy as np
import os, json, uuid



def getAudioSignal_n_Time(audio_file:str)-> tuple[np.ndarray, np.ndarray]:
    """
    Get the audio signal and time from an audio file

    Args:
        audio_file (str): Path to the audio file

    Returns:
        tuple[np.ndarray, np.ndarray]: Audio signal and time
    """
    audio_meta_data: ta.AudioMetaData = ta.info(audio_file)
    audio_signal, _ = ta.load(audio_file)
    sr = audio_meta_data.sample_rate
    nf = audio_meta_data.num_frames 
    tme_interval = 1/sr
    durations = nf/sr
    time = np.arange(0, durations, tme_interval)
    signal = audio_signal.contiguous().numpy().flatten()
    
    return signal, time, nf, sr, durations


# region signal_registry

class signal_registry():
    def __init__(self):
        self.signals_df = {"project_id":None}
        self.current_signal = None
        self.duration = None
        self.samples_size = None
    
    def add_signal(self, 
                   fpath:str, 
                   type:str="audio")-> tuple[np.ndarray, np.ndarray, int]:
        """
        Add a signal to the registry
        Parameters:
        fpath: str
            Path to the signal file
        type: str
            Type of the signal
        Returns:
        tuple[np.ndarray, np.ndarray]: Audio signal, time and signal order
        """
        sig, time, nf, sr, durations = getAudioSignal_n_Time(fpath)
        #BUG remember every audio file may have difrent sampling rate 
        # so time_interval may change so ensure that whenever adding new audio 
        # modify the audio file using interpolation if suitable.
        #XXX padding may increase audio file size don't do zero-padding
        signal_key = uuid.uuid4().hex[:6]
        signal_order = self.__len__() - 1
        self.signals_df.update({
            signal_key: dict(
                fpath=fpath,
                order=signal_order,
                amplitude=sig.max(),
                duration=durations,
                sample_rate=sr,
                num_samples=nf,
                offset=0,
                window_length=durations,
                window_offset=0,
                type=type,
            )
        })
        return sig, time, signal_order, signal_key
    
    def __len__(self):
        return len(self.signals_df)
    
    def saveCache(self, working_dir, **kwargs):
        if (self.signals_df["project_id"] is None) and ("project_id" in kwargs.keys()):            
            self.signals_df["project_id"] = kwargs.pop("project_id") 
        else:
            raise ValueError("Project ID is not set")
            
        with open(os.path.join(working_dir, ".cache/project_cache.json"), "w") as f:
            json.dump(self.signals_df, f)
            f.close()
    
    def getTotalSignal(self):
        #XXX this function made with keeping same sampling rate idea
        buffer_audio = np.zeros(self.samples_size)
        for sigkey, items in self.signals_df.items():
            if sigkey != "project_id":
                sig, _, _, _, _ = getAudioSignal_n_Time(items["fpath"])
                sid = items["offset"]
                endid = sid + len(sig)                
                buffer_audio[sid: endid] += items["amplitude"] * sig 
        
        return buffer_audio/np.abs(buffer_audio).max() # ensure range [-1, 1] 
#endregion          

# region
def plot_time_frequency(audio_signals:dict, 
                        fs:int, 
                        window_size:int=512, 
                        overlap:float=0.8, f_min:int=20, 
                        f_max:int=25000)->np.ndarray:
    """_summary_

    Returns:
        time_frequency_matrix: _description_
    """    
    tf_mat:np.ndarray
    return tf_mat



def setInputSignals(audio_signals:dict, frame):
    plot_time_frequency(audio_signals)
    

from UI.plot_tf_spectrum_static import TimeFrequencyWidget
def getDefultSpectrumWidget():
    default_settings = dict(
        audio_data = np.zeros(48*10**4) + 0.25 * np.random.rand(48*10**4),
        fs=48*10**3
    )
    _tfwidget = TimeFrequencyWidget(**default_settings)
    return _tfwidget
    
# endregion


from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

def create_rotated_text_pixmap(text, font_size=8, width=50, height=100):
    # Create a transparent pixmap
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)

    # Create a painter and rotate text
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setFont(QFont("Arial", font_size))
    painter.setPen(Qt.white)
    
    # Move the origin and rotate
    painter.translate(0, height)
    painter.rotate(270)

    # Draw the text
    painter.drawText(0, 0, height, width, Qt.AlignCenter, text)
    painter.end()

    return pixmap

def getRotatedLabel(name:str, **kwargs):
    label = QLabel()
    rotated_pixmap = create_rotated_text_pixmap(name, **kwargs)
    label.setPixmap(rotated_pixmap)
    label.setFixedSize(rotated_pixmap.size())
    label.setAlignment(Qt.AlignCenter)
    return label 