# Local-voiceprint-comparison-and-recognition
This project uses a noise reduction algorithm to process both parties' voices, then preserves the human voice for comparison, displaying the waveforms and characteristic peaks of both voices. Currently, this project only supports local operation.
# Voiceprint Studio

Voiceprint Studio is a local client app for comparing two human voice samples. It extracts mel-band energy, MFCC voiceprint features, pitch contours, spectral brightness, voicing ratio, and energy statistics in the browser. The app then visualizes the difference map, feature balance, pitch contours, MFCC deltas, and an overall similarity score.

Audio processing stays on the local device. The score is an analytic review signal and is not a legal identity decision.

## Run From Source

```powershell
python .\desktop\voiceprint_launcher.py
```

The launcher starts a localhost server and opens the app in the default browser.

## Build Windows EXE Installer

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

Outputs:

- `dist\VoiceprintStudio.exe`
- `dist\VoiceprintStudio-Setup.exe`

The installer copies the app to `%LOCALAPPDATA%\VoiceprintStudio`, creates desktop and Start Menu shortcuts, and opens the app.

## Build Android APK

The Android wrapper is in `android\`. Building requires an installed Android SDK, Java 17+, and Gradle or a Gradle wrapper.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_android.ps1
```

Output:

- `dist\VoiceprintStudio-debug.apk`

If the build script reports missing `ANDROID_HOME`, Java, or Gradle, install Android Studio or the Android command-line tools, then run the script again.
