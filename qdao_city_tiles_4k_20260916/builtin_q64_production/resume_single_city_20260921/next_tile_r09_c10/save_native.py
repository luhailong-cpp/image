"""Preserve exact built-in image bytes and a factual receipt; no acceptance implied."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil,sys
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ident=sys.argv[1];src=Path(sys.argv[2]);status=sys.argv[3] if len(sys.argv)>3 else 'unreviewed'
stem=sys.argv[4] if len(sys.argv)>4 else ident
plan=json.loads((P/'plan.json').read_text());patch=next(p for p in plan['patches'] if p['id']==ident)
dst=P/'native'/f'{stem}.png';assert not dst.exists(),'Never overwrite original generated outputs'
im=Image.open(src);im.load();assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
shutil.copyfile(src,dst);prompt=Path(patch['promptFile']);refs=[Path(f) for f in patch['submittedImages']]
rec={'schemaVersion':2,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','requestedModel':plan['requestedModel'],'requestedQuality':plan['requestedQuality'],'actualModel':None,'actualQuality':None,'backendModelVerified':False,'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'toolResponseFields':['image_url','output_hint'],'toolResponseModelMetadataAvailable':False,'toolOutputPath':str(src),'toolOutputSha256':sha(src),'toolOutputBytes':src.stat().st_size,'nativePixels':list(im.size),'imageMode':im.mode,'nativeSha256':sha(dst),'nativeFile':str(dst),'promptFile':str(prompt),'promptSha256':sha(prompt),'promptTransport':'File contents with leading and trailing whitespace stripped','submittedImages':[{'path':str(r),'sha256':sha(r)} for r in refs],'selectedTargetImageOneBased':1,'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':[str(r) for r in refs]},'finalArtUpscaled':False,'resampled':False,'visualStatus':status,'accepted':False,'runtimePublished':False}
(P/'native'/f'{stem}.record.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
patch['status']=status;patch['nativeSha256']=sha(dst);patch['nativePixels']=list(im.size);patch['outputFile']=f'native/{stem}.png';(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'id':ident,'sha256':sha(dst),'bytes':dst.stat().st_size,'pixels':list(im.size),'status':status}))
