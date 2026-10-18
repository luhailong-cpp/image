from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).parent;O=T/'qa/local-repair-20261016';base=T/'qa/core-baseline/1368c15ca794536c2a6b/r08_c09-core-baseline.candidate.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(base).convert('RGB');before=im.copy();records=[]
for name,origin,roi in [('upper-right-paving',(2842,397),(90,390,1254,1220)),('blue-band-step',(2320,1400),(150,300,1130,920))]:
 f=T/'native/repairs'/(name+'-local-v1-20261016.png');r=Image.open(f).convert('RGB');x,y=origin;a,b,c,d=roi;im.paste(r.crop(roi),(x+a,y+b));records.append({'id':name,'native':str(f),'nativeSha256':sha(f),'nativeCrop':roi,'destination':[x+a,y+b,x+c,y+d]})
 copy=im.copy()
 for r in records:
  box=r['destination'];copy.paste(before.crop(box),box[:2])
 assert ImageChops.difference(copy,before).getbbox() is None
dest=O/'r08_c09-local-v1-20261016.candidate.png';assert not dest.exists();im.save(dest)
for name,origin in [('upper-right-paving',(2842,397)),('blue-band-step',(2320,1400))]:
 x,y=origin;im.crop((x,y,x+1254,y+1254)).save(O/(name+'-composed-v1.png'))
record={'candidate':str(dest),'candidateSha256':sha(dest),'base':str(base),'baseSha256':sha(base),'repairs':records,'operation':'integer native crop and paste only','outsideRepairRectanglesByteIdenticalToBase':True,'internalPassed':False,'adopted':False}
(O/'composition-v1.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record))
