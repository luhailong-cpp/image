"""Chroma spill cleanup only: preserve alpha/geometry, sample nearby existing subject colors."""
from pathlib import Path
import json,hashlib,importlib.util,sys
import numpy as np
from PIL import Image
char=Path(__file__).resolve().parent
narrow='--narrow' in sys.argv
def chroma(a):
 return ((a[:,:,0]>180)&(a[:,:,1]<90)&(a[:,:,2]>180)&(a[:,:,3]>0)) if narrow else ((a[:,:,0].astype(int)>a[:,:,1].astype(int)+20)&(a[:,:,2].astype(int)>a[:,:,1].astype(int)+20)&(np.minimum(a[:,:,0],a[:,:,2])>45)&(a[:,:,3]>0))
spec=importlib.util.spec_from_file_location('sprite',Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
directions=['S','SW','W','NW','N','NE','E','SE'];record={'operation':'RGB chroma-spill cleanup from nearest existing non-magenta subject pixel; alpha and geometry unchanged','palette_reason':'Han Xiangzi source has sky-blue/ivory/navy clothing and gold/jade accessories; saturated magenta is backdrop contamination','prior_narrow_cleanup':'processing/edge-cleanup-initial.json','chroma_detection':'r>g+20 and b>g+20 and min(r,b)>45, alpha>0','files':{}}
paths=[char/'portrait.png']+[char/'walk'/d/f'{i:02d}.png' for d in directions for i in range(1,5)]
for p in paths:
 im=Image.open(p).convert('RGBA');a=np.array(im);original=a.copy();m=chroma(a);ys,xs=np.where(m)
 for y,x in zip(ys,xs):
  choices=[]
  for radius in range(1,9):
   y0=max(0,y-radius);y1=min(a.shape[0],y+radius+1);x0=max(0,x-radius);x1=min(a.shape[1],x+radius+1)
   for cy in range(y0,y1):
    for cx in range(x0,x1):
     if not m[cy,cx] and original[cy,cx,3]>=128:choices.append(((cy-y)**2+(cx-x)**2,cy,cx))
   if choices:break
  if not choices:
   vy,vx=np.where((~m)&(original[:,:,3]>=128));dist=(vy-y)**2+(vx-x)**2;k=int(np.argmin(dist));choices=[(int(dist[k]),int(vy[k]),int(vx[k]))]
  _,cy,cx=min(choices);a[y,x,:3]=original[cy,cx,:3]
 assert np.array_equal(a[:,:,3],original[:,:,3])
 assert not np.any(chroma(a))
 Image.fromarray(a).save(p)
 record['files'][p.relative_to(char).as_posix()]={'affected_rgb_pixels':len(ys),'alpha_unchanged':True,'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def compose(frames,cols):
 out=Image.new('RGBA',(cols*512,((len(frames)+cols-1)//cols)*512),(0,0,0,0))
 for i,f in enumerate(frames):out.paste(f,((i%cols)*512,(i//cols)*512))
 return out
out={}
for d in directions:
 frames=[Image.open(char/'walk'/d/f'{i:02d}.png').convert('RGBA') for i in range(1,5)];out[d]=frames
 compose(frames,4).save(char/'walk'/d/'strip.png');sp.save_transparent_gif(frames,char/'walk'/d/'walk.gif',120)
for kind,dirs in {'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}.items():compose([f for d in dirs for f in out[d]],4).save(char/f'walk-{kind}.png')
p=char/'processing/frame-transforms.json';f=json.loads(p.read_text(encoding='utf8'))
for d in directions:
 for i,r in enumerate(f[d],1):r['rgba_sha256']=record['files'][f'walk/{d}/{i:02d}.png']['rgba_sha256'];r['magenta_like_pixels']=0;r['rgb_edge_cleanup']='processing/edge-cleanup.json'
p.write_text(json.dumps(f,indent=2),encoding='utf8')
p=char/'manifest.json';m=json.loads(p.read_text(encoding='utf8'))
for f in m['files']:
 p2=char/f['path'];f.update(sha256=hashlib.sha256(p2.read_bytes()).hexdigest(),bytes=p2.stat().st_size)
m['final_edge_cleanup']='processing/edge-cleanup.json';p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
(char/('processing/edge-cleanup-initial.json' if narrow else 'processing/edge-cleanup.json')).write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({'status':'edge_cleanup_done','affected_rgb_pixels':sum(r['affected_rgb_pixels'] for r in record['files'].values()),'alpha_and_geometry':'unchanged'}))
