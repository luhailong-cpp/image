from pathlib import Path
from PIL import Image
import hashlib, json
from datetime import datetime, timezone

T=Path(__file__).parent
B=T/'repairs'/'consolidated-sync'
Q=B/'qa'/'wood-horizontal-native-overlaps'
Q.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
items=[]
for i in range(1,5):
    p=B/'native'/f'wood-horizontal-s{i}.png'
    d=read(str(p)+'.generation.json')
    assert Image.open(p).size==(1254,1254)
    assert sha(p)==d['sha256']==d['evidence']['toolResultSha256']
    raw=Path(d['evidence']['toolResultSourcePath'])
    assert sha(raw)==d['sha256']
    for ref in d['references']:
        assert sha(ref['file'])==ref['sha256'],ref['file']
    assert sha(d['prompt'])==d['promptSha256']
    assert sha(d['requestFile'])==d['requestSha256']
    assert d['actualModel'] is None and d['actualQuality'] is None
    assert d['submittedParameters']['model'] is None and d['submittedParameters']['quality'] is None
    items.append({'id':f'wood-horizontal-s{i}','file':str(p),'sha256':sha(p),'sourceRectXYXY':d['sourceRectXYXY'],'dimensions':[1254,1254],'generationRecordSha256':sha(str(p)+'.generation.json'),'rawBytesAndReferencesVerified':True})
pairs=[]
for a,b in zip(items,items[1:]):
    ar,br=a['sourceRectXYXY'],b['sourceRectXYXY']
    box=[max(ar[0],br[0]),max(ar[1],br[1]),min(ar[2],br[2]),min(ar[3],br[3])]
    w,h=box[2]-box[0],box[3]-box[1]
    out=Image.new('RGB',(w*2,h))
    sources=[]
    for n,item in enumerate((a,b)):
        r=item['sourceRectXYXY']
        crop=[box[0]-r[0],box[1]-r[1],box[2]-r[0],box[3]-r[1]]
        out.paste(Image.open(item['file']).convert('RGB').crop(crop),(n*w,0))
        sources.append({'file':item['file'],'sha256':item['sha256'],'cropXYXY':crop})
    path=Q/f'{a["id"]}--{b["id"]}.png'
    out.save(path)
    rec={'file':str(path),'sha256':sha(path),'operation':'exact same-global-coordinate overlap crops side by side; earlier segment left, later segment right','sourceRectXYXY':box,'derivedFrom':sources,'resized':False,'colourAdjusted':False,'finalArt':False,'dimensions':[w*2,h]}
    save(str(path)+'.generation.json',rec)
    pairs.append(rec)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'nativeSources':items,'pairs':pairs,'sourceAuditPassed':True,'visualReview':'pending','repairAssemblyPerformed':False,'formalAccepted':False,'limitation':'Individual native conversions only. Current 16-source DAY lock has unresolved repair mask drift; no old mask integration authorized.'}
save(Q/'manifest.json',manifest)
print(json.dumps({'sourceAuditPassed':True,'pairs':[x['file'] for x in pairs]}))
