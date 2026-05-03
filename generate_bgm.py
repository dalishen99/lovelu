# -*- coding: utf-8 -*-
"""
原创合成的浪漫钢琴背景音乐 —— 不依赖任何外部音源/版权素材

- 进行：Cmaj7 -> Am7 -> Fmaj7 -> G7 ("doo-wop"/I-vi-IV-V 的扩展，公认的"情歌"和声)
- 60 BPM 的慢速分解和弦
- 加性合成 + 自然指数衰减的钢琴音色
- 简化的 Schroeder 混响营造空间感
- 输出 mono WAV 方便浏览器循环播放，结尾 crossfade 到开头让 loop 无缝
"""
import os
import math
import numpy as np
from scipy.io import wavfile

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "bgm.wav")
SR = 44100  # sample rate

# ---------- MIDI 音高 → 频率 ----------
def note_freq(name):
    """e.g. note_freq('C4') -> 261.63"""
    NAMES = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
             'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
    # 拆 octave
    if name[1] in '#b':
        pitch, octave = name[:2], int(name[2:])
    else:
        pitch, octave = name[:1], int(name[1:])
    midi = 12 * (octave + 1) + NAMES[pitch]
    return 440.0 * (2 ** ((midi - 69) / 12))

# ---------- 钢琴音色（加性合成） ----------
def piano_note(freq, duration_s, amp=0.18):
    n = int(SR * duration_s)
    t = np.arange(n) / SR

    # 基频 + 6 次谐波，谐波越高振幅越小，模拟钢琴
    # 极轻微的非谐性（×1.0005, ×2.0008, ...）让音色更接近真实钢琴
    wave = (
        1.00 * np.sin(2 * np.pi * freq * 1.0000 * t) +
        0.55 * np.sin(2 * np.pi * freq * 2.0008 * t) +
        0.30 * np.sin(2 * np.pi * freq * 3.0020 * t) +
        0.18 * np.sin(2 * np.pi * freq * 4.0040 * t) +
        0.10 * np.sin(2 * np.pi * freq * 5.0070 * t) +
        0.05 * np.sin(2 * np.pi * freq * 6.0100 * t)
    )

    # 钢琴包络：极短攻击 + 指数衰减
    attack = max(1, int(0.005 * SR))
    env = np.exp(-2.4 * t / max(duration_s, 0.001))
    env[:attack] *= np.linspace(0, 1, attack)
    # 平滑收尾，避免咔哒声
    release = max(1, int(0.03 * SR))
    if n > release:
        env[-release:] *= np.linspace(1, 0, release)

    return amp * wave * env

# ---------- 简易 Schroeder 混响 ----------
def reverb(x, mix=0.25, decay=0.65):
    """4 个梳状滤波器 + 2 个全通，简化的 Schroeder reverb。"""
    out = np.zeros_like(x)
    delays = [int(0.0297 * SR), int(0.0371 * SR), int(0.0411 * SR), int(0.0437 * SR)]
    for d in delays:
        buf = np.zeros(d)
        y = np.zeros_like(x)
        for i in range(len(x)):
            y[i] = x[i] + decay * buf[i % d]
            buf[i % d] = y[i]
        out += y
    out /= len(delays)

    # 两个全通让混响更"散开"
    for d_ms, g in [(5.0, 0.7), (1.7, 0.7)]:
        d = int(d_ms / 1000 * SR)
        buf = np.zeros(d)
        y = np.zeros_like(out)
        for i in range(len(out)):
            inp = out[i]
            delayed = buf[i % d]
            y[i] = -g * inp + delayed
            buf[i % d] = inp + g * delayed
        out = y

    return (1 - mix) * x + mix * out

# ---------- 进行 ----------
# (低音根音，分解和弦组成音 [bass八度更低])
PROGRESSION = [
    ('C2', ['C4', 'E4', 'G4', 'B4']),  # Cmaj7
    ('A1', ['A3', 'C4', 'E4', 'G4']),  # Am7
    ('F2', ['F3', 'A3', 'C4', 'E4']),  # Fmaj7
    ('G2', ['G3', 'B3', 'D4', 'F4']),  # G7
]

# 每小节 4 拍，60 BPM => 1 拍 = 1 秒，1 小节 = 4 秒
BPM = 60
BEAT = 60.0 / BPM
BAR  = 4 * BEAT
CYCLE_BARS = len(PROGRESSION)
CYCLES = 4   # 总长 = 4 * 4 * 4s = 64s

def render():
    total = int(SR * (CYCLES * CYCLE_BARS * BAR + 1.5))
    out = np.zeros(total)

    pos = 0
    for cycle in range(CYCLES):
        for bass_name, chord_notes in PROGRESSION:
            # 1) 低音：长按一整小节
            bass = piano_note(note_freq(bass_name), BAR + 0.3, amp=0.12)
            out[pos:pos + len(bass)] += bass[:len(out) - pos]

            # 2) 分解和弦：每拍一个音，让音延伸到下一拍以上
            for i, note in enumerate(chord_notes):
                start = pos + int(i * BEAT * SR)
                if start >= len(out): break
                note_audio = piano_note(note_freq(note), BEAT * 1.8, amp=0.16)
                end = min(start + len(note_audio), len(out))
                out[start:end] += note_audio[:end - start]

            # 3) 高音点缀：在小节中间偷偷放一个高八度的"星星"音
            # 让旋律不那么规律
            sparkle_note = chord_notes[2]   # 第三个组成音的高八度
            sparkle_octave_up = sparkle_note[0] + str(int(sparkle_note[-1]) + 2)
            try:
                sf = note_freq(sparkle_octave_up)
                start = pos + int(2.5 * BEAT * SR)
                if start < len(out):
                    sp = piano_note(sf, BEAT * 1.2, amp=0.06)
                    end = min(start + len(sp), len(out))
                    out[start:end] += sp[:end - start]
            except Exception:
                pass

            pos += int(BAR * SR)

    # 归一化
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.8

    print(f"  原始合成完成: {len(out)/SR:.1f}s, 峰值 {peak:.3f}")

    # 加混响
    print("  加混响 (这步会慢一点，请稍等) …")
    out = reverb(out, mix=0.30, decay=0.55)

    # 再归一化一次（混响会改变音量）
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.55   # 稍轻一些，留 headroom，BGM 不该抢前景

    # ---------- 让 loop 无缝 ----------
    # 把开头复制到结尾做 crossfade
    cycle_len = int(CYCLES * CYCLE_BARS * BAR * SR)
    out = out[:cycle_len + int(0.5 * SR)]    # 留 0.5s 做交叉淡化
    fade_len = int(0.5 * SR)
    fade_in  = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    # 把结尾的 fade_out 部分和开头的 fade_in 部分混合
    out[-fade_len:] = out[-fade_len:] * fade_out + out[:fade_len] * fade_in
    # 真正循环时只用 0..cycle_len 部分
    out = out[:cycle_len]

    # 写文件
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wavfile.write(OUT, SR, (out * 32767).astype(np.int16))
    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"\n  [OK] 写入 {OUT}")
    print(f"       时长 {len(out)/SR:.1f}s, 大小 {size_mb:.2f} MB, mono {SR}Hz")

if __name__ == "__main__":
    print("生成浪漫钢琴 BGM …")
    render()
