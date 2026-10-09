from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;D=N/sys.argv[1];O=D/'join-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(D/'request.json');prep=read(D/'preparation.json');prior=read(D/'local-source-checkpoint-input.json');r=req['row'];c=req['col'];x0,y0=req['tileLocalCropLTRB'][:2]
assert sha(N/'local-source-checkpoint.json')==prep['sourceCheckpoint']['sha256'],'Local predecessor changed'
qa=read(O/'qa-index.json');ack=read(O/'visual-observation.json')
assert ack['allIndexedImagesActuallyViewedAtNativeScale'] and not ack['openFindings']
J=Image.open(O/'joined.png').convert('RGBA');fragment=Image.open(prep['sources']['fragment']['file']).convert('RGBA');before=np.asarray(fragment).copy();mask=np.zeros((4096,4096),bool)
assembly=read(O/'assembly.json');assembly.update(visualReviewPending=False,localVisualAccepted=True);save(O/'assembly.json',assembly)
gen=read(O/'joined.png.generation.json');gen['assembly']=ref(O/'assembly.json');save(O/'joined.png.generation.json',gen)
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'image':ref(O/'joined.png'),'reviewer':'close_c03','viewedNativeImages':[ref(D/'native.png')]+qa['images'],'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'findings':[],'observation':ack['observation'],'limits':'Only this native window and explicit returns reviewed; full tile, missing outside neighbors, runtime and city remain pending.'}
save(O/'visual-review.json',review)
xl=0 if c==1 else (c-1)*1024+115; xr=min(4096,x0+1254); yt=max(0,y0);yb=4096 if r==4 else r*1024-115;retb=min(4096,yb+(176 if r<4 else 0))
specs=[('new-core','r07_c11',[xl,yt,xr,yb],None)]
if c==1:specs.append(('left-return','r07_c10',[4035,yt,4096,retb],prep['sources']['left']))
else:specs.append(('left-return','r07_c11',[x0+54,yt,xl,retb],prep['sources']['fragment']))
if r<4:specs.append(('bottom-return','r07_c11',[xl,yb,xr,retb],prep['sources']['fragment']))
elif c>1:
 for neighbor in prep.get('contextNeighbors',[]):
  if neighbor['tile']=='r08_c11':
   nb=[x0+54,0,xl,61];a=np.array(Image.open(neighbor['file']).convert('RGBA').crop(nb))[:,:,3]
   if np.all(a==255):specs.append(('bottom-left-return','r08_c11',nb,neighbor))
   else:assert not np.any(a),'Partial below-neighbor return needs explicit split'
patches=[]
for name,tile,box,priorSource in specs:
 if tile=='r07_c11':crop=[box[0]-x0,box[1]-y0,box[2]-x0,box[3]-y0]
 elif tile=='r08_c11':crop=[box[0]-x0,box[1]+4096-y0,box[2]-x0,box[3]+4096-y0]
 else:crop=[54,box[1]-y0,115,box[3]-y0]
 assert all(0<=v<=1254 for v in crop);asset=J.crop(crop);f=O/(name+'.png');asset.save(f)
 p={'name':name,'asset':ref(f),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'requiredPriorSource':priorSource,'nativeScale':1,'mustApplyTogether':True};patches.append(p)
 save(O/(name+'.png.generation.json'),{'file':str(f),'sha256':sha(f),'derivedFrom':[ref(O/'joined.png')],'operation':'Exact native crop, no resizing or generation','nativeScale':1,'newModelCalls':0,'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'formalAccepted':False})
 if tile=='r07_c11':
  x1,y1,x2,y2=box;assert not mask[y1:y2,x1:x2].any();mask[y1:y2,x1:x2]=True
  if name=='new-core':assert not before[y1:y2,x1:x2,3].any()
  else:assert np.all(before[y1:y2,x1:x2,3]==255)
  fragment.paste(asset,tuple(box[:2]))
after=np.asarray(fragment);assert np.array_equal(after[~mask],before[~mask]);coverage=int(np.count_nonzero(after[:,:,3]));expected=prior['coveragePixels']+(xr-xl)*(yb-yt);assert coverage==expected
fragment.save(O/'r07_c11-fragment.png')
src={**ref(O/'r07_c11-fragment.png'),'tile':'r07_c11','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':coverage<4096**2,'fullyPainted':coverage==4096**2,'nativeScale':1,'formalAccepted':False,'generationRecord':str(O/'r07_c11-fragment.png.generation.json')}
save(O/'r07_c11-fragment.png.generation.json',{'file':src['file'],'sha256':src['sha256'],'derivedFrom':[prep['sources']['fragment']]+[p['asset'] for p in patches if p['destinationTile']=='r07_c11'],'operation':'Exact native ROI pastes onto prior partial fragment; all pixels outside explicit ROIs identical','newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'coveredNativeTilePixels':coverage,'formalAccepted':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r07_c11','tileGlobalOrigin':req['tileGlobalOrigin'],'nativeScale':1,'windowTileLocalLTRB':req['tileLocalCropLTRB'],'windowGlobalLTRB':req['globalCropLTRB'],'joined':ref(O/'joined.png'),'visualReview':ref(O/'visual-review.json'),'assembly':ref(O/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['sourceCheckpoint'],'requiresPriorManifest':prior['manifest'],'note':'Apply new core and explicit return ROIs together. External prior sources are prospective native composites; compare required ROI, not unrelated old full-tile pixels. Never replace an outside tile with an old whole snapshot.'}
save(O/'manifest.json',manifest)
chain=prior.get('manifestChain',[prior['manifest']])+[ref(O/'manifest.json')]
neighbors=prior.get('contextNeighbors',[])
for p in patches:
 if p['destinationTile']=='r08_c11':
  neighbor=next(v for v in neighbors if v['tile']=='r08_c11');B=Image.open(neighbor['file']).convert('RGBA');B.paste(Image.open(p['asset']['file']),tuple(p['destinationTileLTRB'][:2]));bp=O/'r08_c11-context-fragment.png';B.save(bp);neighbor.update(ref(bp))
save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c11','fragment':src,'coveragePixels':coverage,'contextJoined':ref(O/'joined.png'),'manifest':ref(O/'manifest.json'),'manifestChain':chain,'externalReturnDependencies':prior['externalReturnDependencies']+[p for p in patches if p['destinationTile'] in ['r07_c10','r08_c10']],'contextNeighbors':neighbors,'externalImportEvidence':prior.get('externalImportEvidence',[]),'rootPublished':False,'formalAccepted':False})
print(json.dumps({'manifest':ref(O/'manifest.json'),'fragment':src,'coverage':coverage}))
