from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys,numpy as np
char=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
qc=json.loads((char/'qc.json').read_text(encoding='utf8'))
assert not qc['errors'],qc['errors']
dirs=['S','SW','W','NW','N','NE','E','SE']
seen=set(); review=Image.new('RGB',(880,1760),'#eeeade'); draw=ImageDraw.Draw(review)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
p=Image.open(char/'portrait.png');assert p.size==(1024,1024) and p.mode=='RGBA'
for row,d in enumerate(dirs):
 for n in range(1,5):
  p=char/'walk'/d/f'{n:02d}.png';im=Image.open(p)
  assert im.size==(512,512) and im.mode=='RGBA',p
  ar=np.asarray(im);a=ar[:,:,3]; assert a.min()==0 and a.max()==255,p
  ys,xs=np.where(a>8); assert ys.max()==471,(p,int(ys.max()))
  box=im.getchannel('A').getbbox();assert min(box)>0 and box[2]<512 and box[3]<512,(p,box)
  h=hashlib.sha256(im.tobytes()).hexdigest();assert h not in seen,p;seen.add(h)
  thumb=im.resize((220,220),Image.Resampling.LANCZOS);review.paste(thumb,((n-1)*220,row*220),thumb)
  draw.text(((n-1)*220+8,row*220+5),f'{d} {n}',font=font,fill='#35483e')
 strip=Image.open(char/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
 gif=Image.open(char/'walk'/d/'walk.gif');assert gif.n_frames==4
 for i in range(4):gif.seek(i);assert gif.info['duration']==120,(d,i,gif.info)
(char/'processing').mkdir(exist_ok=True)
review.save(char/'processing/visual-review.jpg',quality=94,subsampling=0)
qc['artifact_validation']={'portrait':'1024x1024 RGBA','independent_walk_frames':32,'unique_frame_hashes':32,'frame_size':[512,512],'directions':8,'strips':'2048x512 RGBA','gifs':8,'gif_frames_each':4,'duration_ms':120,'all_feet_y':471}
(char/'qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(qc['artifact_validation']))
