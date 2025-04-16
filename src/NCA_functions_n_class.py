from df.enhance import enhance, init_df, load_audio, save_audio
import numpy as np
import torch

class Deepfilternet(object):
    def __init__(self):
        self.model, self.df_state, _ = init_df()  # Load default model
    
    def __call__(self, data:np.ndarray, sampling_rate:int):
        if type(data) != torch.Tensor and type(data)==np.ndarray:
            data = torch.tensor(data, dtype=torch.float32)
        x = data.reshape((1, -1))
        enhanced_audio = enhance(self.model, self.df_state, x)
        return enhanced_audio.contiguous().numpy().flatten()
    
        
def getANC_method(index):
    if index  == 0:
        method = Deepfilternet()
        return method
    elif index==1:
        raise NotImplementedError()
    elif index==2:
        raise NotImplementedError()
    elif index==2:
        raise NotImplementedError()
    else:
        raise NotImplementedError()