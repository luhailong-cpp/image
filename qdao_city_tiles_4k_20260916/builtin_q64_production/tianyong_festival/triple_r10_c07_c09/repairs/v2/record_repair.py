from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib,shutil
p=Path(__file__).resolve().parent
ident,source,refs,selected=sys.argv[1],Path(sys.argv[2]),json.loads(sys.argv[3]),int(sys.argv[4])
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
dest=p/'native'/f'{ident}.png'
assert not dest.exists(),dest
assert Image.open(source).size==(1254,1254)
shutil.copyfile(source,dest)
r={'schemaVersion':2,'id':ident,'route':'builtin_image_gen','backendModelVerified':False,'requestedModel':'GPT Image 2.0 (host builtin)','actualNativePixels':[1254,1254],'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'outputFile':str(dest),'outputSha256':sha(dest),'promptFile':str(p/'prompts'/f'{ident}.prompt.txt'),'promptSha256':sha(p/'prompts'/f'{ident}.prompt.txt'),'submittedImages':[{'path':str(p/'inputs'/f'{x}.jpg'),'sha256':sha(p/'inputs'/f'{x}.jpg'),'pixels':[1254,1254]} for x in refs],'selectedTargetImageOneBased':selected,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':len(refs),'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_reviewed_assembly_pending'}}
if ident=='boundary_lower':r['visualQa']={'status':'rejected_geometry_changed','reason':'Bottom short paving row removed and staircase shifted upward; do not compose.'}
(p/'native'/f'{ident}.record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':ident,'sha256':sha(dest),'status':r['visualQa']['status']}))
