import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent/'SE-QA';O.mkdir(exist_ok=True)
S=json.loads((R/'10-work/selection-SE-review.json').read_text(encoding='utf-8-sig'))
for k in ['SE07','SE15']:
 if k not in S and (R/'10-generation'/f'{k}-v1'/'raw.png').exists():S[k]={'archive':k+'-v1'}
keys=[f'SE{i:02}' for i in range(1,17)]+['SEidle']
I={k:Image.open(R/'10-generation'/S[k]['archive']/'raw.png').convert('RGBA') for k in keys}
for name,color in [('light','#f4efe3'),('dark','#1e272b')]:
 for group,ks in [('01-08',keys[:8]),('09-16',keys[8:16]),('seam',[keys[i-1] for i in [15,16,1,2]]),('idle',['SEidle'])]:
  im=Image.new('RGB',(512*min(4,len(ks)),546*((len(ks)+3)//4)),color);d=ImageDraw.Draw(im)
  for n,k in enumerate(ks):
   f=I[k].resize((512,512),Image.Resampling.LANCZOS);x=n%4*512;y=n//4*546;im.paste(f,(x,y),f);d.text((x+10,y+518),k+' '+S[k]['archive'],fill='white' if name=='dark' else 'black')
  im.save(O/f'{name}-{group}.jpg',quality=96)
 for g in range(4):
  im=Image.new('RGB',(2048,625),color);d=ImageDraw.Draw(im)
  for n,k in enumerate(keys[g*4:g*4+4]):
   f=I[k].crop((380,780,920,1230)).resize((512,590),Image.Resampling.LANCZOS);im.paste(f,(n*512,0),f);d.text((n*512+10,600),k,fill='white' if name=='dark' else 'black')
  im.save(O/f'{name}-feet-{g+1}.jpg',quality=96)
(O/'examined-selection.json').write_text(json.dumps(S,indent=2)+'\n',encoding='utf-8')
print(O)
