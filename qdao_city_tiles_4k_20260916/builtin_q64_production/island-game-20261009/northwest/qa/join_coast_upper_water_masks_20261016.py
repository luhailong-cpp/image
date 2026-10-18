from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
stems=['r03_c01_upper_water_left_20261016_a01','r03_c01_upper_water_center_20261016_a01']
original=[Z/'qa'/f'{s}_mask_v1/source_selection_mask.png' for s in stems]
m=[np.array(Image.open(p))==255 for p in original]
a,b=[np.array(Image.open(Z/'native'/f'{s}.png').convert('RGB')) for s in stems]
e=((a[:,1100:].astype(float)-b[:,:154].astype(float))**2).mean(2)
cost=e[0].copy();prev=np.zeros(e.shape,np.int8)
for y in range(1,1254):
 c=np.stack([np.r_[np.inf,cost[:-1]],cost,np.r_[cost[1:],np.inf]])
 choice=np.argmin(c,axis=0);prev[y]=choice-1;cost=c[choice,np.arange(154)]+e[y]
seam=np.empty(1254,np.int32);seam[-1]=np.argmin(cost)
for y in range(1253,0,-1):seam[y-1]=seam[y]+prev[y,seam[y]]
both=m[0][:,1100:]&m[1][:,:154];left=np.arange(154)[None,:]<seam[:,None]
m[0][:,1100:] &= ~both|left
m[1][:,:154] &= ~both|~left
assert not (m[0][:,1100:]&m[1][:,:154]).any()
out=Z/'qa/r03_c01_upper_water_pair_masks_20261016_v1';out.mkdir()
base=np.array(Image.open(Z/'tiles/r03_c01_candidate-v6_4096.png').convert('RGB'))
for i,(s,mask,x) in enumerate(zip(stems,m,[0,1100])):
 mp=out/f'{s}.mask.png';Image.fromarray(mask.astype('uint8')*255).save(mp)
 raw=np.array(Image.open(Z/'native'/f'{s}.png').convert('RGB'));base[550:1804,x:x+1254][mask]=raw[mask]
Image.fromarray(base[800:1500,900:1450]).save(out/'joined_overlap_100pct.png')
record=dict(operation='Exclusive same-coordinate selection between overlapping native repairs using minimum RGB error seam; no pixel synthesis',originalMasks=[info(p) for p in original],rawSources=[info(Z/'native'/f'{s}.png') for s in stems],outputMasks=[info(out/f'{s}.mask.png') for s in stems],seamXByY=seam.tolist(),overlapGlobalBox=[1100,550,1254,1804],resizing=False,feathering=False,colorCorrection=False,registration=False,allSelectedPixelsExactlyNative=True,reviewCrop=info(out/'joined_overlap_100pct.png'),visualStatus='pending')
(out/'derivation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(output=out.as_posix(),masks=record['outputMasks'])))
