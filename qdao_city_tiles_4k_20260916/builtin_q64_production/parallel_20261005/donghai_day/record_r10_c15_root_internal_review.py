from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;D=R/'r10_c15/repairs/internal-integrated-v2';Q=D/'qa/assembly'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected='af95055c00efcb511e8a19e157fa8ec62d885eeaff0d98f83a5471139b1b1bfa';assert sha(D/'candidate.png')==expected
names=['overview-preview-1024']+[f'internal-{orient}-{axis}{n}-full' for orient,axis in [('horizontal','y'),('vertical','x')] for n in [1024,2048,3072]]+[f'intersection-x{x}-y{y}' for y in [1024,2048,3072] for x in [1024,2048,3072]]
v={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidateSha256':expected,'actualVisualInspection':True,'passed':True,'scope':'Internal6fullbands and9intersections, y>=700; overview composition only. North/external/wall-insertion strips not covered by this report.','notes':['Stone joints and wooden post geometry remain continuous across internal seams.','No abrupt broad tonal bands seen at y3072; retained narrow grain color facets are consistent with wood material.','Later integration must compare sheet SHA and repeat changed sheets.'],'viewed':[{'file':str(Q/(n+'.png')),'sha256':sha(Q/(n+'.png'))} for n in names],'formalAccepted':False}
(D/'root-independent-internal-review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(expected)
