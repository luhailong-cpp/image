from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
s=['runtime/run/W/01.png','runtime/run/W/02.png','grounding4/W/03-v3.png','grounding4/W/04-v1.png','grounding4/W/05-v1.png','grounding4/W/06-v1.png','runtime/run/W/04.png','grounding4/W/08-v1.png','runtime/run/W/09.png','runtime/run/W/10.png','runtime/run/W/11.png','grounding4/W/12-v3.png','grounding4/W/13-v2.png','grounding4/W/14-v2.png','grounding4/W/15-v1.png','grounding4/W/16-v1.png']
for i,p in enumerate(s):
 if not (b/p).exists(): print('pending',p)
if all((b/p).exists() for p in s):
 out=Image.new('RGB',(1280,1400),(234,230,220));dr=ImageDraw.Draw(out)
 feet=[]
 for i,p in enumerate(s):
  im=Image.open(b/p);out.paste(im.resize((320,320)),((i%4)*320,(i//4)*350),im.resize((320,320)));dr.text(((i%4)*320+6,(i//4)*350+322),str(i+1)+' '+Path(p).stem,fill='black')
  ar=im.getchannel('A');box=ar.crop((0,800,1024,1024)).getbbox();feet.append([i+1,box[-1]+800 if box else None])
 out.save(b/'grounding4/W/selected-contact.jpg')
 print(json.dumps(feet))

