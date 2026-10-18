import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent;repo=z.parents[3]
sp=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(sp);sp.loader.exec_module(prod)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
tile='r13_c05';patch=sys.argv[1];version=sys.argv[2] if len(sys.argv)>2 else 'v1';stem=f'{tile}_{patch}_{version}'
for suffix in ['.png','.request.json']:assert not (z/'native'/(stem+suffix)).exists(),stem
rules=[]
for rel,expected in [('AGENTS.md','57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'),('docs/MAP_PARALLEL_SPLIT_20261013.json','929a52abdb55e6022f83abbe9b48718182bc33fc8a0bc2d50a14f6232dd4e850')]:
 p=repo/rel;content=p.read_bytes();actual=hashlib.sha256(content).hexdigest()
 if actual!=expected:print(content.decode('utf-8-sig'));raise SystemExit('Rules changed; review before continuing')
 rules.append({'path':p.as_posix(),'sha256':actual,'readBeforeRequest':True})
split=read(repo/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert not any(tile in b['tiles'] for b in split['batches'] if b.get('map')=='fishing-village-game-20261009' and b.get('status')=='allocated_root_reserved')
prod.prepare(tile,patch,version)
rp=z/'native'/(stem+'.request.json');r=read(rp);b=r['coordinates']['globalContextBox'];dst=Path(r['references'][0]['path']);canvas=Image.open(z/'layout-only'/f'{tile}_{patch}.png').convert('RGB');anchors=[]
# Retain only this worker's own selected native patches, then overlay accepted
# neighboring contexts. The independently running r14_c05 queue is not an anchor.
local_sources=[s for s in r['overlaps'] if Path(s['path']).name.startswith(tile+'_')]
for s in local_sources:
 box=read(Path(s['path']+'.generation.json'))['coordinates']['globalContextBox'];i=s['globalOverlapBox']
 with Image.open(s['path']) as im:
  canvas.paste(im.crop((i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1])),(i[0]-b[0],i[1]-b[1]))
r['overlaps']=local_sources
idx=read(z/'art-delivery-index.json')
for a in idx['artAccepted']:
 rr,cc=int(a['tile'][1:3]),int(a['tile'][5:7])
 if abs(rr-13)+abs(cc-5)!=1:continue
 box=[(cc-1)*4096-115,(rr-1)*4096-115,cc*4096+115,rr*4096+115]
 i=[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]
 if i[2]<=i[0] or i[3]<=i[1]:continue
 source=Path(a['nativeContext']['path']);assert prod.sha(source)==a['nativeContext']['sha256']
 with Image.open(source) as im:
  assert im.size==(4326,4326)
  canvas.paste(im.crop((i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1])),(i[0]-b[0],i[1]-b[1]))
 anchors.append({'path':source.as_posix(),'sha256':prod.sha(source),'tile':a['tile'],'globalOverlapBox':i,'operation':'integer crop and paste only'})
canvas.save(dst);r['currentFinalAnchors']=anchors;r['rulesReadBeforeRequest']=rules;prod.write(rp,r)
dp=Path(str(dst)+'.derivation.json');d=read(dp);d.update({'sha256':prod.sha(dst),'nativeSources':local_sources,'currentFinalAnchors':anchors});prod.write(dp,d)
print(json.dumps({'stem':stem,'guide':dst.as_posix(),'anchors':anchors,'references':r['references']}))
