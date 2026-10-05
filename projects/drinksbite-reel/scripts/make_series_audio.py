# Original soundtracks for the DrinksBite reference-driven series.
import numpy as np, wave, sys
SR=44100
rng=np.random.default_rng(11)
def env(n,a=0.002,d=0.2):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
def lp(x,fc):
    k=np.broadcast_to(np.exp(-2*np.pi*np.asarray(fc,float)/SR),x.shape); y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc=acc*k[i]+x[i]*(1-k[i]); y[i]=acc
    return y
def kick(g=1.0):
    n=int(0.45*SR); t=np.arange(n)/SR; f=45+100*np.exp(-t*28)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.18)*g
def snare():
    n=int(0.22*SR); x=rng.standard_normal(n); x=x-np.concatenate([[0],x[:-1]])*0.6
    t=np.arange(n)/SR; body=np.sin(2*np.pi*190*t)*env(n,0.001,0.04)
    return (x*env(n,0.001,0.06)*0.35+body*0.4)
def clap():
    n=int(0.25*SR); x=rng.standard_normal(n); e=np.zeros(n)
    for k in (0,0.011,0.022):
        i=int(k*SR); e[i:]+=env(n-i,0.0005,0.012)
    e+=env(n,0.001,0.07)*0.6; x=x-np.concatenate([[0],x[:-1]])*0.5
    return x*e*0.32
def hat(o=False):
    n=int((0.16 if o else 0.045)*SR); x=rng.standard_normal(n); x=np.diff(np.concatenate([[0],x]))
    return x*env(n,0.0005,0.05 if o else 0.011)*0.2
def bass(f,d):
    n=int(d*SR); t=np.arange(n)/SR; s=np.sin(2*np.pi*f*t)+0.35*np.sign(np.sin(2*np.pi*f*t))
    return lp(s,500)*env(n,0.004,d*0.6)*0.5
def pluck(fs,d=0.3,g=0.09):
    n=int(d*SR); t=np.arange(n)/SR
    return sum(np.sin(2*np.pi*f*t)*np.exp(-t*9)+0.3*np.sin(4*np.pi*f*t)*np.exp(-t*14) for f in fs)*g
def whoosh(d=0.4,g=1.0):
    n=int(d*SR); t=np.arange(n)/SR; x=lp(rng.standard_normal(n),300+6000*(t/d)**2)
    return x*np.sin(np.pi*t/d)**2*1.6*g
def riser(d):
    n=int(d*SR); t=np.arange(n)/SR; x=lp(rng.standard_normal(n),200+7000*(t/d)**3)
    return x*(t/d)**2*1.4
def crunch(d=0.25,g=0.45):
    n=int(d*SR); x=rng.standard_normal(n); gg=(rng.random(n)<0.03).astype(float)
    gg=np.convolve(gg,np.ones(int(0.004*SR)),'same'); return x*np.clip(gg,0,1)*env(n,0.001,d/2.5)*g
def tear(d=0.35):
    n=int(d*SR); x=rng.standard_normal(n); gg=(rng.random(n)<0.12).astype(float)
    gg=np.convolve(gg,np.hanning(int(0.002*SR)),'same'); t=np.arange(n)/SR
    return lp(x,4000)*np.clip(gg,0,1)*np.minimum(1,t/0.02)*np.exp(-t/0.25)*1.2
def pop():
    n=int(0.2*SR); t=np.arange(n)/SR; f=800*np.exp(-t*26)+160
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.0005,0.05); s[:int(0.004*SR)]+=rng.standard_normal(int(0.004*SR))*0.6
    return s
def boom(g=1.0):
    n=int(2.0*SR); t=np.arange(n)/SR; f=32+60*np.exp(-t*6)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.8)+lp(rng.standard_normal(n),180)*env(n,0.002,0.25)*2)*g
def chime(g=0.12):
    n=int(1.6*SR); t=np.arange(n)/SR
    return sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*k) for f,a,k in [(1568,1,2.5),(2349,.6,3),(3136,.4,4),(4699,.25,5)])*g
def clink(): return chime(0.15)
def dust(d=0.8):
    n=int(d*SR); x=lp(rng.standard_normal(n),2500); t=np.arange(n)/SR
    return x*np.exp(-t/0.25)*np.minimum(1,t/0.01)*1.2
def pad(fs,d,g=0.06):
    n=int(d*SR); t=np.arange(n)/SR; s=sum(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*2.003*t) for f in fs)
    return s*np.minimum(1,t/0.4)*np.minimum(1,(d-t)/0.6)*g
class Mix:
    def __init__(s,dur): s.N=int(SR*dur); s.L=np.zeros(s.N); s.R=np.zeros(s.N)
    def add(s,sig,t,g=1.0,pan=0.0):
        i=int(t*SR)
        if i>=s.N: return
        j=min(s.N,i+len(sig)); x=sig[:j-i]*g
        s.L[i:j]+=x*(1-max(0,pan)); s.R[i:j]+=x*(1+min(0,pan))
    def save(s,path):
        m=np.stack([s.L,s.R],1); f=int(0.4*SR); m[-f:]*=np.linspace(1,0,f)[:,None]
        m/=np.max(np.abs(m))*1.12
        w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m*32767).astype('<i2').tobytes()); w.close()

def reel1():  # Three Moods: funky 112 BPM
    D=11.0; m=Mix(D); b=60/112
    A,C,D_,E,G=55.0,65.41,73.42,82.41,98.0; line=[A,A,C,A,D_,A,E,G]
    for i,t in enumerate(np.arange(0,9.4,b/2)):
        if i%2==0: m.add(kick(0.95),t)
        if i%4==2: m.add(clap(),t,0.9)
        m.add(hat(i%8==7),t+b/4,0.8,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass(line[(i//2)%8],b*0.9),t)
        if i%4 in (1,3): m.add(pluck([440,523.3,659.3] if (i//8)%2==0 else [392,493.9,587.3],0.25),t,1,0.2)
    for t in (1.85,3.85,5.85): m.add(whoosh(0.35),t-0.1)
    for k,t in enumerate((6.05,6.3,6.55)): m.add(pop(),t,0.7,(k-1)*0.4)
    m.add(whoosh(0.45),9.2); m.add(boom(0.8),9.4); m.add(clink(),9.7)
    m.save('series/reel1.wav')

def reel2():  # Inside the Bite: dark cinematic, ASMR foley
    D=15.0; m=Mix(D); t=np.arange(m.N)/SR
    drone=(np.sin(2*np.pi*41.2*t)+0.5*np.sin(2*np.pi*61.7*t))*0.12; m.L+=drone; m.R+=drone
    m.add(tear(),0.25); m.add(dust(0.9),0.5,0.6); m.add(riser(0.9),0.45)
    m.add(whoosh(1.7,1.4),1.25); m.add(riser(1.4),1.5,0.8)
    m.add(boom(0.6),3.0); m.add(chime(0.08),3.1)
    for i,tt in enumerate(np.arange(3.0,8.4,0.5)):
        m.add(kick(0.8),tt); m.add(hat(),tt+0.25,0.7)
    m.add(pop(),4.55,1.2); m.add(boom(0.4),4.55)
    m.add(whoosh(0.3),5.75); m.add(dust(1.0),5.85,1.0); m.add(boom(0.5),5.85)
    m.add(crunch(0.35,0.9),7.3); m.add(pop(),7.3,0.6); m.add(chime(0.14),7.32)
    m.add(pad([220,277.2,329.6],2.2,0.05),8.4)
    for tt in (8.4,9.0,9.6): m.add(whoosh(0.25,0.6),tt-0.08)
    m.add(clink(),9.7)
    m.add(riser(0.6),9.8); m.add(boom(0.9),10.4); m.add(crunch(0.3),10.45)
    m.add(pad([220,277.2,329.6,440],4.4,0.07),10.4)
    for k in range(10): m.add(crunch(0.08,0.15),10.6+k*0.22,1,(-1)**k*0.5)
    m.add(chime(0.16),13.05)
    m.save('series/reel2.wav')

def reel3():  # Pick Your Pour: groovy 100 BPM
    D=12.0; m=Mix(D); b=0.6
    for i,tt in enumerate(np.arange(0,10.8,b/2)):
        if i%2==0: m.add(kick(0.9),tt)
        if i%4==2: m.add(snare(),tt,0.9)
        m.add(hat(),tt+b/4,0.7,0.3 if i%2 else -0.3)
        if i%2==0: m.add(bass([49,49,58.27,65.41][(i//4)%4],b*0.9),tt)
        if i%8==4: m.add(pluck([392,466.2,587.3],0.35,0.08),tt)
    for tt in (0.2,0.5,0.8,1.1): m.add(kick(0.6),tt)
    for tt in (1.5,4.0,6.5): m.add(whoosh(0.3),tt-0.12); m.add(clink(),tt+0.35)
    for tt in (2.0,4.5,7.0): m.add(crunch(0.25,0.6),tt)
    m.add(whoosh(0.4),8.88); m.add(boom(0.7),9.0)
    for k,tt in enumerate((9.15,9.35,9.55)): m.add(pop(),tt,0.6,(k-1)*0.5)
    m.add(chime(0.12),10.3)
    m.save('series/reel3.wav')

if __name__ == "__main__":
    for f in sys.argv[1:]: globals()[f](); print("ok", f)
