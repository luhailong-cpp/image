from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
import json,hashlib
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005');A=P/'parent_audit_20261008';D=P/'donghai_lantern';T=D/'r08_c13'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
checks=[];cache={}
def bind(o):
 p=Path(o.get('file') or o.get('path'));expected=o['sha256'];key=(str(p),expected)
 if key not in cache:
  exists=p.is_file();actual=sha(p) if exists else None
  cache[key]={'path':p.as_posix(),'expectedSha256':expected,'actualSha256':actual,'exists':exists,'matches':actual==expected}
  assert actual==expected,cache[key]
 return cache[key]
def all_bindings(node):
 if isinstance(node,list):
  for x in node:all_bindings(x)
 elif isinstance(node,dict):
  if isinstance(node.get('sha256'),str) and isinstance(node.get('file') or node.get('path'),str):bind(node)
  for v in node.values():
   if isinstance(v,(dict,list)):all_bindings(v)
manifests=[]
for f in ['completed-candidate-v2/output/integration-manifest.json','completed-candidate/output/integration-manifest.json','right-stone-sync/tone-matched/output/integration-manifest.json','west-final/output/west-final-manifest.json','internal-repaired/output/internal-integration-manifest.json','tone-assembly/output/tone-assembly-manifest.json']:
 p=T/f;all_bindings(read(p));manifests.append(ref(p))
base_m=read(T/'completed-candidate/output/integration-manifest.json');m=read(T/'completed-candidate-v2/output/integration-manifest.json')
rebuilt=np.concatenate([rgb(x['file']) for x in base_m['derivedFrom']],axis=1)
for job in base_m['repairs']:
 n=rgb(job['native']['file']);mask=np.asarray(Image.open(job['mask']['file']).convert('L'));x,y=job['nativePairXY'];v=rebuilt[y:y+1254,x:x+1254];alpha=mask[:,:,None].astype(np.uint32)
 v[:]=((v.astype(np.uint32)*(255-alpha)+n.astype(np.uint32)*alpha+127)//255).astype(np.uint8)
assert np.array_equal(rebuilt,rgb(base_m['pair']['file']))
base=rebuilt.copy();n=rgb(m['derivedFrom'][1]['file']);mask=np.asarray(Image.open(m['mask']['file']).convert('L'));x,y,_,_=m['mask']['nativePairCropXYXY'];v=rebuilt[y:y+1254,x:x+1254];alpha=mask[:,:,None].astype(np.uint32)
v[:]=((v.astype(np.uint32)*(255-alpha)+n.astype(np.uint32)*alpha+127)//255).astype(np.uint8)
assert np.array_equal(rebuilt,rgb(m['pair']['file']))
support=np.zeros(base.shape[:2],bool);support[y:y+1254,x:x+1254]=mask>0
assert np.array_equal(rebuilt[~support],base[~support])
tiles=[]
for i,o in enumerate(m['tiles']):
 b=rgb(o['file']);assert b.shape==(4096,4096,3);assert np.array_equal(b,rebuilt[:,4096*i:4096*(i+1)])
 im=Image.open(o['file']);assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
 tiles.append({'tileId':Path(o['file']).stem,'core':ref(o['file']),'generationRecord':ref(o['file']+'.generation.json'),'pixelExactPairCrop':True,'pixels':[4096,4096],'opaque':True})
native=[]
for r in range(1,5):
 for c in range(1,5):
  p=T/'native'/f'r{r:02d}_c{c:02d}.png';g=read(str(p)+'.generation.json');bind(g);assert Image.open(p).size==(1254,1254)
  assert g['actualModel'] is None and g['actualQuality'] is None
  bind({'file':g['prompt'],'sha256':g['promptSha256']});bind({'file':g['requestFile'],'sha256':g['requestSha256']})
  all_bindings(g['references']);all_bindings(g['geometryMatchedTo'])
  native.append({'image':ref(p),'record':ref(str(p)+'.generation.json'),'sourcePixels':[1254,1254],'actualModel':None,'actualQuality':None})
reviews=[]
for folder in ['completed-candidate','completed-candidate-v2']:
 q=T/folder/'qa/review.json';d=read(q);all_bindings(d)
 pair=rgb(d['pair']['file']);qachecks=[]
 for qref in d['actualViewed']:
  qg=read(qref['file']+'.generation.json');box=qg.get('pairCropXYXY') or qg['sourceCropPairXYXY'];l,t,r,b=box
  assert np.array_equal(rgb(qref['file']),pair[t:b,l:r])
  qachecks.append({'image':ref(qref['file']),'pairCropXYXY':box,'pixelExact':True})
 reviews.append({'review':ref(q),'ownerResult':d['result'],'scope':d['scope'],'qaPixelBindings':qachecks,'independentVisualReinspection':False})
selp=D/'current-selection.json';sel=read(selp);regp=D/'current-candidates.json';reg=read(regp)
for t in tiles:
 selected=next((e for e in sel['candidates'] if e.get('tile')==t['tileId']),None)
 registered=next((e for e in reg['candidates'] if e.get('tile')==t['tileId']),None)
 t['selectionMatches']=bool(selected and selected['sha256']==t['core']['sha256'] and Path(selected['file']).resolve()==Path(t['core']['path']).resolve())
 t['registryMatches']=bool(registered and registered['sha256']==t['core']['sha256'])
 t['selectedEntry']=selected
proof={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'bounded_source_and_QA_pixel_binding_verified_waiting_current_selection' if not all(t['selectionMatches'] and t['registryMatches'] for t in tiles) else 'current_selection_sources_and_scoped_QA_bound','baseParentIndex':ref(A/'verified-current-index.json'),'selectionSource':ref(selp),'authoritativeRegistry':ref(regp),'tiles':tiles,'manifestChain':manifests,'nativeSourceCount':16,'nativeSources':native,'allListedBindings':list(cache.values()),'lastThreeRepairCompositeReplayPixelExact':True,'lastColorOutsideMaskChangedPixels':0,'pairToTwoTilesPixelExact':True,'ownerScopedReviews':reviews,'formalAccepted':False,'remainingLimitations':['DAY paving geometry synchronization explicitly pending.','Only owner-recorded targeted visual scopes are inherited; no independent visual re-review or full tile, city or client acceptance.'],'childModified':False}
p=A/'donghai-lantern-c13-source-audit.json';p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'file':str(p),'sha256':sha(p),'status':proof['status'],'bindingCount':len(cache),'tiles':[{k:t[k] for k in ['tileId','selectionMatches','registryMatches']} for t in tiles]}))
