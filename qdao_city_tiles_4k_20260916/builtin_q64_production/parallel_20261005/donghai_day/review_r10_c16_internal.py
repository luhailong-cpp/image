from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
import integrate_c15_repairs as j
R=a.ROOT;T=a.TILE;D=T/'repairs/internal-final-v2';Q=D/'qa';C=D/'candidate.png';BASE=T/'output/r10_c16.png'
expected='8f922a70ffaf382e80a273c688205c7a8c038548863335fa950600f1aa0d581d';baseline='76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7'
assert a.sha(C)==expected and a.sha(BASE)==baseline
im=j.rgb(C);raw=j.rgb(BASE);ex=j.rgb(D/'extended-context.png');oe=j.rgb(T/'output/extended-context.png')
assert np.array_equal(im[:700],raw[:700]);halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False;assert np.array_equal(ex[halo],oe[halo]);assert np.array_equal(ex[115:4211,115:4211],im)
with np.load(D/'fields/final-correction.npz') as n:
 delta=n['correction_rgb_i16'];assert np.array_equal(np.clip(raw.astype(np.int16)+delta,0,255).astype(np.uint8),im);assert not delta[:700].any()
sources,entries,missing=a.load_sources();assert len(entries)==16 and not missing
j.valid_patch(T/'repairs/internal-bucket/edited-native.png')
names=sorted(p.name for p in Q.glob('*.png') if p.name.startswith(('internal-','intersection-')));assert len(names)==15
views=[dict(j.ref(Q/f),actualView=True,result='pass-internal-y700-and-below',nativePixelScale=1) for f in names]
for f in ['bucket-native-detail.png','overview-preview-1024.png']:views.append(dict(j.ref(Q/f),actualView=True,result='pass-internal-scope',nativePixelScale=None if 'overview' in f else 1))
review=dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidateSha256=expected,result='pass-internal-scope',scope='Only core y>=700 internal seams, intersections and bucket water guide strip. North and west external joints are excluded and assigned to root.',actualViews=views,observations=['Same-material RGB difference fields remove the horizontal/vertical tonal boundaries in timber and open water while retaining original geometry and texture selection.','The17px difference filter removes residual thin zigzag tone changes that remained under the49px field; the image itself is never filtered.','Native bucket-water inpainting removes the original vertical guide boundary. Bucket rims, metal, timber, post and left foam are protected by the water-only eligibility mask and local insertion ROI.'],northCore700ExactlyPreserved=True,allHaloExactlyPreserved=True,nativeSourcesValidated=16,canonicalOutputUnchanged=True,imageBlur=False,geometryWarp=False,resampling=False,formalAccepted=False)
a.save_json(D/'visual-review.json',review)
m=a.load_json(D/'manifest.json');m.update(visualReview=j.ref(D/'visual-review.json'),status='frozen-internal-scope-pass');a.save_json(D/'manifest.json',m)
a.save_json(D/'handoff.json',dict(createdAtUtc=a.utc_now(),owner='root is sole canonical writer',candidate=j.ref(C),extendedContext=j.ref(D/'extended-context.png'),baseline=j.ref(BASE),manifest=j.ref(D/'manifest.json'),review=j.ref(D/'visual-review.json'),finalCorrection=j.ref(D/'fields/final-correction.npz'),integration='Preferred: use this candidate as the internal baseline before north and west repairs. Alternatively add final-correction.npz correction_rgb_i16 exactly once to the SHA-validated original core; it already includes both color compensation and the bucket native insertion. Never also apply the intermediate color-only field.',minimumChangedCoreY=700,allHaloExactlyPreserved=True,northCorrection=False,scope='Internal y>=700 only; no permission or claim to finalize north/west external joints.',bucketNative=j.ref(T/'repairs/internal-bucket/edited-native.png'),actualModel=None,actualQuality=None,selectedColorCandidate=j.ref(T/'repairs/internal-color-match-v2/candidate.png'),fieldOnlyMaxChannelCorrection=31,canonicalOutputUnchanged=True))
print(dict(candidate=expected,field=a.sha(D/'fields/final-correction.npz'),review=a.sha(D/'visual-review.json'),handoff=a.sha(D/'handoff.json')))
