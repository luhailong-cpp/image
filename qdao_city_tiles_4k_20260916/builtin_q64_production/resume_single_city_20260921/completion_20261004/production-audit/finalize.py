from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
SESSION=OUT.parent.parent
PROD=SESSION.parent
BASE=PROD.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

batch=read(PROD/'current-batch.json');work=read(SESSION/'continuation_20261004/current-work.json')
bykey={(c['appearance'],c['tile']):c for c in batch['candidates']}
for c in work['workingCandidates']:
    bykey[('tianyong_festival',c['tile'])]={'appearance':'tianyong_festival','tile':c['tile'],**c['candidate']}
verified=[]
for (appearance,tile),c in bykey.items():
    p=BASE/c['file'];assert p.is_file(),p
    assert sha(p)==c['sha256'],p
    assert Image.open(p).size==(4096,4096),p
    verified.append({'appearance':appearance,'tile':tile,**info(p),'pixels':[4096,4096]})
assert len(verified)==29

probes=[]
for name in ['c07/full-native-attempt/native.png.generation.json','c08/full-native/rejected-size.native.png.generation.json','c09/native2304-probe/native.png.generation.json']:
    p=OUT.parent/name;d=read(p);f=Path(d['file'])
    probes.append({'record':info(p),'requestedPixels':d.get('requestedPixels',d.get('requestedNativePixels',[4096,4096])),
                   'returnedPixels':[d['width'],d['height']], 'retainedImageExists':f.exists(),
                   'retainedImageShaVerified':f.exists() and sha(f)==d['sha256'], 'submittedSize':d.get('submittedParameters',{}).get('size')})

write(OUT/'verified-scope.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceBatch':info(PROD/'current-batch.json'),
     'sourceWorkSet':info(SESSION/'continuation_20261004/current-work.json'),'unique4kCandidates':verified,'candidateCoordinateCount':29,
     'missingCandidateCount':1763,'remainingBasePatchesAt16PerTile':28208,'optimisticIfLoneLanxianPatchReusable':28207,
     'remainingCountExcludes': ['layout studies','failed retries','seam repairs','rework of existing candidates','visual and runtime acceptance'],
     'formalAccepted':0,'wholeCityComplete':0,'builtinProbesThisRound':probes,
     'builtinSizeConclusion':'These three actual calls returned 1254 square despite larger prompt requests. This is session evidence, not an assertion of global model or official product limits.'})

td=OUT.parent/'c09/tone-candidate-v1';a=read(td/'assembly.json');f=td/'r08_c09.png'
assert sha(f)==a['candidate']['sha256'];src=Path(a['source']['file']);assert sha(src)==a['source']['sha256']
arr=np.asarray(Image.open(f).convert('RGB'));before=np.asarray(Image.open(src).convert('RGB'))
qa=[]
for axis in 'xy':
    for at in [1024,2048,3072]:
        board=Image.new('RGB',(1024,1280))
        for seg in range(4):
            box=(at-160,seg*1024,at+160,(seg+1)*1024) if axis=='x' else (seg*1024,at-160,(seg+1)*1024,at+160)
            part=Image.fromarray(arr).crop(box)
            if axis=='x':part=part.transpose(Image.Transpose.ROTATE_90)
            board.paste(part,(0,seg*320))
        p=td/'qa'/f'{axis}{at}-full.png';assert np.array_equal(np.asarray(board),np.asarray(Image.open(p)))
        qa.append({**info(p),'viewedAt':'original 1:1','reconstructedFromCandidatePixelEqual':True,'axis':axis,'coordinate':at,'bandWidth':320,'fullSpan':4096,'visualResult':'pass_for_this_internal_band'})
board=Image.new('RGB',(1536,1536))
for yi,y in enumerate([1024,2048,3072]):
    for xi,x in enumerate([1024,2048,3072]):board.paste(Image.fromarray(arr).crop((x-256,y-256,x+256,y+256)),(xi*512,yi*512))
p=td/'qa/nine-junctions.png';assert np.array_equal(np.asarray(board),np.asarray(Image.open(p)))
qa.append({**info(p),'viewedAt':'original 1:1','reconstructedFromCandidatePixelEqual':True,'centers':[[x,y] for y in [1024,2048,3072] for x in [1024,2048,3072]],'cropSize':[512,512],'visualResult':'pass_for_these_nine_internal_junctions'})
edge_equal=all(np.array_equal(arr[e],before[e]) for e in [np.s_[0,:,:],np.s_[-1,:,:],np.s_[:,0,:],np.s_[:,-1,:]])
write(OUT/'c09-tone-independent-review.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'independent verify_model agent',
     'candidate':info(f),'assembly':info(td/'assembly.json'),'source':info(src),'actuallyViewedEvidence':qa,
     'conclusion':'pass_for_six_internal_320px_bands_and_nine_512px_internal_junction_crops_only',
     'observations':['No residual hard 1024-grid rectangular tone jumps identifiable in the viewed native bands/crossings.',
                     'No new displaced/double gold edges or blurred seam strips identifiable in this scope.',
                     'Broad subtle hand-painted tone variation remains; this did not form a new visible rectangular boundary in reviewed evidence.'],
     'outermostPixelEqualityMechanicallyVerified':edge_equal,'maxDecodedRgbPixelDifference':int(np.abs(arr.astype(np.int16)-before.astype(np.int16)).max()),
     'notVisuallyReviewedThisCheck':['external neighbor joins','all non-seam interior pixels','formal four-tile junctions','game runtime'],
     'formalAccepted':False,'wholeTileAccepted':False,'newModelCalls':0})
print(json.dumps({'verifiedCandidateCoordinates':len(verified),'missing':1763,'basePatchCount':28208,'toneQAImagesVerified':len(qa),'outermostPixelsEqual':edge_equal}))
