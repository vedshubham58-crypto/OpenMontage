# Quirky-classy 16 s bed per SKU (transposed), with a few playful accents synced to the edit.
import sys, numpy as np
sys.path.insert(0, "../drinksbite-intro/scripts")
from make_jingles import SR, kick, clap, hat, crunch, cap_pop, whoosh, Mix, hz
from make_signatures_v2 import fm_bass, piano, chorus_lead, strings, S16
def build(key, tr):
    m = Mix(16.0); kicks = []
    CH = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 67]]
    RT = [38, 35, 31, 33]
    # 0–1.55: tiptoe pizzicato tension, building
    for i, t in enumerate(np.arange(0.0, 1.5, 0.25)):
        m.add(piano([hz(74 + tr + (i % 2) * 2)], 0.2, 0.05 + i * 0.01), t, 1, (-1) ** i * 0.3, "wet")
    m.add(cap_pop(0.8), 1.55); m.add(crunch(0.3, 0.6), 1.56)
    m.add(whoosh(0.45, 0.5), 2.15, 1, 0, "wet"); m.add(whoosh(0.4, 0.4), 11.0, 1, 0, "wet"); m.add(whoosh(0.45, 0.45), 11.6, 1, 0, "wet")
    for t in (7.75, 9.95):
        m.add(chorus_lead(hz(81 + tr), 0.12, 0.12), t, 1, 0, "wet"); m.add(chorus_lead(hz(86 + tr), 0.2, 0.12), t + 0.08, 1, 0, "wet")
    for i, ts in enumerate(np.arange(1.55, 14.0, S16)):
        b = int((ts - 1.55) // 2.0) % 4; st = i % 16
        if st in (0, 6, 10): m.add(kick(0.75), ts); kicks.append(ts)
        if st in (4, 12): m.add(clap(0.32), ts, 1, 0, "wet")
        if st % 2: m.add(hat(0.03), ts, 1, 0.3)
        if st in (0, 3, 6, 10, 13): m.add(fm_bass(hz(RT[b] + tr + (12 if st in (3, 13) else 0)), 0.18, 0.42, 0.9), ts, 1, 0, "duck")
        if st in (2, 7, 10, 15): m.add(piano([hz(n + tr) for n in CH[b][1:]], 0.25, 0.07), ts, 1, (st % 3 - 1) * 0.3, "duckwet")
    for t in np.arange(1.55, 14.0, 2.0): pass
    m.add(strings([hz(n + tr) for n in (62, 66, 69, 74)], 2.2, 0.06, 0.05), 14.0, 1, 0, "wet")
    m.add(fm_bass(hz(38 + tr), 1.2, 0.5, 0.3), 14.0); m.add(kick(0.8), 14.0)
    for k, n in enumerate((69, 74, 78)): m.add(chorus_lead(hz(n + tr), 0.3 if k < 2 else 1.0, 0.12, "saw"), 14.1 + k * 0.18, 1, 0, "wet")
    m.save(f"assets/soundtrack-{key}-raw.wav", kicks); print("ok", key)
for k, tr in (("beer", 0), ("rum", 3), ("whiskey", -2)): build(k, tr)
