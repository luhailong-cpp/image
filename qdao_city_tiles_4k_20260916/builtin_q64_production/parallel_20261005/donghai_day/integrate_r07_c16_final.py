from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/integrated-south-v1';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
if '--center' in sys.argv:D=T/'repairs/integrated-south-v2';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
BASE='2dbf08054591651fb62f3477ef79926f2d7696f773eaf26b5f8f1b18d886a06a';WATER='f9ce61978e9cf7c97ffe931283731a8cdb5a45a3fb8c1a938a7e76eeb222666c';SOUTH='2a527f5e6fa7f35cc7dda8a9abf716a1c6847e1ea463e390fcdb8b8d010e85e2'
S=T/'output/r07_c16.png';W=T/'repairs/internal-color-match/candidate.png';N=T/'repairs/south-thin/candidate.png';SO=R/'r08_c16/output/r08_c16.png';SX=R/'r08_c16/output/extended-context.png'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE and a.sha(W)==WATER and a.sha(N)==SOUTH
assert a.sha(SO)=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de' and a.sha(SX)=='0055b578b51057e9c05d6ca050bd83d84c20aae92bc72cd47d424610b6e02689'
base=j.rgb(S);water=j.rgb(W);north=j.rgb(N);south=j.rgb(SO)
wm=np.any(water!=base,axis=2);nm=np.any(north!=base,axis=2);assert not np.any(wm&nm) and not wm[3469:].any() and not nm[:3469].any()
image=water.copy();image[nm]=north[nm];before=image.copy()
P=T/'repairs/south-spar-center' if '--center' in sys.argv else T/'repairs/south-spar-edit'
patch,e=j.valid_patch(P/'edited-native.png');meta=a.load_json(P/'input.png.generation.json');pair=np.concatenate([north,south],axis=0);assert j.raw(j.cut(pair,meta['sourceRectInPairXYXY']))==meta['rawSourceRGBSha256']
box=meta['sourceRectInPairXYXY'][:];box[3]=4096;j.insert(image,patch[:4096-box[1]],box,48,'spar-contour',rects=meta['intendedRepairRectsXYXY'])
assert np.array_equal(image[j.GLOBAL_MASK==0],before[j.GLOBAL_MASK==0]);union=wm|nm|(j.GLOBAL_MASK>0);assert np.array_equal(image[~union],base[~union])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/internal-color-match/extended-context.png');ex[115:4211,115:4211]=image;ex[4211:,115:4211]=south[:115];ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));mi=a.save_image(M/'all-changes.png',Image.fromarray(union.astype(np.uint8)*255))
a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south));extras=[]
for name,box in [('rope-insertion',[1420,3469,2210,4096]),('rope-joint',[1480,3800,2200,4400]),('spar-insertion',[1350,3740,1710,4096])]:
 arr=np.concatenate([image,south],axis=0) if name=='rope-joint' else image
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(arr,box))),sourceRectXYXY=box,resized=False,visualReview='pending'))
waterqa=T/'repairs/internal-color-match/qa';comparisons=[]
for file in sorted((Q/'assembly').glob('*.png')):
 peer=waterqa/file.name
 if peer.exists():comparisons.append(dict(file=str(file),sha256=a.sha(file),previousFile=str(peer),previousSha256=a.sha(peer),exactSame=a.sha(file)==a.sha(peer)))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=ei,waterSource=j.ref(W),waterHandoff=j.ref(T/'repairs/internal-color-match/handoff.json'),waterCorrectionAppliedOnce=True,southSource=j.ref(N),southManifest=j.ref(T/'repairs/south-thin/manifest.json'),southNative=j.ref(T/'repairs/south-rope-thin/edited-native.png'),localSparRepair=e,disjointBaseCorrectionMasks=True,immutableSouth=j.ref(SO),immutableSouthExtended=j.ref(SX),seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mi,outsideUnionExactlyPreserved=True,resampling=False,artBlur=False,qa=qa,qaComparisonToWaterCandidate=comparisons,insertionQA=extras,westNeighbor='pending-stable-r07-c15',formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,extendedContext=ei,qa=str(Q),changedQa=[Path(x['file']).name for x in comparisons if not x['exactSame']])))
