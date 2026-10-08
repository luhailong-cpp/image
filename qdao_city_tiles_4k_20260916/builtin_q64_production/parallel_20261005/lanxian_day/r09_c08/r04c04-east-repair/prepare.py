from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,shutil
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
T=ROOT/'r09_c08'; O=T/'r04c04-east-repair'; O.mkdir(exist_ok=True)
assert O.resolve().is_relative_to(ROOT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for rel in ['native/r04_c04.png','native/r04_c04.png.generation.json','native/r04_c04.prompt.txt','jobs/r04_c04.json','jobs/r04_c04.receipt.json','prompts/r04_c04.prompt.txt','guides/r04_c04.layout-only.png']:
 src=T/rel; dst=O/'original'/rel; dst.parent.mkdir(parents=True,exist_ok=True); assert not dst.exists(); shutil.copy2(src,dst); assert sha(src)==sha(dst)
 items.append({'sourcePath':str(src),'retainedCopyPath':str(dst),'sha256':sha(src)})
orig=Image.open(T/'native/r04_c04.png').convert('RGB')
eastpath=ROOT/'r09_c09/selected/extended4326.png'; east=Image.open(eastpath).convert('RGB')
strip=east.crop((0,3072,230,4326)); strip.save(O/'east-actual230x1254.png')
guide=orig.copy(); guide.paste(strip.crop((115,115,230,1254)),(1139,115)); guide.save(O/'precise-east-guide1254.png')
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'originalArchive':items,'eastContext':{'sourcePath':str(eastpath),'sha256':sha(eastpath),'sourceCrop':[0,3072,230,4326],'path':str(O/'east-actual230x1254.png'),'outputSha256':sha(O/'east-actual230x1254.png')},'guide':{'path':str(O/'precise-east-guide1254.png'),'sha256':sha(O/'precise-east-guide1254.png'),'base':items[0],'operation':'Paste exact east native strip local [115,115,230,1254] at target [1139,115,1254,1254]. Original top115 unchanged. No blending, no resampling. This is a guide, not accepted art. Visible joint mismatch must be repainted into a smooth approach on the left side.','guideOnly':True},'officialModelVerification':str(ROOT/'preflight/model-verification-20261008.json')}
(O/'prepare.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest['guide'],indent=2))
