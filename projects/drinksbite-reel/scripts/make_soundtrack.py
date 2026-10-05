# Original procedural soundtrack: 120 BPM groove + pop/crunch/clink SFX synced to the edit.
import numpy as np, wave
SR=44100; DUR=15.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig)); s=sig[:j-i]*gain
    L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
def env(n,a=0.002,d=0.2):
    t=np.arange(n)/SR; e=np.minimum(1,t/a)*np.exp(-t/d); return e
def kick():
    n=int(0.45*SR); t=np.arange(n)/SR
    f=45+110*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env(n,0.001,0.18)*1.0
def hat(open_=False):
    n=int((0.18 if open_ else 0.05)*SR); x=rng.standard_normal(n)
    x=np.diff(np.concatenate([[0],x]))  # crude highpass
    return x*env(n,0.0005,0.06 if open_ else 0.012)*0.25
def clap():
    n=int(0.25*SR); x=rng.standard_normal(n); e=np.zeros(n)
    for k in (0,0.01,0.02): e+=env(n,0.0005,0.012)*np.roll(np.ones(n),int(k*SR))*(np.arange(n)>=int(k*SR))
    e+=env(n,0.001,0.08)*0.6
    x=x-np.concatenate([[0],x[:-1]])*0.5
    return x*e*0.35
def bass(freq,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    s=np.sign(np.sin(2*np.pi*freq*t))*0.4+np.sin(2*np.pi*freq*t)
    # simple lowpass
    k=np.exp(-2*np.pi*400/SR); y=np.zeros(n); acc=0
    for i in range(n): acc=acc*k+s[i]*(1-k); y[i]=acc
    return y*env(n,0.004,dur*0.7)*0.45
def pluck(freqs,dur=0.35):
    n=int(dur*SR); t=np.arange(n)/SR; s=sum(np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t) for f in freqs)
    return s*env(n,0.002,0.12)*0.09
def pop():
    n=int(0.18*SR); t=np.arange(n)/SR
    f=900*np.exp(-t*28)+180; s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.0005,0.05)
    s[:int(0.004*SR)]+=rng.standard_normal(int(0.004*SR))*0.6
    return s*0.9
def crunch(d=0.22):
    n=int(d*SR); x=rng.standard_normal(n); g=(rng.random(n)<0.02).astype(float)
    g=np.convolve(g,np.ones(int(0.004*SR)),'same')
    return x*np.clip(g,0,1)*env(n,0.001,d/2.5)*0.45
def clink():
    n=int(1.6*SR); t=np.arange(n)/SR
    s=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*dk) for f,a,dk in [(2637,1,3.0),(3951,0.6,4),(5274,0.4,5),(6645,0.25,6)])
    return s*0.18
def riser(d):
    n=int(d*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    x=x-np.concatenate([[0],x[:-1]])*0.9
    return x*(t/d)**2*0.12
BEAT=0.5
# Hook (0-1.5): sparse hits on word slams
for t in (0.0,0.5,1.0): add(kick(),t,1.0)
add(riser(1.5),0.0)
add(clap(),1.0,0.8)
# Groove from 1.5 to 14.0
A,C,D,E,G=55.0,65.41,73.42,82.41,98.0
bassline=[A,A,C,A,D,A,E,G]
for i,t in enumerate(np.arange(1.5,14.0,BEAT)):
    add(kick(),t,0.95)
    add(hat(),t+0.25,1,0.3)
    if i%2==1: add(clap(),t,0.9,-0.1)
    add(hat(open_=(i%4==3)),t+0.125,0.5,-0.3)
    add(bass(bassline[i%8],0.45),t,1.0)
    if i%4 in (0,2): add(pluck([220,261.6,329.6] if (i//4)%2==0 else [196,246.9,293.7]),t+0.25,1.0,0.2)
# Pack hits: pop + crunch
for t in (3.0,5.5,8.0): add(pop(),t,1.0); add(crunch(),t+0.06,1.0)
for k,t in enumerate((10.5,10.75,11.0)): add(pop(),t,0.8,(k-1)*0.4)
add(crunch(0.4),12.5,1.0)
# End: drop groove, clink sting
add(kick(),14.0,1.0); add(clink(),13.0,1.0)
mix=np.stack([L,R],1)
# fade last 0.3s
f=int(0.3*SR); mix[-f:]*=np.linspace(1,0,f)[:,None]
mix/=np.max(np.abs(mix))*1.12
pcm=(mix*32767).astype('<i2')
w=wave.open('assets/music/drinksbite_groove.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('ok')
