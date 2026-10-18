from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1];T=B/'r15_c06'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cat=read(B/'current-candidates.json')['tiles'];out=[]
for name,tile,box in [('top-r14_c06-current-native-v01','r14_c06',[0,4096,4326,4326]),('left-r15_c05-current-native-v01','r15_c05',[4096,0,4326,4326])]:
 e=cat[tile]['context'];assert sha(e['file'])==e['sha256'];p=T/'pipeline/anchors'/(name+'.png');assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
 im=Image.open(e['file']).convert('RGB');assert im.size==(4326,4326);im.crop(box).save(p)
 d={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceTile':tile,'sourceCurrentAssembly':cat[tile]['assembly'],'source':e['file'],'sourceSha256':e['sha256'],'crop':box,'sourceResampling':False,'operation':'exact crop of actual current assembled native context','nativeAnchor':True,'neighborAccepted':False,'formalAccepted':False,'sha256':sha(p)}
 p.with_suffix('.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');out.append({'anchor':str(p),'sha256':sha(p),'size':Image.open(p).size})
print(json.dumps(out))

