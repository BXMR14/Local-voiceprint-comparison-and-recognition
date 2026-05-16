import numpy as np
import librosa


def reduce_noise(y, sr, n_fft=2048, hop_length=512, n_std_thresh=1.5):
    """
    Simple spectral gating noise reduction.
    - Estimates noise floor per frequency bin using median across time.
    - Zeroes components below a threshold (noise_floor + n_std_thresh * std).
    This is a lightweight, dependency-free approach suitable for local preprocessing.
    """
    # STFT
    S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    mag, phase = np.abs(S), np.angle(S)

    # Noise statistics across time for each frequency bin
    noise_mean = np.median(mag, axis=1, keepdims=True)
    noise_std = np.std(mag, axis=1, keepdims=True)
    thresh = noise_mean + n_std_thresh * noise_std

    # Create mask
    mask = mag >= thresh

    # Smooth mask along time axis (simple moving average)
    from scipy.ndimage import uniform_filter1d
    mask_smooth = uniform_filter1d(mask.astype(float), size=3, axis=1)

    # Apply mask to magnitude
    mag_clean = mag * mask_smooth

    # Reconstruct waveform
    S_clean = mag_clean * np.exp(1j * phase)
    y_clean = librosa.istft(S_clean, hop_length=hop_length)
    return y_clean
