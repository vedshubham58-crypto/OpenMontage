# DrinksBite signature jingle — three original options, scored to the 33 s intro cut.
# Every option shares one sonic logo: cap POP → fizz → the 5-note "PAIR · SIP · RE-PEAT" motif
# (A4 D5 F#5 E5 D5) → crunch. Run from projects/drinksbite-intro.
import numpy as np, wave, sys

SR = 48000
rng = np.random.default_rng(7)
D = 33.0
BEAT = 0.5  # 120 BPM, locked to the edit


def t_(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def adsr(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); nr = min(n - na, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr > 0: e[-nr:] *= np.linspace(1, 0, nr)
    return e
from scipy.signal import butter, sosfilt
def lp(x, fc, o=4): return sosfilt(butter(o, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=4): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos'), x)


# ---------------- instruments ----------------
def rhodes(f, d, g=0.18):
    t = t_(d); I = 1.6 * np.exp(-t * 3.5) + 0.25
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t))
    x += 0.12 * np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 30)       # tine bark
    x *= np.exp(-t * 1.6) * (1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)) * adsr(len(t), 0.003, 0.15)
    return x * g

def vibe(f, d, g=0.22):
    t = t_(d)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 6) + 0.08 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t * 14)
    return x * np.exp(-t * 1.4) * (1 + 0.25 * np.sin(2 * np.pi * 5.5 * t)) * adsr(len(t), 0.002, 0.2) * g

def glass(f, d=1.6, g=0.25):          # tuned glass clink: inharmonic bell partials
    t = t_(d); x = np.zeros_like(t)
    for r, a, k in ((1, 1, 2.2), (2.32, 0.5, 3.5), (4.25, 0.32, 6), (6.63, 0.18, 9), (9.1, 0.08, 14)):
        x += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6)) * np.exp(-t * k)
    x += bp(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 120) * 0.4
    return x * adsr(len(t), 0.0008, 0.1) * g

def santoor(f, d=1.4, g=0.2):         # hammered-string: 3 detuned courses, bright attack
    t = t_(d); x = np.zeros_like(t)
    for dc in (-2.5, 0, 2.5):
        ff = f * 2 ** (dc / 1200)
        for h, a in ((1, 1), (2, 0.6), (3, 0.35), (4, 0.22), (5, 0.12)):
            x += a * np.sin(2 * np.pi * ff * h * t) * np.exp(-t * (1.8 + h * 1.2))
    x += bp(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 200) * 0.6
    return x / 3 * adsr(len(t), 0.001, 0.2) * g

def ks(f, d, damp=0.996, bright=0.5, g=0.3):   # Karplus–Strong pluck (bass / guitar)
    n = int(d * SR); N = max(2, int(SR / f)); y = np.zeros(n + N)
    y[:N] = lp(rng.uniform(-1, 1, N), 400 + 6000 * bright)
    for s in range(N, n + N, N):
        e = min(s + N, n + N); prev = y[s - N:e - N]; prev2 = np.concatenate([[y[s - N - 1] if s - N - 1 >= 0 else 0], prev[:-1]])
        y[s:e] = damp * 0.5 * (prev + prev2)
    return y[N:] * adsr(n, 0.002, 0.08) * g

def sub(f, d, g=0.35):
    t = t_(d); x = np.sin(2 * np.pi * f * t); x = np.tanh(1.6 * x)
    return x * adsr(len(t), 0.01, 0.08) * g

def pad(fs, d, g=0.05, bright=1800):
    t = t_(d); x = np.zeros_like(t)
    for f in fs:
        for dc in (-7, 0, 7):
            ph = rng.uniform(0, 1)
            x += 2 * ((f * 2 ** (dc / 1200) * t + ph) % 1) - 1   # saw
    x = lp(x, bright, 2)
    return x / (3 * len(fs)) * adsr(len(t), 0.4, 0.8) * g * 6

def drone(f, d, g=0.06):                  # tanpura-style shimmering drone
    t = t_(d); x = np.zeros_like(t)
    for h in range(1, 12):
        x += (1 / h) * np.sin(2 * np.pi * f * h * t) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.13 + 0.07 * h) * t + h))
    return x * adsr(len(t), 0.8, 1.0) * g

def kick(g=0.9):
    t = t_(0.45); f = 48 + 90 * np.exp(-t * 32)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    x[:240] += np.linspace(1, 0, 240) * 0.5 * rng.standard_normal(240)
    return np.tanh(1.4 * x) * g

def snare(g=0.35):
    t = t_(0.25); n = bp(rng.standard_normal(len(t)), 1200, 9000) * np.exp(-t * 22)
    return (n + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * g

def clap(g=0.35):
    t = t_(0.3); n = bp(rng.standard_normal(len(t)), 900, 6000)
    e = sum(np.exp(-np.clip(t - o, 0, None) * 60) * (t >= o) for o in (0, 0.011, 0.022)) + np.exp(-t * 12) * 0.5
    return n * e * g * 0.6

def snap(g=0.3):
    t = t_(0.08); return bp(rng.standard_normal(len(t)), 1800, 5000) * np.exp(-t * 90) * g

def hat(g=0.12, open_=False):
    t = t_(0.25 if open_ else 0.06); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * (14 if open_ else 70)) * g

def shaker(g=0.07):
    t = t_(0.12); return bp(rng.standard_normal(len(t)), 4000, 12000) * np.sin(np.pi * t / 0.12) ** 2 * g

def tabla_na(g=0.3):
    t = t_(0.5); x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((520, 1, 9), (1040, 0.4, 14), (1580, 0.25, 20)))
    return (x + bp(rng.standard_normal(len(t)), 2000, 7000) * np.exp(-t * 150) * 0.5) * g

def tabla_ge(g=0.45):                       # bayan with the signature upward glide
    t = t_(0.7); f = 85 + 35 * (1 - np.exp(-t * 6))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) * g

def cap_pop(g=0.6):                         # bottle cap / can pop
    t = t_(0.12); f = 180 + 900 * np.exp(-t * 90)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) + bp(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 120) * 0.8
    return x * g

def fizz(d=1.2, g=0.18):                    # carbonation: hiss + sparse micro-crackles
    t = t_(d); x = hp(rng.standard_normal(len(t)), 6000) * 0.25
    imp = np.zeros(len(t)); idx = rng.integers(0, len(t), int(d * 900)); imp[idx] = rng.uniform(0.3, 1, len(idx))
    x += bp(imp, 3000, 14000) * 2.2
    return x * np.exp(-t * 2.2) * adsr(len(t), 0.005, 0.3) * g

def crunch(d=0.22, g=0.5):
    t = t_(d); x = np.zeros_like(t)
    for _ in range(int(d * 260)):
        o = rng.integers(0, len(t) - 400); L = rng.integers(60, 380)
        x[o:o + L] += bp(rng.standard_normal(L), 900, 7000) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.3, 1)
    return x * np.exp(-t * 6) * g

def boom(g=0.6):
    t = t_(1.6); f = 32 + 40 * np.exp(-t * 4)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.5) * np.exp(-t * 2.2) * g

def whoosh(d=0.5, g=0.35):
    t = t_(d); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    return bp(n, 400, 5000) * env * g

def riser(d=1.0, g=0.25):
    t = t_(d); n = rng.standard_normal(len(t)); y = np.zeros_like(n)
    for i, a in enumerate(np.array_split(np.arange(len(n)), 12)):
        y[a[0]:a[-1] + 1] = bp(n[a[0]:a[-1] + 1], 300 + 500 * i, 1500 + 900 * i)
    return y * (t / d) ** 2 * g

def reverb(x, secs=1.8, mix=0.22):
    from scipy.signal import fftconvolve
    t = t_(secs); ir = rng.standard_normal(len(t)) * np.exp(-t * 6.9 / secs); ir = lp(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
    return x + mix * fftconvolve(x, ir)[:len(x)]


class Mix:
    def __init__(s, d): s.N = int(d * SR); s.L = np.zeros(s.N); s.R = np.zeros(s.N); s.bus = {}
    def add(s, sig, t, g=1.0, pan=0.0, bus="dry"):
        a = int(t * SR)
        if a >= s.N: return
        sig = sig[:s.N - a] * g
        L, R = s.bus.setdefault(bus, [np.zeros(s.N), np.zeros(s.N)])
        L[a:a + len(sig)] += sig * np.sqrt(0.5 * (1 - pan)); R[a:a + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))
    def render(s, duck_times):
        duck = np.ones(s.N)                       # sidechain from the kick
        for kt in duck_times:
            a = int(kt * SR); n = min(int(0.3 * SR), s.N - a)
            if n > 0: duck[a:a + n] = np.minimum(duck[a:a + n], 1 - 0.55 * np.exp(-np.arange(n) / (0.07 * SR)))
        out = [np.zeros(s.N), np.zeros(s.N)]
        for name, (L, R) in s.bus.items():
            if name == "wet": L, R = reverb(L, 2.2, 0.35), reverb(R, 2.3, 0.35)
            if name == "duck": L, R = L * duck, R * duck
            if name == "duckwet": L, R = reverb(L * duck, 2.0, 0.3), reverb(R * duck, 2.1, 0.3)
            out[0] += L; out[1] += R
        m = np.stack(out, 1); f = int(0.6 * SR); m[-f:] *= np.linspace(1, 0, f)[:, None]
        m = np.tanh(m / (np.max(np.abs(m)) + 1e-9) * 1.3) / np.tanh(1.3)
        return m
    def save(s, path, duck_times):
        m = s.render(duck_times)
        w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m * 0.95 * 32767).astype('<i2').tobytes()); w.close()


# ---------------- shared score ----------------
MOTIF = [(0.0, 69), (0.25, 74), (0.5, 78), (0.875, 76), (1.125, 74)]   # PAIR · SIP · RE-PEAT
PROG = {  # one bar = 2 s
    "house": [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 67]],       # Dmaj7 Bm7 Gmaj7 A7
    "desi":  [[62, 66, 69], [64, 67, 71], [62, 66, 69], [60, 64, 67]],                       # D  Em  D  C  (mixolydian lift)
    "noir":  [[62, 66, 69, 73], [59, 62, 66, 69], [64, 67, 71, 74], [57, 61, 64, 67, 71]],   # Dmaj7 Bm7 Em7 A9
}
ROOT = {"house": [38, 35, 31, 33], "desi": [38, 40, 38, 36], "noir": [38, 35, 40, 33]}

def logo(m, t0, voice, big=False):
    m.add(cap_pop(), t0 - 0.35, 0.9, 0.1, "wet"); m.add(fizz(1.4), t0 - 0.3, 1.0, 0.0, "wet")
    for k, (dt, n) in enumerate(MOTIF):
        last = k == len(MOTIF) - 1
        m.add(voice(hz(n), 2.6 if last else 1.2), t0 + dt, (1.0 if not last else 1.15) * (1.7 if big else 1.2), (k - 2) * 0.18, "wet")
        if big: m.add(voice(hz(n - 12), 2.6 if last else 1.0), t0 + dt, 0.5, (k - 2) * 0.18, "wet")
    m.add(crunch(0.25, 0.55), t0 + 1.5, 1.0, 0.0, "dry")

def groove(m, style, t0, t1, kicks, energy=1.0):
    prog, roots = PROG[style], ROOT[style]
    for i, tt in enumerate(np.arange(t0, t1 - 1e-6, BEAT / 2)):      # 8th-note grid
        bar = int((tt - t0) // 2.0) % 4; beat8 = i % 8
        if style == "house":
            if i % 2 == 0: m.add(kick(0.85 * energy), tt); kicks.append(tt)
            if beat8 in (2, 6): m.add(clap(0.4), tt, 1.0, 0.0, "wet")
            m.add(hat(0.07, open_=(i % 2 == 1)), tt + 0.0, 0.8, 0.25 if i % 2 else -0.25)
            if i % 2 == 1: m.add(sub(hz(roots[bar]), 0.22), tt, 1.0, 0, "duck")
        elif style == "desi":
            if beat8 in (0, 3, 6): m.add(kick(0.75 * energy), tt); kicks.append(tt)
            if beat8 in (0, 5): m.add(tabla_ge(0.45), tt, 1.0, -0.15)
            if beat8 in (2, 4, 7): m.add(tabla_na(0.28), tt, 1.0, 0.2, "wet")
            m.add(shaker(0.06), tt + 0.06, 1.0, 0.35 if i % 2 else -0.35)
            if beat8 in (0, 3, 6): m.add(sub(hz(roots[bar]), 0.35), tt, 1.0, 0, "duck")
            if beat8 == 4: m.add(clap(0.3), tt, 1.0, 0.0, "wet")
        else:  # noir: swung, brushed, walking bass
            sw = 0.06 if i % 2 else 0.0
            if beat8 in (0, 5): m.add(kick(0.6 * energy), tt); kicks.append(tt)
            if beat8 in (2, 6): m.add(snap(0.45), tt + sw, 1.0, 0.3, "wet")
            m.add(hat(0.06), tt + sw, 1.0, -0.3)
            if i % 2 == 0:
                walk = [0, 4, 7, 9][(i // 2) % 4]
                m.add(ks(hz(roots[bar] + walk), 0.5, 0.995, 0.25, 0.55), tt, 1.0, 0, "duck")
    for b, tt in enumerate(np.arange(t0, t1 - 0.5, 2.0)):            # harmony per bar
        ch = prog[b % 4]
        if style == "house":
            for k in (0, 0.75, 1.25):
                for n in ch: m.add(rhodes(hz(n), 0.6), tt + k, 0.55, 0.0, "duckwet")
            m.add(pad(ch, 2.2, 0.035), tt, 1.0, 0, "duckwet")
        elif style == "desi":
            m.add(drone(hz(50), 2.2, 0.04), tt, 1.0, 0, "duck")
            for k, n in enumerate([ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]):
                m.add(santoor(hz(n), 0.9, 0.12), tt + 0.5 * k + 0.25, 1.0, (k - 1.5) * 0.3, "wet")
        else:
            for k in (0, 1.25):
                for n in ch: m.add(rhodes(hz(n), 1.0, 0.13), tt + k + 0.06, 0.7, 0.0, "duckwet")

def build(style, out):
    m = Mix(D); kicks = []
    voice = {"house": glass, "desi": santoor, "noir": vibe}[style]
    # HOOK 0–2.7: three colour slashes = three tuned hits, then the sonic logo under the line
    for k, (tt, n) in enumerate(((0.0, 62), (0.07, 66), (0.14, 69))):
        m.add(voice(hz(n), 0.8), tt, 0.9, (k - 1) * 0.6, "wet"); m.add(kick(0.5), tt)
    m.add(pad(PROG[style][0], 2.6, 0.03), 0.3, 1.0, 0, "wet")
    if style == "desi": m.add(drone(hz(50), 2.7, 0.05), 0.0)
    logo(m, 0.6, voice)
    m.add(riser(0.8, 0.22), 1.9, 1.0, 0, "wet")
    # BODY
    m.add(boom(0.6), 2.7); m.add(cap_pop(0.5), 2.7, 0.6, 0.2, "wet")
    groove(m, style, 2.7, 14.2, kicks)
    for tt in (6.6, 8.2): m.add(whoosh(0.35, 0.3), tt - 0.25, 1.0, 0, "wet")
    m.add(crunch(0.4, 0.8), 9.8); m.add(boom(0.45), 9.8)
    for tt, n in ((11.25, 69), (12.15, 74), (13.05, 78)): m.add(voice(hz(n), 0.8), tt, 0.7, 0, "wet")   # claims
    m.add(riser(0.5, 0.2), 13.7, 1.0, 0, "wet")
    # TWIST 14.2–15.6: drop out, motif teased
    m.add(pad(PROG[style][1], 1.6, 0.045), 14.2, 1.0, 0, "wet")
    for dt, n in MOTIF[:3]: m.add(voice(hz(n), 1.0), 14.35 + dt * 1.2, 0.8, 0, "wet")
    # PAIRINGS 15.6–26.2
    groove(m, style, 15.6, 26.2, kicks, 1.05)
    for tt, n in ((15.85, 69), (19.4, 74), (22.9, 78)):
        m.add(glass(hz(n + 12), 1.2, 0.18), tt + 0.45, 1.0, 0.3, "wet")      # glass clink per drink
        m.add(crunch(0.15, 0.35), tt)
    for tt in (15.45, 18.95, 22.45): m.add(whoosh(0.4, 0.28), tt, 1.0, 0, "wet")
    # END 26.2–33: impact, then the full sonic logo on the wordmark, final chord rings out
    m.add(boom(0.65), 26.2); m.add(pad(PROG[style][0], 6.5, 0.05), 26.2, 1.0, 0, "wet")
    for k, tt in enumerate((26.45, 26.53, 26.61)): m.add(kick(0.35), tt, 1.0, (k - 1) * 0.4)
    logo(m, 28.7, voice, big=True)
    for n in PROG[style][0]: m.add((rhodes if style != "desi" else santoor)(hz(n), 3.5), 29.95, 0.6, 0, "wet")
    if style == "desi": m.add(drone(hz(50), 6.8, 0.05), 26.2)
    m.save(out, kicks)

if __name__ == "__main__":
    for st in sys.argv[1:]: build(st, f"hyperframes/assets/jingle-{st}-raw.wav"); print("ok", st)
