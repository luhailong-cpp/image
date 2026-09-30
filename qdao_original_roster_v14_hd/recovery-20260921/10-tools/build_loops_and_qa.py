"""Export real selected frames as 30ms APNG; no interpolated poses."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]
O=R/'10-delivery-preview/current'
Q=R/'10-work/final-qa'
Q.mkdir(exist_ok=True)
M=json.loads((O/'manifest.json').read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
report={}
for d in M['directions']:
 slots=[d+f'{i:02}' for i in range(1,17)]
 if not all(s in M['frames'] for s in slots): continue
 frames=[Image.open(O/M['frames'][s]['file']).convert('RGBA') for s in slots]
 dest=O/'loops'/f'{d}.png';dest.parent.mkdir(exist_ok=True)
 frames[0].save(dest,save_all=True,append_images=frames[1:],duration=[30]*16,loop=0,disposal=0,blend=0)
 with Image.open(dest) as loop:
  assert loop.n_frames==16
  durations=[]
  for i in range(16):
   loop.seek(i); durations.append(loop.info['duration'])
   assert loop.convert('RGBA').tobytes()==frames[i].tobytes()
  assert durations==[30]*16 and sum(durations)==480
 report[d]={'file':str(dest.relative_to(O)),'sha256':sha(dest),'frames':16,'durationsMs':durations,'cycleMs':480,'decodedFramesExactlyMatchSource':True,'sourceFrames':[M['frames'][s] for s in slots]}
 for theme,color in [('light','#f6f1e7'),('dark','#242a31')]:
  for name,indices in [('seam',[14,15,0,1]),('half',[6,7,8,9])]:
   im=Image.new('RGB',(2048,552),color);dr=ImageDraw.Draw(im)
   for col,i in enumerate(indices):
    pic=frames[i].resize((512,512),Image.Resampling.LANCZOS);im.paste(pic,(col*512,0),pic);dr.text((col*512+8,522),slots[i],fill='white' if theme=='dark' else 'black')
   im.save(Q/f'{d}-{theme}-{name}.jpg',quality=96)
  for offset in [0,8]:
   im=Image.new('RGB',(2048,784),color);dr=ImageDraw.Draw(im)
   for col,i in enumerate(range(offset,offset+8)):
    pic=frames[i].crop((256,650,768,1010));x=(col%4)*512;y=(col//4)*392;im.paste(pic,(x,y),pic);dr.text((x+8,y+366),slots[i],fill='white' if theme=='dark' else 'black')
   im.save(Q/f'{d}-{theme}-feet-{offset+1:02}.jpg',quality=96)
 (Q/f'{d}-bindings.json').write_text(json.dumps(report[d],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'loops/manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'loops':len(report),'allDuration30':True,'allCycle480':True,'allDecodedPixelsBound':True}))
