from pathlib import Path
import sys
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T));import workflow_20261016 as w
p=w.p
identifier=sys.argv[1];baseid=sys.argv[2];oldid=sys.argv[3]
e=w.check_rules()
base=T/'native'/(baseid+'.png');im=Image.open(base).convert('RGB')
d=p.read(T/'layout-only'/(oldid+'.actual-core-guide.png.derivation.json'))
for a in d['nativeAnchors']:
 im.paste(Image.open(a['file']).convert('RGB').crop(a['sourceBox']),a['targetBox'][:2])
f=T/'layout-only'/(identifier+'.actual-core-guide.png');p.save_png(f,im)
d.update(role='edit-only exact native candidate plus same-world actual core anchors',guideOnly=True,baseCandidate={'file':str(base),'sha256':p.sha(base)},rules=e)
p.write_json(f.with_suffix('.png.derivation.json'),d,replace=False)
print(f)

