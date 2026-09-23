from pathlib import Path
from PIL import Image
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parent
left=P.parent/'tools/sessions/tianyong_festival/r09_c09/output_resume_20260921/extended-context.png'
layout=json.loads((P/'layout-record.json').read_text());e=layout['neighborConstraints'][0]
a=np.array(Image.open(left).convert('RGB').crop((4096,4096,4326,4326)),dtype=np.int16)
b=np.array(Image.open(e['source']).convert('RGB').crop((12288,0,12518,230)),dtype=np.int16)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(left).convert('RGB').crop((4096,0,4326,4326));im.save(P/'references/left-r09_c09-overlap-unreviewed.png')
im.thumbnail((230,1254));im.save(P/'references/left-overlap-review.jpg',quality=96)
out=Image.new('RGB',(460,230));out.paste(Image.fromarray(a.astype('uint8')),(0,0));out.paste(Image.fromarray(b.astype('uint8')),(230,0));out.save(P/'qa/left-bottom-corner-comparison.png')
record={'leftCandidateSource':str(left),'sha256':sha(left),'leftCandidateStatus':'mechanically_assembled_not_QA_accepted','leftOverlapBoxLTRB':[4096,0,4326,4326],'bottomLeftCornerExactEqual':bool(np.array_equal(a,b)),'cornerMeanAbsoluteError':float(np.abs(a-b).mean()),'cornerMaximumDifference':int(np.abs(a-b).max()),'leftConstraintActivated':False,'reason':'Visual review required. Corner disagreement must be redrawn before treating shared corner as continuous.'}
(P/'qa/left-neighbor-check.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2))
