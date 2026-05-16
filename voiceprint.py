import os
import numpy as np
import librosa
from denoise import reduce_noise
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import cosine_similarity


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def extract_features(wav_path, sr=16000, n_mfcc=20):
    y, _ = librosa.load(wav_path, sr=sr)
    # apply noise reduction to retain clearer vocals
    try:
        y = reduce_noise(y, sr=sr)
    except Exception:
        # if denoising fails, fall back to original
        pass
    # MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Spectral centroid (as a proxy for peaks)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    # Magnitude spectrum peaks via short-time Fourier transform
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    # for peaks, take max energy freq per frame
    peak_idx = np.argmax(S, axis=0)
    peak_freqs = freqs[peak_idx]

    features = {
        'mfcc': mfcc,            # shape (n_mfcc, frames)
        'centroid': centroid,    # shape (1, frames)
        'peak_freqs': peak_freqs,# shape (frames,)
        'sr': sr
    }
    return features


def save_voiceprint(features, name, folder='voiceprints'):
    ensure_dir(folder)
    path = os.path.join(folder, f"{name}.npz")
    np.savez(path, mfcc=features['mfcc'], centroid=features['centroid'], peak_freqs=features['peak_freqs'])
    return path


def load_voiceprint(path):
    data = np.load(path)
    return {
        'mfcc': data['mfcc'],
        'centroid': data['centroid'],
        'peak_freqs': data['peak_freqs']
    }


def compare_mfcc_dtw(mfcc1, mfcc2):
    # use Euclidean distance between MFCC frames and DTW
    # librosa.sequence.dtw expects cost matrix; compute frame-wise cost
    from librosa.sequence import dtw
    # transpose to (frames, n_mfcc)
    x = mfcc1.T
    y = mfcc2.T
    cost = cdist(x, y, metric='euclidean')
    _, wp = dtw(C=cost)
    # path_cost = mean cost along DTW path
    path_vals = cost[tuple(zip(*wp))]
    path_cost = float(np.mean(path_vals)) if path_vals.size > 0 else float('inf')
    return path_cost


def compare_features(features_a, features_b):
    # Compare MFCC via DTW (lower is more similar)
    dtw_cost = compare_mfcc_dtw(features_a['mfcc'], features_b['mfcc'])

    # Cosine similarity of averaged MFCCs (higher is more similar)
    a_mean = features_a['mfcc'].mean(axis=1)
    b_mean = features_b['mfcc'].mean(axis=1)
    cos_sim = cosine_similarity(a_mean.reshape(1, -1), b_mean.reshape(1, -1))[0, 0]

    # Peak frequency correlation
    # make lengths equal
    af = features_a['peak_freqs']
    bf = features_b['peak_freqs']
    m = min(len(af), len(bf))
    if m == 0:
        peak_corr = 0.0
    else:
        peak_corr = np.corrcoef(af[:m], bf[:m])[0, 1]
        if np.isnan(peak_corr):
            peak_corr = 0.0

    # Combine metrics into a score (0..1) where 1 means identical
    # Map dtw_cost to similarity via stable reciprocal mapping
    try:
        dtw_sim = 1.0 / (1.0 + float(dtw_cost))
    except Exception:
        dtw_sim = 0.0

    # ensure peak_corr is valid
    if not np.isfinite(peak_corr):
        peak_corr = 0.0

    # weighted sum
    score = 0.6 * float(cos_sim) + 0.3 * float(dtw_sim) + 0.1 * float(peak_corr)
    # clamp
    score = float(np.clip(score, 0.0, 1.0))
    return {
        'score': score,
        'dtw_cost': float(dtw_cost),
        'cos_sim': float(cos_sim),
        'peak_corr': float(peak_corr)
    }
