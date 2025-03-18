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
        signal_key = uuid.uuid4().hex[:6]
        signal_order = self.__len__() 
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
    
    def row(self, row:int):
        pass
    
    def saveCache(self, working_dir, **kwargs):
        if (self.signals_df["project_id"] is None) and ("project_id" in kwargs.keys()):            
            self.signals_df["project_id"] = kwargs.pop("project_id") 
        else:
            raise ValueError("Project ID is not set")
            
        with open(os.path.join(working_dir, ".cache/project_cache.json"), "w") as f:
            json.dump(self.signals_df, f)
            f.close()
#endregion          