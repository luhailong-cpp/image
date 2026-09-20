import json,sys,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/r08_c08')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'));src=Path(j['source']);out=P/'native'/f"{j['id']}.png";assert not out.exists(),out
im=Image.open(src);im.load();assert im.size==(1254,1254),im.size;assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
shutil.copy2(src,out)
guide=P/'guides'/f"{j['id']}.layout-only.png";prompt=Path(j['promptFile']);refs=[{'path':p,'sha256':sha(p)} for p in j['refs']]
rec={'schemaVersion':1,'id':j['id'],'role':'native_4K_tile_patch','route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':list(im.size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':refs,'selectedTargetReferenceIndex':1,'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':j['refs'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'requestedNativePixels':[1254,1254]},'modelTarget':'ChatGPT Images 2.5; actual host-managed model unverified','createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolOutputReceipt':j.get('receipt',{})}
out.with_suffix('.record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(str(out))