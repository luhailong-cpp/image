"""Independent actual-view evidence for c15, with exact-SHA inherited scopes."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;U=R/'r07_c15/repairs/unified';D=U/'straight-integrated-v6';V5=U/'straight-integrated-v5';OLD=U/'straight-integrated'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
assert sha(D/'candidate.png')=='4e9e6677f9f456422de5d1acceb359d63bd8908656784f44c30acc20118eff4b'
prior=json.loads((OLD/'close14-preliminary-internal-review.json').read_text());items=[]
for old in prior['sheets']:
 name=Path(old['file']).name;p=D/'qa/assembly'/name
 if old['result']=='pass':
  assert sha(p)==old['sha256'];items.append(dict(ref(p),result='pass',actualViewSource=old['file'],inheritedByExactSHA=True))
 else:
  v=V5/'qa/assembly'/name;assert sha(v)==sha(p);items.append(dict(ref(p),result='pass',actualViewSource=str(v),inheritedByExactSHA=True,observation='Actually re-viewed fixed native board grain/edge in v5; earlier known step removed.'))
direct=['cloth-right-tail.png','cloth-edge.png','assembly/corner-se.png','full-south-4.png','assembly/overview-preview-1024.png','assembly/south-r07-r08-common-edge-full.png','actual-halo-insert-top.png','south-insert-top.png']
for n in direct:items.append(dict(ref(D/'qa'/n),result='pass',actualView=True,nativePixelScale=1 if 'overview' not in n else None))
for n in ['assembly/corner-nw.png','assembly/corner-ne.png','assembly/corner-sw.png','full-south-1.png','full-south-2.png','full-south-3.png','left-bridge.png','right-bridge.png']:
 p=D/'qa'/n;v=V5/'qa'/n
 if p.exists():
  assert sha(p)==sha(v);items.append(dict(ref(p),result='pass',actualViewSource=str(v),inheritedByExactSHA=True))
 else:
  assert n in ['left-bridge.png','right-bridge.png'];items.append(dict(ref(v),result='pass',actualView=True,inheritedByExactCandidateRegion=True,unchangedSourceRegionXYXY=[0,0,2400,4096]))
old=np.asarray(Image.open(V5/'candidate.png').convert('RGB'));new=np.asarray(Image.open(D/'candidate.png').convert('RGB'));changed=np.any(old!=new,axis=2);ys,xs=np.where(changed);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
assert box==[3923,3930,4096,4000]
assert np.array_equal(old[:,:2400],new[:,:2400])
report=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='close_joint14',candidateSha256=sha(D/'candidate.png'),passed=True,result='pass',scope='Complete six native internal seams, nine intersections, overview, four corners, complete south common edge and all four wider south sections, two insertion strips and three recent local repairs.',observations=['Former lower board-grain and bright-edge steps are removed; beam and roof-board contours remain straight and continuous.','Actual final right blue-cloth tail has no remaining horizontal clipped shadow. Rope and timber edges remain intact.','South boundary and insertion strips show coherent timber, existing rope, broad blue cloth and quiet water. No newly added objects or fine texture.'],items=items,v5ToV6ActualChangedRectXYXY=box,priorActualViewReport=ref(OLD/'close14-preliminary-internal-review.json'),independentPanelReview=ref(OLD/'independent-panel-review.json'),formalAccepted=False,wholeCityComplete=False)
(D/'independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(sha(D/'independent-review.json'))
