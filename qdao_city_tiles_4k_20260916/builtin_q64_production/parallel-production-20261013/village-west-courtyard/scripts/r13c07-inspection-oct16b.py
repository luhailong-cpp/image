from pathlib import Path
import json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent.parent
D=B/'qa/r13-c07-repair-rock-east-r03-oct16-v1'
O=B/'qa/r13-c07-internal-inspection-oct16b-v1'
O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
j=json.loads((D/'assembly.json').read_text(encoding='utf-8'))
p=D/'context-native.png';assert sha(p)==j['context']['sha256']
im=Image.open(p);assert im.size==(4326,4326)
cs=[]
def crop(name,box):
 q=O/(name+'.png')
 with q.open('xb') as f:im.crop(box).save(f,format='PNG')
 cs.append({'id':name,**ref(q),'contextBox':box,'scale':1,'operation':'integer crop only','reviewed':False})
for r in range(4):
 for c in range(1,4):
  x,y=115+c*1024,115+r*1024;crop(f'vertical-r{r+1:02d}-c{c:02d}',[x-345,y,x+345,y+1024])
for r in range(1,4):
 for c in range(4):
  x,y=115+c*1024,115+r*1024;crop(f'horizontal-r{r:02d}-c{c+1:02d}',[x,y-345,x+1024,y+345])
for r in range(1,4):
 for c in range(1,4):
  x,y=115+c*1024,115+r*1024;crop(f'junction-r{r:02d}-c{c:02d}',[x-345,y-345,x+345,y+345])
q={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c07','assembly':ref(D/'assembly.json'),'context':ref(p),'candidate':ref(D/'r13_c07.candidate.png'),'nativeCrops':cs,'formalAccepted':False,'internalQa':'pending visual review','externalQa':'pending','sourceReplay':j['proof']}
with (O/'inspection-manifest.json').open('x',encoding='utf-8') as f:json.dump(q,f,indent=2);f.write('\n')
print(json.dumps({'output':str(O),'crops':len(cs),'candidate':q['candidate'],'context':q['context']}))
