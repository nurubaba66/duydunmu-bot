"""Telifsiz ses efektleri: hepsi matematiksel olarak sentezlenir, dış kaynak kullanılmaz."""
import wave

import numpy as np

SR = 44100


def _env(n, attack=0.005, decay=0.15):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-t / decay)


def pop(f0=520, f1=980, dur=0.12):
    n = int(SR * dur)
    t = np.arange(n) / SR
    freq = np.linspace(f0, f1, n)
    s = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    return 0.55 * s * _env(n, 0.002, 0.045)


def whoosh(dur=0.45, up=True):
    n = int(SR * dur)
    noise = np.random.default_rng(7).standard_normal(n)
    # basit kayan alçak geçiren filtre
    out, y = np.zeros(n), 0.0
    cut = np.linspace(0.02, 0.35, n) if up else np.linspace(0.35, 0.02, n)
    for i in range(n):
        y += cut[i] * (noise[i] - y)
        out[i] = y
    shape = np.sin(np.pi * np.arange(n) / n) ** 1.5
    return 0.6 * out / (np.abs(out).max() + 1e-9) * shape


def click(dur=0.05):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1800 * t) + 0.5 * np.sin(2 * np.pi * 3200 * t)
    return 0.45 * s * _env(n, 0.0005, 0.008)


def ding(f=1320, dur=0.7):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t) + 0.2 * np.sin(2 * np.pi * f * 3.02 * t)
    return 0.32 * s * _env(n, 0.003, 0.22)


def chime():
    a, b = ding(1046, 0.6), ding(1568, 0.8)
    out = np.zeros(int(SR * 0.95))
    out[:len(a)] += a
    k = int(SR * 0.12)
    out[k:k + len(b)] += b
    return out


def track(events: list[tuple[float, np.ndarray]], total: float, path: str):
    buf = np.zeros(int(SR * total) + SR)
    for t, snd in events:
        i = int(t * SR)
        buf[i:i + len(snd)] += snd[: max(0, len(buf) - i)]
    buf = np.clip(buf * 0.75, -0.95, 0.95)
    stereo = (np.repeat(buf[:, None], 2, axis=1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())
