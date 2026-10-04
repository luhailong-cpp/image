import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
items=[('W idle',Path('D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/W.png'),False),('E00 registered',ROOT/'runtime/run/E/00.png',False),('W00 current',ROOT/'runtime/run/W/00.png',False),('W00 same E matrix trial',ROOT/'runtime/run/W/00.png',True)]
for n in [0,4,8,12]:items.append((f'W{n:02d} same E matrix trial',ROOT/'runtime/run/W'/f'{n:02d}.png',True))
sheet=Image.new('RGB',(1600,856),(33,49,55));d=ImageDraw.Draw(sheet);records=[]
for i,(label,p,trial) in enumerate(items):
 im=Image.open(p).convert('RGBA')
 if trial:
  r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'));src=ROOT/r['derivedFrom'][0]['file']
  native=Image.open(src).convert('RGBA')
  im=Image.new('RGBA',(1024,1024));im.alpha_composite(native.resize((901,901),Image.Resampling.LANCZOS),(61,97))
 else:src=p
 tile=im.resize((400,400),Image.Resampling.LANCZOS);x=(i%4)*400;y=(i//4)*428
 sheet.paste(tile,(x,y),tile);d.line((x,y+941.6875*400/1024,x+399,y+941.6875*400/1024),fill=(180,163,89));d.text((x+8,y+405),label,fill=(255,240,214))
 records.append({'label':label,'input':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native':str(src),'trialOnly':trial})
out=ROOT/'review/run_W_key_camera_proposal_20261003.png';sheet.save(out)
(ROOT/'review/run_W_key_camera_proposal_20261003.json').write_text(json.dumps({'images':records,'runtimeChanged':False,'proposedIdenticalMatrixNativeToRuntime':[[901/1254,0,61],[0,901/1254,97],[0,0,1]],'status':'four independent key frames only; not a full loop, not final camera acceptance','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)

