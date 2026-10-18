from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=T/'qa/core-baseline/3072ac5a7f7ddbf7faeb/r01_c14-core-baseline.candidate.png';src=T/'native/repairs/M02-center-v20261016-fix1.png';bi=Image.open(base).convert('RGB');si=Image.open(src).convert('RGB');out=bi.copy();out.paste(si.crop((115,115,1139,1139)),(1536,1536));dest=T/'candidates/r01_c14.M02-local-v1-20261016.png';dest.parent.mkdir(exist_ok=True);assert not dest.exists();out.save(dest)
diff=ImageChops.difference(bi,out);diff.paste((0,0,0),(1536,1536,2560,2560));assert diff.getbbox() is None
for name,box in [('top',(1408,1408,2688,1664)),('bottom',(1408,2432,2688,2688)),('left',(1408,1408,1664,2688)),('right',(2432,1408,2688,2688))]:out.crop(box).save(Q/('M02-v1-'+name+'.png'))
meta={'candidate':str(dest),'candidateSha256':sha(dest),'baseCandidate':str(base),'baseCandidateSha256':sha(base),'source':str(src),'sourceSha256':sha(src),'sourceROI':[115,115,1139,1139],'destinationROI':[1536,1536,2560,2560],'outsideROIIdentical':True,'operation':'exact integer native crop-paste, no resizing blending painting','nativeEditAttempt':1,'status':'not_yet_adopted_boundary_review_pending'}
(Q/'M02-composition-v1.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))

