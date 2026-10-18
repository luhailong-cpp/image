from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");stem="r06_c04_internal_westmid_tip_20261016_a01";src=Path(r"C:/Users/luyua/.codex/generated_images/01a135c5-877f-7d90-8c3b-84ed4df9904b/exec-5694d41b-7ba4-4225-8ee8-5c77542c5fdd.png")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dst=Z/'native'/f'{stem}.png';assert not dst.exists();shutil.copyfile(src,dst)
im=Image.open(dst);w,h=im.size
ip=Z/'guides'/f'{stem}.input.json';inp=json.loads(ip.read_text())
pp=Z/'prompts'/f'{stem}.prompt.txt'
refs=inp['inputs']
receipt=Z/'receipts'/f'{stem}.receipt.json'
data={'tool':'image_gen.imagegen','route':'builtin','generatedFile':src.as_posix(),'toolOutputHint':"Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a135c5-877f-7d90-8c3b-84ed4df9904b as C:\\Users\\luyua\\.codex\\generated_images\\01a135c5-877f-7d90-8c3b-84ed4df9904b\\exec-5694d41b-7ba4-4225-8ee8-5c77542c5fdd.png by default.\nIf you need to use a generated image at another path, copy it and leave the original in place unless the user explicitly asks you to delete it.\nThe generated image is already displayed to the user. There is no need to render it in the final response as a Markdown image or file link.",'archivedAtUtc':datetime.now(timezone.utc).isoformat(),'submitted':{'promptText':pp.read_text(),'promptFile':pp.as_posix(),'referenced_image_paths':[x['path'] for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'recoveredSourceSha256':sha(src)}
receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2))
g={'file':dst.as_posix(),'sha256':sha(dst),'generatedAt':data['archivedAtUtc'],'nativeWidth':w,'nativeHeight':h,'format':'PNG','sourceOutputPath':src.as_posix(),'sourceOutputSha256':sha(src),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':None,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool did not return actual model or quality. Existing included route; no paid API.','prompt':pp.as_posix(),'promptSha256':sha(pp),'references':[{k:v for k,v in x.items() if k!='derivedFrom'} for x in refs],'evidence':{'receipt':receipt.as_posix()},'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'candidate_pending_native_visual_and_seam_QA'}
gp=dst.with_suffix('.png.generation.json');gp.write_text(json.dumps(g,ensure_ascii=False,indent=2))
print(json.dumps({'native':dst.as_posix(),'sha256':sha(dst),'size':[w,h],'generation':gp.as_posix(),'receipt':receipt.as_posix()}))

