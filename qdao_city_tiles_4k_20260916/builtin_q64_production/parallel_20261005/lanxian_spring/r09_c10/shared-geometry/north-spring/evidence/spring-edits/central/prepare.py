from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT.parent/'lanxian_day/r08_c10/selected/core4096.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)=='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'
im=Image.open(SOURCE).convert('RGB')
boxes={'front':[1200,1400,2454,2654],'back':[1900,1290,3154,2544]}
records=[]
for name,b in boxes.items():
 p=OUT/f'{name}-target-1254.png';im.crop(b).save(p)
 records.append({'name':name,'file':str(p),'sha256':sha(p),'pixels':[1254,1254],'cropInCoreLTRB':b,'resampling':None,'warp':None})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':{'file':str(SOURCE),'sha256':sha(SOURCE)},'crops':records,'role':'original native source crops for strictly surface-only Spring Festival edit'}
(OUT/'source-crops.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
