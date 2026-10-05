# Original sound design for DrinksBite series v2 (restrained, tactile).
import sys, numpy as np
sys.path.insert(0, 'scripts')
from make_series_audio import *  # primitives: Mix, kick, snare, clap, hat, bass, pluck, whoosh, riser, crunch, tear, pop, boom, chime, clink, dust, pad, lp, env, SR, rng

def tick():
    n=int(0.05*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*2200*t)*env(n,0.0005,0.01)*0.3
def hit(g=1.0):
    return boom(0.55*g)[:int(0.7*SR)] + np.pad(crunch(0.18, 0.5*g), (0, int(0.7*SR) - int(0.18*SR)))
def thud(g=0.8):
    n=int(0.25*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(70+60*np.exp(-t*35))/SR)*env(n,0.001,0.06)*g
def murmur(d):
    n=int(d*SR); x=lp(rng.standard_normal(n),700); t=np.arange(n)/SR
    return x*(0.6+0.4*np.sin(2*np.pi*0.7*t))*0.25
def slate(m, t0):
    m.add(boom(0.5), t0); m.add(pad([110,164.8,220,277.2], 3.0, 0.045), t0)
    for k,tt in enumerate((0.35,0.47,0.59)): m.add(thud(0.7), t0+tt, 1, (k-1)*0.4)
    m.add(clink(), t0+1.1)

def r1():
    m=Mix(12.0)
    for k,tt in enumerate((0.0,0.3,0.6,0.9)): m.add(hit(0.9 if k<3 else 1.1), tt, 1, (-1)**k*0.15)
    m.add(whoosh(0.45,0.8),1.15); m.add(pluck([220,277.2,329.6],0.6,0.07),1.45)
    m.add(riser(0.5),1.95); m.add(boom(0.7),2.4)
    b=0.5
    for i,tt in enumerate(np.arange(2.4,9.0,b/2)):
        if i%2==0: m.add(kick(0.75),tt)
        if i%4==2: m.add(snare(),tt,0.55)
        m.add(hat(),tt+b/4,0.5,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass([55,55,65.41,49][(i//8)%4],b*0.9),tt,0.8)
    for tt in (4.55,6.75): m.add(whoosh(0.5,0.9),tt-0.3)
    for tt in (2.6,4.8,7.0): m.add(crunch(0.2,0.35),tt)
    slate(m,9.0); m.save('series-v2/r1.wav')

def r2():
    m=Mix(12.0); t=np.arange(m.N)/SR
    drone=np.sin(2*np.pi*41.2*t)*0.09; m.L+=drone; m.R+=drone
    for k in range(10): m.add(tick(),0.3+k*0.045,0.6)            # type-on THIS IS NOT
    for k in range(6): m.add(tick(),0.85+k*0.045,0.6)             # A CHIP.
    m.add(crunch(0.4,1.0),1.5); m.add(boom(0.6),1.5)              # IT'S POPPED JOWAR
    for i,tt in enumerate(np.arange(1.5,9.0,0.55)):
        m.add(kick(0.6),tt); m.add(hat(),tt+0.275,0.4)
    for tt in (2.9,4.2,5.5,6.8): m.add(whoosh(0.3,0.6),tt-0.1); m.add(thud(0.5),tt+0.08)
    for k,tt in enumerate((8.1,8.25,8.4)): m.add(whoosh(0.25,0.5),tt-0.05,1,(k-1)*0.5)
    m.add(clink(),8.5)
    slate(m,9.0); m.save('series-v2/r2.wav')

def r3():
    m=Mix(12.5)
    mm=murmur(12.5); m.L+=mm[:m.N]*0.8; m.R+=mm[:m.N]*0.7
    for tt in (0.4,3.6,6.4): m.add(clink(),tt,0.5,0.3)
    b=0.6
    for i,tt in enumerate(np.arange(0,9.3,b/2)):
        if i%2==0: m.add(kick(0.55),tt)
        if i%4==2: m.add(snare(),tt,0.4)
        m.add(hat(),tt+b/4,0.35)
    m.add(whoosh(0.35,0.5),1.25); m.add(crunch(0.35,1.0),1.62); m.add(thud(0.6),1.62)   # puff lands
    for tt in (2.95,5.75): m.add(whoosh(0.6,1.1),tt)                                   # pans along the bar
    for tt in (3.9,6.7): m.add(thud(0.8),tt); m.add(crunch(0.15,0.4),tt+0.02)          # pack set down
    m.add(whoosh(0.5,0.8),9.05)
    slate(m,9.5); m.save('series-v2/r3.wav')


def squeak(d=0.25):
    # felt-marker stroke: band-passed noise with a slight pitch sweep
    n=int(d*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    x=lp(x,2600)-lp(x,900); return x*np.sin(np.pi*t/d)*0.9

def r2b():
    m=Mix(12.0); t=np.arange(m.N)/SR
    drone=np.sin(2*np.pi*41.2*t)*0.08; m.L+=drone; m.R+=drone
    m.add(hit(1.0),0.08)                                         # "wait."
    for k in range(17): m.add(tick(),0.32+k*0.042,0.55)          # typing
    m.add(squeak(0.4),0.7); m.add(squeak(0.22),0.95,0.8)         # circle + arrow
    m.add(crunch(0.4,1.0),1.5); m.add(boom(0.5),1.5)
    m.add(squeak(0.25),1.82,1.1); m.add(thud(0.9),2.06); m.add(crunch(0.15,0.4),2.07)
    for i,tt in enumerate(np.arange(1.5,9.0,0.55)):
        m.add(kick(0.6),tt); m.add(hat(),tt+0.275,0.4)
    for tt in (2.9,4.2,5.5,6.8):
        m.add(whoosh(0.3,0.6),tt-0.1); m.add(squeak(0.3),tt+0.5,0.9); m.add(thud(0.6),tt+0.9)
    for k,tt in enumerate((8.1,8.25,8.4)): m.add(whoosh(0.25,0.5),tt-0.05,1,(k-1)*0.5)
    m.add(clink(),8.5)
    slate(m,9.0); m.save('series-v2/r2b.wav')

def r2c():
    # calm and confident: warm pad, soft heartbeat pulse, minimal ticks
    m=Mix(12.0)
    for t0,ch in ((0.0,[110,138.6,164.8]),(3.0,[98,123.5,146.8]),(6.4,[87.3,110,130.8])):
        m.add(pad(ch+[c*2 for c in ch],3.4,0.05),t0)
    for tt in np.arange(0.0,9.0,0.8): m.add(kick(0.45),tt)
    for k,tt in enumerate((0.15,0.47)): m.add(pluck([440,554.4] if k==0 else [493.9,659.3],0.6,0.05),tt)
    m.add(tick(),1.25,0.7); m.add(tick(),1.7,0.6); m.add(crunch(0.25,0.5),1.95)
    m.add(whoosh(0.5,0.6),2.75)
    for tt in (3.4,4.0,4.6): m.add(tick(),tt,0.8); m.add(pluck([659.3],0.4,0.04),tt+0.12)
    m.add(whoosh(0.5,0.6),6.15); m.add(clink(),6.85)
    slate(m,9.0); m.save('series-v2/r2c.wav')

for f in sys.argv[1:]: globals()[f](); print("ok", f)
