from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,importlib.util
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location('exp',R/'tools/export_frame.py');e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
host=Path('C:/Users/luyua/.codex/generated_images/01a100fe-197e-7b91-863c-02ed5327ac7a')
for n,fn in [(6,'exec-08ac60a6-fef8-4c47-8ccb-ea55ecc45c23.png'),(7,'exec-b8f85c65-0ef4-44d5-8e17-1ac88aef0242.png')]:
 dst=R/'cast/staging'/f'cast-E-{n:02}-recovered.png';shutil.copy2(host/fn,dst)
 im=Image.open(dst);reqs=[f'provenance/cast-E-{x:02}-v3.submitted.json' for x in [6,7,16]]
 rec={'file':dst.relative_to(R).as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'generatedAt':datetime.fromtimestamp((host/fn).stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host mtime; exact tool timestamp not exposed','references':[str(R/'cast/staging/cast-E-05-v3.png'),'D:/work/image/designs/jubaozhai-ui/02-characters.png'],'promptCandidates':reqs,'evidence':{'hostPath':str(host/fn),'recovery':'provenance/cast-interrupted-batch-recovery.json','exactRequestOutputMapping':'unconfirmed; assigned delivery slot by actual pose'},'unverifiedReason':'Host-managed; tool metadata not available after interrupted call. Model/quality and exact request mapping unconfirmed.'}
 Path(str(dst)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
versions={1:'v2',2:'v1',3:'v1',4:'v3',5:'v3',6:'recovered',7:'recovered',8:'v2',9:'v5',10:'v2',11:'v2',12:'v2',13:'v3',14:'v2',15:'v2',16:'v4'}
for n,v in versions.items():e.run(R/'cast/staging'/f'cast-E-{n:02}-{v}.png',R/'cast/E'/f'{n:02}.png')
for d in ['E','W']:
 sheet=Image.new('RGB',(1280,1400),'#e5e8e8');draw=ImageDraw.Draw(sheet)
 for n in range(1,17):
  p=R/'cast'/d/f'{n:02}.png';im=Image.open(p).convert('RGBA').resize((320,320));x=((n-1)%4)*320;y=((n-1)//4)*350
  sheet.paste(im,(x,y),im);draw.text((x+6,y+322),f'cast {d} {n:02}',fill='#203040');draw.line((x,y+300,x+320,y+300),fill='#668877')
 (R/'cast'/d/'preview-review').mkdir(exist_ok=True);sheet.save(R/'cast'/d/'preview-review/contact.jpg',quality=94)

