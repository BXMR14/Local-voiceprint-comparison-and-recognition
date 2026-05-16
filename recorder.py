import sounddevice as sd
import soundfile as sf
import threading


class Recorder:
    def __init__(self, filename='last_record.wav', samplerate=16000, channels=1):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self._recording = False
        self._frames = []
        self._stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print('Recorder status:', status)
        self._frames.append(indata.copy())

    def start(self):
        if self._recording:
            return
        self._frames = []
        self._stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self._callback)
        self._stream.start()
        self._recording = True

    def stop(self):
        if not self._recording:
            return
        try:
            if self._stream is not None:
                try:
                    self._stream.stop()
                except Exception:
                    pass
                try:
                    self._stream.close()
                except Exception:
                    pass
        except Exception:
            pass
        self._recording = False
        # concatenate frames and write file
        try:
            import numpy as np
            if not self._frames:
                # nothing recorded
                return None
            data = np.concatenate(self._frames, axis=0)
            sf.write(self.filename, data, self.samplerate)
            return self.filename
        except Exception:
            return None


_global_recorder = None


def start_recording(filename='last_record.wav', samplerate=16000, channels=1):
    global _global_recorder
    if _global_recorder and _global_recorder._recording:
        return
    _global_recorder = Recorder(filename=filename, samplerate=samplerate, channels=channels)
    # run start in a thread to avoid blocking UI
    t = threading.Thread(target=_global_recorder.start, daemon=True)
    t.start()


def stop_recording():
    global _global_recorder
    if not _global_recorder:
        return None
    filename = _global_recorder.stop()
    return filename
