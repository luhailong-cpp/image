"""Record actual native-pixel review and immutable-source checks for south scope."""
from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r07_c16 as a

R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/south-joint-color-v4'
def ref(p):return dict(file=str(p),sha256=a.sha(p))
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
assert a.sha(D/'candidate.png')=='098911dc49894dc80236dea0f8617660be97f1f1c0f1e17097b73cec718af6aa'
m=a.load_json(D/'manifest.json');base=rgb(m['baseline']['file']);out=rgb(D/'candidate.png');ex=rgb(D/'extended-context.png');oldex=rgb(T/'repairs/integrated-southwest-v3/extended-context.png')
mask=np.zeros((4096,4096),bool);mask[3790:4096,790:1400]=True
assert np.array_equal(base[~mask],out[~mask])
assert np.array_equal(out,ex[115:4211,115:4211])
halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False
assert np.array_equal(ex[halo],oldex[halo])
immutable={R/'r08_c16/output/r08_c16.png':'3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de',R/'r08_c16/output/extended-context.png':'0055b578b51057e9c05d6ca050bd83d84c20aae92bc72cd47d424610b6e02689',T/'output/r07_c16.png':'2dbf08054591651fb62f3477ef79926f2d7696f773eaf26b5f8f1b18d886a06a'}
for p,s in immutable.items():assert a.sha(p)==s
items=[]
for p,note in [(D/'mast-joint.png','Aligned timber and rope remain natural at native scale; no broad RGB cutoff. Tiny sloping highlight edge is material contour, not a flat stitch line.'),(D/'mast-top-insertion.png','No jagged top insertion color band or global x1270 vertical correction-field cutoff.'),(D/'qa/south-r07-r08-common-edge-full.png','All4096 south boundary viewed at native pixel scale in four unresampled bands; original rope, spar, timber, and quiet water continue naturally.'),(D/'qa/internal-vertical-x1024-full.png','All4096 internal seam viewed at native scale. Post and rope geometry intact; no residual insertion tone band.')]:
 items.append(dict(ref(p),actualView=True,nativePixelScale=1,result='pass',observation=note))
a.save_json(D/'independent-south-review.json',dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidate=ref(D/'candidate.png'),extendedContext=ref(D/'extended-context.png'),result='pass-south-and-changed-vx1024-scope',items=items,outsideAuthorizedROIExactlyPreserved=True,allHaloExactlyPreserved=True,immutableChecks=[ref(p) for p in immutable],formalAccepted=False,remaining='Western lower joint awaits stable r07c15 source and final whole-tile review.'))
state=a.load_json(T/'repairs/current-work-state.json')
state.update(currentCandidate='south-joint-color-v4/candidate.png',currentCandidateSha256=a.sha(D/'candidate.png'),currentCandidateAcceptance='South rope/spar/mast local and complete south boundary pass; upper west remains provisional until final c15 source ROI validation.',pending=['Stable r07c15 source needed for west s4 native edit and formal west source binding','Validate west s1..3 exact source ROI against final c15, integrate s4 while preserving all x>=627','Final whole-west/south/four-way and independent QA, canonical output/extended/manifest commit, provenance-aware cleanup'])
a.save_json(T/'repairs/current-work-state.json',state)
print(a.sha(D/'independent-south-review.json'))
