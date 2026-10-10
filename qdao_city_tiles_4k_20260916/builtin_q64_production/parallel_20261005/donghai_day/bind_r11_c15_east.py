from pathlib import Path
import hashlib,json,datetime
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r11_c15'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads((T/'plan.json').read_text());ep=json.loads((R/'r11_c16/plan.json').read_text());x,y,w,h=ep['globalRect'];assert [x,y,w,h]==[61440,40960,4096,4096]
expected={2:'f9031ea671b73cd290cad3592fae37842b17cd8073332bc921480cb028ba15b7',3:'85eeefa3394ca22d2b2d14adbb471e534c5b17d9a55fccf8bc9e8063b453f0c7',4:'e58ea33f860647aa4d0f903b421806037a38385c9484051cd9f9a96011b876d2'}
assert not d['externalNativeBindings']
for row,value in expected.items():
 f=R/'r11_c16/native'/f'r{row:02d}_c01.png';rec=Path(str(f)+'.generation.json');v=json.loads(rec.read_text());assert sha(f)==value==v['sha256'];assert Image.open(f).size==(1254,1254)
 d['externalNativeBindings'].append(dict(file=str(f),sha256=value,record=str(rec),recordSha256=sha(rec),tile='r11_c16',row=row,column=1,globalRectXYXY=[x-115,y-115+(row-1)*1024,x+1139,y+1139+(row-1)*1024],role='explicit actual east neighboring native pixels; this is not a complete tile'))
d['externalNativeBoundAtUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(T/'plan.json').write_text(json.dumps(d,indent=2)+'\n')
print('Bound3eastnatives')

