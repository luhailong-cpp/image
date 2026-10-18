from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repairs/right-courses-20261016';D.mkdir(exist_ok=True,parents=True)
base=T/'candidate/r16_c16-4k-candidate-101a9801efaf54800416.png';im=Image.open(base).convert('RGB')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=json.loads((T/'records/p03_04_v20261016T041829_894fc41e.request.json').read_text())['referenced_image_paths'][:3]
jobs=[]
for key,y,desc in [('upper',1320,'UPPER projecting side-wall stone band. The front projecting belt at image-left around y1000..1150 must wrap around the vertical corner at local x440 and continue UP-RIGHT as the SAME uninterrupted broad stone belt. Currently the side band wrongly meets that corner around y840 and ends as a detached high ledge. Remove the detached side band at that old elevation and redraw it lower to meet the front/return belt exactly, running diagonally up-right across the side wall at a uniform slope with equal thickness. Maintain the front belt elevation, the vertical corner, and the existing lower side-wall course near bottom-right.'),('lower',2100,'LOWER projecting side-wall stone band. The front/return lowest projecting belt at image-left around y900..1050 must wrap around vertical corner at local x440 and continue UP-RIGHT as the SAME uninterrupted broad stone belt. Currently the side band meets that corner around y680 and ends as a detached high ledge. Remove this incorrect lower side band and draw it lower to meet the front/return lowest belt exactly, running diagonally up-right with uniform slope and equal thickness. Preserve the upper band, the front belts, vertical corner, wall-foot foliage and all other stone block lines.')]:
 d=D/key;d.mkdir(exist_ok=True);p=d/'target-1254.png';assert not p.exists();im.crop((2842,y,4096,y+1254)).save(p)
 prompt='Use case: precise-object-edit. Edit the LAST image only, exactly 1254 by 1254 opaque pixels. First three images are style references only; this is a native detail crop of a confirmed Daoist Q-style daylight city map. Repair only the incorrect architectural connection of the '+desc+' No new pillar, stairs, trim, doors, symbols, plants, rock or label. Keep crop framing and scale exactly unchanged. Match existing warm ivory stone, restrained grey grain and hand-painted soft shading. No warp, blur, copy patterns, new decoration, false boundary seams, arrows or guides. This is a localized geometry correction, not a redesign.'
 req={'prompt':prompt,'referenced_image_paths':refs+[str(p)],'transparent_background':False}
 for name,data in [('request.json',req),('preparation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':key,'base':str(base),'baseSha256':sha(base),'target':str(p),'targetSha256':sha(p),'coreBox':[2842,y,4096,y+1254],'method':'integer crop only, actual core image, no upscale','formalAccepted':False})]:
  with (d/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
 jobs.append({'key':key,'directory':str(d),'target':str(p),'request':req})
print(json.dumps(jobs))
