# Original sound design for "Meet the 3 Bites": dark ambient bed, 100 BPM pulse,
# whooshes into each reveal, pack rustle + crunch, USP ticks, deep impact on line-up, clink sting.
import numpy as np, wave
SR=44100; DUR=15.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(3)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig)); s=sig[:j-i]*g
    L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
def env(n,a=0.002,d=0.2):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
def lp(x,fc):
    k=np.broadcast_to(np.exp(-2*np.pi*np.asarray(fc,float)/SR),x.shape); y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc=acc*k[i]+x[i]*(1-k[i]); y[i]=acc
    return y
def kick(g=1.0):
    n=int(0.5*SR); t=np.arange(n)/SR; f=40+90*np.exp(-t*25)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.22)*g
def hat():
    n=int(0.04*SR); x=rng.standard_normal(n); x=np.diff(np.concatenate([[0],x])); return x*env(n,0.0005,0.01)*0.12
def whoosh(d=0.45):
    n=int(d*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    x=lp(x,300+5000*(t/d)**2)  # opening filter sweep
    return x*np.sin(np.pi*t/d)**2*1.6
def rustle(d=0.3):
    n=int(d*SR); x=rng.standard_normal(n); g=(rng.random(n)<0.06).astype(float)
    g=np.convolve(g,np.hanning(int(0.003*SR)),'same'); x=x-np.concatenate([[0],x[:-1]])
    return x*np.clip(g,0,1)*env(n,0.01,d/2)*0.35
def crunch(d=0.25):
    n=int(d*SR); x=rng.standard_normal(n); g=(rng.random(n)<0.025).astype(float)
    g=np.convolve(g,np.ones(int(0.004*SR)),'same'); return x*np.clip(g,0,1)*env(n,0.001,d/2.5)*0.4
def tick():
    n=int(0.06*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*1800*t)*env(n,0.0005,0.012)*0.35
def boom():
    n=int(2.2*SR); t=np.arange(n)/SR; f=32+60*np.exp(-t*6)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.9)
    s+=lp(rng.standard_normal(n),180)*env(n,0.002,0.25)*2.0
    return s*1.1
def clink():
    n=int(1.8*SR); t=np.arange(n)/SR
    return sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*k) for f,a,k in [(2637,1,2.6),(3951,.6,3.5),(5274,.35,4.5),(6645,.2,5.5)])*0.16
# ambient bed: A1 + E2 drone with slow swell, plus filtered air
t=np.arange(N)/SR
bed=(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.41*t)+0.25*np.sin(2*np.pi*110*t+np.sin(2*np.pi*0.2*t)))
bed*=0.16*(0.55+0.45*np.sin(np.pi*np.clip(t/DUR,0,1)))
air=lp(rng.standard_normal(N),900)*0.05
L+=bed+air; R+=bed+air*0.9
# intro heartbeat
add(kick(0.7),0.15); add(kick(0.9),0.95); add(whoosh(0.5),1.35)
# pulse 100 BPM from first reveal to USP end
beat=0.6
for i,tt in enumerate(np.arange(1.8,11.6,beat)):
    add(kick(0.75),tt); add(hat(),tt+0.3,1,0.3)
    if i%2: add(hat(),tt+0.15,0.6,-0.3)
# reveals
for tt in (1.8,4.0,6.2):
    if tt>1.8: add(whoosh(),tt-0.4)
    add(rustle(),tt+0.02,1,-0.2); add(crunch(),tt+0.12,1,0.2)
add(whoosh(),8.0)
# USP ticks
for k in range(6): add(tick(),8.75+k*0.42,1,(-1)**k*0.3)
# line-up impact and sting
add(whoosh(0.6),11.2); add(boom(),11.8); add(crunch(0.35),11.85)
add(clink(),13.4)
mix=np.stack([L,R],1); f=int(0.5*SR); mix[-f:]*=np.linspace(1,0,f)[:,None]
mix/=np.max(np.abs(mix))*1.12
w=wave.open('assets/music/meet_the_3_bites.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix*32767).astype('<i2').tobytes()); w.close(); print('ok')
