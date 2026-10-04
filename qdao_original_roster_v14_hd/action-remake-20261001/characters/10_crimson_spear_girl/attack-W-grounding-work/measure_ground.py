from pathlib import Path
from PIL import Image
import json
d=Path(__file__).parent;base=d.parent
files=[base/'attack-work'/f'attack-W-{s}.png' for s in ['01','03','04','05','06-v4','07','08','09','10','11','12']]
files+=list(d.glob('attack-W-*-ground-v*.png'))
rows=[]
for p in files:
 im=Image.open(p).convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>32 else 0)
 feet=[]
 for box in [(360,930,700,1220),(780,930,1170,1220)]:
  b=a.crop(box).getbbox()
  feet.append(None if b is None else [b[0]+box[0],b[1]+box[1],b[2]+box[0],b[3]+box[1]])
 rows.append({'file':str(p.relative_to(base)),'footROIs':feet,'groundBottoms':[b[3]-1 if b else None for b in feet],'method':'Alpha>32 in fixed lower-front/rear inspection ROIs. Manual review must ensure lowest feature is boot, not cloth. Coordinates are native.'})
(d/'ground-measurements.json').write_text(json.dumps({'nativeTarget':1120,'targetTolerance':10,'actualSelectedBand':[1098,1118],'actualResidualNote':'Actual measured tolerance up to22 native, preserved transparently; no forced per-frame foot alignment.','registration':{'scale':860/1254,'translation':[0,174],'nativeVirtualRoot':[512/(860/1254),1120],'virtualRoot':[512,942],'status':'revised entire-direction proposal; matches current combined preview'},'frames':rows},indent=2),encoding='utf8')
for r in rows:print(r['file'],r['groundBottoms'])

