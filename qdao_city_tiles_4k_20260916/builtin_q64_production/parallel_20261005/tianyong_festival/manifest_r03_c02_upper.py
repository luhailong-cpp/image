from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r03_c02-upper-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=json.loads((d/'request.json').read_text());src=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/current/v006/r08_c10-fragment.png');ref={**info(src),'tileLocalLTRB':[909,0,4096,4096]}
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'localAccepted':True,'formalAccepted':False,'image':info(d/'joined.png'),'scope':'Upper397 newly generated rows plus lower100px return. Other source pixels excluded from placement. Adjacent left/right and whole tile pending.','observations':'Full1254x1254 and full1254x250 native return viewed. Six gray slab side outlines continue with no split, abrupt width change, waviness or color rectangle at y397. Profile-correspondence check of18 row/edge controls gives max1px offset; single-peak heuristic confused outer and inner bevel peaks and was not used as geometry evidence. All rows y497 onward are exact source context.','evidence':[info(d/'profile-correspondence.json'),info(d/'qa/upper-return-1254x250.png'),info(d/'assembly.json')]}
write(d/'visual-review.json',review)
im=Image.open(d/'joined.png').convert('RGB');patches=[]
for name,crop,box,prior in [('new',[0,0,1254,397],[909,1933,2163,2330],None),('return',[0,397,1254,497],[909,2330,2163,2430],ref)]:
 p=d/(name+'-placement.png');im.crop(crop).save(p);patches.append({'asset':info(p),'cropFromJoinedLTRB':crop,'destinationTile':'r08_c10','destinationTileLTRB':box,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 write(Path(str(p)+'.generation.json'),{**info(p),'derivedFrom':[info(d/'joined.png')],'cropLTRB':crop,'newModelCalls':0,'nativeScale':1})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'joined':info(d/'joined.png'),'windowTileLocalLTRB':req['tileLocalCropLTRB'],'windowGlobalLTRB':req['globalCropLTRB'],'patches':patches,'visualReview':info(d/'visual-review.json'),'localVisualAccepted':True,'formalAccepted':False,'nativeScale':1,'excludedUnchangedRows':[497,1254]}
write(d/'manifest.json',manifest);print(json.dumps(info(d/'manifest.json')))

