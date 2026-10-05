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

D=40.0; m=Mix(D)
Am=[110,130.8,164.8]; F=[87.3,110,130.8]; C=[130.8,164.8,196]; G=[98,123.5,146.8]
# S1 hook: low pad + heartbeat, tension
m.add(pad(Am+[220],3.4,0.045),0.0)
for tt in (0.2,1.0,1.8,2.5): m.add(heart(0.55),tt)
m.add(tick(0.4),1.8); m.add(riser(0.8),2.4)
# S2 crunch drop
m.add(crunch(0.45,1.1),3.2); m.add(boom(0.75),3.2); m.add(chime(0.09),4.6)
# groove 100 BPM, 3.2-17 and 18.5-32
b=0.6
prog=[Am,F,C,G]; roots=[55,43.65,65.41,49]
def groove(t0,t1,gain=1.0):
    for i,tt in enumerate(np.arange(t0,t1-1e-6,b/2)):
        bar=int((tt-3.2)//(4*b))%4
        if i%2==0: m.add(kick(0.62*gain),tt)
        if i%4==2: m.add(snare(),tt,0.38*gain)
        m.add(hat(),tt+b/4,0.32*gain,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass(roots[bar],b*0.9),tt,0.7*gain)
    for tt in np.arange(t0,t1-0.1,4*b):
        bar=int((tt-3.2)//(4*b))%4
        m.add(pad(prog[bar]+[c*2 for c in prog[bar]],4*b+0.4,0.03),tt)
groove(3.2,17.0); groove(18.5,32.0)
m.add(whoosh(0.5,0.9),5.75); m.add(chime(0.07),7.0); m.add(boom(0.4),8.3); m.add(chime(0.1),8.35)
m.add(whoosh(0.5,0.8),10.75)
for tt in (11.8,13.2,14.6): m.add(tick(0.45),tt); m.add(crunch(0.15,0.35),tt+0.02); m.add(pluck([659.3],0.4,0.04),tt+0.1)
m.add(riser(0.5),16.5)
# twist: dropout, pad only + single heartbeat
m.add(pad([110,164.8,220,277.2],1.8,0.05),17.0); m.add(heart(0.5),17.2)
for tt in (18.2,22.7,27.2): m.add(whoosh(0.5,0.8),tt)
for tt in (18.9,23.4,27.9): m.add(thud(0.75),tt); m.add(crunch(0.12,0.35),tt+0.02)
for tt in (19.6,24.1,28.6): m.add(clink(),tt,0.6,0.3)
# end
m.add(boom(0.6),32.0); m.add(pad([110,164.8,220,277.2],4.5,0.05),32.0); m.add(pad([87.3,130.8,174.6,220],4.0,0.045),36.0)
for k,tt in enumerate((32.2,32.32,32.44)): m.add(thud(0.7),tt,1,(k-1)*0.4)
m.add(tick(0.4),33.6); m.add(chime(0.12),35.0); m.add(clink(),35.6,0.6)
m.save('hyperframes/assets/soundtrack_raw.wav')
