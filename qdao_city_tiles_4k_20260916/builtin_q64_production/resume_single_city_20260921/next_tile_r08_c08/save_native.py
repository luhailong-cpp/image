from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,re,sys,shutil
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ident=sys.argv[1];stem=sys.argv[2] if len(sys.argv)>2 else ident
plan=json.loads((P/'plan.json').read_text(encoding='utf-8'));patch=next(x for x in plan['patches'] if x['id']==ident)
receiptPath=P/'native'/f'{stem}.tool-response.json';receipt=json.loads(receiptPath.read_text(encoding='utf-8'))
match=re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S);assert match
src=Path(match.group(1));dst=P/'native'/f'{stem}.png';assert not dst.exists();shutil.copyfile(src,dst);assert sha(src)==sha(dst)
with Image.open(dst) as im:
 im.load();assert im.size==(1254,1254) and im.mode in ['RGB','RGBA'];assert im.mode=='RGB' or im.getextrema()[3]==(255,255)
 nativePixels=list(im.size);mode=im.mode
prompt=P/'prompts'/f'{stem}.actual-prompt.txt';prompt.write_text(receipt['request']['prompt'],encoding='utf-8')
references=[{'file':str(Path(p).resolve()),'path':str(Path(p).resolve()),'sha256':sha(p),'role':('layout-only exact edit target' if i==0 else 'existing native city material continuity' if i==1 else 'confirmed primary designs drawing/material style, no UI content')} for i,p in enumerate(receipt['request']['referenced_image_paths'])]
r={'schemaVersion':3,'file':str(dst),'sha256':sha(dst),'generatedAt':None,'observedCompletionAt':receipt['observedCompletionAt'],'observedCompletionAtMeaning':'Host-observed tool completion, server generation timestamp undisclosed','width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':plan['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed image tool has no model/quality selectors or disclosed result model/quality metadata','prompt':{'file':str(prompt),'sha256':sha(prompt)},'references':references,'evidence':{'file':str(receiptPath),'sha256':sha(receiptPath)},'nativeSha256':sha(dst),'nativeFile':str(dst),'nativePixels':nativePixels,'imageMode':mode,'toolOutputPath':str(src),'toolOutputSha256':sha(src),'toolOutputBytes':src.stat().st_size,'promptFile':str(prompt),'promptSha256':sha(prompt),'submittedImages':references,'resampled':False,'finalArtUpscaled':False,'visualStatus':'pending_assembly_and_QA','productionAccepted':False,'accepted':False,'runtimePublished':False,'originalNativeBytesPreserved':True}
recordPath=P/'native'/f'{stem}.generation.json';recordPath.write_text(json.dumps(r,indent=2),encoding='utf-8')
patch.update({'status':'native_saved_pending_QA','outputFile':f'native/{stem}.png','generationRecord':{'file':str(recordPath),'sha256':sha(recordPath)},'nativeSha256':sha(dst)})
plan['status']='native_detail_generation_in_progress';(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'id':ident,'file':str(dst),'sha256':sha(dst),'pixels':nativePixels,'accepted':False}))
