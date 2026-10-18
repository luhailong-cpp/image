from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[1];d=B/'r12_c06/repairs-resume-20261012/right-ground-inlay-20261016-v03';a=json.loads((d/'integrated-masked-20261012-v02/assembly.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa=d/'qa-native';assert not qa.exists();qa.mkdir()
im=Image.open(a['contextOutput']['file']).convert('RGB');l,t,r,b=[3072,115,4326,1369]
items=[]
for name,box in [('integrated-target',(l,t,r,b)),('left-interface',(l-60,t,l+160,t+700)),('top-interface',(l,t-60,r,t+160)),('bottom-interface',(l,t+620,r,t+780)),('right-native-anchor',(4096,0,4326,1254))]:
    p=qa/(name+'.png');im.crop(box).save(p);items.append({'name':name,'file':str(p),'crop':list(box),'source':a['contextOutput']['file'],'sourceSha256':a['contextOutput']['sha256'],'sha256':sha(p),'sourceResampling':False})
(qa/'manifest.json').write_text(json.dumps({'assembly':str(d/'integrated-masked-20261012-v02/assembly.json'),'assemblySha256':sha(d/'integrated-masked-20261012-v02/assembly.json'),'items':items,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'core':a['output'],'context':a['contextOutput'],'views':items},ensure_ascii=False))

