from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
OUT=Path(__file__).resolve().parent
RESUME=OUT.parents[1]
JOIN=RESUME/'tools/neighbor_join_v5'
V6=RESUME/'tools/repairs/versions/r09_c09_repair_v6'
OLD=RESUME/'tools/repairs/versions/r09_c09_repair_v4/r09_c09.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def im(p):
 x=Image.open(p).convert('RGB');x.load();return x
def check(item,base=None):
 p=Path(item['file']);p=p if p.is_absolute() else base/p
 return {'file':str(p),'expectedSha256':item['sha256'],'actualSha256':sha(p),'matches':sha(p)==item['sha256']}
j=json.loads((JOIN/'assembly-v5.json').read_text(encoding='utf-8'))
r=json.loads((V6/'repair.json').read_text(encoding='utf-8'))
checks=[check(x) for x in j['sourceFiles']+j['files']+j['qa']]
v6checks=[check(x,V6) for x in r['files'].values()]+[check(r[k]) for k in ['sourceCandidate','sourceRecord','prepared','originalNativeOutput']]
v4im=im(OLD);v5im=im(JOIN/'output/r09_c09.png');v6im=im(V6/'r09_c09.png')
a4=np.array(v4im);a5=np.array(v5im);a6=np.array(v6im)
leftpath=Path(next(x['file'] for x in j['sourceFiles'] if Path(x['file']).name=='r09_c08.png'))
bottompath=Path(next(x['file'] for x in j['sourceFiles'] if Path(x['file']).name=='r10_c09.png'))
left=im(leftpath);bottom=im(bottompath)
flow=np.load(JOIN/'output/flow.npz')['flow'][115:4211,115:4211]
mask=np.array(Image.open(JOIN/'output/mask.png'))[115:4211,115:4211]
nearcap=np.any(np.abs(flow)>=7.999,axis=2)&(mask>0)
exactcap=np.any(np.abs(flow)>=8.0,axis=2)&(mask>0)
points=set(map(tuple,np.argwhere(nearcap).tolist()));groups=[]
while points:
 q=[points.pop()];g=[]
 while q:
  y,x=q.pop();g.append((y,x))
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    p=(y+dy,x+dx)
    if p in points:points.remove(p);q.append(p)
 ys,xs=zip(*g);groups.append({'boundsLTRB':[min(xs),min(ys),max(xs)+1,max(ys)+1],'pixels':len(g)})
evidence=[]
def emit(name,image,box,role):
 p=OUT/(name+'.png');image.save(p);evidence.append({'file':str(p),'sha256':sha(p),'sourceBoxRelativeToTileLTRB':box,'resized':False,'role':role})
v=Image.new('RGB',(512,4096));v.paste(left.crop((3840,0,4096,4096)),(0,0));v.paste(v5im.crop((0,0,256,4096)),(256,0))
for y in [710,3107,3528]:emit(f'near_cap_left_y{y}',v.crop((0,y-256,512,y+256)),[-256,y-256,256,y+256],'native left-seam cap cluster support')
h=Image.new('RGB',(4096,512));h.paste(v5im.crop((0,3840,4096,4096)),(0,0));h.paste(bottom.crop((0,0,4096,256)),(0,256))
emit('near_cap_bottom_x3597',h.crop((3341,0,3853,512)),[3341,3840,3853,4352],'native bottom-seam cap cluster support')
unchanged_junctions=[]
v6junctions=[]
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  box=[x-256,y-256,x+256,y+256]
  c4=v4im.crop(box).tobytes();c5=v5im.crop(box).tobytes();c6=v6im.crop(box).tobytes()
  unchanged_junctions.append({'xy':[x,y],'v5PixelsEqualV4':c5==c4,'v4RawPixelSha256':hashlib.sha256(c4).hexdigest(),'v5RawPixelSha256':hashlib.sha256(c5).hexdigest()})
  e={'xy':[x,y],'v6PixelsEqualV5':c6==c5,'v5RawPixelSha256':hashlib.sha256(c5).hexdigest(),'v6RawPixelSha256':hashlib.sha256(c6).hexdigest()}
  if c6!=c5:emit(f'v6_junction_x{x}_y{y}',v6im.crop(box),box,'v6 changed junction, fresh original-pixel review required')
  v6junctions.append(e)
box=r['canvasBoxLTRB'];fullmask=np.zeros((4096,4096),dtype=np.uint8);fullmask[box[1]:box[3],box[0]:box[2]]=np.array(Image.open(V6/'mask.png').convert('L'))
changed=np.any(a6!=a5,axis=2)
proof={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'v5Assembly':str(JOIN/'assembly-v5.json'),'v5AssemblySha256':sha(JOIN/'assembly-v5.json'),
 'v5Candidate':str(JOIN/'output/r09_c09.png'),'v5Sha256':sha(JOIN/'output/r09_c09.png'),
 'v5Checks':checks,'v5FailedChecks':sum(not c['matches'] for c in checks),
 'v5InteriorEqualsV4':bool(np.array_equal(a4[:3881,215:],a5[:3881,215:])),
 'v5InternalJunctionInheritance':unchanged_junctions,
 'v5NearCap':{'thresholdPixels':7.999,'maskRule':'effective core mask>0','pixelCount':int(nearcap.sum()),'exactEightPixelCount':int(exactcap.sum()),'clusters':groups,
  'interpretation':'Cap counts identify areas to inspect. They do not establish pass or failure.'},
 'v6Candidate':str(V6/'r09_c09.png'),'v6Sha256':sha(V6/'r09_c09.png'),'v6RepairRecordSha256':sha(V6/'repair.json'),
 'v6Checks':v6checks,'v6FailedChecks':sum(not c['matches'] for c in v6checks),
 'v6ChangedPixels':int(changed.sum()),'v6ChangesOutsideMask':int(np.logical_and(changed,fullmask==0).sum()),
 'v6LeftTreatmentBandUnchanged':bool(np.array_equal(a5[:,:375],a6[:,:375])),
 'v6BottomTreatmentBandUnchanged':bool(np.array_equal(a5[3720:],a6[3720:])),
 'v6FullRepairContextMatchesFinalCrop':im(V6/'context-after.png').tobytes()==v6im.crop(box).tobytes(),
 'v6InternalJunctionInheritance':v6junctions,'extraEvidence':evidence}
(OUT/'verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:proof[k] for k in ['v5FailedChecks','v5InteriorEqualsV4','v5NearCap','v6FailedChecks','v6ChangesOutsideMask','v6LeftTreatmentBandUnchanged','v6BottomTreatmentBandUnchanged','v6FullRepairContextMatchesFinalCrop']},indent=2))
