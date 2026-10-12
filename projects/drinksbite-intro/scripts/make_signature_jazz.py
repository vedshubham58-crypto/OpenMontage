# DrinksBite signature tune — premium nu-jazz, music only, scored to the 33 s intro (120 BPM, swung).
# Muted trumpet carries the hook (A D F# (F)E D — "PAIR · SIP · RE-PEAT" with a blue grace note),
# Rhodes in extended voicings, walking upright bass, brushes + ride. Hook stated only 3 times.
# Run from projects/drinksbite-intro.
import sys, numpy as np
sys.path.insert(0, "scripts")
from make_jingles import SR, t_, hz, adsr, lp, hp, bp, kick, rhodes, vibe, ks, pad, Mix, rng

D = 33.0
BEAT = 0.5
SW = BEAT * 2 / 3                 # swung off-beat position inside a beat

# ---------------- instruments ----------------
def trumpet(f, d, g=0.2, scoop=True):
    """Harmon-muted trumpet: brassy harmonic stack, scoop into pitch, delayed vibrato, breath."""
    t = t_(d)
    fr = f * (1 - (0.03 if scoop else 0.0) * np.exp(-t * 35)) * (1 + 0.004 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.18) * 4, 0, 1))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    bright = 0.55 + 0.45 * (1 - np.exp(-t * 25))
    x = np.zeros_like(t)
    for h in range(1, 16):
        x += (h ** -0.9) * (bright ** (h / 3)) * np.sin(h * ph)
    x = bp(x, 650, 4200, 2) * 1.6 + 0.25 * lp(x, 900)          # Harmon-mute nasal colour
    x += bp(rng.standard_normal(len(t)), 1500, 5000) * 0.05      # breath
    return np.tanh(1.2 * x) * adsr(len(t), 0.03, 0.08) * g

def upright(f, d=0.48, g=0.55):
    x = ks(f, d, 0.994, 0.18, 1.0)
    t = t_(d); x += np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * 0.6     # body thump
    return lp(x, 1400) * adsr(len(x), 0.004, 0.06) * g

def ride(g=0.05, open_=1.0):
    t = t_(0.9); x = np.zeros_like(t)
    for f, a in ((3150, 1), (4270, 0.7), (5310, 0.5), (6900, 0.35), (8800, 0.25)):
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    x = x * 0.25 + hp(rng.standard_normal(len(t)), 5000) * 0.6
    return x * np.exp(-t * (4.5 / open_)) * adsr(len(t), 0.001, 0.05) * g

def brush(g=0.06, d=0.18):
    t = t_(d); return bp(rng.standard_normal(len(t)), 1200, 8000) * np.sin(np.pi * t / d) ** 1.5 * g

def rim(g=0.16):
    t = t_(0.09); x = np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 80) + bp(rng.standard_normal(len(t)), 2000, 6000) * np.exp(-t * 120) * 0.5
    return x * g

def hatfoot(g=0.05):
    t = t_(0.07); return bp(rng.standard_normal(len(t)), 5000, 11000) * np.exp(-t * 60) * g

# ---------------- harmony & lines ----------------
#           Dmaj9                Bm11                   Em9                    A13sus → A13
VOICE = [[54, 57, 61, 64], [57, 62, 64, 69], [55, 59, 62, 66], [55, 59, 61, 66]]   # rootless: bass owns the root
ROOT = [38, 35, 40, 33]
WALK = [[0, 4, 7, 8], [0, 3, 7, 4], [0, 3, 7, 6], [0, 7, 9, 4]]      # last step leads chromatically/by 4th to next root
HOOK = [(0.0, 69, 0.30), (0.333, 74, 0.17), (0.5, 78, 0.30), (0.80, 77, 0.06), (0.86, 76, 0.14), (1.0, 74, 1.4)]
LICK = [(0.0, 81, 0.15), (0.167, 78, 0.15), (0.333, 76, 0.15), (0.5, 74, 0.15), (0.667, 71, 0.4)]

def phrase(m, t0, notes, g=1.0, oct_rhodes=False, bus="wet"):
    for dt, n, d in notes:
        m.add(trumpet(hz(n), d + 0.12, 0.2), t0 + dt, g, 0.12, bus)
        if oct_rhodes: m.add(rhodes(hz(n - 12), d + 0.6, 0.12), t0 + dt, g, -0.15, bus)

def comp(m, t0, bar):
    v = [hz(n) for n in VOICE[bar % 4]]
    for k, (dt, dur, gg) in enumerate(((0.0, 0.9, 0.9), (SW + 0.5, 0.35, 0.6), (1.5 - 0.5 + SW, 0.45, 0.7))):
        for f in v: m.add(rhodes(f, dur + 0.5, 0.075), t0 + dt, gg, (k - 1) * 0.2, "duckwet")

def groove(m, t0, t1, kicks, density=1.0):
    nb = int(round((t1 - t0) / 2.0))
    for b in range(nb):
        tb = t0 + b * 2.0; bar = b % 4; R = ROOT[bar]
        comp(m, tb, bar)
        for q in range(4):                                       # walking bass, quarter notes
            m.add(upright(hz(R + WALK[bar][q] - (12 if WALK[bar][q] > 7 else 0)), 0.48), tb + q * BEAT, 1.0, 0, "duck")
        for q in range(4):
            tq = tb + q * BEAT
            m.add(ride(0.045), tq, 1.0, 0.35, "wet")
            if q in (1, 3): m.add(ride(0.03, 0.6), tq + SW, 1.0, 0.35, "wet"); m.add(rim(0.15), tq, 1.0, -0.1, "wet"); m.add(hatfoot(0.05), tq, 1.0, 0.2)
            m.add(brush(0.04 * density), tq, 1.0, -0.3)
        for kt in (tb, tb + 1.5 - 0.5 + SW):                    # soft kick: 1 and the swung "and" of 2
            m.add(kick(0.42), kt); kicks.append(kt)
        if b % 2 == 1: m.add(rim(0.06), tb + 3 * BEAT + SW, 1.0, -0.2, "wet")   # ghost note

def build(out):
    m = Mix(D); kicks = []
    # 0–2.7 · intimate open: Rhodes Dmaj9, bass pickup, the hook on muted trumpet
    for f in VOICE[0]: m.add(rhodes(hz(f), 2.6, 0.07), 0.0, 1.0, 0, "wet")
    m.add(pad([62, 66, 69, 73], 2.8, 0.025, 1500), 0.0, 1.0, 0, "wet")
    m.add(upright(hz(38), 1.4), 0.0, 1.0)
    phrase(m, 0.55, HOOK)
    for q, n in enumerate((45, 47, 49)): m.add(upright(hz(n), 0.3), 2.2 + q * 0.167, 0.9)      # pickup run into the band
    m.add(ride(0.04), 2.2, 1.0, 0.35, "wet")
    # 2.7–14.2 · the band
    groove(m, 2.7, 14.7, kicks)
    phrase(m, 8.7 - 0.5, LICK, 0.8); phrase(m, 12.7 - 0.5, LICK[:3] + [(0.5, 78, 0.5)], 0.7)
    # 14.2–15.6 · break: Rhodes + bass, trumpet teases the first three notes
    for f in VOICE[1]: m.add(rhodes(hz(f), 1.6, 0.075), 14.2, 1.0, 0, "wet")
    m.add(upright(hz(35), 0.9), 14.2, 1.0)
    phrase(m, 14.45, HOOK[:3], 0.85)
    m.add(ride(0.035), 15.1, 1.0, 0.35, "wet")
    # 15.6–28.7 · band returns; hook #2 (with Rhodes octave), sparse answering licks
    groove(m, 15.6, 28.7 + 0.1, kicks, 1.1)
    phrase(m, 15.6, HOOK, 1.0, oct_rhodes=True)
    phrase(m, 21.2, LICK, 0.75); phrase(m, 25.2, LICK, 0.75)
    # 28.7 · signature: hook #3 on the wordmark, then a Dmaj9 (6/9) chord rings out
    for b in range(1):
        comp(m, 28.7, 0)
        for q in range(3): m.add(upright(hz(ROOT[0] + WALK[0][q]), 0.48), 28.7 + q * BEAT, 1.0, 0, "duck")
        for q in range(3): m.add(ride(0.04), 28.7 + q * BEAT, 1.0, 0.35, "wet")
    m.add(kick(0.42), 28.7); kicks.append(28.7)
    phrase(m, 28.7, HOOK, 1.1, oct_rhodes=True)
    end = 30.2
    m.add(upright(hz(38), 2.5, 0.6), end, 1.0)
    for f in (57, 59, 64, 66, 71): m.add(rhodes(hz(f), 3.2, 0.075), end, 1.0, 0, "wet")
    for k, f in enumerate((74, 78, 81, 83)): m.add(vibe(hz(f), 2.5, 0.08), end + 0.08 * k, 1.0, (k - 1.5) * 0.3, "wet")
    m.add(ride(0.06, 2.0), end, 1.0, 0.35, "wet")
    m.save(out, kicks)

if __name__ == "__main__":
    build("hyperframes/assets/signature-jazz-raw.wav"); print("ok")
