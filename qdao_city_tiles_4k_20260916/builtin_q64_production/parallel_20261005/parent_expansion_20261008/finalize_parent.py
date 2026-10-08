from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
E=Path(__file__).resolve().parent;O=E/'current';O.mkdir(exist_ok=True);(O/'qa').mkdir(exist_ok=True)
R=E.parent/'parent_repairs_20261008/current'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
outer=load(E/'integration-v1/outer-fix/manifest.json')
base=E/'integration-v2/r08_c10.png';a=np.asarray(Image.open(base).convert('RGBA')).copy();derived=[dict(file=str(base),sha256=sha(base),generationRecord=str(base)+'.generation.json')]
applied=[]
for patch in outer['repairs']:
 p=Path(patch['file']);context=p.parent/'context.png';b=np.asarray(Image.open(context).convert('RGBA'));n=np.asarray(Image.open(p).convert('RGBA'));d=np.any(n!=b,axis=2)
 x,y,x2,y2=patch['sourceWindow'];target=a[y:y2,x:x2]
 assert np.array_equal(target[d],b[d]),'Changed source inside new correction scope'
 target[d]=n[d]
 derived.append(dict(file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json',operation='Exact changed-pixel transfer against bound native context; no second feather',window=patch['sourceWindow'],changedPixels=int(d.sum())))
 applied.append(dict(name=patch['name'],changedPixels=int(d.sum()),basePixelsExactlyMatched=True))
out=O/'r08_c10.png';Image.fromarray(a).save(out)
rec=dict(file=str(out),sha256=sha(out),width=4096,height=4096,operation='Native 1:1 final parent candidate assembly, two localized outer seam redraws transferred at exact coordinates.',derivedFrom=derived,formalAccepted=False)
save(str(out)+'.generation.json',rec)
selection=load(R/'current-selection.json');west=next(c for c in selection['candidates'] if c['tile']=='r08_c09');westbase=np.asarray(Image.open(west['file']).convert('RGBA')).copy();patch=outer['westPairedUpdate'];bound=np.asarray(Image.open(patch['boundTargetSource']['file']).convert('RGBA'));l,t,r,b=patch['targetLTRB']
assert np.array_equal(westbase[t:b,l:r],bound[t:b,l:r]),'Parent c09 overlap changed'
westbase[t:b,l:r]=np.asarray(Image.open(patch['file']).convert('RGBA'))
wout=O/'r08_c09.png';Image.fromarray(westbase).save(wout)
wrec=dict(file=str(wout),sha256=sha(wout),width=4096,height=4096,operation='Native paired west strip insertion, preserving parent REP repairs elsewhere',derivedFrom=[west,dict(file=patch['file'],sha256=sha(patch['file']),generationRecord=patch['file']+'.generation.json',pasteLTRB=patch['targetLTRB'])],formalAccepted=False)
save(str(wout)+'.generation.json',wrec)
combined=Image.new('RGBA',(4456,4096));combined.paste(Image.fromarray(westbase).crop((3736,0,4096,4096)),(0,0));combined.paste(Image.fromarray(a),(360,0))
qas=[]
def crop(name,box,source,scope):
 im=source.crop(box);q=O/'qa'/(name+'.png');im.save(q);qas.append(dict(file=str(q),sha256=sha(q),cropLTRB=box,nativeScale=1,sourceScope=scope,actuallyViewed=False))
im=Image.fromarray(a)
for name,box in [('outer-north',(100,760,940,1120)),('outer-south',(340,1980,940,2390)),('c03-north',(2030,810,3230,1070)),('c03-south',(2030,2040,3230,2280)),('c03-east',(3030,860,3310,2210))]:crop(name,box,im,'r08_c10')
for i,(t,b) in enumerate([(820,1160),(1100,1530),(1470,1850),(1790,2240)]):crop('west-paired-'+str(i+1),(160,t,600,b),combined,'c09-last360-plus-c10')
pr=im.copy();pr.thumbnail((1024,1024));pr.save(O/'preview.png')
current=dict(createdAt=datetime.now(timezone.utc).isoformat(),status='assembled_pending_final_postexport_qa',output=rec,pairedWest=wrec,sourceSelections=[dict(file=str(R/'current-selection.json'),sha256=sha(R/'current-selection.json')),dict(file=str(E/'integration-v1/assembly.json'),sha256=sha(E/'integration-v1/assembly.json'))],outerApplications=applied,coveragePixels=int((a[:,:,3]==255).sum()),totalPixels=4096**2,newCompleteTileCount=0,formalAccepted=False,wholeCityComplete=False,childSelectionModified=False,qa=qas,priorScopedReview=str(E/'integration-v2/manifest.json'))
save(O/'manifest.json',current)
print(json.dumps(dict(output=rec['sha256'],pairedWest=wrec['sha256'],coverage=current['coveragePixels'],qa=len(qas))))
