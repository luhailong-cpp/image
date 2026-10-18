"""Integrate a verified native r03_c13 east-boundary edit; fixed r03_c14 remains read-only."""
import argparse,shutil
from pathlib import Path
from PIL import Image,ImageChops
import native_seam_v003 as base
B=base.B
def local(p):
 p=Path(p).resolve();assert p.is_relative_to(B);return p
def joined(left,right,box):
 x,y,x1,y1=box;im=Image.new('RGB',(x1-x,y1-y))
 if x<4096:im.paste(left.crop((x,y,min(4096,x1),y1)),(0,0))
 if x1>4096:im.paste(right.crop((max(0,x-4096),y,x1-4096,y1)),(max(0,4096-x),0))
 return im
def main():
 p=argparse.ArgumentParser()
 for k in ('prepare','request','prompt','event-id','session-log','version'):p.add_argument('--'+k,required=True)
 p.add_argument('--source-rect',nargs=4,type=int,required=True);p.add_argument('--feather',type=int,default=16);a=p.parse_args()
 assert a.version.startswith('west-');base.n.verify_contracts()
 prep=base.read(local(a.prepare));req=base.read(local(a.request));prompt=local(a.prompt)
 assert prep['tile']=='r03_c13' and prompt.read_text(encoding='utf-8')==req['prompt']
 beforep=local(prep['baseline']['file']);rightp=local(prep['fixedEastNeighbor']['file']);inp=local(prep['input']['file'])
 for key in ('baseline','fixedEastNeighbor','input'):assert base.sha(local(prep[key]['file']))==prep[key]['sha256']
 assert str(inp) in req['referenced_image_paths']
 src,rec,digest=base.rr.completed_event(Path(a.session_log),a.event_id)
 nat=base.rgb(src,(1254,1254));before=base.rgb(beforep,(4096,4096));right=base.rgb(rightp,(4096,4096))
 sx,sy,ex,ey=a.source_rect;assert 0<=sx<ex<=1254 and 0<=sy<ey<=1254
 cx,cy,_,_=prep['contextTileXYXY'];x,y,x1,y1=cx+sx,cy+sy,cx+ex,cy+ey
 assert 0<=x<x1<=4096 and 0<=y<y1<=4096
 w,h=x1-x,y1-y;f=a.feather;assert 0<=f<=16 and min(w,h)>f*2
 def alpha(px,py):
  distances=[py,h-1-py]
  if x>0:distances.append(px)
  if x1<4096:distances.append(w-1-px)
  return round(255*min(1,min(distances)/f)) if f else 255
 mask=Image.new('L',(w,h));mask.putdata([alpha(px,py) for py in range(h) for px in range(w)])
 after=before.copy();after.paste(nat.crop(a.source_rect),(x,y),mask)
 diff=ImageChops.difference(before,after);diff.paste((0,0,0),(x,y,x1,y1));assert diff.getbbox() is None
 d=base.outdir(a.version);nativep=d/'native-repair.png';shutil.copyfile(src,nativep);assert base.sha(nativep)==digest
 candidate=d/'r03_c13-candidate.png';base.png(candidate,after);base.png(d/'linear-alpha-mask.png',mask);base.js(d/'receipt.json',rec)
 ev=[]
 for name,box in [('north',[x-115,y-115,x1+115,y+115]),('south',[x-115,y1-115,x1+115,y1+115]),('west',[x-115,y-115,x+115,y1+115]),('east',[x1-240,y-115,x1+240,y1+115])]:
  box=[max(0,box[0]),max(0,box[1]),min(8192,box[2]),min(4096,box[3])]
  q=d/(name+'-perimeter-100pct.png');base.png(q,joined(after,right,box));ev.append({**base.artifact(q),'cropAcrossTileXYXY':box})
 q=d/'repaired-context-100pct.png';base.png(q,joined(after,right,prep['contextTileXYXY']))
 record={**prep,'createdAtUtc':base.n.now(),'previousCandidate':base.artifact(beforep),'candidate':base.artifact(candidate),'nativeRepair':base.artifact(nativep),'sourceNativeROIXYXY':a.source_rect,'editTileXYXY':[x,y,x1,y1],'inputPrepare':base.artifact(local(a.prepare)),'submittedRequest':base.artifact(local(a.request)),'exactPrompt':base.artifact(prompt),'references':[base.artifact(local(q)) for q in req['referenced_image_paths']],'receipt':base.artifact(d/'receipt.json'),'perimeterEvidence':ev,'contextEvidence':base.artifact(q),'nativeEventBytesMatch':True,'nativeOutputPixels':[1254,1254],'candidatePixels':[4096,4096],'actualModel':None,'actualModelEvidence':'未返回','entryPoint':'builtin image_gen.imagegen','alphaPerimeterPixels':f,'unfeatheredPhysicalEdges':['east'] if x1==4096 else [],'sourceROIIncludesHalo':True,'noResize':True,'noWarp':True,'noImageBlur':True,'unchangedOutsideEditVerified':True,'fixedNeighborSha256Unchanged':base.sha(rightp)==prep['fixedEastNeighbor']['sha256'],'integrationTool':base.artifact(Path(__file__).resolve()),'originalCoreCount':16,'additionalCoreCount':0,'formalAcceptedCount':0,'visualQa':'pending'}
 base.js(d/'integration.json',record);print(record['candidate'])
if __name__=='__main__':main()

