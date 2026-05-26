# Local-voiceprint-comparison-and-recognition

本项目使用 Kivy 在本地实现声纹（voiceprint）特征提取、注册与比对，并提供桌面 EXE 与移动 APK 的打包模板。

主要功能：
- 本地提取 MFCC、谱峰与谱质心等特征
- 在本地保存声纹样本（`voiceprints` 目录）并进行比对
- 可视化比较 MFCC 热图与峰值曲线，便于直接区分声纹特征

- 内置轻量降噪处理：在特征提取前对音频应用光谱门降噪（spectral gating），以减少环境噪声并保留清晰人声，提升比对鲁棒

快速开始
1. 安装依赖（推荐在虚拟环境中）:

```bash
pip install -r requirements.txt
```

2. 运行桌面程序:

```bash
python main.py
```

3. 注册与比对
- 使用左侧文件浏览器选择一个 `.wav` 或 `.flac` 音频文件，点击“注册为新声纹”保存到本地。
- 选择待比对文件，点击“与库中比对”查看匹配结果与可视化图像（会生成 `compare_plot.png`）。

- 实时录音支持：界面下方提供“开始录音”，“停止录音并注册”，“停止录音并比对”按钮，可直接使用麦克风录入并注册或比对。

打包
- 生成 EXE（示例）: `./build_exe.sh`（需安装 PyInstaller）
- 生成 APK（示例）: 编辑并使用 `buildozer.spec`，在支持的环境中运行 `buildozer android debug`

运行评估
- 将数据集按照 `dataset/<speaker>/*.wav` 组织（每个说话人一个子文件夹）。脚本会用每个子文件夹的第一个文件作为注册样本，其余作为 probe 测试样本。

示例：

```bash
python evaluate.py --dataset dataset --out results.csv
```

评估输出为 CSV（`results.csv`），包含每个 probe 的预测、相似度得分及是否正确；终端会打印总体准确率。
注意与性能
- 本项目提供基于 MFCC + DTW + 均值余弦相似度的本地比对实现，作为原型可用。
- 要达到 99% 的识别率和 ≤0.5% 误差，需要大量高质量的训练/评估数据、噪声鲁棒性处理以及更复杂的模型与阈值调优，本仓库实现为可扩展的本地引擎基线。

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
