"""r04_c14 only: actual native ROI including physical east halo; immutable integer composition."""
import argparse,json,shutil
from pathlib import Path
from PIL import Image,ImageChops
import native_seam_v003 as s
B=s.B
p=argparse.ArgumentParser()
for k in ('prepare','request','prompt','event-id','version','session-log'):p.add_argument('--'+k,required=True)
p.add_argument('--source-rect',nargs=4,type=int,required=True);p.add_argument('--feather',type=int,default=16);a=p.parse_args()
assert a.version.startswith('right-');s.n.verify_contracts()
def local(v):
 p=Path(v).resolve();assert p.is_relative_to(B);return p
prep=s.read(local(a.prepare));req=s.read(local(a.request));assert prep['tile']=='r04_c14'
old=local(prep['baseline']['file']);inp=local(prep['input']['file']);assert s.sha(old)==prep['baseline']['sha256'] and s.sha(inp)==prep['input']['sha256']
assert local(a.prompt).read_text('utf-8')==req['prompt'] and str(inp) in req['referenced_image_paths']
source,receipt,digest=s.rr.completed_event(Path(a.session_log),a.event_id);native=s.rgb(source,(1254,1254));before=s.rgb(old,(4096,4096))
sx,sy,ex,ey=a.source_rect;assert 0<=sx<ex<=1254 and 0<=sy<ey<=1254
cx,cy,_,_=prep['contextTileXYXY'];x,y,x1,y1=cx+sx,cy+sy,cx+ex,cy+ey
assert 0<=x<x1<=4096 and 0<=y<y1<=4096
f=a.feather;w,h=ex-sx,ey-sy;assert 0<=f<=16 and min(w,h)>2*f
released=[k for k,v in [('west',x==0),('north',y==0),('east',x1==4096),('south',y1==4096)] if v]
def alpha(px,py):
 ds=[]
 if x>0:ds.append(px)
 if y>0:ds.append(py)
 if x1<4096:ds.append(w-1-px)
 if y1<4096:ds.append(h-1-py)
 return round(255*min(1,min(ds)/f)) if f and ds else 255
mask=Image.new('L',(w,h));mask.putdata([alpha(px,py) for py in range(h) for px in range(w)])
after=before.copy();after.paste(native.crop(a.source_rect),(x,y),mask);delta=ImageChops.difference(before,after);delta.paste((0,0,0),(x,y,x1,y1));assert delta.getbbox() is None
d=s.outdir(a.version);np=d/'native-repair.png';shutil.copyfile(source,np);assert s.sha(np)==digest
cp=d/'r04_c14-candidate.png';s.png(cp,after);mp=d/'linear-alpha-mask.png';s.png(mp,mask);s.js(d/'receipt.json',receipt)
evidence=[]
for name,box in [('north',[x-115,y-115,x1+115,y+115]),('south',[x-115,y1-115,x1+115,y1+115]),('west',[x-115,y-115,x+115,y1+115]),('east',[x1-115,y-115,x1+115,y1+115])]:
 box=[max(0,box[0]),max(0,box[1]),min(4096,box[2]),min(4096,box[3])];q=d/(name+'-perimeter-100pct.png');s.png(q,after.crop(box));evidence.append({**s.artifact(q),'crop':box})
ctx=d/'repaired-context-100pct.png';s.png(ctx,after.crop(prep['contextTileXYXY']))
rec={**prep,'schemaVersion':2,'createdAtUtc':s.n.now(),'previousCandidate':s.artifact(old),'candidate':s.artifact(cp),'nativeRepair':s.artifact(np),'inputPrepare':s.artifact(local(a.prepare)),'submittedRequest':s.artifact(local(a.request)),'exactPrompt':s.artifact(local(a.prompt)),'references':[s.artifact(local(z)) for z in req['referenced_image_paths']],'receipt':s.artifact(d/'receipt.json'),'actualModel':None,'actualModelEvidence':'未返回','sourceNativeROIXYXY':a.source_rect,'sourceCoreXYXY':[115,115,1139,1139],'sourceROIIncludesHalo':sx<115 or sy<115 or ex>1139 or ey>1139,'editTileXYXY':[x,y,x1,y1],'repairOverlayPixels':[w,h],'candidatePixels':[4096,4096],'originalCoreCount':16,'additionalCoreCount':0,'formalAcceptedCount':0,'operations':['integer actual native ROI; no resize/warp/imageblur','linear alpha<=16 at interior ROI edges','physical east edge uses actual native pixels without alpha'],'integrationTool':s.artifact(Path(__file__).resolve()),'noResize':True,'noWarp':True,'noImageBlur':True,'alphaPerimeterPixels':f,'unfeatheredPhysicalEdges':released,'alphaMask':s.artifact(mp),'unchangedOutsideEditVerified':True,'nativeEventBytesMatch':True,'perimeterEvidence':evidence,'contextEvidence':s.artifact(ctx),'eastNeighborStatus':'Original northeast/r04_c15 directory absent on recovery audit; externalE NOT verified or accepted','visualQa':'pending; formalAcceptedCount=0'}
s.js(d/'integration.json',rec);print(json.dumps({'candidate':rec['candidate'],'record':str(d/'integration.json')}))