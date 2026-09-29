"""Build actual E/NE selected-frame composites and timing metadata, never auto-approve art."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from common import DELIVERY,sha,utc_now
sel=json.loads((DELIVERY/'east-qa/selection-20260928v2.json').read_text(encoding='utf-8'))
out=DELIVERY/'east-qa/complete-20260928v2';out.mkdir(exist_ok=True)
findings=[]
for d in ['E','NE']:
 items=[i for i in sel['items'] if i['direction']==d]
 walk=sorted([i for i in items if i['kind']=='walk'],key=lambda i:i['frame'])
 frames=[Image.open(i['output']).convert('RGBA') for i in walk]
 for i,im in zip(walk,frames):
  a=np.asarray(im)[:,:,3]
  assert im.size==(1024,1024) and a.min()==0 and a.max()==255
  assert max(a[0].max(),a[-1].max(),a[:,0].max(),a[:,-1].max())==0
  assert sha(i['output'])==i['outputSha256']
 assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in frames})==16
 for theme,color in [('light',(242,239,225)),('dark',(25,32,40))]:
  comps=[];sheet=Image.new('RGB',(1600,1680),color);draw=ImageDraw.Draw(sheet)
  for n,im in enumerate(frames):
   comp=Image.new('RGBA',im.size,color+(255,));comp.alpha_composite(im);comp=comp.convert('RGB');comps.append(comp)
   x=n%4*400;y=n//4*420;sheet.paste(comp.resize((400,400),Image.Resampling.LANCZOS),(x,y+20));draw.text((x+6,y+4),f'{d} {n+1:02}',fill='white' if theme=='dark' else 'black')
  sheet.save(out/f'{d}-{theme}-contact.png')
  for group in range(2):
   legs=Image.new('RGB',(1470,1280),color);ld=ImageDraw.Draw(legs)
   for k in range(8):
    n=group*8+k;x=k%3*490;y=k//3*420;legs.paste(comps[n].crop((350,550,840,950)),(x,y+20));ld.text((x+6,y+4),f'{d} {n+1:02} native pixels',fill='white' if theme=='dark' else 'black')
   legs.save(out/f'{d}-{theme}-details-{group+1}.png')
  seam=Image.new('RGB',(1536,420),color);sd=ImageDraw.Draw(seam)
  for j,n in enumerate([15,16,1,2]):
   seam.paste(comps[n-1].resize((384,384),Image.Resampling.LANCZOS),(j*384,30));sd.text((j*384+6,8),f'{d} {n:02}',fill='white' if theme=='dark' else 'black')
  seam.save(out/f'{d}-{theme}-seam.png')
  for size in [256,1024]:
   anim=[im.resize((size,size),Image.Resampling.LANCZOS) if size!=1024 else im for im in comps]
   p=out/f'{d}-{theme}-{size}-30ms.gif';anim[0].save(p,save_all=True,append_images=anim[1:],duration=30,loop=0,disposal=2,optimize=False)
   with Image.open(p) as gif:
    ds=[]
    for k in range(gif.n_frames):gif.seek(k);ds.append(gif.info['duration'])
   assert ds==[30]*16
   findings.append({'file':str(p),'sha256':sha(p),'frames':16,'durationsMs':ds,'cycleMs':sum(ds)})
  idle=Image.open([i for i in items if i['kind']=='idle'][0]['output']).convert('RGBA');canvas=Image.new('RGBA',idle.size,color+(255,));canvas.alpha_composite(idle);canvas.convert('RGB').save(out/f'{d}-{theme}-idle.png')
report={'createdAt':utc_now(),'selectionSha256':sha(DELIVERY/'east-qa/selection-20260928v2.json'),'walkCount':32,'idleCount':2,'pixelAndMetadataChecks':'passed','animations':findings,'artReview':'pending','browserPlayback':'not_performed'}
(out/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
