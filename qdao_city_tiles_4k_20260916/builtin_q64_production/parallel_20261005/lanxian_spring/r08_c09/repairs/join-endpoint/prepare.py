from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
OUT=Path(__file__).resolve().parent
ASM=OUT.parents[1]/'assembly_v2'
SOURCE=ASM/'candidate_4096.png'
HALO=ASM/'candidate_with_halo.png'
RECT=(509,413,1763,1667)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)=='a24f141b631eeefab13439339af7df0e1834a857d3c89c382b15380a603bb8a4'
assert sha(HALO)=='0a60eaf7f570b42ef5f1a2a6b6d3320dbf5259e9950a889a03d5efde32c23a05'
with Image.open(SOURCE) as im:
    im.crop(RECT).save(OUT/'edit-target-1254.png')
    im.crop((996,916,1316,1176)).save(OUT/'before-local-320x260.png')
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'coreSource':str(SOURCE),'coreSourceSha256':sha(SOURCE),
 'haloSource':str(HALO),'haloSourceSha256':sha(HALO),'cropLTRB':RECT,'sourceDefectLTRB':[1126,1020,1146,1060],
 'cropDefectLTRB':[617,607,637,647],'file':str(OUT/'edit-target-1254.png'),'sha256':sha(OUT/'edit-target-1254.png'),
 'pixels':[1254,1254],'operation':'exact crop; no resampling or warp','resampling':None,'warp':None}
(OUT/'edit-target-1254.derived.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
