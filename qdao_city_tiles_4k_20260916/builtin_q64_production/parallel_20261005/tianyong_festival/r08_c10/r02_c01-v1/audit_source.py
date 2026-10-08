from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent;O=P/'qa-source';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cpf=T/'r08_c10/current/v012/source-checkpoint.json';cp=read(cpf)
left=cp['coupledNeighbors']['r08_c09'];active=cp['fragment']
for ref in [left,active]:assert sha(ref['file'])==ref['sha256']
li=Image.open(left['file']).convert('RGBA');fi=Image.open(active['file']).convert('RGBA')
def img(n,im,refs,operation,**extra):
 im.save(O/n);save(n+'.generation.json',{**info(O/n),'derivedFrom':refs,'newModelCalls':0,'operation':operation,**extra})
context=Image.new('RGBA',(1254,1254));context.paste(li.crop((3981,909,4096,2163)),(0,0));context.paste(fi.crop((0,909,1139,2163)),(115,0))
img('v012-context-study.png',context,[left,active],'Exact native source composition for planning only; future top and right neighbors not ready',windowTileLocalLTRB=[-115,909,1139,2163])
master=Path('D:/work/image/tianyong_festival_hd_20260910/tianyong_city_master_6144.png')
glob=[36749,29581,38003,30835]
with Image.open(master) as mi:
 layout=mi.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in glob))
img('layout-reference-only.png',layout,[info(master)],'Canonical location-only crop, upsampled for inspection; forbidden final pixels',windowGlobalLTRB=glob)
for y in [2048,3072]:
 for x in [0,1024,2048,3072]:
  b=[x,y-80,x+1024,y+80];img(f'c09-y{y}-x{x}.png',li.crop(b),[left],'Exact native source crop for audit',cropLTRB=b)
board=Image.new('RGBA',(768,4096));board.paste(li.crop((3712,0,4096,4096)),(0,0));board.paste(fi.crop((0,0,384,4096)),(384,0))
for y in [0,1024,2048,3072]:img(f'common-edge-y{y}.png',board.crop((0,y,768,y+1024)),[left,active],'Exact native shared-edge montage; x384 is c09/c10 boundary',tileLocalYRange=[y,y+1024],c09LocalXRange=[3712,4096],c10LocalXRange=[0,384])
a=np.asarray(li).astype(np.float32);stats=[]
for y in [2048,3072]:
 d=a[y,:,:3]-a[y-1,:,:3]
 for x in range(0,4096,256):
  roi=d[x:x+256];stats.append({'y':y,'xRange':[x,x+256],'meanDeltaRGB':roi.mean(0).tolist(),'meanAbsDeltaRGB':np.abs(roi).mean(0).tolist(),'maxAbs':float(np.abs(roi).max())})
save('source-measurements.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'checkpoint':info(cpf),'sources':[left,active],'rowBoundaryPixelDeltas':stats,'interpretation':'Adjacent-row deltas locate discontinuities but are not a standalone visual acceptance test. Known material edges are inspected separately.','currentRootChanged':False})
print(json.dumps({'directory':str(O),'version':cp['version'],'knownPixels':int((np.asarray(context)[:,:,3]==255).sum()),'topRightPending':True}))
