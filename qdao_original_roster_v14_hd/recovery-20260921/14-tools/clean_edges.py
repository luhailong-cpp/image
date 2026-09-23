"""User-authorized color-only removal of neon edge contamination, 2026-09-23.
Does not change alpha, geometry, size, pose, or any non-neon pixel.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]/'14-delivery-preview/assets'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(path):
 im=Image.open(path).convert('RGBA');a=np.asarray(im).copy();rgb=a[:,:,:3].astype(int);alpha=a[:,:,3]
 visible=alpha>8
 neon=((rgb[:,:,0]-rgb[:,:,1]>80)&(rgb[:,:,2]-rgb[:,:,1]>80))|((rgb[:,:,2]-rgb[:,:,0]>120)&(rgb[:,:,2]-rgb[:,:,1]>120))
 candidate=np.zeros_like(visible);change=np.zeros_like(visible)
 clean_reference=(alpha>=224)&~neon
 before_sha=sha(path);before_alpha=hashlib.sha256(alpha.tobytes()).hexdigest();out=a.copy()
 for y,x in zip(*np.where(visible&neon)):
  y0,y1=max(0,y-8),min(a.shape[0],y+9);x0,x1=max(0,x-8),min(a.shape[1],x+9)
  yy,xx=np.ogrid[y0:y1,x0:x1];dist=(yy-y)**2+(xx-x)**2
  if not np.any((~visible[y0:y1,x0:x1])&(dist<=16)):continue
  candidate[y,x]=True;ok=clean_reference[y0:y1,x0:x1]&(dist<=64)
  if not ok.any():continue
  rr,cc=np.unravel_index(np.argmin(np.where(ok,dist,999)),dist.shape)
  out[y,x,:3]=a[y0+rr,x0+cc,:3];change[y,x]=True
 assert np.array_equal(out[:,:,3],a[:,:,3])
 assert np.array_equal(out[~change],a[~change])
 if change.any():Image.fromarray(out).save(path)
 stats={'operation':'color-only-neon-edge-despill','authorizedAt':'2026-09-23','processedAt':datetime.now(timezone.utc).isoformat(),'beforeSHA256':before_sha,'afterSHA256':sha(path),'candidatePixels':int(candidate.sum()),'changedPixels':int(change.sum()),'unresolvedCandidates':int((candidate&~change).sum()),'maxBoundaryDistancePx':4,'maxCleanReferenceDistancePx':8,'alphaSHA256Before':before_alpha,'alphaSHA256After':hashlib.sha256(out[:,:,3].tobytes()).hexdigest(),'alphaUnchanged':True,'geometryUnchanged':True,'nonCandidatePixelsUnchanged':True,'noNewFrameSynthesized':True}
 side=Path(str(path)+'.generation.json');meta=json.loads(side.read_text(encoding='utf-8'))
 history=meta.setdefault('colorCleanup',[])
 if change.any() or not history:history.append(stats)
 meta['sha256']=sha(path);side.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return {'file':str(path.relative_to(ROOT)),**stats}
def main():
 p=argparse.ArgumentParser();p.add_argument('--file',type=Path);a=p.parse_args();paths=[a.file.resolve()] if a.file else sorted(ROOT.rglob('*.png'))
 for p in paths:assert p.resolve().is_relative_to(ROOT.resolve())
 rows=[clean(p) for p in paths]
 report={'files':len(rows),'changedPixels':sum(x['changedPixels'] for x in rows),'unresolvedCandidates':sum(x['unresolvedCandidates'] for x in rows),'allAlphaUnchanged':all(x['alphaUnchanged'] for x in rows),'rows':rows}
 target=ROOT.parent/('color-cleanup.json' if not a.file else 'color-cleanup-trial.json');target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
if __name__=='__main__':main()
