from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
E=Path(__file__).resolve().parent;T=E.parent/'tianyong_festival';R=E.parent/'parent_repairs_20261008/current';O=E/'child-selected';O.mkdir(exist_ok=True);(O/'qa').mkdir(exist_ok=True)
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checked={}
def verify(e):
 p=Path(e['file']); h=sha(p);assert h==e['sha256'],str(p);checked[str(p)]=h;return p
progress=load(T/'progress.json');sel=Path(progress['candidateSet']);s=load(sel);save(O/'source-selection-snapshot.json',s)
c=next(x for x in s['candidates'] if x['tile']=='r08_c10');cw=next(x for x in s['candidates'] if x['tile']=='r08_c09');verify(c);verify(cw)
steps=[T/'r08_c10/current'/v/'assembly.json' for v in ['v016','v017']]
latest=int(sel.parent.name[1:]);steps += [T/'r07_c10/current'/f'v{i:03}'/'assembly.json' for i in range(1,latest+1)]
proof=[]
for ap in steps:
 d=load(ap); manifest=load(verify(d['manifest'])); review=load(verify(d['visualReview'])); js=manifest.get('joined')
 if js:joined=Image.open(verify(js)).convert('RGBA')
 else:joined=None
 reviewitems=review.get('inspectedImages',review.get('inspected',[]))
 for q in reviewitems:
  if isinstance(q,dict) and q.get('file') and q.get('sha256'):verify(q)
 rows=[]
 for tile,output in d['outputs'].items():
  if tile not in ['r08_c10','r08_c09']:continue
  ins=next((x for x in d['sourceInputs'] if x['tile']==tile),None)
  if not ins:continue
  im=Image.open(verify(ins)).convert('RGBA')
  for p in d['patches']:
   if p['destinationTile']!=tile:continue
   piece=Image.open(verify(p['asset'])).convert('RGBA');l,t,r,b=p['destinationTileLTRB'];assert piece.size==(r-l,b-t)
   if joined is not None and p.get('cropFromJoinedLTRB'):assert np.array_equal(np.asarray(piece),np.asarray(joined.crop(p['cropFromJoinedLTRB'])))
   im.paste(piece,(l,t))
  actual=Image.open(verify(output)).convert('RGBA');assert np.array_equal(np.asarray(im),np.asarray(actual)),str(ap)+' '+tile
  rows.append(dict(tile=tile,output=output,exactReconstruction=True))
 proof.append(dict(assembly=dict(file=str(ap),sha256=sha(ap)),manifest=d['manifest'],visualReview=d['visualReview'],reviewImageHashCount=len(reviewitems),outputs=rows))
# Transfer only existing parent REP changed pixels, guarded against current child edits.
parent=next(x for x in load(R/'current-selection.json')['candidates'] if x['tile']=='r08_c09');verify(parent)
old=parent['childEntryBeforeParentRepair'];verify(old)
b=np.asarray(Image.open(old['file']).convert('RGBA'));p=np.asarray(Image.open(parent['file']).convert('RGBA'));target=np.asarray(Image.open(cw['file']).convert('RGBA')).copy();delta=np.any(p!=b,axis=2);assert np.array_equal(target[delta],b[delta]),'REP and child edits conflict'
target[delta]=p[delta];wp=O/'r08_c09.png';Image.fromarray(target).save(wp)
wrec=dict(file=str(wp),sha256=sha(wp),width=4096,height=4096,operation='Exact disjoint delta transfer: parent REP repaired pixels applied on latest child c09, retaining child required shared edge',derivedFrom=[cw,parent,old],changedPixels=int(delta.sum()),pixelGuardMatched=True,formalAccepted=False)
save(str(wp)+'.generation.json',wrec)
a=Image.open(c['file']).convert('RGBA');full=Image.new('RGBA',(4456,4096));full.paste(Image.fromarray(target).crop((3736,0,4096,4096)),(0,0));full.paste(a,(360,0));qas=[]
for i,(top,bot) in enumerate([(850,1170),(1100,1500),(1440,1800),(1740,2110)]):
 box=[160,top,600,bot];f=O/'qa'/f'west-{i+1}.png';full.crop(box).save(f);qas.append(dict(file=str(f),sha256=sha(f),cropLTRB=box,source='c09 last360 plus c10',actuallyViewed=False))
for name,box in [('c01-full',[0,900,1254,2154]),('c03-full',[1900,900,3154,2154])]:
 f=O/'qa'/(name+'.png');a.crop(box).save(f);qas.append(dict(file=str(f),sha256=sha(f),cropLTRB=box,source='r08_c10',actuallyViewed=False))
out=dict(createdAt=datetime.now(timezone.utc).isoformat(),sourceSelection=dict(file=str(sel),sha256=sha(sel)),selectedEntry=c,childPairedWest=cw,parentCompatibleWest=wrec,reconstructionSteps=proof,verifiedFileCount=len(checked),checkedFileHashes=checked,coveragePixels=int((np.asarray(a)[:,:,3]==255).sum()),size=list(a.size),newCoordinateEligible=True,formalAccepted=False,wholeTileAccepted=False,wholeCityComplete=False,qa=qas,status='sources_reconstructed_current_native_QA_pending',parentCompetingCandidateDiscardRecommended=True)
save(O/'audit.json',out);print(json.dumps({'audit':str(O/'audit.json'),'tile':c,'files':len(checked),'steps':len(proof),'coverage':out['coveragePixels']}))
