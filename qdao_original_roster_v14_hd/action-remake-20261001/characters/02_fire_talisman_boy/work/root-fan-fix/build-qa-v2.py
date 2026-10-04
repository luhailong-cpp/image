import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2]
for rp in sorted((root/'records').glob('root-fan-cast-*-20261003-v2.json')):
 if '.receipt.' in rp.name:continue
 r=json.loads(rp.read_text(encoding='utf-8-sig'));np=Path(r.get('native',{}).get('sourceFile',''))
 if not np.is_file():continue
 hp=Path(r['evidence']['hostOutput']);sha=hashlib.sha256(np.read_bytes()).hexdigest()
 with Image.open(np) as new:
  new.load();ns=list(new.size);mode=new.mode;norm=new.resize((1024,1024),Image.Resampling.LANCZOS)
 r['native'].update(width=ns[0],height=ns[1],mode=mode,sha256=sha)
 r['evidence']['actualHostSHA']=hashlib.sha256(hp.read_bytes()).hexdigest();r['evidence']['actualNativeMatchesHost']=r['evidence']['actualHostSHA']==sha
 r['unverifiedReason']='宿主无型号/质量选择器，实际返回未披露版本及质量。'
 target=Image.open(r['references'][0]['path']).convert('RGBA')
 canvas=Image.new('RGB',(1024,850),'#263142');draw=ImageDraw.Draw(canvas)
 for i,im in enumerate([target,norm]):
  thumb=im.resize((512,512),Image.Resampling.LANCZOS);canvas.paste(thumb,(i*512,0),thumb)
  crop=im.crop((120,260,670,690) if r['requested_slot'].startswith('run') else (350,470,750,750));crop.thumbnail((500,300));canvas.paste(crop,(i*512,540),crop)
  draw.text((i*512+8,516),'original six-card target' if i==0 else 'AI local revision',fill='white')
 canvas.save(root/'work/root-fan-fix'/f"{r['call_id']}-compare.jpg",quality=95)
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(r['requested_slot'],ns,mode,sha,r['evidence']['actualNativeMatchesHost'])
