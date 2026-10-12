# DrinksBite signature tune — round 2: synth-native styles (they sound authentic when synthesised).
#   citypop  : 80s city-pop, royal-road jazzy changes, FM slap bass, DX piano, chorus synth lead
#   frenchhouse : filtered disco-house loop, filter opens on the drop, pumping sidechain
#   bollydisco  : 80s Bollywood synth-disco, octave bass, syndrum "pew", string-synth stabs, square lead
# Music only (no SFX). Same arrangement map as the intro: hook 0.55, drop 2.7, break 14.2, return 15.6,
# signature 28.7, final chord 30.2. Run from projects/drinksbite-intro.
import sys, numpy as np
sys.path.insert(0, "scripts")
from make_jingles import SR, t_, hz, adsr, lp, hp, bp, kick, clap, hat, rhodes, pad, Mix, rng
from make_signature_funk import snare, brass

D = 33.0
S16 = 0.125

# ---------------- synths ----------------
def saw(f, t, det=0.0): return 2 * ((f * 2 ** (det / 1200) * t + rng.uniform()) % 1) - 1

def fm_bass(f, d=0.24, g=0.5, slap=1.0):
    t = t_(d); I = 2.8 * slap * np.exp(-t * 14) + 0.4
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t)) + 0.6 * np.sin(2 * np.pi * f * t)
    return np.tanh(1.3 * x) * np.exp(-t * 4) * adsr(len(t), 0.002, 0.05) * g

def chorus_lead(f, d, g=0.16, wave="square"):
    t = t_(d); fr = f * (1 - 0.02 * np.exp(-t * 30)) * (1 + 0.005 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) * 4, 0, 1))
    ph = np.cumsum(fr) / SR; x = np.zeros_like(t)
    for dc in (-9, 0, 9):
        p = ph * 2 ** (dc / 1200) + rng.uniform()
        x += (np.sign(np.sin(2 * np.pi * p)) * 0.6 + np.sin(2 * np.pi * p) * 0.6) if wave == "square" else (2 * (p % 1) - 1)
    x = lp(x / 3, 3800 if wave == "square" else 5200)
    return x * adsr(len(t), 0.012, 0.12) * g

def strings(fs, d, g=0.06, att=0.08):
    t = t_(d); x = sum(saw(f, t, dc) for f in fs for dc in (-12, 0, 12))
    return lp(x / (3 * len(fs)), 3200) * adsr(len(t), att, 0.25) * g * 3

def syndrum(f0=900, g=0.22):
    t = t_(0.45); f = f0 * 0.22 + f0 * np.exp(-t * 7)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * g

def gated_snare(g=0.32):
    t = t_(0.2); n = bp(rng.standard_normal(len(t)), 900, 8000)
    e = np.where(t < 0.13, 1.0, np.exp(-(t - 0.13) * 120))
    return (n * e + 0.5 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)) * g

def piano(fs, d=0.5, g=0.09):                      # bright DX/house piano stab
    t = t_(d); x = np.zeros_like(t)
    for f in fs:
        I = 1.2 * np.exp(-t * 8)
        x += np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * 2 * f * t)) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    return x / len(fs) * np.exp(-t * 3.5) * adsr(len(t), 0.002, 0.08) * g * 2

def sweep_lp(x, cut):                              # time-varying low-pass (block-wise)
    y = np.zeros_like(x); B = 480
    for a in range(0, len(x), B):
        seg = x[max(0, a - 4 * B):a + B]
        y[a:a + B] = lp(seg, float(np.clip(cut[min(a, len(cut) - 1)], 120, 18000)), 2)[-len(x[a:a + B]):]
    return y

# ---------------- shared map ----------------
def hook_notes(minor=False):
    third = 77 if minor else 78
    return [(0.0, 69, 0.22), (0.25, 74, 0.22), (0.5, third, 0.32), (0.875, 76, 0.22), (1.125, 74, 1.1)]

def bars(t0, t1): return [(t0 + 2.0 * b, b % 4) for b in range(int(round((t1 - t0) / 2.0)))]

# ======================= CITY POP =======================
def citypop(out):
    m = Mix(D); kicks = []
    CH = [[55, 59, 62, 66, 69], [57, 61, 64, 67, 71], [54, 57, 61, 64, 69], [47, 54, 57, 62, 66]]   # Gmaj9 A13 F#m7 Bm9
    RT = [43, 45, 42, 47]
    H = hook_notes()
    def lead(t0, g=1.0):
        for dt, n, d in H: m.add(chorus_lead(hz(n), d + 0.15, 0.15, "square"), t0 + dt, g, 0.1, "wet")
    def band(t0, t1):
        for tb, b in bars(t0, t1):
            for k, dt in enumerate((0.0, 0.75, 1.25, 1.75)):               # DX piano comping, syncopated
                m.add(rhodes(hz(CH[b][0]), 0.1, 0.0), tb, 0)               # (keeps rng stream stable)
                for n in CH[b][1:]: m.add(rhodes(hz(n), 0.55, 0.06), tb + dt, 0.9 if k == 0 else 0.6, (k - 1.5) * 0.2, "duckwet")
            m.add(strings([hz(n) for n in CH[b][1:4]], 2.1, 0.035, 0.3), tb, 1.0, 0, "duckwet")
            for i in range(16):
                tt = tb + i * S16
                if i in (0, 8): m.add(kick(0.75), tt); kicks.append(tt)
                if i in (4, 12): m.add(gated_snare(0.28), tt, 1.0, 0, "wet")
                m.add(hat(0.04 if i % 2 else 0.028), tt, 1.0, 0.3 if i % 2 else -0.3)
                if i in (0, 3, 6, 8, 10, 11, 14):                              # FM slap bass line
                    iv = {0: 0, 3: 12, 6: 0, 8: 0, 10: 7, 11: 12, 14: 10}[i]
                    m.add(fm_bass(hz(RT[b] + iv), 0.2, 0.45, 1.2 if iv == 12 else 0.8), tt, 1.0, 0, "duck")
    # intro: piano chord + lead hook, bass pickup
    for n in CH[0][1:]: m.add(rhodes(hz(n), 2.4, 0.07), 0.0, 1.0, 0, "wet")
    m.add(strings([hz(n) for n in CH[0][1:4]], 2.6, 0.04, 0.6), 0.0, 1.0, 0, "wet")
    lead(0.55)
    for q, n in enumerate((43, 45, 47, 49)): m.add(fm_bass(hz(n), 0.15, 0.4), 2.2 + q * 0.125, 1.0)
    band(2.7, 14.2); lead(2.7, 0.9); lead(10.7, 0.8)
    for n in CH[3][1:]: m.add(rhodes(hz(n), 1.4, 0.07), 14.2, 1.0, 0, "wet")
    for dt, n, d in H[:3]: m.add(chorus_lead(hz(n), d + 0.2, 0.13), 14.5 + dt, 1.0, 0, "wet")
    band(15.6, 28.7); lead(15.6); lead(23.6, 0.85)
    band(28.7, 30.7); lead(28.7, 1.15)
    for n in (55, 62, 66, 69, 74): m.add(rhodes(hz(n), 3.0, 0.07), 30.2, 1.0, 0, "wet")
    m.add(strings([hz(n) for n in (62, 66, 69, 74)], 2.8, 0.05, 0.1), 30.2, 1.0, 0, "wet")
    m.add(fm_bass(hz(43), 1.6, 0.5, 0.6), 30.2, 1.0)
    m.save(out, kicks)

# ======================= FRENCH DISCO-HOUSE =======================
def frenchhouse(out):
    m = Mix(D); kicks = []
    CH = [[59, 62, 66, 69], [64, 68, 71, 74], [62, 67, 71, 74], [61, 64, 69, 73]]   # Bm7 E9 Gmaj7(add) A6
    RT = [35, 40, 43, 45]
    H = hook_notes()
    N = int(D * SR); loop = np.zeros(N)
    def lay(sig, t):
        a = int(t * SR); sig = sig[:N - a]; loop[a:a + len(sig)] += sig
    # chopped disco loop: string-synth + piano stabs on the off-beats, runs the whole spot
    for tb, b in bars(0.0, 30.2):
        for i in (0, 3, 6, 8, 11, 14):
            lay(strings([hz(n) for n in CH[b]], 0.22, 0.09, 0.005), tb + i * S16)
            lay(piano([hz(n + 12) for n in CH[b][1:]], 0.3, 0.06), tb + i * S16)
    tt = np.arange(N) / SR
    cut = np.interp(tt, [0, 2.6, 2.7, 13.6, 14.2, 15.5, 15.6, 28.7, 30.2, 33], [500, 900, 7000, 9000, 900, 1400, 7000, 12000, 16000, 16000])
    loop = sweep_lp(loop, cut)
    m.add(loop, 0.0, 1.0, -0.1, "duck"); m.add(loop * 0.7, 0.0, 1.0, 0.25, "duckwet")
    def lead(t0, g=1.0):
        for dt, n, d in H: m.add(chorus_lead(hz(n), d + 0.15, 0.13, "saw"), t0 + dt, g, 0.0, "wet")
    def beat(t0, t1):
        for tb, b in bars(t0, t1):
            for i in range(16):
                ts = tb + i * S16
                if i % 4 == 0: m.add(kick(0.9), ts); kicks.append(ts)
                if i in (4, 12): m.add(clap(0.4), ts, 1.0, 0, "wet")
                if i % 4 == 2: m.add(hat(0.06, open_=True), ts, 1.0, 0.25)
                elif i % 2: m.add(hat(0.025), ts, 1.0, -0.25)
                if i in (2, 6, 10, 14): m.add(fm_bass(hz(RT[b] + (12 if i in (6, 14) else 0)), 0.2, 0.42, 0.5), ts, 1.0, 0, "duck")
    lead(0.55, 0.9)
    beat(2.7, 14.2); lead(2.7, 0.8); lead(10.7, 0.8)
    for dt, n, d in H[:3]: m.add(chorus_lead(hz(n), d + 0.2, 0.12, "saw"), 14.5 + dt, 1.0, 0, "wet")
    beat(15.6, 30.2); lead(15.6); lead(23.6, 0.85); lead(28.7, 1.15)
    m.add(strings([hz(n) for n in (62, 66, 69, 74)], 2.8, 0.06, 0.05), 30.2, 1.0, 0, "wet")
    m.add(fm_bass(hz(38), 1.4, 0.5, 0.3), 30.2, 1.0); m.add(kick(0.8), 30.2)
    m.save(out, kicks)

# ======================= RETRO BOLLYWOOD DISCO =======================
def bollydisco(out):
    m = Mix(D); kicks = []
    CH = [[62, 65, 69], [58, 62, 65], [60, 64, 67], [57, 61, 64, 67]]   # Dm  Bb  C  A7
    RT = [38, 34, 36, 33]
    H = hook_notes(minor=True)
    def lead(t0, g=1.0):
        for dt, n, d in H:
            m.add(chorus_lead(hz(n), d + 0.15, 0.15, "square"), t0 + dt, g, 0.0, "wet")
            m.add(chorus_lead(hz(n + 12), d + 0.15, 0.05, "saw"), t0 + dt, g, 0.0, "wet")
    def band(t0, t1):
        for tb, b in bars(t0, t1):
            for i in range(16):
                tt = tb + i * S16
                if i % 4 == 0: m.add(kick(0.8), tt); kicks.append(tt)
                if i in (4, 12): m.add(clap(0.38), tt, 1.0, 0, "wet"); m.add(gated_snare(0.18), tt, 1.0, 0, "wet")
                if i % 2: m.add(hat(0.035), tt, 1.0, 0.25)
                if i % 2 == 0: m.add(fm_bass(hz(RT[b] + (12 if i % 4 == 2 else 0)), 0.18, 0.42, 0.6), tt, 1.0, 0, "duck")   # octave disco bass
            for k, dt in enumerate((0.25, 0.75, 1.25, 1.75)):
                m.add(strings([hz(n) for n in CH[b]], 0.18, 0.08, 0.004), tb + dt, 1.0, (k % 2 - 0.5) * 0.4, "wet")
            m.add(pad(CH[b], 2.1, 0.022, 1800), tb, 1.0, 0, "duckwet")
            if b % 2 == 1:
                for k, f0 in enumerate((1100, 850, 650)): m.add(syndrum(f0, 0.18), tb + 1.5 + k * S16, 1.0, (k - 1) * 0.5, "wet")
    m.add(strings([hz(n) for n in CH[0]], 2.6, 0.05, 0.5), 0.0, 1.0, 0, "wet")
    lead(0.55)
    for k, f0 in enumerate((1200, 950, 750, 600)): m.add(syndrum(f0, 0.18), 2.2 + k * S16, 1.0, (k - 1.5) * 0.4, "wet")
    band(2.7, 14.2); lead(2.7, 0.9); lead(10.7, 0.8)
    m.add(strings([hz(n) for n in CH[1]], 1.4, 0.05, 0.2), 14.2, 1.0, 0, "wet")
    for dt, n, d in H[:3]: m.add(chorus_lead(hz(n), d + 0.2, 0.13), 14.5 + dt, 1.0, 0, "wet")
    band(15.6, 28.7); lead(15.6); lead(23.6, 0.85)
    band(28.7, 30.7); lead(28.7, 1.15)
    m.add(strings([hz(n) for n in (62, 65, 69, 74)], 2.8, 0.06, 0.05), 30.2, 1.0, 0, "wet")
    m.add(fm_bass(hz(38), 1.4, 0.5, 0.4), 30.2, 1.0); m.add(kick(0.8), 30.2)
    m.save(out, kicks)

if __name__ == "__main__":
    for st in sys.argv[1:]:
        globals()[st](f"hyperframes/assets/sig2-{st}-raw.wav"); print("ok", st)
