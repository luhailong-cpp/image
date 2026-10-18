from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/curb-x1024-y990-20261016'
D.mkdir(exist_ok=False)
base=T/'candidate/native-21-source-incremental-20261016T051437643050Z-4c25acc467787266/candidate.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(base)=='36f4b8391d331c8d8f2025e11db6937187317085afe9372c027c9686b60b77cb'
im=Image.open(base).convert('RGB').crop((397,397,1651,1651))
assert im.size==(1254,1254)
im.save(D/'edit-target.png')
im.crop((500,480,780,740)).save(D/'before-detail.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','source':str(base),'sourceSha256':sha(base),'candidateCropLTRB':[397,397,1651,1651],'originInTile':[397,397],'worldBox':[12685,29069,13939,30323],'resampled':False,'targetSha256':sha(D/'edit-target.png'),'knownProblemCandidateLTRB':[989,959,1069,1029]},indent=2),encoding='utf-8')
print(str(D/'edit-target.png'))

