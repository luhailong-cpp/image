from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

D=Path(__file__).resolve().parent
OUT=D/'output'
BASE=D.parent/'repairs/approved-sync-final/output'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p): return {'file':str(p),'sha256':sha(p)}
def load(p): return np.asarray(Image.open(p).convert('RGB'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')

base_path=BASE/'extended-context.png'
core_path=OUT/'r08_c15.png'
west_path=OUT/'r08_c14.png'
frozen={base_path:'2e080175bafb8192b1ff16b90e41a39a47ad9b9e112f55e4be4fe77613753efd',
 core_path:'7c18bf09e962b458ee285c04067655d6198c426d2bb53cccbe13bc58f24c8a4f',
 west_path:'df507f4a389a3408eb96c113cb5bcd2f842aa5577a4ef9c0694e0a9556ecd48a',
 OUT/'west-final-manifest.json':'f77f87113f7f9345f75e05c5336afbbea86da6a88e4ecec114a00282eb0dd66d',
 D/'qa/review.json':'17e42bc6e557d50ff72173d6a113b004b0ae624751bfadbeac914c31d636ea6b'}
for p,s in frozen.items(): assert sha(p)==s, str(p)
dest=OUT/'extended-context.png'
assert not dest.exists(), 'immutable extension already exists'
base=load(base_path);core=load(core_path);west=load(west_path)
assert base.shape==(4326,4326,3)
assert core.shape==west.shape==(4096,4096,3)
assert np.array_equal(base[115:4211,115:4211],load(BASE/'r08_c15.png'))
extended=base.copy()
extended[115:4211,115:4211]=core
extended[115:4211,0:115]=west[:,3981:4096]
assert np.array_equal(extended[115:4211,115:4211],core)
assert np.array_equal(extended[115:4211,0:115],west[:,3981:4096])
assert np.array_equal(extended[:115],base[:115])
assert np.array_equal(extended[4211:],base[4211:])
assert np.array_equal(extended[:,4211:],base[:,4211:])
protected=np.ones((4326,4326),dtype=bool);protected[115:4211,0:4211]=False
assert np.array_equal(extended[protected],base[protected])
Image.fromarray(extended).save(dest)
readback=load(dest);assert np.array_equal(readback,extended)
data={**ref(dest),'pixels':[4326,4326],'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'operation':'exact integer pixel placement: updated c15 core plus true updated c14 western halo; other true halo pixels retained',
 'generatedByAI':False,'actualModel':None,'actualQuality':None,'artResampled':False,
 'imageBlur':False,'geometryWarped':False,'extendedBase':ref(base_path),
 'extendedBaseGenerationRecord':ref(BASE/'extended-context.png.generation.json'),
 'core':ref(core_path),'westNeighbor':ref(west_path),
 'coreDestinationRectXYXY':[115,115,4211,4211],
 'westHaloDestinationRectXYXY':[0,115,115,4211],
 'westNeighborSourceRectXYXY':[3981,0,4096,4096],
 'reviewedPairManifest':ref(OUT/'west-final-manifest.json'),'reviewedPairQA':ref(D/'qa/review.json'),
 'assertions':{'coreExactlyMatchesFinalC15':True,'westHaloExactlyMatchesFinalC14Last115Columns':True,
 'northHaloIncludingCornersExactlyPreserved':True,'southHaloIncludingCornersExactlyPreserved':True,
 'eastHaloIncludingCornersExactlyPreserved':True,'allFourCornersExactlyPreserved':True,
 'outsideCoreAndWestMiddleHaloExactlyPreserved':True,'savedPixelsReadBackExactly':True,
 'existingReviewedManifestUnmodified':True},
 'changedPixelsFromExtendedBase':int(np.any(extended!=base,axis=2).sum()),
 'script':ref(Path(__file__)),'DAYWritten':False,'globalRegistryModified':False,'formalAccepted':False}
write(OUT/'extended-context.png.generation.json',data)
manifest={'createdAtUtc':data['createdAtUtc'],'output':ref(dest),'generationRecord':ref(OUT/'extended-context.png.generation.json'),
 'inputs':[ref(base_path),ref(core_path),ref(west_path)],'assertions':data['assertions'],
 'replacementRects':{'core':[115,115,4211,4211],'trueWestHaloMiddle':[0,115,115,4211]},
 'protectedHaloSource':ref(base_path),'reviewedManifestUnmodified':ref(OUT/'west-final-manifest.json'),
 'DAYWritten':False,'globalRegistryModified':False,'formalAccepted':False}
write(OUT/'extension-manifest.json',manifest)
for p,s in frozen.items(): assert sha(p)==s,str(p)
print(json.dumps({'output':ref(dest),'sidecar':ref(OUT/'extended-context.png.generation.json'),
 'manifest':ref(OUT/'extension-manifest.json'),'assertions':data['assertions']},ensure_ascii=False))
