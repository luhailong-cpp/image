from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/paving-x1024-y3090-20261016';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=T/'candidate/native-21-source-incremental-20261016T051437643050Z-4c25acc467787266/candidate.png'
assert sha(base)=='36f4b8391d331c8d8f2025e11db6937187317085afe9372c027c9686b60b77cb'
box=[397,2445,1651,3699]; im=Image.open(base).convert('RGB').crop(box);im.save(D/'edit-target.png');im.crop((510,520,790,790)).save(D/'before-detail.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','worldBox':[12685,31117,13939,32371],'originInTile':[397,2445],'candidate':str(base),'candidateSha256':sha(base),'sourceBox':box,'resampled':False,'editTargetSha256':sha(D/'edit-target.png')},indent=2),encoding='utf-8')

