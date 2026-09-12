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
  foot_x=float(np.median(xs[ys>=np.percentile(ys,90)])); assert abs(foot_x-256)<=0.5,(p,foot_x)
  box=im.getchannel('A').getbbox();assert min(box)>0 and box[2]<512 and box[3]<512,(p,box)
  h=hashlib.sha256(im.tobytes()).hexdigest();assert h not in seen,p;seen.add(h)
  thumb=im.resize((220,220),Image.Resampling.LANCZOS);review.paste(thumb,((n-1)*220,row*220),thumb)
  draw.text(((n-1)*220+8,row*220+5),f'{d} {n}',font=font,fill='#35483e')
 strip=Image.open(char/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
 for i in range(4): assert strip.crop((i*512,0,(i+1)*512,512)).tobytes()==Image.open(char/'walk'/d/f'{i+1:02d}.png').tobytes(),(d,i,'strip mismatch')
 gif=Image.open(char/'walk'/d/'walk.gif');assert gif.n_frames==4
 for i in range(4):gif.seek(i);assert gif.info['duration']==120,(d,i,gif.info)
for kind,rows in {'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}.items():
 sheet=Image.open(char/f'walk-{kind}.png'); assert sheet.size==(2048,2048) and sheet.mode=='RGBA'
 for y,d in enumerate(rows):
  for x in range(4): assert sheet.crop((x*512,y*512,(x+1)*512,(y+1)*512)).tobytes()==Image.open(char/'walk'/d/f'{x+1:02d}.png').tobytes(),(kind,d,x,'sheet mismatch')
m=json.loads((char/'manifest.json').read_text(encoding='utf8'))
assert len(m['files'])==51
for f in m['files']:
 p=char/f['path']; assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],p
(char/'processing').mkdir(exist_ok=True)
review.save(char/'processing/visual-review.jpg',quality=94,subsampling=0)
qc['artifact_validation']={'portrait':'1024x1024 RGBA','independent_walk_frames':32,'unique_frame_hashes':32,'frame_size':[512,512],'directions':8,'strips':'2048x512 RGBA','gifs':8,'gif_frames_each':4,'duration_ms':120,'all_feet_y':471,'foot_x_max_error_px':0.5,'direction_sheets':'2 x 2048x2048 RGBA','strip_and_sheet_frames_match':True,'manifest_hashes_verified':51}
(char/'qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(qc['artifact_validation']))
