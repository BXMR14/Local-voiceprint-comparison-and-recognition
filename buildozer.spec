# Buildozer spec template - edit as needed before running buildozer
[app]
title = LocalVoiceprint
package.name = localvoiceprint
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,mp3,wav,npz
requirements = python3,kivy,librosa,numpy,scipy,matplotlib,soundfile,scikit-learn
orientation = portrait
android.arch = armeabi-v7a

[buildozer]
log_level = 2
