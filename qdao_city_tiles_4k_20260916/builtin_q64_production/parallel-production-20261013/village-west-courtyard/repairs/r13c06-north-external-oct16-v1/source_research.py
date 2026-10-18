from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for tile,row in [('r12_c06',4),('r13_c06',1)]:
    for col in range(1,5):
        p=B/'native'/f'{tile}_p{row:02d}_{col:02d}_v01.png'
        box=[20365+(col-1)*1024,48013 if tile=='r12_c06' else 49037,21619+(col-1)*1024,49267 if tile=='r12_c06' else 50291]
        with Image.open(p) as im:assert im.size==(1254,1254);dims=list(im.size)
        records.append({'path':str(p),'sha256':sha(p),'dimensions':dims,'globalNativeBox':box,'role':'Original lower native row, partly superseded in frozen anchor' if tile=='r12_c06' else 'Original upper native row, partly superseded by W01..03 and later repair traces'})
anchor=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
rec={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'read-only source research before W19 handoff; no candidate assembled','frozenNorthAnchor':{'path':str(anchor),'sha256':sha(anchor),'globalContextBox':[20365,44941,24691,49267],'nativeBottomOverlays':['repairs/r12c06-resume-20261016-v1/w10-I13.generated-v1.png','repairs/r12c06-resume-20261016-v1/w11-I14.generated-v1.png'],'traceManifest':str(anchor.parent.parent/'delivery-manifest-v1.json')},'exactGlobalOverlap':[20365,49037,24691,49267],'northContextRows':[4096,4326],'southContextRows':[0,230],'actualCoreSeam':{'globalY':49152,'northContextY':4211,'southContextY':115},'proposedHardBoundaryRangeInSouth':[115,229],'sourceOriginalNativeRows':records,'constraint':'Only handed-off W19 complete context may be used as mutable-baseline input; north frozen anchor stays read-only. Inspect both actual core seam and moved lower selection boundary before any pass.','aiGenerationUsed':False,'artworkMutated':False}
with (R/'source-research-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(R/'source-research-v1.json'),'sha256':sha(R/'source-research-v1.json'),'nativeSourcesVerified':len(records)}))
