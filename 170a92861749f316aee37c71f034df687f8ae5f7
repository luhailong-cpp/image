import json,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
t=ROOT/job['appearance']/'r08_c08';out=t/'native'/f"{job['id']}.png";out.parent.mkdir(exist_ok=True)
assert not out.exists(),out
src=Path(job['source']);im=Image.open(src);im.load();assert im.size==(1254,1254),im.size
assert im.mode!='RGBA' or im.getextrema()[3]==(255,255),im.getextrema()
shutil.copy2(src,out)
prompt=t/'prompts'/job.get('prompt',f"{job['id']}.prompt.txt");guide=t/'guides'/f"{job['id']}.layout-only.png"
refs=[{'path':str(t/'guides'/f'{r}.input-preview.jpg'),'sha256':sha(t/'guides'/f'{r}.input-preview.jpg')} for r in job['refs']]
rec={'schemaVersion':1,'id':job['id'],'role':'native_4K_tile_patch','route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':list(im.size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':refs,'selectedTargetReferenceIndex':job['selected'],'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':len(refs),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'requestedNativePixels':[1254,1254]},'referenceInputNote':'referenced_image_paths failed with Windows deny-read ACL helper; displayed exact JPEG bytes and used conversation-image references','toolOutputHint':job.get('hint',''),'createdAtUtc':datetime.now(timezone.utc).isoformat()}
out.with_suffix('.record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(job['appearance'],job['id'],sha(out))