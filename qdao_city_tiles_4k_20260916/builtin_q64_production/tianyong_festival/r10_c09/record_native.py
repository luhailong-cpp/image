from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
ident,src=sys.argv[1],Path(sys.argv[2])
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
out=p/'native'/f'{ident}.png'
if out.exists():raise RuntimeError('Refusing to overwrite existing native')
size=Image.open(src).size
if size!=(1254,1254):raise RuntimeError(f'Unexpected native size {size}')
shutil.copyfile(src,out)
prompt=p/'prompts'/f'{ident}.prompt.txt';guide=p/'guides'/f'{ident}.layout-only.png'
row=ident.split('_')[0]
refs=[p/'guides'/f'{row}_c{c:02}.input-preview.jpg' for c in range(1,5)]
selected=int(ident.split('_c')[1])
r={'schemaVersion':2,'id':ident,'route':'builtin_image_gen','backendModelVerified':False,'requestedModel':'GPT Image 2.0 (host builtin)','actualNativePixels':list(size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':f'native/{ident}.png','outputSha256':sha(out),'promptFile':f'prompts/{ident}.prompt.txt','promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':[{'path':str(x),'sha256':sha(x),'pixels':[1254,1254]} for x in refs],'selectedTargetImageOneBased':selected,'finalArtUpscaled':False,'resizedAfterGeneration':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':4,'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_review_done_assembly_pending','note':'Native generation visually observed; geometry and 4K assembly joins require separate check.'}}
(p/'native'/f'{ident}.record.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({'id':ident,'pixels':list(size),'sha256':sha(out)}))
