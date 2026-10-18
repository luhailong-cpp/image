import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';pre='external-r08c04-1017-v8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def load(r):
 p=Path(r['path']);assert sha(p)==r['sha256'];return np.array(Image.open(p).convert('RGB'))
def png(n,a):
 p=q/(pre+'-'+n+'.png');assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
base=q/'external-r08c04-1017-v7-trace.json';bt=json.loads(base.read_text());prep=q/(pre+'-local-preparation.json');pr=json.loads(prep.read_text());repair=next(x for x in pr['repairs'] if x['id']=='f2')
ctx={e['tile']:load(e['context']) for e in bt['tiles']};cores={k:v[115:4211,115:4211].copy() for k,v in ctx.items()};coords={'r08_c04':(0,0),'r08_c05':(4096,0),'r09_c04':(0,4096),'r09_c05':(4096,4096)}
box=repair['tileContextBox'];mp=Path(repair['mask']['path']);assert sha(mp)==repair['mask']['sha256'];mask=np.load(mp).astype(bool);new=load(repair['native'])
for tile,(tx,ty) in coords.items():
 l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
 if l<r and t<b:
  sel=mask[t-box[1]:b-box[1],l-box[0]:r-box[0]];cores[tile][t-ty:b-ty,l-tx:r-tx][sel]=new[t-box[1]:b-box[1],l-box[0]:r-box[0]][sel]
def crop(box):
 l,t,r,b=box;out=np.zeros((b-t,r-l,3),np.uint8)
 for tile,(tx,ty) in coords.items():
  x=max(l,tx);y=max(t,ty);xx=min(r,tx+4096);yy=min(b,ty+4096)
  if x<xx and y<yy:out[y-t:yy-t,x-l:xx-l]=cores[tile][y-ty:yy-ty,x-tx:xx-tx]
 return out
idx=json.loads((z/'art-delivery-index.json').read_text());accepted={t['tile']:t for t in idx['artAccepted']}
tr={'status':'repair_required_not_exportable','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseTrace':ref(base),'repairPreparation':ref(prep),'adoptedRepairs':['f2'],'unselectedRepair':'e2','script':ref(Path(__file__)),'noResize':True,'noFeather':True,'sourcePixelIdentity':True,'tiles':[],'qa':[]}
for tile,ar in ctx.items():
 cx,cy=coords[tile];cx-=115;cy-=115
 for other,core in cores.items():
  ox,oy=coords[other];l=max(cx,ox);t=max(cy,oy);r=min(cx+4326,ox+4096);b=min(cy+4326,oy+4096)
  if l<r and t<b:ar[t-cy:b-cy,l-cx:r-cx]=core[t-oy:b-oy,l-ox:r-ox]
 ent={'tile':tile,'context':png(tile+'-context-native',ar),'candidate':png(tile+'-candidate-4096',cores[tile])}
 if tile in accepted:
  a=load(accepted[tile]['file']);diff=np.any(a!=cores[tile],axis=2);ys,xs=np.where(diff);ent['versusAccepted']={'input':accepted[tile]['file'],'changedPixelCount':int(len(xs)),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'north230Same':bool(np.array_equal(a[:230],cores[tile][:230])),'south230Same':bool(np.array_equal(a[-230:],cores[tile][-230:])),'west230Same':bool(np.array_equal(a[:,:230],cores[tile][:,:230])),'east230Same':bool(np.array_equal(a[:,-230:],cores[tile][:,-230:]))}
 tr['tiles'].append(ent)
for name,box in [('stair-footer',[3000,1700,4254,2300]),('four-corner',[3596,3596,4596,4596]),('wall-top-join',[3750,3200,4450,3900])]:
 tr['qa'].append(dict(png(name+'-100pct',crop(box)),coreMosaicBox=box))
p=q/(pre+'-trace.json');assert not p.exists();p.write_text(json.dumps(tr,indent=2),encoding='utf-8');print(json.dumps({'trace':ref(p),'tiles':tr['tiles'],'qa':tr['qa']}))

