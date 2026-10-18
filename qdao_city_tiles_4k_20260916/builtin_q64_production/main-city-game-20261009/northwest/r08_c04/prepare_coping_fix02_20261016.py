from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');old=T/'repair-batches/coping-x3072-row4-20261016';D=T/'repair-batches/coping-full-span-fix02-20261016';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
basefile=T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png'
im=Image.open(basefile).convert('RGB');native=Image.open(old/'native.png').convert('RGB');mask=Image.open(old/'selection-mask-v2.png')
im.paste(native,(2445,2957),mask)
box=[2360,2842,3614,4096];im.crop(box).save(D/'edit-target.png')
Image.open(basefile).crop(box).save(D/'original-context.png')
(D/'input-provenance.json').write_text(json.dumps({'baseCandidate':str(basefile),'baseSha256':sha(basefile),'supplementSource':str(old/'native.png'),'sourceSha256':sha(old/'native.png'),'supplementMask':str(old/'selection-mask-v2.png'),'maskSha256':sha(old/'selection-mask-v2.png'),'inputIsUnacceptedTrial':True,'sourceOriginInTile':[2360,2842],'sourceWorldBox':[14648,31514,15902,32768],'resampled':False,'blended':False,'purpose':'Repair boundaries of concentrated coping trial; first native output not adopted.'},indent=2))
print(str(D))

