from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil
B=Path(__file__).resolve().parent
src=B.parent.parent/'lanxian_day/r08_c10/selected'
out=B/'shared-geometry';out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
expected={'core4096.png':'bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f','extended4326.png':'2d4552bb7fa01baeb6fc0ac759360a50a08b9a90f65b285536a88947356e9e6e'}
for name,digest in expected.items():
    assert sha(src/name)==digest
    shutil.copyfile(src/name,out/name)
    assert sha(out/name)==digest
e=out/'source-evidence';e.mkdir(exist_ok=True)
records=[]
for path in src.parent.rglob('*.json'):
    rel=path.relative_to(src.parent);dest=e/rel;dest.parent.mkdir(exist_ok=True,parents=True)
    shutil.copyfile(path,dest);records.append({'source':str(path),'snapshot':str(dest),'sha256':sha(dest)})
wr(out/'source.json',{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'selectedDayGeometry':expected,'sourceDirectory':str(src),'records':records,'sourceUnchanged':True,'formalAccepted':False,'crossAppearanceIntent':'Use exact day geometry and retain all pixels except masked seasonal surface edits. Independent spring regional and four native pieces superseded, not final.'})
r=B/'spring-edits/southwest';r.mkdir(parents=True,exist_ok=True)
im=Image.open(out/'extended4326.png').convert('RGB');box=[0,3072,1254,4326];p=r/'edit-target-1254.png';im.crop(box).save(p)
wr(r/'edit-target-1254.derived.json',{'file':str(p),'sha256':sha(p),'source':str(out/'extended4326.png'),'sourceSha256':expected['extended4326.png'],'cropInExtended':box,'pixels':[1254,1254],'resized':False,'coreOrigin':[-115,2957]})
print(json.dumps({'core':str(out/'core4096.png'),'snapshotCount':len(records),'crop':str(p)},ensure_ascii=False))
