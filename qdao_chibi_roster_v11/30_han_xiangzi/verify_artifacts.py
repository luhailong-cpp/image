from pathlib import Path
import json, hashlib, sys
import numpy as np
from PIL import Image, ImageDraw
char=Path(__file__).resolve().parent
directions=['S','SW','W','NW','N','NE','E','SE']
report={'portrait':{},'frames':{},'gifs':{},'errors':[]}
portrait=Image.open(char/'portrait.png'); report['portrait']={'size':list(portrait.size),'mode':portrait.mode,'alpha_range':list(portrait.getchannel('A').getextrema())}
assert portrait.size==(1024,1024) and portrait.mode=='RGBA'
contact=Image.new('RGB',(1120,8*290+50),(226,229,220));draw=ImageDraw.Draw(contact)
draw.text((16,10),'Han Xiangzi | S SW W NW N NE E SE | original 4 phase walk',fill=(35,55,50))
all_hashes=[]
for row,d in enumerate(directions):
 draw.text((8,55+row*290),d,fill=(25,40,35))
 for i in range(1,5):
  p=char/'walk'/d/f'{i:02d}.png';im=Image.open(p).convert('RGBA');assert im.size==(512,512)
  ar=np.asarray(im);yy,xx=np.where(ar[:,:,3]>8);fy=int(yy.max());fx=float(np.median(xx[yy>=np.percentile(yy,90)]));assert fy==471
  h=hashlib.sha256(im.tobytes()).hexdigest();all_hashes.append(h)
  report['frames'][f'{d}/{i:02d}']={'feet':[fx,fy],'rgba_sha256':h,'size':list(im.size)}
  small=im.resize((270,270),Image.Resampling.LANCZOS);contact.paste(small,(30+(i-1)*270,60+row*290),small)
 strip=Image.open(char/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
 gif=Image.open(char/'walk'/d/'walk.gif');ds=[]
 for i in range(gif.n_frames):gif.seek(i);ds.append(gif.info.get('duration'))
 assert gif.n_frames==4 and ds==[120]*4
 report['gifs'][d]={'frames':gif.n_frames,'duration_ms':ds}
assert len(set(all_hashes))==32
report['unique_frame_hashes']=len(set(all_hashes));report['status']='passed_artifact_contract'
(char/'processing/artifact-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
contact.save(char/'processing/visual-review.jpg',quality=92)
print(json.dumps({'status':report['status'],'unique_frames':len(set(all_hashes)),'contact':str(char/'processing/visual-review.jpg')}))
