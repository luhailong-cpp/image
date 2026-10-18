from pathlib import Path
import sys,json
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
m=p.read(T/'qa/source-review/s03_01_fix01/manifest.json')
p.write_json(T/'qa/source-review/s03_01_fix01/review.json',dict(reviewer='/root/resume_r06_c08_20261017',actuallyViewed=True,status='rejected_not_selected',selected=False,finding='Full-source apparent rectangle removed, but exact neighboring west core still dark: vertical cyan tonal step remains at tile x0 around y2048..2120. West/NW crops remain needs_repair. No claim for four unviewed crops.',cropReviews=[dict(file=c['file'],sha256=c['sha256'],status='needs_repair' if c['name'] in ['west-seam','northwest-junction'] else 'passed',actuallyViewed=True) for c in m['crops'] if c['name'] in ['north-seam','west-seam','northwest-junction','east-seam']],formalAccepted=False),replace=False)
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig');split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert 'r06_c08' not in [t for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']]
orig=T/'native/s03_01_native01.png'; im=Image.open(orig).convert('RGB');der=p.read(T/'layout-only/s03_01_native01.actual-core-guide.png.derivation.json')
for a in der['nativeAnchors']:
 assert p.sha(a['file'])==a['sha256']
 im.paste(Image.open(a['file']).convert('RGB').crop(a['sourceBox']),a['targetBox'][:2])
f=T/'layout-only/s03_01_fix02.actual-composite.png';p.save_png(f,im)
p.write_json(f.with_suffix('.png.derivation.json'),dict(guideOnly=True,base=dict(file=str(orig),sha256=p.sha(orig)),anchors=der['nativeAnchors'],worldBox=der['worldBox'],resampled=False,productionArt=False),replace=False)
p.write_json(T/'receipts/s03_01_fix02.rules-read.json',dict(agentsSha256=p.sha(p.REPO/'AGENTS.md'),splitSha256=p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json'),rulesActuallyRead=True),replace=False)

