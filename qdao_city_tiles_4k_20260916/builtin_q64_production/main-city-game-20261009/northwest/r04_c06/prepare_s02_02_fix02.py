from pathlib import Path
import sys
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import production_v2 as p
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig')
split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert 'r04_c06' not in {x for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for x in b['tiles']}
base=T/'native/s02_02_fix01.png'
im=Image.open(base).convert('RGB')
d=p.read(T/'layout-only/s02_02_native01.actual-core-guide.png.derivation.json')
for a in d['nativeAnchors']:
 assert p.sha(a['file'])==a['sha256']
 im.paste(Image.open(a['file']).convert('RGB').crop(a['sourceBox']),a['targetBox'][:2])
out=T/'layout-only/s02_02_fix02.actual-core-guide.png'
p.save_png(out,im)
p.write_json(out.with_suffix('.png.derivation.json'),{'guideOnly':True,'role':'Technical same-world native repair reference; never production art','base':{'file':str(base),'sha256':p.sha(base)},'nativeAnchors':d['nativeAnchors'],'worldBox':d['worldBox'],'rulesRead':True,'agentsSha256':p.sha(p.REPO/'AGENTS.md'),'splitSha256':p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')},replace=False)
print(str(out))

