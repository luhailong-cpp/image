from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;T=D.parent.parent;O=D/'trial-v2';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
base=T/'candidate/r16_c16-4k-candidate-101a9801efaf54800416.png';ctx=T/'candidate/r16_c16-context-4326-101a9801efaf54800416.png'
old=np.array(Image.open(base).convert('RGB'));out=old.copy();occupied=np.zeros((4096,4096),bool);ops=[]
for key,y,poly in [('upper',1320,[(425,650),(1254,170),(1254,760),(425,1220)]),('lower',2100,[(425,550),(1254,-10),(1254,600),(425,1150)])]:
 r=json.loads((D/key/'attempt2/receipt.json').read_text());src=Path(r['native']);n=np.array(Image.open(src).convert('RGB'))
 m=Image.new('L',(1254,1254),0);ImageDraw.Draw(m).polygon(poly,fill=255);inside=np.array(m)>0
 # Integer alpha only selects actual AI pixels; no art resizing or procedural repaint.
 yy,xx=np.mgrid[:1254,:1254];dist=np.full((1254,1254),1e9)
 for i,(ax,ay) in enumerate(poly):
  bx,by=poly[(i+1)%len(poly)]
  if ax==bx==1254:continue
  dist=np.minimum(dist,((bx-ax)*(yy-ay)-(by-ay)*(xx-ax))/((bx-ax)**2+(by-ay)**2)**0.5)
 a=np.rint(np.clip(dist/6,0,1)*255).astype('uint8');ap=O/(key+'-alpha.png');Image.fromarray(a).save(ap)
 assert not np.any(occupied[y:y+1254,2842:4096]&(a>0));occupied[y:y+1254,2842:4096]|=a>0
 p=out[y:y+1254,2842:4096];mix=((p.astype('uint32')*(255-a[...,None])+n.astype('uint32')*a[...,None]+127)//255).astype('uint8');out[y:y+1254,2842:4096]=mix
 Image.fromarray(mix).save(O/(key+'-composed-local-1254.png'))
 ops.append({'id':key,'source':info(src),'receipt':info(D/key/'attempt2/receipt.json'),'alpha':info(ap),'destinationCoreBox':[2842,y,4096,y+1254],'nativeCrop':[0,0,1254,1254],'polygon':poly,'fadePixels':6})
core=O/'candidate-4096.png';Image.fromarray(out).save(core);ci=Image.open(ctx).convert('RGB');ci.paste(Image.fromarray(out),(115,115));cp=O/'context-4326.png';ci.save(cp)
assert np.array_equal(out[~occupied],old[~occupied])
replay=old.copy()
for op in ops:
 x,y,x1,y1=op['destinationCoreBox'];a=np.array(Image.open(op['alpha']['path']));n=np.array(Image.open(op['source']['path']).convert('RGB'));loc=replay[y:y1,x:x1]
 for channel in range(3):
  loc[:,:,channel]=((loc[:,:,channel].astype('int64')*(255-a.astype('int64'))+n[:,:,channel].astype('int64')*a.astype('int64')+127)//255).astype('uint8')
assert np.array_equal(replay,out)
for key,y in [('upper',1320),('lower',2100)]:
 for tag,b in [('corner',(3150,y+650,3430,min(y+1254,4096))),('left-boundary',(3210,y+520,3360,min(y+1254,4096))),('right-map-border',(3920,y,4096,min(y+1254,4096)))]:Image.fromarray(out).crop(b).save(O/(key+'-'+tag+'-100pct.png'))
data={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':info(base),'baseContext':info(ctx),'operations':ops,'blendArithmetic':'(old*(255-alpha)+native*alpha+127)//255 RGB integers','outsideMaskExact':True,'independentChannelReplayExact':True,'masksDisjoint':True,'resampling':False,'RGBColorCorrection':False,'core':info(core),'context':info(cp),'status':'pending_native_boundary_visual_QA','formalAccepted':False}
with (O/'composition.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps({'core':info(core),'composition':info(O/'composition.json')}))
