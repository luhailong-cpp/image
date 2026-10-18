from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/coping-x3072-row4-20261016';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png'
assert sha(base)=='00b6fd40e61bceffdf6fd10b9c140c532831c46f63be92a54c5e0f729eb65c68'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(base).convert('RGB').crop((2445,2957,3699,4096)),(0,0))
sources=[(T/'native/s04_03_fix01.png',[512,1139,1139,1254],[0,1139]),(T/'native/s04_04_fix02.png',[115,1139,742,1254],[627,1139])]
for f,box,xy in sources:im.paste(Image.open(f).convert('RGB').crop(box),xy)
im.save(D/'edit-target.png');im.crop((450,200,900,1100)).save(D/'before-detail.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','worldBox':[14733,31629,15987,32883],'originInTile':[2445,2957],'candidate':str(base),'candidateSha256':sha(base),'sourceBox':[2445,2957,3699,4096],'haloBottomContextOnly':{'targetRows':[1139,1254],'parts':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':xy} for f,box,xy in sources]},'resampled':False,'editTargetSha256':sha(D/'edit-target.png')},indent=2),encoding='utf-8')

