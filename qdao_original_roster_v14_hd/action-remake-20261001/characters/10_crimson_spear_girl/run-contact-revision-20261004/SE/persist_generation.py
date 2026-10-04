from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
mode=sys.argv[1];work=Path(sys.argv[2]);root=work.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads((work/'request.json').read_text(encoding='utf-8'))
if mode=='prepare':
 req['requestedAt']=datetime.now(timezone.utc).isoformat();req['status']='submitted'
 req['references']=[{'path':p,'sha256':sha(Path(p)),'role':req.get('referenceRoles',['exact edit target','support continuity','approved09 same-direction anatomy','primary paint style'])[i]} for i,p in enumerate(req['referenced_image_paths'])]
 (work/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(req,ensure_ascii=False))
else:
 src=Path(sys.argv[3]);native=work/'native.png';out=work/'review1024.png'
 shutil.copy2(src,native);im=Image.open(native);im.load()
 if im.mode!='RGBA' or min(im.size)<1024:raise ValueError('invalid native '+str(im.mode)+str(im.size))
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 rec={'tool':'image_gen.imagegen','route':'builtin','generatedAt':datetime.now(timezone.utc).isoformat(),'configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality selector or verified result values exposed.','request':str((work/'request.json').relative_to(root)).replace('\\','/'),'prompt':str((work/'prompt.txt').relative_to(root)).replace('\\','/'),'receipt':str((work/'receipt.json').relative_to(root)).replace('\\','/'),'references':req['references'],'nativeSize':list(im.size),'format':'PNG RGBA','slot':req['slot'],'outputScalePolicy':'full-canvas-to1024-no-translation','status':'generated-pending-visual-check','hostOutputPath':str(src)}
 for p,size in [(native,im.size),(out,(1024,1024))]:
  d={**rec,'file':p.relative_to(root).as_posix(),'sha256':sha(p),'width':size[0],'height':size[1]}
  if p==out:d.update(derivedFrom={'file':native.relative_to(root).as_posix(),'sha256':sha(native),'generationRecord':str(native.relative_to(root))+'.generation.json'},operation='whole-canvas LANCZOS resize to1024 only; no translation/crop/bbox normalization/pose interpolation')
  Path(str(p)+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'slot':req['slot'],'native':str(native),'review':str(out),'nativeSize':list(im.size),'sha256':sha(native),'alphaExtrema':im.getchannel('A').getextrema()}))
