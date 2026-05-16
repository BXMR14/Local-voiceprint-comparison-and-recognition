import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import mainthread
from kivy.uix.image import Image

from voiceprint import extract_features, save_voiceprint, load_voiceprint, compare_features
from recorder import start_recording, stop_recording
import numpy as np
import matplotlib.pyplot as plt

KV = """
#:import utils kivy.utils
<RootWidget>:
    orientation: 'horizontal'
    padding: dp(8)
    spacing: dp(8)
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.45
        canvas.before:
            Color:
                rgba: 0.88, 0.95, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: '本地声纹注册/比对'
            size_hint_y: None
            height: dp(40)
            color: 0, 0, 0, 1

        FileChooserListView:
            id: fc
            filters: ['*.wav', '*.flac']

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Button:
                text: '注册为新声纹'
                on_release: root.register_voice(fc.path, fc.selection and fc.selection[0] or '')
                background_color: 0.6, 0.85, 1, 1
            Button:
                text: '与库中比对'
                on_release: root.compare_voice(fc.path, fc.selection and fc.selection[0] or '')

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Button:
                text: '开始录音'
                on_release: root.start_record()
                background_color: 0.6, 0.85, 1, 1
            Button:
                text: '停止录音并注册'
                on_release: root.stop_and_register()
            Button:
                text: '停止录音并比对'
                on_release: root.stop_and_compare()

        Label:
            id: status
            text: root.status_text
            size_hint_y: None
            height: dp(30)

    BoxLayout:
        orientation: 'vertical'
        padding: dp(8)
        spacing: dp(8)
        Label:
            text: '比对结果与可视化'
            size_hint_y: None
            height: dp(40)
        Image:
            id: plot_image
            source: root.plot_path
        Label:
            text: root.result_text
            size_hint_y: None
            height: dp(60)

"""


class RootWidget(BoxLayout):
    status_text = StringProperty('')
    result_text = StringProperty('')
    plot_path = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voice_dir = os.path.join(os.getcwd(), 'voiceprints')
        os.makedirs(self.voice_dir, exist_ok=True)

    def _list_registered(self):
        files = [f for f in os.listdir(self.voice_dir) if f.endswith('.npz')]
        return files

    def register_voice(self, folder, filepath):
        if not filepath or not os.path.exists(filepath):
            self.status_text = '请先选择一个音频文件(.wav/.flac)'
            return
        name = os.path.splitext(os.path.basename(filepath))[0]
        self.status_text = f'正在提取特征并注册：{name}'
        features = extract_features(filepath)
        save_voiceprint(features, name, folder=self.voice_dir)
        self.status_text = f'已注册：{name}'

    def start_record(self):
        # start recording to a temp file
        self.status_text = '开始录音...'
        self._record_file = os.path.join(os.getcwd(), 'last_record.wav')
        start_recording(filename=self._record_file, samplerate=16000, channels=1)

    def stop_and_register(self):
        fname = stop_recording()
        if not fname or not os.path.exists(fname):
            self.status_text = '录音失败或文件不存在'
            return
        name = os.path.splitext(os.path.basename(fname))[0]
        self.status_text = f'正在提取特征并注册录音：{name}'
        features = extract_features(fname)
        save_voiceprint(features, name, folder=self.voice_dir)
        self.status_text = f'已注册录音：{name}'

    def stop_and_compare(self):
        fname = stop_recording()
        if not fname or not os.path.exists(fname):
            self.status_text = '录音失败或文件不存在'
            return
        self.status_text = '正在提取特征并比对录音...'
        try:
            probe = extract_features(fname)
        except Exception:
            self.status_text = '提取 probe 特征失败'
            return

        regs = self._list_registered()
        if not regs:
            self.result_text = '未找到已注册的声纹样本（voiceprints 为空）'
            self.status_text = '比对取消'
            return

        best = None
        best_score = -1
        details = None
        for f in regs:
            try:
                reg = load_voiceprint(os.path.join(self.voice_dir, f))
                res = compare_features(probe, reg)
            except Exception:
                continue
            if res['score'] > best_score:
                best_score = res['score']
                best = f
                details = res

        if best is None or details is None:
            self.result_text = '没有找到匹配结果'
            self.status_text = '比对失败'
            return

        self.result_text = f'最佳匹配: {best}  相似度: {best_score:.4f}\n详情: DTW={details["dtw_cost"]:.3f}, cos={details["cos_sim"]:.3f}, peak_corr={details["peak_corr"]:.3f}'
        self.status_text = '比对完成'
        reg_path = os.path.join(self.voice_dir, best)
        if os.path.exists(reg_path):
            self._plot_compare(fname, reg_path)
        else:
            self.status_text = '比对完成，但注册文件丢失，跳过可视化'

    def compare_voice(self, folder, filepath):
        if not filepath or not os.path.exists(filepath):
            self.status_text = '请先选择一个音频文件(.wav/.flac)'
            return
        self.status_text = '正在提取特征并比对...'
        try:
            probe = extract_features(filepath)
        except Exception:
            self.status_text = '提取 probe 特征失败'
            return

        regs = self._list_registered()
        if not regs:
            self.result_text = '未找到已注册的声纹样本（voiceprints 为空）'
            self.status_text = '比对取消'
            return

        best = None
        best_score = -1
        details = None
        for f in regs:
            try:
                reg = load_voiceprint(os.path.join(self.voice_dir, f))
                res = compare_features(probe, reg)
            except Exception:
                continue
            if res['score'] > best_score:
                best_score = res['score']
                best = f
                details = res

        if best is None or details is None:
            self.result_text = '没有找到匹配结果'
            self.status_text = '比对失败'
            return

        self.result_text = f'最佳匹配: {best}  相似度: {best_score:.4f}\n详情: DTW={details["dtw_cost"]:.3f}, cos={details["cos_sim"]:.3f}, peak_corr={details["peak_corr"]:.3f}'
        self.status_text = '比对完成'
        reg_path = os.path.join(self.voice_dir, best)
        if os.path.exists(reg_path):
            self._plot_compare(filepath, reg_path)
        else:
            self.status_text = '比对完成，但注册文件丢失，跳过可视化'

    @mainthread
    def _plot_compare(self, probe_path, reg_npz_path):
        if not os.path.exists(reg_npz_path):
            self.status_text = '注册文件不存在，无法绘图'
            return
        try:
            probe = extract_features(probe_path)
            reg = load_voiceprint(reg_npz_path)
        except Exception:
            self.status_text = '绘图所需特征提取失败'
            return
        fig, axes = plt.subplots(3, 1, figsize=(6, 8))
        # mfcc heatmaps
        im1 = axes[0].imshow(probe['mfcc'], aspect='auto', origin='lower')
        axes[0].set_title('Probe MFCC')
        fig.colorbar(im1, ax=axes[0])
        im2 = axes[1].imshow(reg['mfcc'], aspect='auto', origin='lower')
        axes[1].set_title('Registered MFCC')
        fig.colorbar(im2, ax=axes[1])
        # peak freqs
        axes[2].plot(probe['peak_freqs'], label='probe peaks', color='tab:blue')
        axes[2].plot(reg['peak_freqs'], label='registered peaks', color='tab:orange')
        axes[2].set_title('Peak Frequencies (per frame)')
        axes[2].legend()
        plt.tight_layout()
        out = os.path.join(os.getcwd(), 'compare_plot.png')
        fig.savefig(out)
        plt.close(fig)
        self.plot_path = out


class VoiceprintApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()


if __name__ == '__main__':
    VoiceprintApp().run()
