from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib, re

O=Path(__file__).resolve().parent
def read(f): return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
out=[]
for t in read(O/'current-candidates.json')['candidates']:
    if t['candidatePixelsUnchangedFromV03']:continue
    f=Path(t['file']); d=read(str(f)+'.derivation.json')
    qr=read(t['currentProductionReview']['file'])
    assert d['sha256']==t['sha256']==sha(f)==qr['candidateSha256']
    sources=[];crops=[]
    with Image.open(f) as original:
        original=original.convert('RGB')
        for s in d['sources']:
            h=sha(s['file']);assert h==s['sha256']
            with Image.open(s['file']) as im:
                assert im.size==(1254,1254)
                native=im.crop(s['coreCrop']).convert('RGB')
            x,y=s['tileLocalPaste'];actual=original.crop((x,y,x+1024,y+1024))
            assert actual.tobytes()==native.tobytes()
            sources.append({'id':s['id'],'file':s['file'],'sha256':h,'nativeSize':[1254,1254],
                            'coreCrop':s['coreCrop'],'tileLocalPaste':[x,y],'exactNativeCorePixels':True})
        for q in qr.get('items',qr.get('images',[])):
            h=sha(q['file']);assert h==q['sha256']
            with Image.open(q['file']) as im:
                im=im.convert('RGB');w,he=im.size;name=Path(q['file']).stem
                if q.get('candidateCrop'):box=q['candidateCrop']
                elif m:=re.match(r'core-(\d)-(\d)-100pct',name):
                    r,c=map(int,m.groups());box=[(c-1)*1024,(r-1)*1024,c*1024,r*1024]
                elif m:=re.match(r'vertical-(\d)-segment-(\d)-100pct',name):
                    b,s=map(int,m.groups());box=[b*1024-w//2,(s-1)*1024,b*1024+w//2,s*1024]
                elif m:=re.match(r'horizontal-(\d)-segment-(\d)-100pct',name):
                    b,s=map(int,m.groups());box=[(s-1)*1024,b*1024-he//2,s*1024,b*1024+he//2]
                elif m:=re.match(r'cross-(\d)-(\d)-100pct',name):
                    r,c=map(int,m.groups());box=[c*1024-w//2,r*1024-he//2,c*1024+w//2,r*1024+he//2]
                else:raise RuntimeError('Cannot map crop '+name)
                assert im.tobytes()==original.crop(box).tobytes(),name
            assert q.get('status','').startswith('passed'),q
            crops.append({'file':q['file'],'sha256':h,'candidateCrop':box,'exactCurrentCandidatePixels':True,
                          'reusedStatus':q['status'],'actuallyViewedThisBatch':False})
    assert len(sources)==16 and len(crops)==49
    assert not d.get('requiredOverlays')
    out.append({'tileId':t['tileId'],'file':t['file'],'sha256':t['sha256'],'size':[4096,4096],
                'selectionMatchesDerivation':set(x for row in t['selectedCores'] for x in row)==set(s['id'] for s in sources),
                'nativeSources':sources,'reusedInspectionCrops':crops,'reusedProductionReview':t['currentProductionReview'],
                'reusedVisualEvidenceItemCount':len(crops),'currentCandidatePixelsRebuiltInMemoryNotSaved':True,
                'sourceWrites':0,'newArtwork':False})
data={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'tiles':out,'nativeSourcesVerified':sum(len(t['nativeSources']) for t in out),
      'inspectionCropsVerified':sum(len(t['reusedInspectionCrops']) for t in out),'allChecksPassed':True,
      'policy':'Visual passes are reused from existing hash-bound records; this batch verifies exact sources and pixels only. No repeated visual audit.'}
(O/'reused-full-pixel-verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if k!='tiles'},ensure_ascii=False))
