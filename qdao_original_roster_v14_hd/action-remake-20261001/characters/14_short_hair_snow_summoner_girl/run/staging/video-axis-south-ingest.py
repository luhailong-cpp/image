from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
src=Path(sys.argv[1]);label=sys.argv[2]
assert label.startswith('video-axis-SE-')
req=json.loads((R/f'provenance/{label}.request.json').read_text(encoding='utf-8'))
dst=R/f'run/staging/{label}.png';shutil.copyfile(src,dst)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(dst);assert min(im.size)>=1024
refs=[{'file':p,'sha256':sha(Path(p)),'role':role} for p,role in zip(req['submittedParameters']['referenced_image_paths'],req['referenceRoles'])]
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
rec={'label':label,'generatedAt':datetime.now(timezone.utc).isoformat(),'file':dst.relative_to(R).as_posix(),'sha256':sha(dst),'width':im.width,'height':im.height,'mode':im.mode,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':cfg,'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin route does not expose model or quality selectors or confirmation.','submittedParameters':req['submittedParameters'],'references':refs,'sourceMode':'direct_registered_canvas_redraw','hostOutput':str(src),'receipt':f'provenance/{label}.receipt.json','status':'native_candidate_pending_visual_review'}
Path(str(dst)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'label':label,'file':str(dst),'nativeSize':list(im.size),'sha256':sha(dst)}))

