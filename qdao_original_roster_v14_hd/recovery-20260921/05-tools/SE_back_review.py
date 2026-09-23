"""Static QA and selection handoff for SE slots 10,11,12,14,15,16 only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
from PIL import Image,ImageDraw
import numpy as np
G=Path(__file__).resolve().parent.parent/'05-generation'
O=G/'SE-back-review';O.mkdir(exist_ok=True)
owned=[10,11,12,14,15,16]
versions={1:1,9:2,13:2}
images=[];rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in [9,10,11,12,13,14,15,16,1]:
 d=G/f'SE{n:02d}-single-v{versions.get(n,1)}'
 c=d/'staging/candidate/05_celestial_musician_girl'
 p=c/f'walk/SE/{n:02d}.png'
 if not p.is_file():continue
 im=Image.open(p).convert('RGBA');a=np.asarray(im);yy,xx=np.where(a[:,:,3]>8)
 assert im.size==(1024,1024)
 rec=json.loads((c/'processing/frame-sources.json').read_text())[f'walk/SE/{n:02d}.png']
 assert rec['common_scale']==.84 and rec['chroma_thresholds']==[50,75]
 images.append((n,im))
 if n in owned:
  rows.append({'frame':n,'slot':f'walk/SE/{n:02d}.png','archive':d.name,'output':str(p),'sha256':sha(p),'raw':str(d/'raw.png'),'rawSha256':sha(d/'raw.png'),'generationRecord':str(d/'raw.png.generation.json'),'prompt':str(d/'prompt.txt'),'receipt':str(d/'generation-receipt.json'),'sourceMapping':str(c/'processing/frame-sources.json'),'validation':str(c/f'review/validation-SE-{n:02d}.json'),'nativeSize':rec['source']['native_size'],'outputSize':[1024,1024],'alphaBbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'commonScale':.84,'chromaThresholds':[50,75],'pixelSha256':hashlib.sha256(im.tobytes()).hexdigest(),'actualModel':None,'actualQuality':None})
for name,color,ink in [('dark','#202b38','white'),('light','#f0eee4','black')]:
 for kind in ['normal','legs']:
  tw,th=(256,288) if kind=='normal' else (480,310)
  sheet=Image.new('RGB',(tw*3,th*math.ceil(len(images)/3)),color)
  for i,(n,im) in enumerate(images):
   content=im.resize((256,256),Image.Resampling.LANCZOS) if kind=='normal' else im.crop((290,700,770,980))
   x=i%3*tw;y=i//3*th
   sheet.paste(content,(x,y+30),content);ImageDraw.Draw(sheet).text((x+8,y+8),f'SE{n:02d}',fill=ink)
  sheet.save(O/f'contact-{kind}-{name}.png')
report={'character':'05_celestial_musician_girl','direction':'SE','ownedFrames':owned,'frameCount':len(rows),'complete':len(rows)==len(owned),'at':datetime.now(timezone.utc).isoformat(),'selection':{f'{r["frame"]:02d}':r['archive'] for r in rows},'rows':rows,'sourceDistinctCount':len({r['rawSha256'] for r in rows}),'pixelDistinctCount':len({r['pixelSha256'] for r in rows}),'reviewImages':[str(p) for p in O.glob('*.png')],'status':'static_pending_root_loop','approval':False,'canonicalModified':False}
(G/'SE-back-selection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ownedFramesReady':[r['frame'] for r in rows],'heights':[r['alphaBbox'][3]-r['alphaBbox'][1] for r in rows],'review':str(O)}))
