# Warm festive bed for the 7 s Diwali end slate: soft pad, bell chimes on each reveal, gentle pack thuds.
import numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000; D = 7.0; N = int(D * SR)
L = np.zeros(N); Rr = np.zeros(N); rng = np.random.default_rng(3)
t_ = lambda d: np.arange(int(d * SR)) / SR
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def add(sig, t, g=1.0, pan=0.0):
    a = int(t * SR); sig = sig[:N - a] * g
    L[a:a + len(sig)] += sig * np.sqrt(0.5 * (1 - pan)); Rr[a:a + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))
def pad(ns, d, g):
    t = t_(d); x = sum(np.sin(2 * np.pi * hz(n) * (1 + dc) * t) for n in ns for dc in (-0.002, 0, 0.002))
    e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.5); return x * e * g / len(ns)
def bell(n, d=2.5, g=0.18):
    t = t_(d); f = hz(n)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in ((1, 1, 1.6), (2.0, 0.5, 2.5), (3.01, 0.3, 4), (4.2, 0.15, 6)))
    return x * np.minimum(1, t / 0.003) * g
def thud(g=0.4):
    t = t_(0.4); return np.sin(2 * np.pi * np.cumsum(55 + 50 * np.exp(-t * 30)) / SR) * np.exp(-t * 9) * g
add(pad([50, 57, 62, 66, 69, 76], 7.0, 0.22), 0.0)
for k, n in enumerate((74, 78)): add(bell(n), 0.3 + k * 0.14, 1, -0.3 + k * 0.3)
for k, n in enumerate((81, 78)): add(bell(n), 1.5 + k * 0.14, 1, 0.3 - k * 0.3)
for k, n in enumerate((86, 90, 93, 98)): add(bell(n, 3.0, 0.12), 2.4 + k * 0.07, 1, (k - 1.5) * 0.3)
for k, t in enumerate((3.25, 3.37, 3.49)): add(thud(0.35), t, 1, (k - 1) * 0.4)
for k, n in enumerate((74, 81, 86)): add(bell(n, 3.0, 0.1), 3.8 + k * 0.12, 1, (k - 1) * 0.4)
ir = rng.standard_normal(int(2.2 * SR)) * np.exp(-np.arange(int(2.2 * SR)) / SR * 3.2); ir = sosfilt(butter(2, 6000, 'low', fs=SR, output='sos'), ir); ir /= np.sqrt((ir ** 2).sum())
L = L + 0.35 * fftconvolve(L, ir)[:N]; Rr = Rr + 0.35 * fftconvolve(Rr, ir)[:N]
m = np.stack([L, Rr], 1); f = int(0.8 * SR); m[-f:] *= np.linspace(1, 0, f)[:, None]; m /= np.abs(m).max() * 1.15
w = wave.open("assets/soundtrack-raw.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype("<i2").tobytes()); w.close()
print("ok")
