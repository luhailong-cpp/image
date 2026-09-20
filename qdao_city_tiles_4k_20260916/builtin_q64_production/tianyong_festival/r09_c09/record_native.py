from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ident,src=sys.argv[1],Path(sys.argv[2]);sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
plan=json.loads((P/'plan.json').read_text());patch=next(e for e in plan['patches'] if e['id']==ident)
out=P/'native'/f'{ident}.png';rf=out.with_suffix('.record.json');assert not out.exists() and not rf.exists()
im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
refs=[Path(f) for f in patch['submittedImages']];assert sha(refs[0])==patch['guideSha256'];assert sha(refs[1])==plan['styleReferenceSha256']
shutil.copyfile(src,out)
rec={'schemaVersion':2,'id':ident,'route':'builtin_image_gen','requestedModel':'gpt-image-2.5-sunburst','requestedQuality':'max','backendModelVerified':False,'actualModel':None,'actualQuality':None,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(P/patch['promptFile']),'promptSha256':sha(P/patch['promptFile']),'guidePath':str(refs[0]),'guideSha256':sha(refs[0]),'submittedImages':[{'path':str(f),'sha256':sha(f),'pixels':list(Image.open(f).size)} for f in refs],'selectedTargetImageOneBased':1,'finalArtUpscaled':False,'resizedAfterGeneration':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':[str(f) for f in refs],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_generation_observed_assembly_pending'}}
rf.write_text(json.dumps(rec,indent=2),encoding='utf-8');print(json.dumps({'id':ident,'sha256':sha(out),'pixels':[1254,1254]}))
