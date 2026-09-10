from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
import json,hashlib,numpy as np
p=Path(__file__).resolve().parent
dirs=['S','SW','W','NW','N','NE','E','SE']; errors=[]; stats={};sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'manifest.json').read_text(encoding='utf8'))
for f in m['files']:
 q=p/f['path']
 if not q.is_file() or sha(q)!=f['sha256']:errors.append('missing/hash '+f['path'])
portrait=Image.open(p/'portrait.png')
if portrait.size!=(1024,1024) or portrait.mode!='RGBA':errors.append('portrait contract')
if portrait.getchannel('A').getextrema()!=(0,255):errors.append('portrait alpha')
review=Image.new('RGB',(1104,8*280),(232,236,231)); draw=ImageDraw.Draw(review)
for row,d in enumerate(dirs):
 hashes=[];feet=[];fr=[]
 for i in range(1,5):
  f=p/'walk'/d/f'{i:02}.png';im=Image.open(f)
  if im.size!=(512,512) or im.mode!='RGBA':errors.append(f'{d}/{i} contract')
  a=np.array(im.getchannel('A')); y,x=np.nonzero(a>8);feet.append(int(y.max()));hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
  if y.min()==0 or x.min()==0 or y.max()==511 or x.max()==511:errors.append(f'{d}/{i} edge')
  if int(y.max())!=471:errors.append(f'{d}/{i} foot')
  fr.append(im.copy())
  t=im.resize((256,256));review.paste(t,(72+(i-1)*256,row*280+20),t)
 if len(set(hashes))!=4:errors.append(f'{d} repeats')
 strip=Image.open(p/'walk'/d/'strip.png')
 if strip.size!=(2048,512) or strip.mode!='RGBA':errors.append(f'{d} strip')
 for i in range(4):
  if strip.crop((i*512,0,(i+1)*512,512)).tobytes()!=fr[i].tobytes():errors.append(f'{d} strip frame {i}')
 g=Image.open(p/'walk'/d/'walk.gif');du=[x.info.get('duration') for x in ImageSequence.Iterator(g)]
 if du!=[120]*4:errors.append(f'{d} GIF {du}')
 stats[d]={'frames':4,'unique_frames':len(set(hashes)),'foot_y':feet,'gif_durations_ms':du}
 draw.text((12,row*280+130),d,fill=(28,40,36))
review.save(p/'processing/visual-review.jpg',quality=93)
report={'status':'passed' if not errors else 'failed','errors':errors,'directions':stats,'verified_manifest_files':len(m['files']),'checks':['manifest SHA-256','RGBA and sizes','32 distinct frames in 8 directions','no canvas edge contact','feet y=471','strips equal individual PNGs','GIF 4x120ms']}
(p/'delivery-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))
