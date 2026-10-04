import json,hashlib,shutil
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1]
for i,stem,oldstem in [(3,'run_SW_03_v4','run_SW_03_v3'),(9,'run_SW_09_v3','run_SW_09_v2')]:
 out=B/'runtime/run/SW'/f'{i:02d}.png';source=B/'work'/f'{stem}.png';rec=source.with_name(source.name+'.generation.json')
 r=json.loads(rec.read_text(encoding='utf-8'));im=Image.open(source);im.load()
 assert im.size==(1254,1254) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 old=out.with_name(out.name+'.generation.json');d=json.loads(old.read_text(encoding='utf-8'))
 assert d['derivedFrom'][0]['file']==f'work/{oldstem}.png'
 shutil.copy2(old,B/'records'/f'{oldstem}_runtime_superseded.json')
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 d.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),derivedFrom=[{'file':r['file'],'sha256':r['sha256'],'generationRecord':rec.relative_to(B).as_posix()}],native=r['native'],visualReview=r['visualReview'],generatedAt=r['generatedAt'])
 old.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 r.update(exported=True,exportPath=out.relative_to(B).as_posix());rec.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(stem+' exported')

