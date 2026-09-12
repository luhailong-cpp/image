"""Validate exported files and create pixel-derived PNG/GIF contact views; never draw art."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageSequence
char=Path(__file__).resolve().parent
directions=['S','SW','W','NW','N','NE','E','SE']
report={'portrait':{},'frames':{},'gifs':{},'sheets':{},'errors':[]}
portrait=Image.open(char/'portrait.png')
report['portrait']={'size':list(portrait.size),'mode':portrait.mode,'alpha_range':list(portrait.getchannel('A').getextrema())}
assert portrait.size==(1024,1024) and portrait.mode=='RGBA' and portrait.getchannel('A').getextrema()==(0,255)
all_hashes=[]
views={}
for start in [0,4]:
 out=Image.new('RGB',(1120,4*290+50),(226,229,220));d=ImageDraw.Draw(out)
 d.text((16,10),'Han Xiangzi | original four phase walk | PNG RGBA',fill=(35,55,50))
 views[start]=(out,d)
gif_view=Image.new('RGB',(1120,8*290+50),(55,65,70));gd=ImageDraw.Draw(gif_view)
gd.text((16,10),'Decoded transparent GIF phases | 120 ms each | S SW W NW N NE E SE',fill=(235,235,225))
for row,d in enumerate(directions):
 out,draw=views[0 if row<4 else 4];r=row%4
 draw.text((8,55+r*290),d,fill=(25,40,35));gd.text((8,55+row*290),d,fill=(235,235,225))
 frames=[]
 for i in range(1,5):
  p=char/'walk'/d/f'{i:02d}.png';im=Image.open(p);assert im.size==(512,512) and im.mode=='RGBA'
  ar=np.asarray(im);alpha=ar[:,:,3];yy,xx=np.where(alpha>8);fy=int(yy.max());fx=float(np.median(xx[yy>=np.percentile(yy,90)]));assert fy==471 and abs(fx-256)<=0.5
  assert alpha.min()==0 and alpha.max()==255 and not np.any(np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]))
  magenta=int(((ar[:,:,0]>180)&(ar[:,:,1]<90)&(ar[:,:,2]>180)&(alpha>32)).sum());assert magenta==0
  h=hashlib.sha256(im.tobytes()).hexdigest();all_hashes.append(h);frames.append(im)
  report['frames'][f'{d}/{i:02d}']={'feet':[fx,fy],'rgba_sha256':h,'size':list(im.size),'mode':im.mode,'alpha_range':[int(alpha.min()),int(alpha.max())],'edge_touch':False,'magenta_like_pixels':magenta}
  small=im.resize((270,270),Image.Resampling.LANCZOS);out.paste(small,(30+(i-1)*270,60+r*290),small)
 strip=Image.open(char/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
 for i,im in enumerate(frames):assert strip.crop((i*512,0,(i+1)*512,512)).tobytes()==im.tobytes()
 gif=Image.open(char/'walk'/d/'walk.gif');ds=[];hashes=[]
 assert gif.info.get('loop')==0
 for i,frame in enumerate(ImageSequence.Iterator(gif)):
  ds.append(frame.info.get('duration'));im=frame.convert('RGBA');assert im.getpixel((0,0))[3]==0
  hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
  small=im.resize((270,270),Image.Resampling.LANCZOS);gif_view.paste(small,(30+i*270,60+row*290),small)
 assert gif.n_frames==4 and ds==[120]*4 and len(set(hashes))==4
 report['gifs'][d]={'frames':gif.n_frames,'duration_ms':ds,'loop':0,'transparent_corner':True,'unique_decoded_frames':len(set(hashes))}
for kind,dirs in {'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}.items():
 im=Image.open(char/f'walk-{kind}.png');assert im.size==(2048,2048) and im.mode=='RGBA'
 for r,d in enumerate(dirs):
  for c in range(4):assert im.crop((c*512,r*512,(c+1)*512,(r+1)*512)).tobytes()==Image.open(char/'walk'/d/f'{c+1:02d}.png').tobytes()
 report['sheets'][kind]={'size':list(im.size),'mode':im.mode,'row_order':dirs,'matches_individual_frames':True}
assert len(set(all_hashes))==32
manifest=json.loads((char/'manifest.json').read_text(encoding='utf8'))
for f in manifest['files']:assert hashlib.sha256((char/f['path']).read_bytes()).hexdigest()==f['sha256']
report['manifest_files_verified']=len(manifest['files']);report['unique_frame_hashes']=len(set(all_hashes));report['status']='passed_artifact_contract'
(char/'processing/artifact-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
for i,(out,draw) in views.items():out.save(char/f'processing/visual-review-{i//4+1}.jpg',quality=94)
gif_view.save(char/'processing/gif-decoded-review.jpg',quality=94)
print(json.dumps({'status':report['status'],'unique_frames':len(set(all_hashes)),'manifest_files':len(manifest['files']),'contacts':['processing/visual-review-1.jpg','processing/visual-review-2.jpg','processing/gif-decoded-review.jpg']}))
