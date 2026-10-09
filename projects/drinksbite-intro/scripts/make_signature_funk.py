# DrinksBite signature tune — "retro funk", music only (no SFX), scored to the 33 s intro.
# Premium funk with 90s-ad warmth; Indian instruments as colour (sitar hook, dholak pocket,
# harmonium stabs), never classical. Hook = A4 D5 F#5 E5 D5 ("PAIR · SIP · RE-PEAT").
# Run from projects/drinksbite-intro.
import sys, numpy as np
sys.path.insert(0, "scripts")
from make_jingles import SR, t_, hz, adsr, lp, hp, bp, kick, clap, hat, pad, reverb, Mix, rng

D = 33.0
S16 = 0.125                     # 16th note at 120 BPM

# ---------------- instruments ----------------
def sitar(f, d=0.9, g=0.22):
    """Pop-riff sitar: fast meend scoop into the note, buzzing (jawari) bloom on upper partials."""
    t = t_(d); fr = f * (1 - 0.035 * np.exp(-t * 60)); ph = 2 * np.pi * np.cumsum(fr) / SR
    bloom = (1 - np.exp(-t * 35)) * np.exp(-t * 5)
    x = np.zeros_like(t)
    for h in range(1, 18):
        a = h ** -0.75 * (1.0 if h < 4 else 0.35 + 1.6 * bloom)
        x += a * np.sin(h * ph + h) * np.exp(-t * (1.6 + 0.35 * h))
    x += 0.15 * np.sin(2 * np.pi * f * 2.003 * t) * np.exp(-t * 1.2)          # sympathetic shimmer
    x = np.tanh(1.3 * x) * adsr(len(t), 0.002, 0.12)
    return lp(x, 7000) * g

def slap(f, d=0.22, pop=False, g=0.42):
    t = t_(d)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 20)
    saw = 2 * ((f * t) % 1) - 1
    x += lp(saw, 600 + 4000 * (1.0 if pop else 0.4)) * (0.8 if pop else 0.35) * np.exp(-t * (18 if pop else 9))
    x[:200] += np.linspace(1, 0, 200) * (0.9 if pop else 0.4) * np.sign(np.sin(np.arange(200) * 0.9))
    return np.tanh(1.5 * x * np.exp(-t * 6)) * adsr(len(t), 0.001, 0.04) * g

def wah(fs, d=0.11, centre=1200, g=0.16):
    t = t_(d); x = np.zeros_like(t)
    for f in fs: x += 2 * ((f * t + rng.uniform()) % 1) - 1
    x = bp(x, centre * 0.6, centre * 1.6, 2) * np.exp(-t * 22)
    return np.tanh(2 * x) * adsr(len(t), 0.001, 0.02) * g

def brass(fs, d=0.32, g=0.16):
    t = t_(d); x = np.zeros_like(t)
    for f in fs:
        fr = f * (1 - 0.02 * np.exp(-t * 40))
        for dc in (-6, 0, 6): x += 2 * ((np.cumsum(fr * 2 ** (dc / 1200)) / SR + rng.uniform()) % 1) - 1
    cut = 700 + 4200 * (1 - np.exp(-t * 60)) * np.exp(-t * 4)
    y = np.zeros_like(x)                            # time-varying low-pass in short blocks
    for a in range(0, len(x), 480):
        y[a:a + 480] = lp(x[max(0, a - 960):a + 480], float(cut[a]), 2)[-len(x[a:a + 480]):]
    return np.tanh(1.4 * y / (3 * len(fs)) * 4) * adsr(len(t), 0.012, 0.08) * g

def harmonium(fs, d=0.16, g=0.07):
    t = t_(d); x = np.zeros_like(t)
    for f in fs:
        for dc in (-4, 4): x += np.sign(np.sin(2 * np.pi * f * 2 ** (dc / 1200) * t)) * 0.5
    return lp(x, 2400) * adsr(len(t), 0.01, 0.05) / len(fs) * g * 2

def dholak_ge(g=0.4):
    t = t_(0.45); f = 95 + 45 * (1 - np.exp(-t * 9))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * g

def dholak_ta(g=0.22):
    t = t_(0.18); x = np.sin(2 * np.pi * 440 * t) * np.exp(-t * 30) + bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 90) * 0.6
    return x * g

def snare(g=0.3):
    t = t_(0.22); n = bp(rng.standard_normal(len(t)), 1500, 9000) * np.exp(-t * 26)
    return (n + 0.5 * np.sin(2 * np.pi * 200 * t) * np.exp(-t * 35)) * g

def cassette(x):                                   # nostalgic tape colour for the intro only
    return np.tanh(1.8 * lp(hp(x, 120), 5200)) * 0.7

# ---------------- score ----------------
PROG = [[62, 66, 69, 73, 76], [59, 62, 66, 69], [64, 67, 71, 74], [57, 62, 64, 67]]   # D9  Bm7  Em9  A7sus
ROOT = [38, 35, 40, 33]
MOTIF = [(0.0, 69), (0.25, 74), (0.5, 78), (0.875, 76), (1.125, 74)]
BASS = [(0, 0, False), (3, 12, True), (6, 0, False), (7, 10, False), (10, 0, False), (11, 12, True), (14, 7, False), (15, 5, False)]
WAH = [1, 3, 6, 9, 11, 14]

def hook(m, t0, big=False, bus="wet"):
    for k, (dt, n) in enumerate(MOTIF):
        last = k == len(MOTIF) - 1
        m.add(sitar(hz(n), 1.6 if last else 0.7), t0 + dt, 1.0, (k - 2) * 0.12, bus)
        if big:
            ch = [hz(n), hz(n - 5), hz(n - 9)]
            m.add(brass(ch, 0.9 if last else 0.22), t0 + dt, 1.0, 0.0, bus)

def groove(m, t0, t1, kicks, full=True):
    for i, tt in enumerate(np.arange(t0, t1 - 1e-6, S16)):
        bar = int((tt - t0) // 2.0) % 4; s = i % 16; R = ROOT[bar]
        if s in (0, 7, 10): m.add(kick(0.8), tt); kicks.append(tt)
        if s in (4, 12): m.add(snare(0.3), tt, 1.0, 0, "wet"); m.add(clap(0.32), tt, 1.0, 0.05, "wet")
        m.add(hat(0.05 if s % 2 else 0.035, open_=(s in (6, 14))), tt, 1.0, 0.25 if s % 2 else -0.25)
        if s in (0, 3, 8, 11): m.add(dholak_ge(0.32), tt, 1.0, -0.2)
        if s in (6, 13, 15): m.add(dholak_ta(0.18), tt, 1.0, 0.25)
        for st, iv, pop in BASS:
            if s == st: m.add(slap(hz(R + iv), 0.2 if pop else 0.24, pop), tt, 1.0, 0, "duck")
        if full and s in WAH:
            ch = [hz(n) for n in PROG[bar][1:4]]
            m.add(wah(ch, 0.1, 700 + 1400 * ((s % 4) / 3)), tt, 1.0, 0.45)
        if full and s in (2, 10): m.add(harmonium([hz(n) for n in PROG[bar][:3]], 0.14), tt, 1.0, -0.4, "wet")
    for b, tt in enumerate(np.arange(t0, t1 - 0.5, 2.0)):
        ch = PROG[b % 4]
        m.add(pad(ch, 2.1, 0.028, 2200), tt, 1.0, 0, "duckwet")
        if full and b % 2 == 1: m.add(brass([hz(n) for n in ch[:3]], 0.24), tt + 1.75, 1.0, 0.1, "wet")   # anticipation stab

def build(out):
    m = Mix(D); kicks = []
    # INTRO 0–2.7: sitar hook alone over warm, tape-coloured chords (nostalgia), light pulse
    intro = Mix(2.9)
    intro.add(pad(PROG[0], 2.9, 0.05, 1600), 0.0, 1.0, 0, "dry")
    hook(intro, 0.55, bus="dry")
    for tt in np.arange(0.55, 2.6, 0.5): intro.add(dholak_ge(0.18), tt, 1.0, 0)
    intro.add(slap(hz(38), 0.4), 2.2, 0.6); intro.add(slap(hz(45), 0.3, True), 2.45, 0.6)
    for name, (L, R) in intro.bus.items():
        L2, R2 = cassette(L), cassette(R)
        m.add(L2, 0.0, 1.0, -0.15, "wet"); m.add(R2, 0.0, 1.0, 0.15, "wet")
    # DROP 2.7: full band, hook with brass
    groove(m, 2.7, 14.2, kicks)
    hook(m, 2.7, big=True); hook(m, 10.7, big=True)
    # BREAK 14.2–15.6: bass, claps and a sitar tease only
    for i, tt in enumerate(np.arange(14.2, 15.6 - 1e-6, S16)):
        s = i % 16
        if s in (4, 12): m.add(clap(0.3), tt, 1.0, 0, "wet")
        for st, iv, pop in BASS:
            if s == st: m.add(slap(hz(ROOT[1] + iv), 0.2, pop), tt, 0.8, 0, "duck")
    for dt, n in MOTIF[:3]: m.add(sitar(hz(n), 0.9), 14.5 + dt, 1.0, 0, "wet")
    # PAIRINGS + END 15.6–28.7: groove returns, hook every 4 bars
    groove(m, 15.6, 28.7, kicks)
    hook(m, 15.6, big=True); hook(m, 23.6, big=True)
    # SIGNATURE 28.7: hook big on the wordmark, final chord rings out
    for i, tt in enumerate(np.arange(28.7, 30.2, S16)):
        s = i % 16
        if s in (0, 7, 10): m.add(kick(0.75), tt); kicks.append(tt)
        if s in (4, 12): m.add(clap(0.32), tt, 1.0, 0, "wet")
        m.add(hat(0.04), tt, 1.0, 0.2)
    hook(m, 28.7, big=True)
    m.add(slap(hz(38), 1.2), 30.2, 1.0, 0, "dry"); m.add(kick(0.8), 30.2)
    m.add(brass([hz(n) for n in (62, 66, 69, 74)], 1.4, 0.2), 30.2, 1.0, 0, "wet")
    m.add(pad(PROG[0], 2.8, 0.05, 2600), 30.2, 1.0, 0, "wet")
    m.add(sitar(hz(74), 2.4, 0.18), 30.2, 1.0, 0.2, "wet")
    m.save(out, kicks)

if __name__ == "__main__":
    build("hyperframes/assets/signature-funk-raw.wav"); print("ok")
