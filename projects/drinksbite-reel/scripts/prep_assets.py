from PIL import Image, ImageFilter
import numpy as np, shutil
from scipy import ndimage
P='projects/drinksbite-reel/'
B=P+'assets/brand/'
O=P+'hyperframes/assets/'
S='/tmp/claude-0/-home-user-OpenMontage/15f1c238-6ff4-51a5-9c2a-a8cdfaecc234/scratchpad/'
for src,name in [('08_a98cfd26.jpg','pack-beer'),('10_238b00f1.jpg','pack-rum'),('12_f887069b.jpg','pack-whiskey')]:
    im=Image.open(B+src).convert('RGB'); a=np.asarray(im).astype(int)
    bright=(a.min(axis=2)>200)&((a.max(axis=2)-a.min(axis=2))<25)
    lab,n=ndimage.label(bright)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(border))
    fg=ndimage.binary_fill_holes(fg)
    fg=ndimage.binary_opening(fg,iterations=2)
    alpha=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))
    out=im.copy(); out.putalpha(alpha)
    out=out.crop(out.getbbox()); out.save(O+name+'.png'); print(name,out.size)
for src,name in [('13_f221685c.jpg','pour-beer'),('14_c5495eca.jpg','pour-rum'),('15_2965c86a.jpg','pour-whiskey')]:
    im=Image.open(B+src).convert('RGB'); w,h=im.size; cw=int(h*1080/1920); x0=(w-cw)//2
    im.crop((x0,0,x0+cw,h)).resize((1080,1920),Image.LANCZOS).save(O+name+'.jpg',quality=92)
for src,name in [('16_0ee2155d.jpg','bowl-beer'),('17_09b5bf0c.jpg','bowl-whiskey'),('18_f1fb5446.jpg','bowl-rum'),('19_1de023d6.jpg','bowl-hero')]:
    shutil.copy(B+src,O+name+'.jpg')
shutil.copy(B+'05_851adc87.png',O+'pattern.png')
shutil.copy(B+'07_300df5fc.svg',O+'logo.svg')
for src,name in [('01_ff8d17cf.ttf','geometr.ttf'),('02_226efac6.ttf','aprilio.ttf'),('03_55a42921.ttf','bernard.ttf'),('04_6f2885d8.ttf','berlin.ttf')]:
    shutil.copy(B+src,O+name)
c=Image.new('RGB',(1500,720),(40,120,40))
for i,n in enumerate(['pack-beer','pack-rum','pack-whiskey']):
  im=Image.open(O+n+'.png'); im.thumbnail((480,700)); c.paste(im,(i*500,0),im)
c.save(S+'cut.jpg')
p=Image.new('RGB',(810,480))
for i,n in enumerate(['pour-beer','pour-rum','pour-whiskey']):
  im=Image.open(O+n+'.jpg'); im.thumbnail((270,480)); p.paste(im,(i*270,0))
p.save(S+'pours.jpg')
