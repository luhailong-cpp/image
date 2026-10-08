from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');O=T/'c02-north-repair';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ctx=json.loads((T/'regional/context.json').read_text());n=Path(ctx['northCore']['file']);base=T/'native/r01_c02.png';east=T/'native/r01_c03.png'
assert sha(n)==ctx['northCore']['sha256'];assert sha(base)=='aee6d1245cff2f953dc965dff267ac747083dee1ccffcc7d0d5c04f7bd68d2ea'
north=Image.open(n).convert('RGB').crop((909,3469,2163,4096));south=Image.open(base).convert('RGB').crop((0,115,1254,742))
im=Image.new('RGB',(1254,1254));im.paste(north,(0,0));im.paste(south,(0,627));out=O/'true-north-south1254.png';assert not out.exists();im.save(out)
meta={'createdAt':datetime.now(timezone.utc).isoformat(),'output':{'file':str(out),'sha256':sha(out),'pixels':[1254,1254]},'purpose':'Original-resolution actual north core627 rows above current south627 rows; boundary y627. No scaling/blur/generated context.','sourceMappings':[{'file':str(n),'sha256':sha(n),'sourceBox':[909,3469,2163,4096],'destinationBox':[0,0,1254,627]},{'file':str(base),'sha256':sha(base),'sourceBox':[0,115,1254,742],'destinationBox':[0,627,1254,1254]}],'eastLock':{'file':str(east),'sha256':sha(east),'sourceBox':[115,115,230,1254],'destinationCellBox':[1139,115,1254,1254]},'finalArt':False,'resampling':'none'}
(O/'prepare.manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta))

