from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08')
O=T/'top-right-preqa'/'north-planning';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ctx=json.loads((T/'regional/context.json').read_text());n=Path(ctx['northCoreBand']['file']);r=T/'regional/regional.png';nc=Path(ctx['northCore']['file'])
assert sha(n)==ctx['northCoreBand']['sha256']
assert sha(nc)==ctx['northCore']['sha256']
north=Image.open(n).convert('RGB');regional=Image.open(r).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC);core=Image.open(nc).convert('RGB')
outputs=[]
for col in (1,2):
 x=(col-1)*1024
 guide=regional.crop((x,0,x+1254,512));guide.paste(north.crop((x,0,x+1254,115)),(0,0))
 name=f'r01_c{col:02d}-north115-regional397-guide-only.png';target=O/name
 assert not target.exists();guide.save(target)
 true=core.crop((x,3840,x+1024,4096));tf=O/f'r01_c{col:02d}-true-north-bottom256.png';assert not tf.exists();true.save(tf)
 outputs.append({'cell':f'r01_c{col:02d}','guide':{'file':str(target),'sha256':sha(target),'pixels':[1254,512],'northSource':str(n),'northSourceSha256':sha(n),'northSourceBox':[x,0,x+1254,115],'northTargetBox':[0,0,1254,115],'regionalSource':str(r),'regionalSourceSha256':sha(r),'regionalOperation':'BICUBIC guide-only resize to4326; crop '+str([x,0,x+1254,512]),'guideOnly':True,'finalArt':False,'eastContextPresent':False},'trueNorth':{'file':str(tf),'sha256':sha(tf),'pixels':[1024,256],'source':str(nc),'sourceSha256':sha(nc),'sourceBox':[x,3840,x+1024,4096],'resampling':'none'}})
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'purpose':'Read-only planning for future left two cells. No r01_c03 used; these images must never be final artwork or actual native generation guides.','outputs':outputs,'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest))

