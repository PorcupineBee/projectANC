#%%
# from df import enhance, init_df
from df.enhance import enhance, init_df, load_audio, save_audio
from df.utils import download_file
import numpy as np
import matplotlib.pyplot as plt
import sys, os

root = os.path.dirname(__file__).replace("\\", "/")

# os.path.dirname()
# sys.path.append(os.getcwd())

#%%
model, df_state, _ = init_df()  # Load default model
# noisy_audio_path = "A:/gitclones/EEproject/raw_data/assets_noisy_snr0.wav"
noisy_audio_path = "A:/gitclones/EEproject/Test4.wav"
# ===== down load audio file if not have in local 
# audio_path = download_file(
#         "https://github.com/Rikorose/DeepFilterNet/raw/e031053/assets/noisy_snr0.wav",
#         download_dir=".",
#     )
noisy_audio, _ = load_audio(noisy_audio_path) #, sr=df_state.sr())

enhanced_audio = enhance(model, df_state, noisy_audio)

#%%
print(type(noisy_audio))
# %%
plt.figure()
plt.plot(noisy_audio.numpy().flatten())
plt.show()
# %%
plt.figure()
plt.plot(enhanced_audio.numpy().flatten())
plt.show()

# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def plot_time_frequency_spectrum(data, fs, window_size=256, overlap=0.75, 
                                nperseg=None, noverlap=None, 
                                f_min=None, f_max=None, 
                                cmap='viridis', title=None, 
                                log_scale=True):
    """
    Generate a time vs frequency spectrum with power contour plot.
    
    Parameters:
    -----------
    data : numpy.ndarray
        Input time-series data
    fs : float
        Sampling frequency of the data in Hz
    window_size : int, optional
        Size of the window for STFT (default: 256)
    overlap : float, optional
        Overlap between windows as a fraction (0 to 1) (default: 0.75)
    nperseg : int, optional
        Length of each segment for STFT. If None, uses window_size
    noverlap : int, optional
        Number of points to overlap. If None, calculated from overlap fraction
    f_min : float, optional
        Minimum frequency to display (Hz)
    f_max : float, optional
        Maximum frequency to display (Hz)
    cmap : str, optional
        Colormap for the contour plot (default: 'viridis')
    title : str, optional
        Title for the plot
    log_scale : bool, optional
        Whether to use logarithmic scale for power (default: True)
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure containing the plot
    ax : matplotlib.axes.Axes
        Axes containing the plot
    """
    # Set default parameters if not provided
    if nperseg is None:
        nperseg = window_size
    if noverlap is None:
        noverlap = int(nperseg * overlap)
        
    # Compute the spectrogram
    frequencies, times, Sxx = signal.spectrogram(
        data, 
        fs=fs,
        window='hamming',
        nperseg=nperseg,
        noverlap=noverlap,
        detrend='constant',
        scaling='density'
    )
    
    # Convert to power in dB if log_scale is True
    if log_scale:
        # Add small value to avoid log(0)
        Sxx = 10 * np.log10(Sxx + 1e-10)
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Frequency range limits
    if f_min is not None or f_max is not None:
        f_min = 0 if f_min is None else f_min
        f_max = fs/2 if f_max is None else f_max
        
        # Find indices within the requested frequency range
        freq_mask = (frequencies >= f_min) & (frequencies <= f_max)
        frequencies = frequencies[freq_mask]
        Sxx = Sxx[freq_mask, :]
    
    # Create the contour plot
    contour = ax.contourf(times, frequencies, Sxx, 100, cmap=cmap)
    
    # Add a colorbar
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Power Spectral Density' + (' (dB/Hz)' if log_scale else ' (V²/Hz)'))
    
    # Set labels and title
    # ax.set_yscale("log")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    if title:
        ax.set_title(title)
    else:
        ax.set_title('Time-Frequency Power Spectrum')
    
    # Improve layout
    plt.tight_layout()
    
    return fig, ax

#%%
fs = 48000 
# Plot the time-frequency spectrum
fig, ax = plot_time_frequency_spectrum(
    noisy_audio.flatten()[:-1], 
    fs=fs,
    window_size=512, 
    overlap=0.8,
    f_min=20,
    f_max=24000,
    title="Chirp Signal with Fixed Frequency Component",
    cmap="inferno"
    
)
plt.show()

#%%
fig, ax = plot_time_frequency_spectrum(
    enhanced_audio.flatten()[:-1], 
    fs=fs,
    window_size=512, 
    overlap=0.8,
    f_min=10,
    f_max=24000,
    title="Chirp Signal with Fixed Frequency Component",
    cmap="inferno"
    
)
plt.show()


#%%
save_audio("t4_enhanced_audio.wav", enhanced_audio, df_state.sr())
# %%
