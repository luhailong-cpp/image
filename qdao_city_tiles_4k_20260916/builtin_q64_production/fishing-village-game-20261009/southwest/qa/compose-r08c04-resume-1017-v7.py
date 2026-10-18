import sys,json,hashlib,datetime,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';pre='external-r08c04-1017-v7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def png(name,a):
 p=q/(pre+'-'+name+'.png');assert not p.exists();Image.fromarray(a).save(p);return dict(ref(p),size=[a.shape[1],a.shape[0]])
def load(r):
 p=Path(r['path']);assert sha(p)==r['sha256'];return np.array(Image.open(p).convert('RGB'))
base=q/'external-r08c04-1016-v6-trace.json';bt=json.loads(base.read_text())
contexts={t['tile']:load(t['context']) for t in bt['tiles']};cores={t:a[115:4211,115:4211].copy() for t,a in contexts.items()}
coords={'r08_c04':(0,0),'r08_c05':(4096,0),'r09_c04':(0,4096),'r09_c05':(4096,4096)}
def crop(box):
 l,t,r,b=box;out=np.zeros((b-t,r-l,3),np.uint8)
 for tile,(tx,ty) in coords.items():
  x=max(l,tx);y=max(t,ty);x2=min(r,tx+4096);y2=min(b,ty+4096)
  if x<x2 and y<y2:out[y-t:y2-t,x-l:x2-l]=cores[tile][y-ty:y2-ty,x-tx:x2-tx]
 return out
sp=importlib.util.spec_from_file_location('rc',q/'repair-compose.py');rc=importlib.util.module_from_spec(sp);sp.loader.exec_module(rc)
sp=importlib.util.spec_from_file_location('sh',z/'tools/seam_helpers.py');sh=importlib.util.module_from_spec(sp);sp.loader.exec_module(sh)
stem='r08_c04_repair_d_external_1016_v2';req=json.loads((z/'native'/(stem+'.request.json')).read_text());box=req['coordinates']['tileContextBox']
old=crop(box);assert np.array_equal(old,load(req['references'][0]))
native=z/'native'/(stem+'.png');gen=json.loads(Path(str(native)+'.generation.json').read_text());assert sha(native)==gen['sha256']
new=np.array(Image.open(native).convert('RGB'));bounds=[100,250,1235,1254];mask,paths=rc.closed_mask(old,new,bounds,75,box,sh._minimum_vertical_seam)
after=np.where(mask[:,:,None].astype(bool),new,old)
l,t,r,b=box;cores['r08_c04'][t:b,l:r]=after
mp=q/(pre+'-d2-mask.npy');assert not mp.exists();np.save(mp,mask,allow_pickle=False)
trace={'status':'pending_native_visual_qa','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseTrace':ref(base),'nativeRepair':ref(native),'generation':ref(Path(str(native)+'.generation.json')),'source':req['references'][0],'mask':ref(mp),'paths':paths,'bounds':bounds,'tileContextBox':box,'script':ref(Path(__file__)),'noResize':True,'noFeather':True,'sourcePixelIdentity':True,'tiles':[],'qa':[]}
trace['qa'].append(dict(png('d2-after-1254',after),role='repair_interior'))
for name,bb in [('d2-top',[l,t-150,r,t+200]),('d2-bottom',[l,b-200,r,b+150]),('d2-left',[l-150,t,l+250,b]),('d2-right',[r-250,t,r+150,b])]:trace['qa'].append(dict(png(name+'-100pct',crop(bb)),role='repair_perimeter',coreMosaicBox=bb))
for tile,ctx in contexts.items():
 cx,cy=coords[tile];cx-=115;cy-=115
 for other,core in cores.items():
  ox,oy=coords[other];x=max(cx,ox);y=max(cy,oy);r=min(cx+4326,ox+4096);b=min(cy+4326,oy+4096)
  if x<r and y<b:ctx[y-cy:b-cy,x-cx:r-cx]=core[y-oy:b-oy,x-ox:r-ox]
 trace['tiles'].append({'tile':tile,'context':png(tile+'-context-native',ctx),'candidate':png(tile+'-candidate-4096',cores[tile])})
p=q/(pre+'-trace.json');assert not p.exists();p.write_text(json.dumps(trace,indent=2),encoding='utf-8');print(json.dumps({'trace':ref(p),'qa':trace['qa']}))

