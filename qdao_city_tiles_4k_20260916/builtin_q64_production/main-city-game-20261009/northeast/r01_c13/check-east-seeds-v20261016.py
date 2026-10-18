from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/quick-20261016';Q.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
east=T.parent/'r01_c14';p=json.loads((east/'tile-progress.json').read_text(encoding='utf-8-sig'));candidate=Path(p['candidate']);assert sha(candidate)==p['candidateSha256'];im=Image.open(candidate).convert('RGB');records=[]
for patch,row in [('p14',0),('p44',3)]:
 f=T/'native'/(patch+'-v20261016.png');native=Image.open(f).convert('RGB');out=Image.new('RGB',(384,1024));out.paste(native.crop((947,115,1139,1139)),(0,0));out.paste(im.crop((0,row*1024,192,(row+1)*1024)),(192,0));dest=Q/(patch+'-east-native-join.png');assert not dest.exists();out.save(dest)
 records.append({'patch':patch,'file':str(f),'sha256':sha(f),'eastCandidate':str(candidate),'eastCandidateSha256':sha(candidate),'window':str(dest),'windowSha256':sha(dest),'operation':'exact native integer crops only'})
(Q/'east-seeds-sources.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records))

