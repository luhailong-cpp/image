from pathlib import Path
import sys, copy
import numpy as np
from PIL import Image
F=Path(__file__).resolve().parent;ROOT=F.parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from production import read,write,sha,now,deriv
import finalize_scoped as finalizer
EXPECTED='1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180'
ctx=finalizer.context('r11_c13',EXPECTED);required=finalizer.requirements(ctx);records=[]
for item in required.values():
 p=item['path'];im=item['image'];sources=[ctx['references'][k] for k in item['roles']]
 if p.exists():
  assert np.array_equal(np.asarray(im),np.asarray(Image.open(p).convert('RGB')))
  rec=read(str(p)+'.generation.json');assert sha(p)==rec['sha256']
 else:
  p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
  rec=dict(file=str(p),sha256=sha(p),pixels=list(im.size),nativeScale=1,actuallyViewed=False,verdict='pending_visual_QA',operation=item['operation'],sources=sources)
  write(str(p)+'.generation.json',rec)
 records.append(rec)
mp=F/'output/manifest.json';assert not mp.exists();manifest=copy.deepcopy(ctx['assembly']);manifest.update(qa=records,status='native_4K_candidate_available_pending_visual_QA',sourceManifest=finalizer.ref(ctx['assemblyPath']),currentCandidateGeneration=finalizer.ref(ctx['generation']),runtimeDependencies=[finalizer.ref(ctx['candidate'])],writtenAt=now())
write(mp,manifest)
write(F/'progress.json',dict(updatedAt=now(),tile='r11_c13',nativePatches=16,pixels=[4096,4096],completePixelCoverage=True,file=str(ctx['candidate']),sha256=EXPECTED,scopedLocalSeamsPassed=False,formalAccepted=False,navigationVerified=False,clientVerified=False))
q=F/'qa/composition-preview.png';ctx['image'].resize((1024,1024),Image.Resampling.LANCZOS).save(q);deriv(q,[ctx['candidate']],dict(kind='composition preview only',sourceUpscaling=False,scale=.25,productionPixels=False,seamAcceptance=False))
print(dict(candidate=EXPECTED,requiredQA=len(required),nativeCount=16,acceptance=False))
