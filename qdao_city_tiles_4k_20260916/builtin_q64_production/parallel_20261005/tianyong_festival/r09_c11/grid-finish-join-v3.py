"""Native composition and explicit source-bound ROI packaging; never changes root state."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent
D=N/sys.argv[1]; phase=sys.argv[2]; O=D/'join-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def origin(tile):return [(int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096]
req=read(D/'request.json'); prep=read(D/'preparation.json'); tile=req['tile']; r=req['row']; c=req['col']
world=req['globalCropLTRB']; local=req['tileLocalCropLTRB']; lx=115 if c==1 else 230; ty=115 if r==1 else 230
right=1139 if c==4 else 1254; bottom=1139 if r==4 else 1254
if phase=='assemble':
 src=Path(sys.argv[3]); assert not (D/'native.png').exists(); shutil.copy2(src,D/'native.png'); O.mkdir(exist_ok=False)
 A=np.asarray(Image.open(D/'native.png').convert('RGB')); K=np.asarray(Image.open(D/'context.png').convert('RGBA')); assert A.shape==(1254,1254,3)
 save(D/'native.png.generation.json',{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'pixels':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes neither model nor quality selectors or returned identifiers','evidence':[ref(D/'tool-receipt.json'),ref(src)],'prompt':str(D/'prompt.txt'),'references':prep['references'],'nativeScale':1,'formalAccepted':False})
 def smooth(a):a=np.clip(a,0,1); return a*a*(3-2*a)
 x=np.arange(1254)[None,:]; y=np.arange(1254)[:,None]; w=smooth((x-54)/(lx-54))*smooth((y-54)/(ty-54))
 if r==4:w*=smooth((1200-y)/61)
 w[K[:,:,3]==0]=1
 J=np.rint(A*w[:,:,None]+K[:,:,:3]*(1-w[:,:,None])).astype(np.uint8)
 assert np.array_equal(J[K[:,:,3]==0],A[K[:,:,3]==0]); Image.fromarray(J).save(O/'joined.png'); Image.fromarray(np.rint(w*255).astype(np.uint8)).save(O/'native-weight.png')
 canvas=Image.new('RGBA',(1654,1654)); cx,cy=world[0]-200,world[1]-200
 for name,v in prep['sources'].items():
  assert sha(v['file'])==v['sha256']; ox,oy=origin(name); canvas.alpha_composite(Image.open(v['file']).convert('RGBA'),(ox-cx,oy-cy))
 canvas.paste(Image.fromarray(J),(200,200)); canvas.crop((0,0,1654,660)).save(O/'top-native-qa.png'); canvas.crop((0,0,660,1654)).save(O/'left-native-qa.png')
 save(O/'assembly.json',{'output':ref(O/'joined.png'),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'nativeWeight':ref(O/'native-weight.png'),'nativeScale':1,'registrationApplied':False,'toneCorrectionApplied':False,'resized':False,'operation':f'Native 1:1; smoothstep x54..{lx} and y54..{ty} in known top/left context only. All missing pixels equal actual native output.','visualReviewPending':True,'formalAccepted':False,'qa':{'worldTopLeft':[cx,cy],'joinedAt':[200,200],'nativeScale':1,'sources':list(prep['sources'].values())}})
 if r==4:
  assembly=read(O/'assembly.json');assembly['knownBottomNativeWeightFade']={'rangeY':[1139,1200],'operation':'Smoothstep native weight 1 to 0 only on already known pixels; unknown pixels always native'};save(O/'assembly.json',assembly)
 save(O/'joined.png.generation.json',{'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'operation':'Native composition; no resize or generation','derivedFrom':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(O/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
 print(json.dumps({'joined':ref(O/'joined.png')})); sys.exit()
assert phase=='package'; observation=sys.argv[3]; assert observation.strip()
J=Image.open(O/'joined.png').convert('RGBA'); K=np.asarray(Image.open(D/'context.png').convert('RGBA'))
assembly=read(O/'assembly.json'); assembly.update(visualReviewPending=False,localVisualAccepted=True); save(O/'assembly.json',assembly)
g=read(O/'joined.png.generation.json');g['assembly']=ref(O/'assembly.json');save(O/'joined.png.generation.json',g)
save(O/'visual-review.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'image':ref(O/'joined.png'),'reviewer':'root','viewedNativeImages':[ref(O/n) for n in ['joined.png','top-native-qa.png','left-native-qa.png']],'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'findings':[],'observation':observation,'limits':'Only this native window and explicit returns; full tile, unbuilt neighbors and city runtime remain pending.'})
specs=[('new-core',[lx,ty,right,bottom],None),('top-return',[lx,54,right,ty],'prior'),('left-return',[0,0,lx,1200 if r==4 else bottom],'prior')]
patches=[]; fragment=Image.open(prep['sources'][tile]['file']).convert('RGBA') if tile in prep['sources'] else Image.new('RGBA',(4096,4096))
def rectangles(mask):
 active={}; out=[]
 for y,row in enumerate(mask):
  edges=np.flatnonzero(np.diff(np.r_[False,row,False])); runs=[tuple(edges[i:i+2]) for i in range(0,len(edges),2)]; current={}
  for a,b in runs:current[(a,b)]=active.pop((a,b),[int(a),y,int(b),y]);current[(a,b)][3]=y+1
  out.extend(active.values());active=current
 out.extend(active.values());return out
for name,crop,prior_flag in specs:
 for dest in ([tile] if prior_flag is None else prep['sources']):
  ox,oy=origin(dest); l=max(crop[0],ox-world[0]);t=max(crop[1],oy-world[1]);rr=min(crop[2],ox+4096-world[0]);b=min(crop[3],oy+4096-world[1])
  if l>=rr or t>=b:continue
  if prior_flag:
   mask=K[t:b,l:rr,3]==255
   rects=[[a+l,bb+t,cc+l,dd+t] for a,bb,cc,dd in rectangles(mask)]
  else:
   assert not np.any(K[t:b,l:rr,3]);rects=[[l,t,rr,b]]
  for rc in rects:
   box=[rc[i]+world[i%2]-[ox,oy][i%2] for i in range(4)]; label=f'{len(patches):02d}-{name}-{dest}';f=O/(label+'.png');asset=J.crop(rc);asset.save(f)
   prior=prep['sources'][dest] if prior_flag else None
   p={'name':label,'asset':ref(f),'cropFromJoinedLTRB':rc,'destinationTile':dest,'destinationTileLTRB':box,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True};patches.append(p)
   save(O/(label+'.png.generation.json'),{'file':str(f),'sha256':sha(f),'derivedFrom':[ref(O/'joined.png')],'operation':'Exact native crop; no resize or generation','nativeScale':1,'newModelCalls':0,'cropFromJoinedLTRB':rc,'destinationTile':dest,'destinationTileLTRB':box,'formalAccepted':False})
   if dest==tile:fragment.paste(asset,tuple(box[:2]))
fragment.save(O/(tile+'-fragment.png')); coverage=int((np.asarray(fragment)[:,:,3]==255).sum())
src={**ref(O/(tile+'-fragment.png')),'tile':tile,'pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':coverage<4096**2,'fullyPainted':coverage==4096**2,'nativeScale':1,'formalAccepted':False,'generationRecord':str(O/(tile+'-fragment.png.generation.json'))}
save(Path(src['generationRecord']),{'file':src['file'],'sha256':src['sha256'],'derivedFrom':[prep['sources'].get(tile),ref(O/'joined.png')],'operation':'Explicit native ROI placement retaining all prior pixels outside ROI','newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'coveredNativeTilePixels':coverage,'formalAccepted':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':tile,'tileGlobalOrigin':req['tileGlobalOrigin'],'nativeScale':1,'windowTileLocalLTRB':local,'windowGlobalLTRB':world,'joined':ref(O/'joined.png'),'visualReview':ref(O/'visual-review.json'),'assembly':ref(O/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'note':'Apply all explicit ROIs together. Preserve all external and partial tile pixels outside those ROIs.'}
save(O/'manifest.json',manifest);save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,'fragment':src,'coveragePixels':coverage,'contextJoined':ref(O/'joined.png'),'manifest':ref(O/'manifest.json'),'rootPublished':False,'formalAccepted':False})
print(json.dumps({'manifest':ref(O/'manifest.json'),'coverage':coverage,'patches':len(patches)}))
