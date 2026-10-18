from workflow import *
from PIL import Image
tid='r14_c13';rev='right-full-20261016-v02';overlays=[]
for rc in ['13','14']:
 f=ROOT/'native'/f'{tid}_p{rc}_v02.png';c=int(rc[1]);sx,sy,sx1,sy1=850,115,1139,450;x=(c-1)*1024+sx-115;y=0
 overlays.append({'file':str(f),'sha256':sha(f),'sourceCrop':[sx,sy,sx1,sy1],'destinationBox':[x,y,x+sx1-sx,y+sy1-sy]})
f=ROOT/'native/r14_c13_repair_j22_v01.png'
overlays.append({'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destinationBox':[1536,1536,2560,2560]})
m=ROOT/'qa'/f'{tid}-{rev}.overlays.json';write(m,{'tile':tid,'overlays':overlays})
write(ROOT/'qa'/f'{tid}-{rev}.spec.json',{'tile':tid,'patchVersions':{f'{r}{c}':'v01' for r in range(1,5) for c in range(1,5)},'overlayManifests':[str(m)]})
print('Three exact world-registered source rectangles prepared.')

