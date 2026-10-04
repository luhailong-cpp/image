from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
source,label=Path(sys.argv[1]),sys.argv[2]
dest=R/'run/staging'/f'{label}.png'
if not label.startswith('south-bamboo-'): raise ValueError('outside subtask')
shutil.copy2(source,dest)
req=json.loads((R/'provenance'/f'{label}.request.json').read_text(encoding='utf-8'))
im=Image.open(dest)
if min(im.size)<1024: raise ValueError('native below1024')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'nativeSize':list(im.size),'width':im.width,'height':im.height,'mode':im.mode,'generatedAt':datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host file mtime; tool did not disclose generated timestamp','recordedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed tool exposes neither model selector/quality selector nor returned actual model/quality.','references':[{'path':p,'sha256':sha(p),'role':role} for p,role in zip(req['submittedParameters']['referenced_image_paths'],req['referenceRoles'])],'inputSourceMode':req['sourceMode'],'previousGenerationRecord':req['previousGenerationRecord'],'previousOfficialSha':req['previousOfficialSha'],'evidence':{'toolReturnedPath':str(source),'returnedFields':['image_url','output_hint'],'workspaceCopyShaMatchesSource':sha(dest)==sha(source)},'request':f'provenance/{label}.request.json','receipt':f'provenance/{label}.receipt.json','review':{'status':'pending_direct_comparison'},'registrationApplied':False}
Path(str(dest)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'label':label,'file':str(dest),'nativeSize':list(im.size),'sha256':sha(dest)}))
