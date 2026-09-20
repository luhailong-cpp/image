from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
id,src,qa=sys.argv[1],Path(sys.argv[2]),sys.argv[3]
out=r/'native'/f'{id}.png'
if out.exists():raise RuntimeError('refuse overwrite')
shutil.copyfile(src,out)
size=list(Image.open(out).size)
assert size==[1254,1254]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((r/'plan.json').read_text(encoding='utf8'));entry=next(x for x in plan['patches'] if x['id']==id)
pr=r/'prompts'/f'{id}.prompt.txt';g=Path(entry['guide']);j=Path(entry['submittedReference'])
rec={'id':id,'route':'builtin_image_gen','backendModelVerified':False,'role':'native_local_seam_repair','actualNativePixels':size,'outputPath':str(out),'outputSha256':sha(out),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'promptPath':str(pr),'promptSha256':sha(pr),'guidePath':str(g),'guideSha256':sha(g),'submittedReferencePath':str(j),'submittedReferenceSha256':sha(j),'boxInFinal':entry['boxInFinal'],'finalArtUpscaled':False,'resizedAfterGeneration':False,'visualQa':qa,'generatedAtUtc':datetime.now(timezone.utc).isoformat()}
(r/'native'/f'{id}.record.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
print(json.dumps({'id':id,'actualPixels':size,'sha256':sha(out)}))
