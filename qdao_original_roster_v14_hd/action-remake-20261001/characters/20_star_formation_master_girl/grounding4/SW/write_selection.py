from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
s=['runtime/run/SW/01.png','runtime/run/SW/02.png','grounding4/SW/03-v5.png','grounding4/SW/04-v4.png','grounding4/SW/05-v2.png','grounding4/SW/06-v2.png','runtime/run/SW/04.png','grounding4/SW/08-v1.png','runtime/run/SW/09.png','grounding4/SW/10-v1.png','grounding4/SW/11-v1.png','grounding4/SW/12-v2.png','grounding4/SW/13-v3.png','grounding4/SW/14-v4.png','runtime/run/SW/12.png','grounding4/SW/16-v1.png']
selected=[]
for i,p in enumerate(s):
 im=Image.open(b/p);assert im.size==(1024,1024) and im.mode=='RGBA';j=b/(p+'.generation.json');assert j.exists()
 selected.append({'frame':i+1,'exportFile':p,'nativeFile':json.loads(j.read_text(encoding='utf-8')).get('native',{}).get('file',p),'generationRecord':p+'.generation.json','sha256':hashlib.sha256((b/p).read_bytes()).hexdigest(),'supportFoot':'right' if i<8 else 'left','position':['front_landing','under_hip','behind_hip','rear_push'][(i%8)//2],'mode':'retain' if p.startswith('runtime/') and p.endswith(f'{i+1:02d}.png') else 'replace_or_rephase','visualStaticReviewed':True})
assert len(set(x['sha256'] for x in selected))==16
(b/'grounding4/SW/selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
out=Image.new('RGB',(1280,1400),(234,230,220));dr=ImageDraw.Draw(out);anim=[]
for i,p in enumerate(s):
 im=Image.open(b/p).resize((320,320));out.paste(im,((i%4)*320,(i//4)*350),im);dr.text(((i%4)*320+6,(i//4)*350+322),f'{i+1:02d} '+Path(p).stem,fill='black')
 frame=Image.new('RGBA',(320,350),(234,230,220,255));frame.alpha_composite(im);ImageDraw.Draw(frame).text((10,325),f'SW {i+1:02d}/16  1200ms',fill='black');anim.append(frame)
out.save(b/'grounding4/SW/selected-contact.jpg')
anim[0].save(b/'grounding4/SW/selected-normal.png',save_all=True,append_images=anim[1:],duration=75,loop=0,disposal=0,blend=0)
print('SW selected 16 distinct. Static contact sheet and normal75ms APNG exported.')

