from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
j=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'));d=Path(j['directory']);src=Path(j['source']);out=d/'native'/f"{j['id']}.png";assert not out.exists();im=Image.open(src);im.load();assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copy2(src,out);prompt=d/'prompts'/f"{j['id']}.prompt.txt";guide=d/'guides'/f"{j['id']}.jpg"
rec={'id':j['id'],'role':'native_targeted_seam_repair','route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':list(im.size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':[{'path':str(guide),'sha256':sha(guide)}],'selectedTargetReferenceIndex':1,'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':1},'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolOutputHint':j['hint'],'createdAtUtc':datetime.now(timezone.utc).isoformat()}
out.with_suffix('.record.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print(j['id'],sha(out))