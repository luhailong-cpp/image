from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;D=N/'full-review-native-v1';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
cp=read(N/'local-source-checkpoint.json');root=read(T/'source-checkpoint.json');latest={v['tile']:v for v in root['candidateSet']}
sources={'r07_c08':dict(cp['fragment'],tile='r07_c08')}
for t in ['r07_c09','r08_c08','r08_c09','r08_c07']:sources[t]=latest[t]
ims={}
for t,v in sources.items():
 assert sha(v['file'])==v['sha256']
 ims[t]=Image.open(v['file']).convert('RGBA')
A=ims['r07_c08'];assert A.size==(4096,4096) and np.all(np.array(A)[:,:,3]==255)
checks=[]
for k,t,box in [('prospectiveRight','r07_c09',[0,0,384,4096]),('prospectiveBottom','r08_c08',[0,0,4096,384])]:
 v=cp[k];assert sha(v['file'])==v['sha256'];P=Image.open(v['file']).convert('RGBA')
 eq=bool(np.array_equal(np.array(P.crop(box)),np.array(ims[t].crop(box))))
 assert eq,(t,'root has not applied external returns or subsequent changes need review')
 checks.append({'tile':t,'localProspectiveSource':v,'rootSource':sources[t],'roi':box,'pixelExact':eq})
records=[]
def emit(name,im,kind,**kw):
 p=D/name;im.save(p);records.append(dict(ref(p),kind=kind,pixels=list(im.size),nativeScale=1,**kw))
for j,y in enumerate([0,1280,2560]):
 for i,x in enumerate([0,1280,2560]):
  box=[x,y,x+1536,y+1536];emit(f'full-{j+1}{i+1}.png',A.crop(box),'full-native-coverage',ownLTRB=box)
E=Image.new('RGBA',(768,4096));E.paste(A.crop((3712,0,4096,4096)),(0,0));E.paste(ims['r07_c09'].crop((0,0,384,4096)),(384,0))
S=Image.new('RGBA',(4096,768));S.paste(A.crop((0,3712,4096,4096)),(0,0));S.paste(ims['r08_c08'].crop((0,0,4096,384)),(0,384))
for i,p0 in enumerate([0,1280,2560]):
 for kind,im,box in [('east',E,[0,p0,768,p0+1536]),('south',S,[p0,0,p0+1536,768])]:
  emit(f'{kind}-{i+1}.png',im.crop(box),kind,assembledLTRB=box,boundaryAt=384)
cornerSpecs={
 'northwest':[('r07_c08',[0,0,384,384],[384,384])],
 'northeast':[('r07_c08',[3712,0,4096,384],[0,384]),('r07_c09',[0,0,384,384],[384,384])],
 'southwest':[('r07_c08',[0,3712,384,4096],[384,0]),('r08_c07',[3712,0,4096,384],[0,384]),('r08_c08',[0,0,384,384],[384,384])],
 'southeast':[('r07_c08',[3712,3712,4096,4096],[0,0]),('r07_c09',[0,3712,384,4096],[384,0]),('r08_c08',[3712,0,4096,384],[0,384]),('r08_c09',[0,0,384,384],[384,384])]}
for name,spec in cornerSpecs.items():
 im=Image.new('RGBA',(768,768));regions=[]
 for tile,box,xy in spec:im.paste(ims[tile].crop(box),xy);regions.append({'tile':tile,'sourceLTRB':box,'destinationXY':xy})
 emit('corner-'+name+'.png',im,'known-corner',regions=regions,unknownTransparent=True)
save(D/'local-checkpoint-frozen.json',cp);save(D/'root-checkpoint-frozen.json',root)
save(D/'native-crop-index.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,'localCheckpoint':ref(D/'local-checkpoint-frozen.json'),'rootCheckpoint':ref(D/'root-checkpoint-frozen.json'),'latestEdgeChecks':checks,'crops':records,'fullCoveragePixels':16777216,'formalAccepted':False,'pendingUnknownTiles':['r06_c07','r06_c08','r06_c09','r07_c07']})
print(json.dumps({'directory':str(D),'crops':len(records),'edgeChecks':checks}))
