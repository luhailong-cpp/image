from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;D=N/'full-review-native-v1';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
cp=read(N/'local-source-checkpoint.json');root=read(T/'source-checkpoint.json');sources={k:cp[k] for k in ['fragment','prospectiveRight','prospectiveBottom']}
for s in sources.values():assert sha(s['file'])==s['sha256']
A=Image.open(cp['fragment']['file']).convert('RGBA');R=Image.open(cp['prospectiveRight']['file']).convert('RGBA');B=Image.open(cp['prospectiveBottom']['file']).convert('RGBA');assert A.size==(4096,4096) and np.all(np.array(A)[:,:,3]==255)
records=[]
for j,y in enumerate([0,1280,2560]):
 for i,x in enumerate([0,1280,2560]):
  box=[x,y,x+1536,y+1536];p=D/f'full-{j+1}{i+1}.png';A.crop(box).save(p);records.append(dict(ref(p),kind='full-native-coverage',ownLTRB=box,pixels=[1536,1536],nativeScale=1))
E=Image.new('RGBA',(512,4096));E.paste(A.crop((3840,0,4096,4096)),(0,0));E.paste(R.crop((0,0,256,4096)),(256,0))
S=Image.new('RGBA',(4096,512));S.paste(A.crop((0,3840,4096,4096)),(0,0));S.paste(B.crop((0,0,4096,256)),(0,256))
for i,p0 in enumerate([0,1280,2560]):
 for kind,im,box in [('east',E,[0,p0,512,p0+1536]),('south',S,[p0,0,p0+1536,512])]:
  p=D/f'{kind}-{i+1}.png';im.crop(box).save(p);records.append(dict(ref(p),kind=kind,nativeScale=1,assembledLTRB=box,boundaryAt=256))
matches=[]
for tile,im,box in [('r07_c10',R,[0,0,256,4096]),('r08_c09',B,[0,0,4096,256])]:
 v=next(v for v in root['candidateSet'] if v['tile']==tile);assert sha(v['file'])==v['sha256'];latest=Image.open(v['file']).convert('RGBA');matches.append({'tile':tile,'latestRootSource':v,'edgeLTRB':box,'prospectiveEqualsRootEdge':bool(np.array_equal(np.array(im.crop(box)),np.array(latest.crop(box))))})
save(D/'source-checkpoint-frozen.json',cp);save(D/'root-checkpoint-frozen.json',root)
save(D/'native-crop-index.json',{'sources':sources,'sourceCheckpoint':ref(D/'source-checkpoint-frozen.json'),'rootCheckpoint':ref(D/'root-checkpoint-frozen.json'),'latestEdgeChecks':matches,'crops':records,'coveragePixels':16777216,'northWestExternalPending':True,'formalAccepted':False})
# A sidecar corrects an earlier diagnostic-reference label without altering frozen manifest hashes.
for name in ['r03_c03-v1','r03_c02-v1']:
 d=N/name;p=d/'repair-v1/profile-assembly/profile-peaks.json'
 if p.exists():save(d/'registration-diagnostic-reference-correction.json',{'note':'Final-v2 controls native is repair-v1/native.png; actual matching profiles are this repaired-native diagnostic. The controls generic diagnosticSource points to initial final-v1 and is a label error only; image, controls, fields and frozen manifests are unchanged.','correctDiagnosticSource':ref(p),'native':ref(d/'repair-v1/native.png'),'appliesTo':ref(d/'final-v2/registration-controls.json')})
print(json.dumps({'directory':str(D),'cropCount':len(records),'coverage':16777216,'latestEdgeChecks':matches}))
