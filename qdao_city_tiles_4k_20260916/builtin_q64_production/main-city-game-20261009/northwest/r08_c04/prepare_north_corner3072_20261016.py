from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest');T=Z/'r08_c04';D=T/'repair-batches/north-corner3072-20261016';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
south=T/'candidate/native-23-source-incremental-20261016T070108286530Z-20aa64f66666c666/candidate.png'
north=Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png'
assert sha(south)=='511b06130673a88fcf7aa081aa1b08f8d0051ca64d449529c8c275648f9a605d' and sha(north)=='12a5ba0622b6ba365a7e89971a7d7682065f1194bdefe6c2d6141c28cece9a20'
parts=[(north,[2445,3469,3699,4096],[0,0]),(south,[2445,0,3699,627],[0,627])]
im=Image.new('RGB',(1254,1254))
for f,box,xy in parts:im.paste(Image.open(f).convert('RGB').crop(box),xy)
im.save(D/'edit-target.png');im.crop((470,470,810,810)).save(D/'before-detail.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','worldBox':[14733,28045,15987,29299],'originInTile':[2445,-627],'parts':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':xy} for f,box,xy in parts],'resampled':False,'north627PixelsReadOnly':True,'editTargetSha256':sha(D/'edit-target.png')},indent=2),encoding='utf-8')

