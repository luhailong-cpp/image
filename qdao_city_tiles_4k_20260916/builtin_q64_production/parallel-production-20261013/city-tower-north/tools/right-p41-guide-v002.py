from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');T=B/'versions/right-r04c14-p41-guide-v002/r04_c14/guides';T.mkdir(parents=True,exist_ok=False)
a=B/'versions/right-r04c14-p41-native-v001/r04_c14/native/p41.png';n=B/'versions/right-r04c14-p31-native-v001/r04_c14/native/p31.png';im=Image.open(a).convert('RGB');src=Image.open(n).convert('RGB');im.paste(src.crop((115,1024,1139,1139)),(115,0));out=T/'p41-REPAIR-INPUT-only.png';im.save(out)
(T/'p41-REPAIR-INPUT-only.json').write_text(json.dumps({'role':'exact-pixel-guide-only-not-native-art','target':str(a),'targetSha256':hashlib.sha256(a.read_bytes()).hexdigest(),'topCoreSource':str(n),'topSourceSha256':hashlib.sha256(n.read_bytes()).hexdigest(),'sourceCrop':[115,1024,1139,1139],'paste':[115,0],'resized':False,'inputSha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2),encoding='utf-8');print(out)

