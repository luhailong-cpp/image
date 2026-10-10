"""Persist actual views and exact-identity inheritance for the reviewed tile."""
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
R=a.ROOT;T=a.TILE;D=T/'repairs/final-rail-v2';B=T/'repairs/final-west-joint';Q=D/'qa';C=D/'candidate.png'
expected='de2ffe83eff08483741521f59e81bbc1ea62927024a86229cb6890eb55477ad0'
assert a.sha(C)==expected
m=a.load_json(D/'manifest.json');im=j.rgb(C);base=j.rgb(B/'candidate.png');ex=j.rgb(D/'extended-context.png')
assert np.array_equal(im,j.rgb(D/'extended-context.png')[115:4211,115:4211])
assert np.array_equal(im[:,780:],base[:,780:]) and np.array_equal(im[:3928],base[:3928])
for key in ('west','westExtended','south','southwest'):assert a.sha(m[key]['file'])==m[key]['sha256']
assert a.sha(R/'r08_c16/output/extended-context.png')=='0055b578b51057e9c05d6ca050bd83d84c20aae92bc72cd47d424610b6e02689'
assert a.sha(R/'r08_c15/output/extended-context.png')=='1824c937740587c2d7fa029c43ebfe15df4380ce9d15ad204924cbbe60572c72'
actual=['south-rail-close.png','rail-east-insertion.png','rail-top-insertion.png','four-way-corner.png','west-common-full.png','east-insertion-full.png','assembly/south-r07-r08-common-edge-full.png','assembly/overview-preview-1024.png','assembly/corner-sw.png','assembly/corner-nw.png','assembly/corner-ne.png','assembly/corner-se.png','assembly/internal-vertical-x2048-full.png']
for name in ['upper-left-join.png','timber-underside.png','upper-overlap.png','post-waterline.png','lower-overlap.png']:
 src=B/'qa'/name;dest=Q/name;shutil.copyfile(src,dest);assert a.sha(src)==a.sha(dest)
 prior=next(x for x in m['priorInsertionQA'] if Path(x['file']).name==name);assert a.sha(dest)==prior['sha256']
 if not any(Path(x['file']).name==name for x in m['insertionQA']):m['insertionQA'].append({**prior,'file':str(dest),'visualReview':'pass'})
 actual.append(name)
views=[dict(j.ref(Q/f),actualView=True,nativePixelScale=None if 'overview' in f else 1,result='pass') for f in actual]
reports=[T/'repairs/internal-color-match/visual-review.json',T/'repairs/south-joint-color-v4/independent-south-review.json',B/'independent-fill15-initial-review.json']
evidence={}
for f in reports:
 doc=a.load_json(f)
 for v in doc.get('sheets',doc.get('items',doc.get('actualViews',[]))):
  assert a.sha(v['file'])==v['sha256'];evidence[v['sha256']]=dict(sourceView=v,report=j.ref(f),reviewer=doc['reviewer'])
evidence[a.sha(Q/'assembly/internal-vertical-x2048-full.png')]=dict(actualView=True,reviewer='close_joint14')
internal=[]
for f in sorted((Q/'assembly').glob('*.png')):
 if not f.name.startswith(('internal-','intersection-')):continue
 sh=a.sha(f);assert sh==a.sha(B/'qa/assembly'/f.name)
 assert sh in evidence,f.name
 internal.append(dict(j.ref(f),result='pass',exactSHAInherited=True,evidence=evidence[sh]))
assert len(internal)==15
for entry in m['nativeRepairs']:j.valid_patch(Path(entry['file']))
arrays,sources,missing=a.load_sources();assert not missing and len(sources)==16
m.update(visualReview='producer-review-pass-independent-review-required',nativeSourcesRevalidated=16)
a.save_json(D/'manifest.json',m)
a.save_json(D/'review.json',dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidateSha256=expected,extendedContextSha256=a.sha(D/'extended-context.png'),result='pass',actualViews=views,internalSeamsAndCrosses=internal,fullWestAndSouthReviewed=True,neighborHashesExactlyPreserved=True,sourceNativeCount=16,allColumnsFrom780ExactlyPreserved=True,observations=['Native rail edit removed the jagged upper splice and protruding highlight step. Exact lower-neighbor halo provides continuous timber lower face at the physical south boundary.','All six internal seams and nine intersections match SHA-bound actual-reviewed sheets. Full south and west joints plus four-way corner are continuous.','Bounded material color differences affect insertion transitions only; no spatial resampling, shape warp or image blur.'],formalAccepted=False,wholeCityComplete=False))
print(expected)
