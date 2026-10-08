"""Read-only source audit, writes only c13 QA JSON evidence."""
from pathlib import Path
import sys, json, hashlib, importlib.util
from datetime import datetime, timezone
import numpy as np
from PIL import Image

QA=Path(__file__).resolve().parent
TILE=QA.parent
OWN=TILE.parent
DAY=OWN.parent/'donghai_day'
sys.dont_write_bytecode=True
sys.path.insert(0,str(TILE))
import assemble_c13_shared as shared

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name, obj): (QA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

prior=read(QA/'assembly-preflight.json')
manifest=read(shared.DAY_MANIFEST)
manifest_hash=sha(shared.DAY_MANIFEST)
assert manifest_hash==prior['dayManifest']['sha256']
masks, mask_evidence=shared.load_day_masks(manifest)
arrays={}
for e in manifest['nativeSources']:
    r,c=int(e['id'][1:3]),int(e['id'][5:7])
    arrays[r,c]=shared.load_rgb(e['file'],e['sha256'],(1254,1254))
    assert sha(e['recordFile'])==e['recordSha256']
replay,_=shared.assemble(arrays,masks)
expected=shared.load_rgb(manifest['extendedContext']['file'],manifest['extendedContext']['sha256'],(4326,4326))
assert np.array_equal(replay,expected)
helper=shared.load_helpers()
_,own=helper.load_patches(False)
west,west_info=helper.load_west()
write('source-revalidation.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'dayManifest':{'file':str(shared.DAY_MANIFEST),'sha256':manifest_hash},'sameDayManifestAsPreflight':True,'dayNativeCount':16,'dayMaskCount':15,'dayPixelReplayExactlyMatchesExtended':True,'ownNativeCount':len(own),'ownNative':own,'west':west_info,'dayDirectoryWritten':False,'formalAccepted':False})

next_tile=DAY/'r08_c14'
plan=read(next_tile/'plan.json')
sources=[]
for p in sorted((next_tile/'native').glob('r??_c??.png')):
    recpath=Path(str(p)+'.generation.json')
    rec=read(recpath)
    assert sha(p)==rec['sha256']
    with Image.open(p) as im:
        assert im.size==(1254,1254) and im.mode in ('RGB','RGBA')
    assert rec['route']=='builtin' and rec['resizedAfterGeneration'] is False and not rec.get('finalArtUpscaled')
    assert rec['evidence']['toolResultSha256']==rec['sha256']
    assert sha(rec['prompt'])==rec['promptSha256']
    assert len(rec['references'])==len(rec['submittedParameters']['referenced_image_paths'])
    for ref, actual in zip(rec['references'], rec['submittedParameters']['referenced_image_paths']):
        assert Path(ref['file']).resolve()==Path(actual).resolve() and sha(ref['file'])==ref['sha256']
    sources.append({'id':p.stem,'file':str(p),'sha256':rec['sha256'],'recordFile':str(recpath),'recordSha256':sha(recpath),'pixels':[1254,1254],'nativeAndReferenceHashesVerified':True,'modelQualityActualUnconfirmed':rec['actualModel'] is None and rec['actualQuality'] is None,'visualReviewByThisAgent':False})
expected_ids=[f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)]
assert plan['globalRect']==[53248,28672,4096,4096]
assert plan['nativeGrid']==[4,4] and plan['core']==1024 and plan['halo']==115
assert sha(plan['westNeighbor'])==plan['westNeighborSha256']
write('next-source-readiness.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c14','dayPlan':{'file':str(next_tile/'plan.json'),'sha256':sha(next_tile/'plan.json')},'globalCoreXYWH':plan['globalRect'],'nativeWindowOriginXY':[53133,28557],'nativePixels':[1254,1254],'core':1024,'halo':115,'overlap':230,'dayNativeAvailable':len(sources),'dayNativeRequired':16,'sources':sources,'missingNativeIds':[x for x in expected_ids if x not in {s['id'] for s in sources}],'dayAssemblyManifestPresent':(next_tile/'output/assembly-manifest.json').is_file(),'geometryAuthority':'Each actual DAY native SHA, not the enlarged layout/structure guide','ownC13WestBindingForNextTile':'Must bind completed selected own c13 pixels before native conversion guides are prepared','dayWestNeighbor':{'file':plan['westNeighbor'],'sha256':plan['westNeighborSha256'],'verified':True},'dayDirectoryWritten':False,'formalAccepted':False,'crossAppearanceGeometryAccepted':False,'readyForAll16Conversion':len(sources)==16})
print(json.dumps({'c13DayReplay':True,'c13OwnNativeCount':len(own),'c14DayNativeCount':len(sources),'written':['source-revalidation.json','next-source-readiness.json']}))
