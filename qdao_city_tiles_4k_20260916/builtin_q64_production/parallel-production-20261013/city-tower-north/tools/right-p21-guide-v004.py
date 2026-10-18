from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');T=B/'versions/right-r04c14-p21-guide-v004/r04_c14/guides';T.mkdir(parents=True,exist_ok=False)
a=B/'versions/right-r04c14-p21-native-v002/r04_c14/native/p21.png';s=B/'versions/right-r04c14-p31-native-v001/r04_c14/native/p31.png';im=Image.open(a).convert('RGB');im.paste(Image.open(s).convert('RGB').crop((115,115,1139,230)),(115,1139));out=T/'p21-REPAIR-INPUT-only.png';im.save(out)
(T/'p21-REPAIR-INPUT-only.json').write_text(json.dumps({'role':'guide-only-not-art','target':str(a),'targetSha256':hashlib.sha256(a.read_bytes()).hexdigest(),'southSource':str(s),'southSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'sourceCrop':[115,115,1139,230],'paste':[115,1139],'resized':False,'inputSha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2),encoding='utf-8')

