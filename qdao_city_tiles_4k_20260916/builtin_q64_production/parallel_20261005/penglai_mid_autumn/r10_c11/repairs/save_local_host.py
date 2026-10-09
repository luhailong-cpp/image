from pathlib import Path
from PIL import Image
import json,hashlib,datetime,sys,shutil
D=Path(sys.argv[1]);src=Path(sys.argv[2]);dst=D/'host-result.png';req=json.loads((D/'repair.request.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
if dst.exists():assert sha(dst)==sha(src)
else:shutil.copy2(src,dst)
assert Image.open(dst).size==(1254,1254)
for x in req['references']:assert sha(x['file'])==x['sha256']
p=Path(str(dst)+'.generation.json');assert not p.exists();rec=dict(**ref(dst),generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],prompt=req['prompt'],references=req['references'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed; no selectors or reliable returned actual model/quality metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False);p.write_bytes((json.dumps(rec,ensure_ascii=False,indent=2)+'\n').encode());print(sha(dst))
