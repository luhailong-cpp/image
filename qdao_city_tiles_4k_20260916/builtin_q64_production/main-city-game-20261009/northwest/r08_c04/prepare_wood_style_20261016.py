from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/wood-post-style-20261016';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(base).convert('RGB').crop((2140,2957,3394,4096)),(0,0))
parts=[(T/'native/s04_03_fix01.png',[207,1139,1139,1254],[0,1139]),(T/'native/s04_04_fix02.png',[115,1139,437,1254],[932,1139])]
for f,box,xy in parts:im.paste(Image.open(f).convert('RGB').crop(box),xy)
im.save(D/'edit-target.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','worldBox':[14428,31629,15682,32883],'originInTile':[2140,2957],'candidate':str(base),'candidateSha256':sha(base),'sourceBox':[2140,2957,3394,4096],'haloBottomContextOnly':{'targetRows':[1139,1254],'parts':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':xy} for f,box,xy in parts]},'resampled':False,'editTargetSha256':sha(D/'edit-target.png'),'target':'wood post only; stone coping remains unfixed'},indent=2))
print(str(D))

