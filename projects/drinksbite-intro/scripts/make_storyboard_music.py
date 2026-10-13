# Music for the 30 s storyboard film: filtered disco-house, opens on the reveal (2.0), dips for the
# moment (18) and the idea (24.6), full on the end card (27). Music only + one soft crunch at 19.0.
import sys, numpy as np
sys.path.insert(0, "scripts")
from make_jingles import SR, kick, clap, hat, crunch, Mix
from make_signatures_v2 import strings, piano, fm_bass, chorus_lead, sweep_lp, hook_notes, hz, S16
D = 30.0
CH = [[59, 62, 66, 69], [64, 68, 71, 74], [62, 67, 71, 74], [61, 64, 69, 73]]
RT = [35, 40, 43, 45]
m = Mix(D); kicks = []; N = int(D * SR); loop = np.zeros(N)
def lay(sig, t):
    a = int(t * SR); sig = sig[:N - a]; loop[a:a + len(sig)] += sig
for b, tb in enumerate(np.arange(0, 29.0, 2.0)):
    for i in (0, 3, 6, 8, 11, 14):
        lay(strings([hz(n) for n in CH[b % 4]], 0.22, 0.09, 0.005), tb + i * S16)
        lay(piano([hz(n + 12) for n in CH[b % 4][1:]], 0.3, 0.06), tb + i * S16)
tt = np.arange(N) / SR
cut = np.interp(tt, [0, 1.9, 2.0, 17.8, 18.0, 19.9, 20.0, 24.5, 24.6, 26.9, 27.0, 30],
                    [450, 900, 6500, 9000, 1300, 1600, 8000, 9500, 1500, 2200, 15000, 15000])
loop = sweep_lp(loop, cut)
m.add(loop, 0, 1.0, -0.1, "duck"); m.add(loop * 0.7, 0, 1.0, 0.25, "duckwet")
def beat(t0, t1, full=True):
    for i, ts in enumerate(np.arange(t0, t1 - 1e-6, S16)):
        b = int(ts // 2.0) % 4; s = i % 16
        if s % 4 == 0: m.add(kick(0.9), ts); kicks.append(ts)
        if full and s in (4, 12): m.add(clap(0.38), ts, 1.0, 0, "wet")
        if full and s % 4 == 2: m.add(hat(0.055, open_=True), ts, 1.0, 0.25)
        elif full and s % 2: m.add(hat(0.024), ts, 1.0, -0.25)
        if s in (2, 6, 10, 14): m.add(fm_bass(hz(RT[b] + (12 if s in (6, 14) else 0)), 0.2, 0.42, 0.5), ts, 1.0, 0, "duck")
def lead(t0, g=1.0):
    for dt, n, d in hook_notes(): m.add(chorus_lead(hz(n), d + 0.15, 0.13, "saw"), t0 + dt, g, 0.0, "wet")
beat(2.0, 18.0); beat(18.0, 20.0, full=False); beat(20.0, 24.6); beat(27.0, 29.0)
lead(0.4, 0.8); lead(6.0, 0.7); lead(10.0, 0.7); lead(14.0, 0.7); lead(22.0, 0.9); lead(27.0, 1.1)
m.add(crunch(0.22, 0.35), 19.0)
m.add(strings([hz(n) for n in (62, 66, 69, 74)], 2.2, 0.06, 0.05), 28.9, 1.0, 0, "wet")
m.add(fm_bass(hz(38), 1.2, 0.5, 0.3), 29.0, 1.0); m.add(kick(0.8), 29.0)
m.save("../drinksbite-storyboard/hyperframes/assets/soundtrack-raw.wav", kicks); print("ok")
