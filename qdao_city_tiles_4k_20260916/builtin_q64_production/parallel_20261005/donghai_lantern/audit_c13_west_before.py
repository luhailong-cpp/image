"""Unscaled c12/c13 pre-repair seam crops; no image editing or global state writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
DAY=ROOT.parent/'donghai_day'
OUT=ROOT/'r08_c13/repairs/west-common-edge/pre-repair-qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
OUT.mkdir(parents=True,exist_ok=True)
sources={
 'festival':[(ROOT/'r08_c12/west-final/output/r08_c12.png','fd839140eabb7c9ab5ecdfd76425db43602d6eee9011faa2a804dfb0098cea44'),(ROOT/'r08_c13/tone-assembly/output/r08_c13.png','1716a3d15381c91019b6e58b0bde3acdb361e64f468697a90b3b5ad66e540b54')],
 'day':[(DAY/'tiles/r08_c12.png',None),(DAY/'r08_c13/output/r08_c13.png','cce78295d75e75670b96462945b6624044841aba400003961e9c8f8fe3bfafb0')]}
items=[];bindings={}
for kind,entries in sources.items():
    ims=[];bindings[kind]=[]
    for p,digest in entries:
        if digest:assert sha(p)==digest
        im=Image.open(p);im.load();assert im.size==(4096,4096)
        ims.append(im.convert('RGB'));bindings[kind].append(info(p))
    band=Image.new('RGB',(1024,4096));band.paste(ims[0].crop((3584,0,4096,4096)),(0,0));band.paste(ims[1].crop((0,0,512,4096)),(512,0))
    for part in range(4):
        p=OUT/f'{kind}-common-edge-part{part+1:02}.png'
        band.crop((0,part*1024,1024,(part+1)*1024)).save(p)
        rec={**info(p),'kind':kind,'pairRectXYXY':[3584,part*1024,4608,(part+1)*1024],'globalRectXYWH':[48640,28672+part*1024,1024,1024],'globalSeamX':49152,'derivedFrom':bindings[kind],'pixelScale':1,'resized':False,'review':'pending'}
        Path(str(p)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');items.append(rec)
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'pre-repair common edge; source strip has unresolved geometry, not accepted','sources':bindings,'items':items,'formalAccepted':False,'globalStateModified':False}
(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaFolder':str(OUT),'nativeImages':len(items),'sources':bindings},indent=2))
