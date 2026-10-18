import sys,json,hashlib,datetime,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';pre='external-r08c04-1016-v6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def png(s,a):
 p=q/(pre+'-'+s+'.png');assert not p.exists();Image.fromarray(a).save(p);return dict(ref(p),size=[a.shape[1],a.shape[0]])
base=q/'join-r08c04-1016-v4-trace.json';bt=json.loads(base.read_text())
contexts={t['tile']:np.array(Image.open(t['context']['path']).convert('RGB')) for t in bt['tiles']}
se=q/'west-corner-r08r09c04c05-v3-r09_c05-context-native.png';contexts['r09_c05']=np.array(Image.open(se).convert('RGB'))
tiles={k:a[115:4211,115:4211].copy() for k,a in contexts.items()};coords={'r08_c04':(0,0),'r08_c05':(4096,0),'r09_c04':(0,4096),'r09_c05':(4096,4096)}
rp=q/'repair-compose.py';sp=importlib.util.spec_from_file_location('rc',rp);rc=importlib.util.module_from_spec(sp);sp.loader.exec_module(rc)
hp=z/'tools/seam_helpers.py';sp=importlib.util.spec_from_file_location('sh',hp);sh=importlib.util.module_from_spec(sp);sp.loader.exec_module(sh)
def crop(box):
 out=np.zeros((1254,1254,3),np.uint8)
 for tile,(tx,ty) in coords.items():
  l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
  if l<r and t<b:out[t-box[1]:b-box[1],l-box[0]:r-box[0]]=tiles[tile][t-ty:b-ty,l-tx:r-tx]
 return out
repairs=[]
for key,bounds in [('d',[0,100,1200,1254]),('e',[250,330,1100,850]),('f',[100,100,1180,1100])]:
 stem='r08_c04_repair_'+key+'_external_1016_v1';req=json.loads((z/'native'/(stem+'.request.json')).read_text());box=req['coordinates']['tileContextBox'];old=crop(box);native=z/'native'/(stem+'.png');new=np.array(Image.open(native).convert('RGB'));mask,paths=rc.closed_mask(old,new,bounds,20,box,sh._minimum_vertical_seam)
 # Shared native repair is applied to every affected core.
 after=np.where(mask[:,:,None].astype(bool),new,old)
 for tile,(tx,ty) in coords.items():
  l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
  if l<r and t<b:
   sel=mask[t-box[1]:b-box[1],l-box[0]:r-box[0]].astype(bool)
   tiles[tile][t-ty:b-ty,l-tx:r-tx][sel]=new[t-box[1]:b-box[1],l-box[0]:r-box[0]][sel]
 mp=q/(pre+'-'+key+'-mask.npy');assert not mp.exists();np.save(mp,mask,allow_pickle=False)
 repairs.append({'id':key,'native':ref(native),'generation':ref(z/'native'/(stem+'.png.generation.json')),'source':req['references'][0],'tileContextBox':box,'bounds':bounds,'mask':ref(mp),'paths':paths,'after':png(key+'-after-1254',after),'sharedNativeRepair':True})
# All halo pixels for known cores come from the owner core, never interpolated.
for tile,ctx in contexts.items():
 cx,cy=coords[tile];cx-=115;cy-=115
 for other,core in tiles.items():
  ox,oy=coords[other];l=max(cx,ox);t=max(cy,oy);r=min(cx+4326,ox+4096);b=min(cy+4326,oy+4096)
  if l<r and t<b:ctx[t-cy:b-cy,l-cx:r-cx]=core[t-oy:b-oy,l-ox:r-ox]
trace={'status':'candidate_pending_external_geometry_qa','baseTrace':ref(base),'extraCornerContext':ref(se),'repairs':repairs,'script':ref(Path(__file__)),'noResize':True,'noFeather':True,'sharedNativeRepairAcrossAffectedCores':True,'tiles':[]}
for tile,a in contexts.items():
 original=next((np.array(Image.open(t['candidate']['path']).convert('RGB')) for t in bt['tiles'] if t['tile']==tile),None)
 if original is None:original=np.array(Image.open(se).convert('RGB'))[115:4211,115:4211]
 diff=np.any(tiles[tile]!=original,axis=2);ys,xs=np.where(diff);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
 if tile in ['r08_c05','r09_c05']:assert np.array_equal(tiles[tile][:,-230:],original[:,-230:]),'c06 shared edge rollback'
 trace['tiles'].append({'tile':tile,'context':png(tile+'-context-native',a),'candidate':png(tile+'-candidate-4096',tiles[tile]),'coreChanged':bool(len(xs)),'changedPixelCount':int(len(xs)),'actualPixelChangeBbox':bbox,'c06SideLast230Unchanged':True if tile in ['r08_c05','r09_c05'] else None})
p=q/(pre+'-trace.json');assert not p.exists();p.write_text(json.dumps(trace,indent=2),encoding='utf-8');print(json.dumps({'trace':ref(p),'outputs':[x['after'] for x in repairs]}))

