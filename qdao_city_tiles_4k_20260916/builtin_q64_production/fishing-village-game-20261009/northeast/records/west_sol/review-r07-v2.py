import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
from pathlib import Path
from PIL import Image
qa=w.Z/'qa/r07_c11-west-resume-v2';m=w.read(qa/'manifest.json');oldq=w.Z/'qa/r07_c11-west-resume-v1';oldm=w.read(oldq/'manifest.json');oldr=w.read(oldq/'roof-resume-review-v1.json');old={Path(x['file']).name:x for x in oldm['qa']};oldchecks={Path(x['file']).name:x for x in oldr['checks']};checks=[]
quick={'v_p33_p34':('r07_c11_p34-v4','left'),'v_p41_p42':('r07_c11_p42-v2','left'),'v_p42_p43':('r07_c11_p42-v2','right'),'h_p24_p34':('r07_c11_p34-v4','top'),'h_p32_p42':('r07_c11_p42-v2','top'),'h_p34_p44':('r07_c11_p34-v4','bottom')}
for e in m['qa']:
 name=Path(e['file']).name;short=name.split('.')[0];x=dict(file=e['file'],sha256=e['sha256'],kind=e['kind'],visualPassed=True,formalAccepted=False)
 if old[name]['sha256']==e['sha256']:
  assert oldchecks[name]['visualPassed'];x.update(method='Reuse prior passed view; identical full QA file SHA256',priorView=w.ref(old[name]['file']),priorReview=w.ref(oldq/'roof-resume-review-v1.json'))
 elif e['kind'] in ('vertical_boundary','horizontal_boundary'):
  stem,side=quick[short];f=w.Z/'qa/west_sol'/stem/(side+'.native-1to1.png');im=Image.open(f).convert('RGB');c=im.crop((0,115,256,1139) if e['kind']=='vertical_boundary' else (115,0,1139,256));assert c.tobytes()==Image.open(e['file']).convert('RGB').tobytes();x.update(method='Directly inspected new local edge; byte-exact RGB subset verified',quickView=w.ref(f),exactPixelSubsetVerified=True)
 elif e['kind']=='four_patch_junction':x.update(method='Direct native1to1 512px view after final repairs',note='Four source contours, stone/wood transitions and rail geometry continuous')
 else:
  pid='r07_c11_'+short.removeprefix('core_');src=Path(w.own_selection('r07_c11')[pid]['path']);rp=w.R/(src.stem.removesuffix('-west_sol')+'.review.json');x.update(method='New full native1254 directly viewed after repair; core crop verified by assembler',source=w.ref(src),reviewRecord=w.ref(rp))
 checks.append(x)
assert len(checks)==49
out=dict(schemaVersion=1,reviewer='roof_resume',reviewedAtUtc=w.now(),candidate=m['candidate'],selection=m['selection'],manifest=w.ref(qa/'manifest.json'),checks=checks,checkedCount=49,passCount=49,pendingCount=0,unchangedPassedViewsReused=37,changedViewsReviewed=12,internalVisualPassed=True,independentAccepted=False,formalAccepted=False,status='internal_49QA_passed_pending_independent_review',resolvedIssues=['Blue bollard cap/stave row3/4 seam repaired by p34-v4 against stable p44-v2; external right strip also locally checked','Artificial p42 stone/wood vertical line replaced with natural diagonal boundary by p42-v2'],limitations=['External perimeter and cross-zone whole-map acceptance remains separate','Navigation/client mapping/capacity not validated by this tile production'])
w.write(qa/'roof-resume-review-v2.json',out)
new=[]
for rp in w.R.glob('r07_c11_*.receipt.json'):
 d=w.read(rp)
 if d.get('observedAtUtc','')>='2026-10-16':
  stem=rp.name.removesuffix('.receipt.json');native=w.Z/'native'/f'{stem}-west_sol.png'
  if native.exists():new.append(dict(source=w.ref(native),receipt=w.ref(rp),observedAtUtc=d['observedAtUtc']))
handoff=dict(schemaVersion=1,createdAtUtc=w.now(),worker='roof_resume',authorizedTiles=['r06_c11','r07_c11','r06_c10','r07_c10'],tile='r07_c11',nativeSelectedCount=16,newNativeOutputsThisResume=len(new),newSources=new,candidate=m['candidate'],selection=m['selection'],QA=w.ref(qa/'manifest.json'),review=w.ref(qa/'roof-resume-review-v2.json'),internalVisualPassed=True,independentAccepted=False,formalAccepted=False,actualModel=None,actualQuality=None,route='builtin image_gen.imagegen',remainingOriginalScope=['r06_c11 known pending retained unchanged','r06_c10','r07_c10'],sharedProgressModified=False,gitOperated=False)
w.write(w.R/'r07_c11.resume-batch-handoff-20261016.json',handoff)
print(dict(candidate=m['candidate'],review=str(qa/'roof-resume-review-v2.json'),newNativeOutputs=len(new),selected=16,internalChecks=49,passed=49))

