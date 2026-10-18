from pathlib import Path
import json,datetime,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;D.mkdir(exist_ok=True)
R=D.parent
for key in ['upper','lower']:
 src=next((R/key/'attempt2').glob('actual-native-*.png'));im=Image.open(src)
 if key=='upper':boxes={'corner-raw':[390,1000,580,1254],'joint-raw':[730,850,900,1080]}
 else:boxes={'corner-raw':[380,820,660,1160],'joint-raw':[740,790,900,990]}
 for n,b in boxes.items():
  p=D/(key+'-'+n+'.png');assert not p.exists();im.crop(b).save(p)
N=R.parent/'north-corner-20261016/trial-v1'
qa=json.loads((N/'visual-qa.json').read_text(encoding='utf-8'))
p=N/'root-independent-qa-20261016.json';assert not p.exists()
doc=dict(reviewer='/root',recordedBy='/root/assembly_resume',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),authority='ROOT message: 已实际看N02 6张证据，真实north竖线已连续，四mask边界无新断头，局部通过；选源由root统一合并。',reviewedCore=qa['core'],evidence=qa['evidence'],status='passed_local',published=False,formalAccepted=False)
p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(rootN02QA=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())))

