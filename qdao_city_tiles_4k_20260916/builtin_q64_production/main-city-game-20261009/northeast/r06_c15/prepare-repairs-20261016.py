from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/resume-20261016';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=T/'candidates/r06_c15.local-repairs-resume2-v1.png';assert sha(p)=='18b1d2776b4f22e734484b3b70d957cb942d3ef38ed5c09a921ad5147432136b'
im=Image.open(p).convert('RGB');items=[]
for id,xy in [('panel',[0,2842]),('roof',[2580,2600]),('wallrail',[840,1600]),('upperroof',[680,570])]:
 f=Q/(id+'-input-v1.png');assert not f.exists();im.crop((xy[0],xy[1],xy[0]+1254,xy[1]+1254)).save(f)
 items.append({'id':id,'origin':xy,'file':str(f),'sha256':sha(f),'size':[1254,1254],'resized':False,'samePointPriorAIAttempts':1})
plan={'tile':'r06_c15','baseCandidate':{'file':str(p),'sha256':sha(p),'pixels':[4096,4096]},'repairs':items}
(Q/'repair-plan-v1.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=T.parent/'r07_c16/save-local-repair-20261016.py';dest=T/'save-local-repair-20261016.py';assert not dest.exists();dest.write_text(src.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(plan,ensure_ascii=False))

