from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib
A=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
I=read(A/'verified-current-index.json');D=A/'shared-edge-priority-crops';D.mkdir(exist_ok=True)
targets=[('tianyong_festival','r09_c09','r09_c10','vertical'),('tianyong_festival','r09_c10','r10_c10','horizontal'),('donghai_day','r08_c12','r08_c13','vertical')]
records=[]
for ap,ta,tb,ori in targets:
    entries=next(a['entries'] for a in I['appearances'] if a['appearance']==ap)
    ea,eb=[next(e for e in entries if e['tileId']==t) for t in [ta,tb]]
    for e in [ea,eb]:assert sha(e['path'])==e['sha256'],e['path']
    ia,ib=[Image.open(e['path']).convert('RGB') for e in [ea,eb]]
    if ori=='vertical':
        band=Image.new('RGB',(256,4096));band.paste(ia.crop((3968,0,4096,4096)),(0,0));band.paste(ib.crop((0,0,128,4096)),(128,0))
        out=Image.new('RGB',(1024,1024))
        for k in range(4):out.paste(band.crop((0,k*1024,256,(k+1)*1024)),(k*256,0))
    else:
        band=Image.new('RGB',(4096,256));band.paste(ia.crop((0,3968,4096,4096)),(0,0));band.paste(ib.crop((0,0,4096,128)),(0,128))
        out=Image.new('RGB',(1024,1024))
        for k in range(4):out.paste(band.crop((k*1024,0,(k+1)*1024,256)),(0,k*256))
    path=D/f'{ap}-{ta}-{tb}.png';out.save(path)
    records.append({'appearance':ap,'tiles':[ta,tb],'orientation':ori,'sources':[{'path':e['path'],'sha256':e['sha256']} for e in [ea,eb]],'crop':{'path':path.as_posix(),'sha256':sha(path),'pixels':[1024,1024],'nativeScale':1,'packing':'four 1024-long segments placed without scaling','seamInEachSegment':128,'bandWidth':256},'actualVisualReview':'pending'})
(D/'manifest.json').write_text(json.dumps({'createdAt':datetime.now(timezone.utc).isoformat(),'indexSha256':sha(A/'verified-current-index.json'),'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
