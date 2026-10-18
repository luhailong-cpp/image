from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'I01-only-reviewed-20261016';O.mkdir(exist_ok=False)
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,a):assert not p.exists();Image.fromarray(a).save(p);return ev(p)
old=rd(D/'trial-v1/I01-blind-stone-grout/composition.json')
base=rgb(old['base']['path']);ctx=rgb(old['baseContext']['path']);new=base.copy()
a=np.array(Image.open(old['alpha']['path']));native=rgb(old['actualNative']['path'])
x0,y0,x1,y1=old['destinationCoreBox'];u0,v0,u1,v1=old['nativeCrop'];cut=native[v0:v1,u0:u1]
aa=a.astype(np.uint32)[...,None];new[y0:y1,x0:x1]=((base[y0:y1,x0:x1].astype(np.uint32)*(255-aa)+cut.astype(np.uint32)*aa+127)//255).astype(np.uint8)
scalar=base.copy()
for y in range(y1-y0):
 for x in range(x1-x0):
  w=int(a[y,x])
  for c in range(3):scalar[y0+y,x0+x,c]=(int(base[y0+y,x0+x,c])*(255-w)+int(cut[y,x,c])*w+127)//255
assert np.array_equal(new,scalar)
support=np.zeros((4096,4096),bool);support[y0:y1,x0:x1]=a>0
assert np.array_equal(new[~support],base[~support]);assert np.array_equal(new[3712:],base[3712:]);assert np.array_equal(new[:,:384],base[:,:384])
core=save(O/'candidate-4096.png',new);ctx[115:4211,115:4211]=new;context=save(O/'context-4326.png',ctx)
manifest={k:old[k] for k in ('schemaVersion','id','base','baseContext','actualNative','receipt','preparation','nativeCrop','destinationCoreBox','alpha','minimumErrorPaths','seamWidths','fadePixels','blendArithmetic','RGBColorCorrection','resampling')}
manifest.update(status='I01_repaired_pending_root_review_W01_unchanged_pending',core=core,context=context,independentScalarReplayExact=True,outsideMaskExact=True,south384PixelsExact=True,west384PixelsExact=True,formalAccepted=False,published=False)
write(O/'composition.json',manifest)
prior=rd(D/'prepared-index.json')['qa'];qa=rd(prior['path']);reusable=[];changed=[]
for e in qa['evidence']:
 if e['source']=='candidate':
  xx0,yy0,xx1,yy1=e['box'];intersect=bool(np.any(support[yy0:yy1,xx0:xx1]))
  if intersect:
   ne=save(O/(e['name']+'-100pct.png'),new[yy0:yy1,xx0:xx1]);ne.update(name=e['name'],box=e['box'],scale='1:1',resampling=False);changed.append(ne)
  else:
   assert np.array_equal(new[yy0:yy1,xx0:xx1],base[yy0:yy1,xx0:xx1]);reusable.append(dict(name=e['name'],priorStatus=e['status'],unchangedPixels=True))
 else:reusable.append(dict(name=e['name'],priorStatus=e['status'],unchangedPixels=True))
write(O/'evidence-index.json',dict(priorQA=prior,core=core,changedEvidence=changed,reusedEvidence=reusable,formalAccepted=False))
print(json.dumps(dict(core=core,context=context,composition=ev(O/'composition.json'),changedEvidence=changed,reusedCount=len(reusable))))

