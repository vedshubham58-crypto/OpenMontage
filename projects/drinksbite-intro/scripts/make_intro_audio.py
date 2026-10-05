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

D=33.0; m=Mix(D)
Am=[110,130.8,164.8]; F=[87.3,110,130.8]; C=[130.8,164.8,196]; G=[98,123.5,146.8]
# H hook 0-2.7: three colour slashes = three hits, then pulse under the type
for k,tt in enumerate((0.0,0.07,0.14)): m.add(thud(0.9),tt,1,(k-1)*0.5); m.add(crunch(0.1,0.4),tt,1,(k-1)*0.5)
m.add(whoosh(0.35,0.8),0.33)
m.add(pad(Am+[220],2.9,0.045),0.4)
for tt in (0.5,1.0,1.45,1.95): m.add(heart(0.55),tt)
m.add(tick(0.4),1.42); m.add(riser(0.6),2.1)
b=0.5; prog=[Am,F,C,G]; roots=[55,43.65,65.41,49]
def groove(t0,t1):
    for i,tt in enumerate(np.arange(t0,t1-1e-6,b/2)):
        bar=int((tt-2.7)//(4*b))%4
        if i%2==0: m.add(kick(0.62),tt)
        if i%4==2: m.add(snare(),tt,0.4)
        m.add(hat(),tt+b/4,0.32,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass(roots[bar],b*0.9),tt,0.7)
    for tt in np.arange(t0,t1-0.1,4*b):
        bar=int((tt-2.7)//(4*b))%4
        m.add(pad(prog[bar]+[c*2 for c in prog[bar]],4*b+0.3,0.03),tt)
groove(2.7,14.2); groove(15.7,26.2)
m.add(boom(0.75),2.7)
for k,tt in enumerate((2.92,3.0,3.08)): m.add(thud(0.6),tt,1,(k-1)*0.4)
m.add(chime(0.1),3.8); m.add(chime(0.07),4.2)
m.add(whoosh(0.3,0.8),6.45); m.add(thud(0.7),6.6); m.add(whoosh(0.3,0.8),8.05); m.add(thud(0.7),8.2)
m.add(crunch(0.4,1.0),9.8); m.add(boom(0.5),9.8); m.add(whoosh(0.55,0.9),10.85)
for tt in (11.25,12.15,13.05): m.add(tick(0.45),tt); m.add(crunch(0.12,0.35),tt+0.02); m.add(pluck([659.3],0.35,0.04),tt+0.08)
m.add(riser(0.5),13.7)
m.add(pad([110,164.8,220,277.2],1.6,0.05),14.2); m.add(heart(0.5),14.3); m.add(chime(0.08),14.6)
for tt in (15.45,18.7,22.2): m.add(whoosh(0.45,0.8),tt)
for tt in (15.85,19.4,22.9): m.add(thud(0.75),tt); m.add(crunch(0.12,0.35),tt+0.02)
for tt in (16.3,19.85,23.35): m.add(clink(),tt,0.6,0.3)
m.add(boom(0.6),26.2); m.add(pad([110,164.8,220,277.2],3.0,0.05),26.2); m.add(pad([87.3,130.8,174.6,220],4.6,0.045),28.7)
for k,tt in enumerate((26.45,26.53,26.61)): m.add(thud(0.7),tt,1,(k-1)*0.4)
m.add(tick(0.4),27.6); m.add(chime(0.12),28.7); m.add(clink(),29.1,0.6)
m.save('hyperframes/assets/soundtrack_raw.wav')
