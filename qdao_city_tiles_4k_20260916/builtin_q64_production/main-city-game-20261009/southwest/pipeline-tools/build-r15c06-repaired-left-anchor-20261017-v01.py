from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1];D=B/'r15_c05/repairs-resume-20261016/exported-inner-rim-20261016-v02'
a_path=D/'integrated-masked-20261016-v01/assembly.json';a=json.loads(a_path.read_text(encoding='utf-8-sig'))
src=Path(a['contextOutput']['file']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(src)==a['contextOutput']['sha256']=='fb99b1ec7eb3e314ecfd2959a2524d26ca8ceb7f54299f8ea214b208b733f390'
out=B/'r15_c06/pipeline/anchors/left-r15_c05-inner-rim-repaired-provisional-20261017-v02.png'
assert not out.exists()
with Image.open(src) as im:
 assert im.size==(4326,4326)
 im.crop((4096,0,4326,4326)).save(out)
v={'file':str(out),'sha256':sha(out),'pixels':[230,4326],'operation':'exact crop of current native16 context, no resampling','sourceResampling':False,'sourceFile':str(src),'sourceSha256':sha(src),'sourceCrop':[4096,0,4326,4326],'assembly':str(a_path),'assemblySha256':sha(a_path),'visualReview':str(D/'qa/review.json'),'reviewSha256':sha(D/'qa/review.json'),'provisionalOnly':True,'notAcceptedAnchor':True,'remainingIssue':'white inner rim removed, genuine outer gray-blue boundary unchanged; shallow blue material front near source context y1210 remains failed, nonblocking local material issue only; do not claim exterior passed','internalPassed':False,'externalPassed':False,'formalAccepted':False,'recordedAtUtc':datetime.now(timezone.utc).isoformat()}
Path(str(out)+'.derivation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False))

