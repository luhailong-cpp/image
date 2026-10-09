from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json

T=Path(__file__).parent
B=T/'repairs'/'consolidated-sync'
Q=B/'qa'/'water-native-5'
IDS=['a-left-cross','b-right-cross','c-left-bottom','d-right-bottom','g-left-insertion']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Q.mkdir(parents=True,exist_ok=True)
items={}
for name in IDS:
    p=B/'native'/f'{name}.png'; d=read(str(p)+'.generation.json')
    assert Image.open(p).size==(1254,1254)
    assert sha(p)==d['sha256']==d['evidence']['toolResultSha256']
    assert sha(d['evidence']['toolResultSourcePath'])==d['sha256']
    assert d['actualModel'] is None and d['actualQuality'] is None
    assert d['submittedParameters']['model'] is None and d['submittedParameters']['quality'] is None
    for r in d['references']:assert sha(r['file'])==r['sha256']
    assert sha(d['prompt'])==d['promptSha256'] and sha(d['requestFile'])==d['requestSha256']
    assert d['festivalSource']['role']=='same actual festival tile window; palette only, DAY repair is geometry authority'
    items[name]={'file':str(p),'sha256':sha(p),'sourceRectXYXY':d['sourceRectXYXY'],'generationRecordSha256':sha(str(p)+'.generation.json'),'allReferenceAndOriginalToolBytesVerified':True}
pairs=[]
for left,right in [(IDS[0],IDS[1]),(IDS[0],IDS[2]),(IDS[1],IDS[3]),(IDS[2],IDS[3]),(IDS[2],IDS[4])]:
    a,b=items[left],items[right];ar,br=a['sourceRectXYXY'],b['sourceRectXYXY']
    box=[max(ar[0],br[0]),max(ar[1],br[1]),min(ar[2],br[2]),min(ar[3],br[3])]
    w,h=box[2]-box[0],box[3]-box[1]; assert w>0 and h>0
    horizontal=w<h
    dst=Image.new('RGB',(w*2,h) if horizontal else (w,h*2))
    refs=[]
    for i,(name,src) in enumerate([(left,a),(right,b)]):
        r=src['sourceRectXYXY'];c=[box[0]-r[0],box[1]-r[1],box[2]-r[0],box[3]-r[1]]
        dst.paste(Image.open(src['file']).convert('RGB').crop(c),(i*w,0) if horizontal else (0,i*h))
        refs.append({'file':src['file'],'sha256':src['sha256'],'cropXYXY':c})
    p=Q/f'{left}--{right}.png'; dst.save(p)
    d={'file':str(p),'sha256':sha(p),'operation':'unaltered same-global-overlap crops; first named source left/top, second right/bottom','sourceRectXYXY':box,'derivedFrom':refs,'pixels':list(dst.size),'resized':False,'colourAdjusted':False,'finalArt':False}
    write(str(p)+'.generation.json',d);pairs.append(d)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'nativeSources':items,'pairs':pairs,'sourceAuditPassed':True,'visualReview':'pending','repairAssemblyPerformed':False,'formalAccepted':False}
write(Q/'manifest.json',manifest)
print(json.dumps({'sourceAuditPassed':True,'pairs':[x['file'] for x in pairs]}))
