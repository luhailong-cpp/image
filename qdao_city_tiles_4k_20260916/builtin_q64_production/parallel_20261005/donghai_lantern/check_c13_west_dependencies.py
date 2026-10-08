"""Read-only upstream audit; writes one own c13 west dependency snapshot only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
DAY=ROOT.parent/'donghai_day'
DEST=ROOT/'r08_c13/repairs/west-common-edge'
WEST=ROOT/'r08_c12/west-final/output/r08_c12.png'
WEST_SHA='fd839140eabb7c9ab5ecdfd76425db43602d6eee9011faa2a804dfb0098cea44'
TONE=ROOT/'r08_c12/tone-assembly/output/r08_c12.png'
TONE_SHA='e68df01c16b449b7cbce2010331a73ab2550d2ddedcab6bf50654f5ff176ce97'
DM=DAY/'tiles/west-integration-r08_c13-manifest.json'
DR=DAY/'r08_c13/repairs/west-common-edge'
EAST=ROOT/'r08_c13/tone-assembly/output/r08_c13.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):return {'file':str(p),'sha256':sha(p)}
def pixels(p,size):
    with Image.open(p) as im:
        im.load();assert im.size==size and im.format=='PNG'
        if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
        return np.asarray(im.convert('RGB')).copy()

assert sha(WEST)==WEST_SHA and sha(TONE)==TONE_SHA
wr=Path(str(WEST)+'.generation.json');tr=Path(str(TONE)+'.generation.json')
assert read(wr)['sha256']==WEST_SHA and read(tr)['sha256']==TONE_SHA
a,b=pixels(WEST,(4096,4096)),pixels(TONE,(4096,4096))
equal=[]
for width in (512,627):
    aa,bb=a[:,-width:],b[:,-width:]
    assert np.array_equal(aa,bb),'c12 east binding changed'
    equal.append({'widthPixels':width,'localRectXYXY':[4096-width,0,4096,4096],
      'exactPixelEquality':True,'changedPixels':0,
      'currentRGBBytesSha256':hashlib.sha256(aa.tobytes()).hexdigest(),
      'toneRGBBytesSha256':hashlib.sha256(bb.tobytes()).hexdigest()})
native=[]
for i in range(1,5):
    p=DR/f's{i}.png';r=Path(str(p)+'.generation.json')
    entry={'id':f's{i}','file':str(p),'available':p.is_file(),'recordAvailable':r.is_file()}
    if p.is_file():
        pixels(p,(1254,1254));entry.update(info(p))
        if r.is_file():
            record=read(r);assert record['sha256']==entry['sha256'];entry['record']=info(r)
    native.append(entry)
contract=None;seams=[];day_ready=False
if DM.is_file():
    d=read(DM);assert d['tile']=='r08_c13'
    assert d['parameters']['patchYStarts']==[0,1024,2048,2842]
    assert d['parameters']['stripPairRectXYXY']==[3469,0,4723,4096]
    assert len(d['nativeRepairSources'])==4 and len(d['seams'])==5
    for s in d['nativeRepairSources']:
        assert sha(s['file'])==s['sha256'];assert sha(s['recordFile'])==s['recordSha256']
    for s in d['seams']:
        for key in ('maskPng','maskNpz'):assert sha(s[key]['file'])==s[key]['sha256']
        seams.append({'id':s['id'],'orientation':s['orientation'],'pairOverlapRectXYXY':s['pairOverlapRectXYXY'],'maskPng':s['maskPng'],'maskNpz':s['maskNpz']})
    contract=info(DM);day_ready=all(n['available'] and n['recordAvailable'] for n in native)
east={'file':str(EAST),'available':EAST.is_file()}
if EAST.is_file():
    pixels(EAST,(4096,4096));east.update(info(EAST))
    r=Path(str(EAST)+'.generation.json');east['recordAvailable']=r.is_file()
    if r.is_file():assert read(r)['sha256']==east['sha256'];east['record']=info(r)
else:east['recordAvailable']=False
observed=[]
for p in (DAY/'r08_c13/current-work.json',DAY/'r08_c13/qa/internal-review.json',DAY/'r08_c13/output/assembly-manifest.json'):
    if p.is_file():observed.append(info(p))
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'donghai_lantern','tile':'r08_c13',
 'status':'ready-for-conversion-preparation' if day_ready and east['available'] and east['recordAvailable'] else 'waiting-for-upstream-common-edge-contract-or-own-tone-candidate',
 'dayReadOnly':True,'dayRepairDirectoryExists':DR.is_dir(),'dayIntegrationManifestAvailable':DM.is_file(),
 'dayNativeRepairSources':native,'dayGeometryContract':contract,'daySeams':seams,'dayCommonEdgeContractReady':day_ready,
 'otherCurrentDayMetadata':observed,'availableDayTileManifestNames':sorted(p.name for p in (DAY/'tiles').glob('*.json')),
 'festivalWestCurrent':{**info(WEST),'generationRecord':info(wr)},'festivalWestEarlierTone':{**info(TONE),'generationRecord':info(tr)},
 'westEastEdgeExactEquality':equal,'festivalEastToneCandidate':east,
 'plannedGlobalPairOriginXY':[45056,28672],'plannedRepairGlobalRectXYWH':[48525,28672,1254,4096],
 'plannedRepairPairRectXYXY':[3469,0,4723,4096],'plannedNativePixels':[1254,1254],'plannedYStarts':[0,1024,2048,2842],
 'plannedCoordinatesAreNotProofOfUpstreamGeometry':True,
 'nextAction':'Wait for the actual DAY c13 west 4 native repairs and 5-mask integration manifest, and for own c13 tone candidate; pin all actual hashes before preparing generation references. Do not independently invent a repair geometry.',
 'generatedNewImages':False,'conversionRequestsPrepared':False,'globalStateModified':False,'formalAccepted':False}
own_native=[]
for i in range(1,5):
    p=DEST/'native'/f's{i}.png';r=Path(str(p)+'.generation.json')
    if p.is_file() and r.is_file():
        assert read(r)['sha256']==sha(p)
        own_native.append({**info(p),'record':info(r)})
result['festivalNativeRepairsSaved']=own_native
result['generatedNewImages']=bool(own_native)
result['conversionRequestsPrepared']=any((DEST/'prompts').glob('*.request.json'))
review=ROOT/'r08_c13/west-final/qa/review.json'
if review.is_file():
    reviewed=read(review)
    for output in reviewed['candidateOutputs']:assert sha(output['file'])==output['sha256']
    result['status']='converted-and-composed-shared-source-geometry-repair-pending' if reviewed['remainingFindings'] else 'converted-and-composed-scoped-qa-pass'
    result['festivalCompositionReview']=info(review)
    result['festivalCandidateOutputs']=reviewed['candidateOutputs']
    result['nextAction']='Resolve the inherited DAY paving interruption with a corrected shared source and matching local mask, then review the same festival native area. Current full 4K candidates are not formally accepted.' if reviewed['remainingFindings'] else 'Parent selects verified candidates and continues remaining map work; no whole-map acceptance is implied.'
DEST.mkdir(parents=True,exist_ok=True)
p=DEST/'dependency-readiness.json';assert p.resolve().is_relative_to(ROOT.resolve())
p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'record':info(p),'status':result['status'],'dayNativeReady':sum(n['available'] for n in native),
 'dayManifestReady':DM.is_file(),'eastToneAvailable':east['available'],'c12East512And627ExactEquality':True},indent=2))
