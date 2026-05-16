import os
import numpy as np
from voiceprint import extract_features, compare_features
from denoise import reduce_noise


DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'dataset')


def test_demo_files_exist():
    # basic check: dataset should exist and contain speakers
    assert os.path.exists(DATASET_DIR)
    speakers = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    assert len(speakers) >= 2


def test_extract_features_and_keys():
    # pick one sample
    sp = os.listdir(DATASET_DIR)[0]
    f = os.path.join(DATASET_DIR, sp, os.listdir(os.path.join(DATASET_DIR, sp))[0])
    feats = extract_features(f)
    assert 'mfcc' in feats and 'peak_freqs' in feats and 'centroid' in feats
    assert feats['mfcc'].size > 0


def test_denoise_runs():
    sp = os.listdir(DATASET_DIR)[0]
    f = os.path.join(DATASET_DIR, sp, os.listdir(os.path.join(DATASET_DIR, sp))[0])
    import librosa
    y, sr = librosa.load(f, sr=16000)
    y2 = reduce_noise(y, sr)
    assert len(y2) > 0
    assert np.all(np.isfinite(y2))


def test_same_vs_different_scores():
    # choose alice_0, alice_1 and bob_0 if available
    speakers = sorted([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])
    assert len(speakers) >= 2
    a = speakers[0]
    b = speakers[1]
    a_files = sorted([f for f in os.listdir(os.path.join(DATASET_DIR, a)) if f.endswith('.wav')])
    b_files = sorted([f for f in os.listdir(os.path.join(DATASET_DIR, b)) if f.endswith('.wav')])
    assert len(a_files) >= 2 and len(b_files) >= 1
    a0 = os.path.join(DATASET_DIR, a, a_files[0])
    a1 = os.path.join(DATASET_DIR, a, a_files[1])
    b0 = os.path.join(DATASET_DIR, b, b_files[0])

    fa0 = extract_features(a0)
    fa1 = extract_features(a1)
    fb0 = extract_features(b0)

    same = compare_features(fa0, fa1)['score']
    diff = compare_features(fa0, fb0)['score']
    # ensure scores are finite and within [0,1]
    assert np.isfinite(same) and 0.0 <= same <= 1.0
    assert np.isfinite(diff) and 0.0 <= diff <= 1.0
