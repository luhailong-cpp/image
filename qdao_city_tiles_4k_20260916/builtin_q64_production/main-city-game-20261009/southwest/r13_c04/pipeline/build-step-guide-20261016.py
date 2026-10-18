from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
T=Path(__file__).resolve().parents[1];p=T/'pipeline/guides/p01_04.left-step-20261016-v02.geometry-only.png';assert not p.exists()
lines=[[820,0,820,815],[820,815,745,875],[745,875,745,1254],[745,0,745,800],[745,800,670,875],[670,875,670,1254],[820,300,1254,300],[820,790,1254,790]]
im=Image.new('RGB',(1254,1254),(246,246,246));d=ImageDraw.Draw(im)
for a in lines:d.line(a,fill=(35,35,35),width=3)
im.save(p);Path(str(p)+'.derivation.json').write_text(json.dumps({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':lines,'category':'mechanical approved-layout constraint only; not artwork','resampling':False,'formalAccepted':False},indent=2)+'\n',encoding='utf-8');print(p)
