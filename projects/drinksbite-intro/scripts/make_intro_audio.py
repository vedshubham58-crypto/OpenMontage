# Original sound design for the DrinksBite brand intro film (40 s). Run from projects/drinksbite-intro.
import sys, numpy as np
sys.path.insert(0, '../drinksbite-reel/scripts')
from make_series_audio import Mix, kick, snare, hat, bass, pluck, whoosh, riser, crunch, boom, chime, clink, pad, lp, env, SR, rng

def tick(g=0.3):
    n=int(0.05*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*2200*t)*env(n,0.0005,0.01)*g
def thud(g=0.8):
    n=int(0.25*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(70+60*np.exp(-t*35))/SR)*env(n,0.001,0.06)*g
def heart(g=0.6):  # soft lub-dub
    return thud(g) + np.pad(thud(g*0.6), (int(0.16*SR), 0))[:int(0.25*SR)]

D=31.0; m=Mix(D)
Am=[110,130.8,164.8]; F=[87.3,110,130.8]; C=[130.8,164.8,196]; G=[98,123.5,146.8]
# S1 hook 0-2.5: pad + double-time heartbeat, riser into the cut
m.add(pad(Am+[220],2.7,0.045),0.0)
for tt in (0.05,0.75,1.25,1.75): m.add(heart(0.55),tt)
m.add(tick(0.4),1.28); m.add(riser(0.7),1.8)
# 120 BPM groove: 2.5-12.0 and 13.5-24.0
b=0.5; prog=[Am,F,C,G]; roots=[55,43.65,65.41,49]
def groove(t0,t1):
    for i,tt in enumerate(np.arange(t0,t1-1e-6,b/2)):
        bar=int((tt-2.5)//(4*b))%4
        if i%2==0: m.add(kick(0.62),tt)
        if i%4==2: m.add(snare(),tt,0.4)
        m.add(hat(),tt+b/4,0.32,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass(roots[bar],b*0.9),tt,0.7)
    for tt in np.arange(t0,t1-0.1,4*b):
        bar=int((tt-2.5)//(4*b))%4
        m.add(pad(prog[bar]+[c*2 for c in prog[bar]],4*b+0.3,0.03),tt)
groove(2.5,12.0); groove(13.5,24.0)
# pack reveal + punches
m.add(boom(0.75),2.5); m.add(whoosh(0.35,0.7),2.3); m.add(chime(0.08),2.8)
for tt in (4.0,5.5): m.add(whoosh(0.25,0.8),tt-0.2); m.add(thud(0.8),tt)
m.add(chime(0.07),4.35)
# puff macro + pull back
m.add(crunch(0.4,1.0),7.5); m.add(boom(0.5),7.5); m.add(whoosh(0.6,0.9),8.35)
for tt in (9.05,10.0,10.95): m.add(tick(0.45),tt); m.add(crunch(0.12,0.35),tt+0.02); m.add(pluck([659.3],0.35,0.04),tt+0.08)
m.add(riser(0.5),11.5)
# twist: dropout
m.add(pad([110,164.8,220,277.2],1.7,0.05),12.0); m.add(heart(0.5),12.1)
for tt in (13.3,16.4,19.9): m.add(whoosh(0.45,0.8),tt)
for tt in (13.75,17.3,20.8): m.add(thud(0.75),tt); m.add(crunch(0.12,0.35),tt+0.02)
for tt in (14.2,17.75,21.25): m.add(clink(),tt,0.6,0.3)
# end
m.add(boom(0.6),24.0); m.add(pad([110,164.8,220,277.2],3.5,0.05),24.0); m.add(pad([87.3,130.8,174.6,220],4.0,0.045),27.0)
for k,tt in enumerate((24.05,24.15,24.25)): m.add(thud(0.7),tt+0.2,1,(k-1)*0.4)
m.add(tick(0.4),25.4); m.add(chime(0.12),26.5); m.add(clink(),27.0,0.6)
m.save('hyperframes/assets/soundtrack_raw.wav')
