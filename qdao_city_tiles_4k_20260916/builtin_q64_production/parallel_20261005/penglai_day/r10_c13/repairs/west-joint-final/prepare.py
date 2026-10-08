from pathlib import Path
from PIL import Image
import json
from ai_helper import derived,sha
O=Path(__file__).parent;B=O.parents[2]
L=B/'r10_c12/repairs/north/joint-v4/r10_c12-north-joint-candidate.png'
R=B/'r10_c13/repairs/r10_c13-combined-v8.png'
NL=B/'r10_c12/repairs/north/joint-v4/r09_c12-north-joint-candidate.png'
NR=B/'r10_c13/repairs/r09_c13-north-revised-v5.png'
l,r,nl,nr=[Image.open(p).convert('RGB') for p in [L,R,NL,NR]]
a=Image.new('RGB',(1254,4096));a.paste(l.crop((3469,0,4096,4096)),(0,0));a.paste(r.crop((0,0,627,4096)),(627,0))
p=O/'joint-source.png';a.save(p);derived(p,[L,R],{'operation':'native pixel juxtaposition','jointOriginInLeftTile':[3469,0],'seamX':627,'scale':1})
for y in [0,1024,2048,2842]:
 p1=O/f'input-{y}.png';a.crop((0,y,1254,y+1254)).save(p1);derived(p1,[p],{'nativeCrop':[0,y,1254,y+1254],'scale':1})
q=Image.new('RGB',(1254,1254));q.paste(nl.crop((3469,3469,4096,4096)),(0,0));q.paste(nr.crop((0,3469,627,4096)),(627,0));q.paste(a.crop((0,0,1254,627)),(0,627));pq=O/'north-four-corner.png';q.save(pq);derived(pq,[L,R,NL,NR],{'operation':'native four-tile corner','scale':1})
preview=Image.new('RGB',(2048,1024));preview.paste(l.resize((1024,1024)),(0,0));preview.paste(r.resize((1024,1024)),(1024,0));pp=O/'preview-source.png';preview.save(pp);derived(pp,[L,R],{'operation':'QA preview only','scale':.25})
(O/'sources.json').write_text(json.dumps([{'file':str(p),'sha256':sha(p)} for p in [L,R,NL,NR]],indent=2))
print(O);print([sha(p) for p in [L,R]])
