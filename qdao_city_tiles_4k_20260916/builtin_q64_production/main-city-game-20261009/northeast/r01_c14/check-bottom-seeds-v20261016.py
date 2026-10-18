from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/quick-20261016';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
below=T.parent/'r02_c14';bp=json.loads((below/'tile-progress.json').read_text());bfile=Path(bp['candidate']);assert sha(bfile)==bp['candidateSha256'];bi=Image.open(bfile).convert('RGB');records=[]
for p,col in [('p41',0),('p44',3)]:
 f=T/'native'/(p+'-v20261016.png');im=Image.open(f).convert('RGB');out=Image.new('RGB',(1024,384));out.paste(im.crop([115,947,1139,1139]),(0,0));out.paste(bi.crop([col*1024,0,(col+1)*1024,192]),(0,192));dest=Q/(p+'-south-native-join.png');assert not dest.exists();out.save(dest)
 records.append({'patch':p,'source':str(f),'sha256':sha(f),'southCandidate':str(bfile),'southCandidateSha256':sha(bfile),'window':str(dest),'operation':'Integer source crops without resampling'})
(Q/'first-bottom-seed-sources.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))

