from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,sys,hashlib,shutil
P=Path(__file__).resolve().parent
ident=sys.argv[1];src=Path(sys.argv[2]);dst=P/'native'/f'{ident}.png'
assert not dst.exists()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
with Image.open(src) as im:
 im.load();assert im.size==(1254,1254);alpha=im.getextrema()[3] if im.mode=='RGBA' else (255,255);assert alpha==(255,255)
shutil.copyfile(src,dst)
prompt=P/'prompts'/f'{ident}.prompt.txt';ref=P/'guides'/f'{ident}.jpg';guide=P/'guides'/f'{ident}.png';e=next(e for e in json.loads((P/'plan.json').read_text())['entries'] if e['id']==ident)
r={'id':ident,'route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(dst),'outputSha256':sha(dst),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':[{'path':str(ref),'sha256':sha(ref),'pixels':[1254,1254]}],'selectedTargetImageOneBased':1,'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':1},'sourceBoxLTRB':e['box'],'plannedRoiLTRB':e['roi'],'finalArtUpscaled':False,'resizedAfterGeneration':False,'alphaExtrema':alpha,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'visualQa':{'status':'pending_placement_and_roi_reconnection'}}
(P/'native'/f'{ident}.record.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps({'id':ident,'path':str(dst),'sha256':sha(dst)}))
