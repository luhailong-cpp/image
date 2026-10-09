"""Build a private, source-bound preparation checkpoint; never publish root state."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent;O=N/'prepared-state-v005';O.mkdir(exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=read(T/'source-checkpoint.json');inputref=ref(T/'source-checkpoint.json'); save(O/'root-input.json',cp)
sources={v['tile']:v for v in cp['candidateSet']}; images={}; chains={}
queue=[('r04_c01-v1/join-v3/manifest.json','cb9b50ae45324fb04607e597dfad1af360dcb282647123aff49bbbedead03ec8'),('r01_c02-v1/join-v1/manifest.json','dd8175f11c188decdc5e8569960ae2da2707ae8d2616629fd74d7500968b3fa6')]
for rel,expected in queue:
 p=N/rel;assert sha(p)==expected;m=read(p);assert m['localVisualAccepted']
 for patch in m['patches']:
  tile=patch['destinationTile'];v=sources[tile]
  if tile not in images:
   assert sha(v['file'])==v['sha256'];images[tile]=Image.open(v['file']).convert('RGBA');chains[tile]=[]
  box=patch['destinationTileLTRB']; prior=patch.get('requiredPriorSource');asset=patch['asset']
  assert sha(asset['file'])==asset['sha256'];a=Image.open(asset['file']).convert('RGBA');assert a.size==(box[2]-box[0],box[3]-box[1])
  current=np.asarray(images[tile].crop(box))
  if prior:
   assert sha(prior['file'])==prior['sha256'];assert np.array_equal(current,np.asarray(Image.open(prior['file']).convert('RGBA').crop(box)))
  else:assert np.all(current[:,:,3]==0)
  images[tile].paste(a,tuple(box[:2]));chains[tile].append({'manifest':ref(p),'patch':patch['name']})
for tile,im in images.items():
 out=O/(tile+'.png');im.save(out);covered=int((np.asarray(im)[:,:,3]==255).sum())
 save(O/(tile+'.png.generation.json'),{'file':str(out),'sha256':sha(out),'derivedFrom':[sources[tile]],'applied':chains[tile],'newModelCalls':0,'nativeScale':1,'operation':'Private exact native ROI composition for dependent preparation only','actualModel':None,'actualQuality':None,'rootPublished':False,'formalAccepted':False})
 sources[tile]={**sources[tile],**ref(out),'generationRecord':str(O/(tile+'.png.generation.json')),'fullyPainted':covered==4096**2,'partialFragment':covered<4096**2}
cp['candidateSet']=sorted(sources.values(),key=lambda v:v['tile']);cp['fragment']=sources['r09_c11'];cp['rootPublished']=False;cp['privatePreparationOnly']=True;cp['rootInput']=ref(O/'root-input.json');cp['rootInputAtRead']=inputref
save(O/'source-checkpoint.json',cp)
assert sha(T/'source-checkpoint.json')==inputref['sha256']
print(json.dumps(ref(O/'source-checkpoint.json')))
