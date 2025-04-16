import torchaudio as ta
import numpy as np
import os, json, uuid, shutil
import torchaudio.transforms as T


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
    signal = audio_signal.contiguous().numpy().flatten()
    time = np.arange(len(signal)) * tme_interval        
    return signal, time, nf, sr, time[-1]


# region signal_registry

class signal_registry():
    def __init__(self, working_dir):
        self.signals_df = {"project_id":None}
        self.current_signal = None
        self.duration = None
        self.samples_size = None
        self.WorkingDir = working_dir
        self._audio_folder = os.path.join(working_dir, ".cache/Audios")
        if not os.path.exists(self._audio_folder): os.mkdir(self._audio_folder)
        self.maxsigsize = 0
            
    
    def add_signal(self, 
                   fpath:str, 
                   type:str="audio",
                   _sr:int=16000,
                   recorded:bool=False)-> tuple[np.ndarray, np.ndarray, int]:
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
        #BUG remember every audio file may have difrent sampling rate 
        # so time_interval may change so ensure that whenever adding new audio 
        # modify the audio file using interpolation if suitable.
        #XXX padding may increase audio file size don't do zero-padding
        signal_key = uuid.uuid4().hex[:6]
        signal_order = self.__len__() - 1
        
        newfpath, sig, time= copyFile(self._audio_folder, fpath, _sr, method="get", recorded=recorded) 
        
        self.maxsigsize = len(sig) if len(sig) > self.maxsigsize else self.maxsigsize
        
        self.signals_df.update({
            signal_key: dict(
                fpath=fpath,
                newfpath=newfpath,
                order=signal_order,
                amplitude=sig.max(),
                sample_rate=_sr,
                num_samples=len(sig),
                durations=time[-1],         # time
                offset=0,                   # time
                window_length=time[-1],     # time
                window_offset=0,            # time
                type=type,
                active_flag=True
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
    
    def getTotalSignal(self, sampling_rate, signal_only_added=False, *args):
        """_summary_

        Args:
            sampling_rate (_type_): _description_
            signal_only_added (bool, optional): _description_. Defaults to True.
                            true: signal only added no resampling

        Returns:
            _type_: _description_
            
        case 1 : only add new signal
        case 2:  change sampling rate, add new signal, signal removed
        """
        def _process(prop, _res_signal:np.ndarray):
            newfpath = copyFile(self._audio_folder, prop["newfpath"], new_sr=sampling_rate)     
            audio_signal, _ = ta.load(newfpath)
            audio_signal = audio_signal.contiguous().numpy().flatten()
            
            sampleOffset = int(prop["offset"] * sampling_rate) 
            duration = len(audio_signal) #int(prop["durations"] * sampling_rate)
            window_length = int(prop["window_length"] * sampling_rate)
            window_offset = int(prop["window_offset"] * sampling_rate)
            
            total_offset = sampleOffset + window_offset if window_offset > 0 else sampleOffset
            right_bound = window_length if window_length < duration else duration
            
            _res_signal[total_offset: total_offset + right_bound] += prop["amplitude"] * audio_signal[window_offset:
                                min(len(_res_signal)-total_offset, right_bound)]
            
            _res_signal = _res_signal/np.abs(_res_signal).max()
            return _res_signal.astype(np.float32)
        
        if signal_only_added and len(args)>0:
            # only add new signal to the resultant signal
            res_signal = np.load(f"{self.WorkingDir}/resultant_signal.npy")
            prop = self.signals_df[args[0]]
            res_signal = _process(prop, res_signal)
                
        else:
            res_signal = np.zeros(self.maxsigsize)
            for key, prop in self.signals_df.items():
                if key != "project_id":
                    if prop["active_flag"] == True:
                        res_signal = _process(prop, res_signal)
                    
        # save resultant signal as npy file
        np.save(f"{self.WorkingDir}/resultant_signal.npy", res_signal)
        np.save(f"{self.WorkingDir}/resultant_signal.npy", res_signal)
        
        return res_signal        
    
def copyFile(_audio_folder, audio_file, new_sr=16000, method="save", recorded=False):
    new_file_path =  os.path.join(_audio_folder, os.path.basename(audio_file))
    if os.path.exists(new_file_path) and not recorded: 
        audio_signal, old_sr = ta.load(new_file_path)
        if old_sr == new_sr:
            if method == "save":
                return new_file_path
            
            elif method=="get":
                sig = audio_signal.contiguous().numpy().flatten()
                time = np.arange(len(sig)) * 1/new_sr
                return new_file_path, sig, time
    else:
        audio_signal, old_sr = ta.load(audio_file)
        
    resampler = T.Resample(orig_freq=old_sr, new_freq=new_sr)
    y_16k = resampler(audio_signal)
    ta.save(new_file_path, y_16k, new_sr)
    # else:
    #     shutil.copy(audio_file, _audio_folder)

    if method=="get":
        sig = y_16k.contiguous().numpy().flatten()
        time = np.arange(len(sig)) * 1/new_sr
        return new_file_path, sig, time
    
    return new_file_path
    
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
    

from UI.plot_tf_spectrum_static import TimeFrequencyWidget, EnhancedTimeFrequencyWidget
def getDefultSpectrumWidget(winflag):
    default_settings = dict(
        audio_data = np.empty(0), # + 0.25 * np.random.rand(48*10**4),
        fs=16000
    )
    if winflag:
        _tfwidget = TimeFrequencyWidget(**default_settings)
    else:
        _tfwidget = EnhancedTimeFrequencyWidget(**default_settings)
        
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