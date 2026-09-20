import json,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
jobs=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
for j in jobs:
 t=ROOT/j['appearance']/'r09_c12'; out=t/'native'/f"{j['id']}.png"; out.parent.mkdir(exist_ok=True)
 assert not out.exists(),out
 src=Path(j['source']); im=Image.open(src); assert im.size==(1254,1254)
 assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 shutil.copy2(src,out)
 prompt=t/'prompts'/f"{j['id']}.prompt.txt"; guide=t/'guides'/f"{j['id']}.layout-only.png"
 refs=[{'path':(t/'guides'/f'{r}.input-preview.jpg').as_posix(),'sha256':sha(t/'guides'/f'{r}.input-preview.jpg')} for r in j['refs']]
 rec={'schemaVersion':1,'id':j['id'],'role':'native_4K_tile_patch','route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':refs,'selectedTargetReferenceIndex':j['selected'],'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':len(refs),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'requestedNativePixels':[1254,1254]},'toolOutputHint':j['hint'],'createdAtUtc':datetime.now(timezone.utc).isoformat()}
 out.with_suffix('.record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 print(j['appearance'],j['id'],sha(out))
