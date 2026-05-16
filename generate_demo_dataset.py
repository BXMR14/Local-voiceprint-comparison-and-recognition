import os
import numpy as np
import soundfile as sf


def synth_voice(base_f, formants, sr, duration, noise_level=0.01, seed=None):
    if seed is not None:
        np.random.seed(seed)
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # harmonic series
    sig = np.zeros_like(t)
    for h in range(1, 6):
        amp = 1.0 / h
        sig += amp * np.sin(2 * np.pi * base_f * h * t + np.random.uniform(0, 2 * np.pi))

    # add formant resonances as low-amplitude sinusoids
    for f in formants:
        sig += 0.3 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))

    # vibrato
    sig *= (1.0 + 0.02 * np.sin(2 * np.pi * 5 * t))

    # add background noise
    sig += np.random.normal(scale=noise_level, size=sig.shape)

    # normalize
    sig = sig / np.max(np.abs(sig)) * 0.9
    return sig


def make_dataset(out_dir='dataset', sr=16000, duration=2.0):
    os.makedirs(out_dir, exist_ok=True)
    speakers = {
        'alice': {'base': 110, 'formants': [700, 1200]},
        'bob': {'base': 130, 'formants': [600, 1000]},
        'carol': {'base': 150, 'formants': [800, 1400]}
    }

    for sp, cfg in speakers.items():
        spdir = os.path.join(out_dir, sp)
        os.makedirs(spdir, exist_ok=True)
        for i in range(6):
            # small random variation per file
            base = cfg['base'] * (1.0 + np.random.uniform(-0.02, 0.02))
            formants = [f * (1.0 + np.random.uniform(-0.01, 0.01)) for f in cfg['formants']]
            noise = 0.005 + np.random.uniform(0, 0.02)
            sig = synth_voice(base, formants, sr, duration, noise_level=noise)
            fname = os.path.join(spdir, f'{sp}_{i}.wav')
            sf.write(fname, sig, sr)
    print('Demo dataset generated in', out_dir)


if __name__ == '__main__':
    make_dataset()
