from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=read(T/'selected-native.json')
for patch in ['p24','p34']:
    f=T/'native'/(patch+'-v20261016.png')
    j=read(Path(str(f)+'.generation.json'))
    assert sha(f)==j['sha256'] and Image.open(f).size==(1254,1254)
    sel[patch]=f.name
(T/'selected-native.json').write_text(json.dumps(sel,indent=2)+'\n')
Q=T/'qa/recovery-20261016';Q.mkdir(exist_ok=True)
east=read(T.parent/'r01_c14/tile-progress.json');ep=Path(east['candidate']);assert sha(ep)==east['candidateSha256']
im=Image.open(ep).convert('RGB');records=[]
for patch,row in [('p24',1),('p34',2)]:
    src=T/'native'/sel[patch];ni=Image.open(src).convert('RGB')
    win=Image.new('RGB',(384,1024));win.paste(ni.crop((947,115,1139,1139)),(0,0));win.paste(im.crop((0,row*1024,192,(row+1)*1024)),(192,0))
    out=Q/(patch+'-east-native-join.png');assert not out.exists();win.save(out)
    records.append({'native':str(src),'sha256':sha(src),'east':str(ep),'eastSha256':sha(ep),'window':str(out),'operation':'integer native crop-paste, no resizing'})
(Q/'east-new-sources.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))
