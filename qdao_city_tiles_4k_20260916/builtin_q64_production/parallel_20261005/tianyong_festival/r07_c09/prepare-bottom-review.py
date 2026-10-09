from pathlib import Path
from PIL import Image
import json,hashlib
N=Path(__file__).parent;T=N.parent;Q=N/'review-bottom-row-v1';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cp=read(N/'local-source-checkpoint.json');root=read(T/'source-checkpoint.json');A=Image.open(cp['fragment']['file']).convert('RGBA');source=next(i for i in root['candidateSet'] if i['tile']=='r08_c09');B=Image.open(source['file']).convert('RGBA')
m=read(cp['manifest']['file']);applied=[]
for p in m['patches']:
 if p['destinationTile']!='r08_c09':continue
 roi=p['destinationTileLTRB'];P=Image.open(p['asset']['file']).convert('RGBA');old=B.crop(roi)
 if old.tobytes()!=P.tobytes():
  assert old.tobytes()==Image.open(p['requiredPriorSource']['file']).convert('RGBA').crop(roi).tobytes()
  B.paste(P,roi[:2]);applied.append(p['asset'])
B.save(Q/'frozen-prospective-r08_c09.png')
out=[]
for i,(l,r) in enumerate([(0,1536),(1280,2816),(2560,4096)]):
 f=Q/f'native-row-{i+1}.png';A.crop((l,2957,r,4096)).save(f);out.append(dict(ref(f),region=[l,2957,r,4096],tile='r07_c09'))
S=Image.new('RGBA',(4096,512));S.paste(A.crop((0,3840,4096,4096)),(0,0));S.paste(B.crop((0,0,4096,256)),(0,256))
for i,(l,r) in enumerate([(0,1152),(1024,2176),(2048,3200),(2944,4096)]):
 f=Q/f'native-south-{i+1}.png';S.crop((l,0,r,512)).save(f);out.append(dict(ref(f),r07Region=[l,3840,r,4096],r08Region=[l,0,r,256]))
(Q/'inspection-index.json').write_text(json.dumps({'frozenLocalCheckpoint':cp,'rootCheckpointAtFreeze':ref(T/'source-checkpoint.json'),'rootBottomSource':source,'lastPendingReturnsApplied':applied,'frozenProspectiveBottom':ref(Q/'frozen-prospective-r08_c09.png'),'nativeScale':1,'inspectionCrops':out},indent=2))
print(json.dumps({'qa':str(Q),'cropCount':len(out)}))
