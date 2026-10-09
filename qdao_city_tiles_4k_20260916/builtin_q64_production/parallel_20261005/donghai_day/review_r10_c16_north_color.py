"""Record the completed native-pixel visual inspection, then hand off to root."""
from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
import integrate_c15_repairs as j

T=a.TILE;D=T/'repairs/north-integrated-color-v3';V=T/'repairs/north-integrated';B=T/'repairs/internal-final-v2';Q=D/'qa'
EXPECTED='38f9ab047e8dccca8e49e2db392465f42d9447b5edcf4b2aa4d9432ea94304a4'
assert a.sha(D/'candidate.png')==EXPECTED
im=j.rgb(D/'candidate.png');original=j.rgb(V/'candidate.png');ex=j.rgb(D/'extended-context.png');oldex=j.rgb(V/'extended-context.png')
assert np.array_equal(im[800:],original[800:])
assert np.array_equal(ex[115:4211,115:4211],im)
halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False
assert np.array_equal(ex[halo],oldex[halo])
with np.load(D/'fields/final-correction.npz') as data:
 delta=data['correction_rgb_i16'];assert np.array_equal(np.clip(original.astype(np.int16)+delta,0,255).astype(np.uint8),im);assert not delta[800:].any()
ys,xs=np.nonzero(np.any(delta!=0,axis=2));changed_rect=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
m=a.load_json(D/'manifest.json');assert a.sha(Path(m['north']['file']))==m['north']['sha256'];assert a.sha(Path(m['northExtended']['file']))==m['northExtended']['sha256']
for name in ('n2','n3'):j.valid_patch(T/'repairs/north-joint'/name/'edited-native.png')
sources,entries,missing=a.load_sources();assert len(entries)==16 and not missing

# Every listed image was actually displayed, at native pixel size except overview.
viewnames=['n2-full-joint.png','n3-full-joint.png']+[f'insertion-bottom-{i}.png' for i in range(1,5)]+['n2-left-vertical.png','n2-n3-overlap-vertical.png','n3-right-vertical.png']+[f'prefix-transition-{i}.png' for i in range(1,4)]+['assembly/north-r09-r10-common-edge-full.png','assembly/overview-preview-1024.png','assembly/corner-nw.png','assembly/corner-ne.png']+[f'assembly/internal-vertical-x{x}-full.png' for x in (1024,2048,3072)]+[f'assembly/intersection-x{x}-y1024.png' for x in (1024,2048,3072)]
views=[dict(j.ref(Q/name),actualView=True,result='pass',nativePixelScale=None if 'overview' in name else 1) for name in viewnames]
prior=a.load_json(B/'visual-review.json');inherited=[];changed=[]
for old in prior['actualViews']:
 name=Path(old['file']).name
 if not name.startswith(('internal-','intersection-')):continue
 current=Q/'assembly'/name
 if a.sha(current)==old['sha256']:
  inherited.append(dict(j.ref(current),originalActualView=old,inheritance='identical file SHA256',result='pass'))
 else:changed.append(j.ref(current))

review=dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidateSha256=EXPECTED,passed=True,result='pass-north-and-insertion-scope',scope='North common edge, two native geometry repairs, their halo and rectangular insertion boundaries, plus authorized original internal-color prefix through core y799. West external edge remains assigned to root.',actualViews=views,identicalInternalQAInherited=inherited,changedInternalQAForIndependentReview=changed,priorInternalReview=j.ref(B/'visual-review.json'),observations=['Native white hanging cloth, wood poles and ropes join the immutable north tile without displaced contours. The previous halo/native waves and bottom insertion tone cutoffs are gone.','The old r01 c03/c04 water seam continued beyond the north patch. The saved original r01 RGB fields now cover their missing prefix and complement the existing y700..800 fade; the right water region is continuous.','Prefix transition1 was inspected around the previously repaired bucket water and wooden rim; no new tonal cutoff or distorted rim was found.','Only RGB difference fields are smoothed. No image pixels are spatially blurred, stretched or shifted; root native geometry alpha masks remain fixed.'],changedRectCoreXYXY=changed_rect,maximumActualChannelDelta=int(np.abs(delta).max()),belowCoreY800ExactlyPreserved=True,allHaloExactlyPreserved=True,north09ExactlyPreserved=True,scopeAuthorization=j.ref(T/'repairs/north-color-scope-authorization.json'),nativeSourcesValidated=16,nativeRepairRecordsValidated=2,canonicalWritten=False,formalAccepted=False)
a.save_json(D/'visual-review.json',review)
m.update(visualReview=j.ref(D/'visual-review.json'),status='frozen-north-and-insertion-scope-pass');a.save_json(D/'manifest.json',m)
handoff=dict(createdAtUtc=a.utc_now(),owner='root is sole canonical writer',candidate=j.ref(D/'candidate.png'),extendedContext=j.ref(D/'extended-context.png'),baseline=j.ref(V/'candidate.png'),manifest=j.ref(D/'manifest.json'),review=j.ref(D/'visual-review.json'),finalCorrection=j.ref(D/'fields/final-correction.npz'),integration='Use this frozen candidate as baseline before root west correction. Alternatively apply final-correction.npz correction_rgb_i16 once to SHA89d337e9 north-integrated baseline. Do not reapply internal fields or native bucket/north patches: they are already present.',permittedChangedCoreRows=[0,800],belowCoreY800ExactlyPreserved=True,allHaloExactlyPreserved=True,north09ExactlyPreserved=True,originalGeometryPreserved=True,canonicalWritten=False,formalAccepted=False)
if (D/'independent-internal-review.json').exists():handoff['independentInternalReview']=j.ref(D/'independent-internal-review.json')
a.save_json(D/'handoff.json',handoff)
print(dict(candidate=EXPECTED,changedRect=changed_rect,maxDelta=int(np.abs(delta).max()),inheritedInternal=len(inherited),changedInternal=len(changed),changedNames=[Path(x['file']).name for x in changed],review=a.sha(D/'visual-review.json'),handoff=a.sha(D/'handoff.json')))
