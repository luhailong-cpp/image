"""Record actual native views performed by shared_edge on 2026-10-08."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parent
QA=ROOT/'r08_c13/repairs/west-common-edge/pre-repair-qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((QA/'manifest.json').read_text(encoding='utf-8'))
for e in m['items']:assert sha(e['file'])==e['sha256']
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'shared_edge','status':'failed-unrepaired-shared-geometry','scope':'Full 4096-pixel c12/c13 common edge, 512 pixels on each side; four 1024x1024 native crops per appearance','sources':m['sources'],'imagesActuallyViewed':[{'file':e['file'],'sha256':e['sha256'],'detail':'original','resized':False} for e in m['items']],
'findings':[
 {'id':'C12-C13-PAVING-JOINT-01','priority':'required','appearances':['day','festival'],'globalApproxRectXYXY':[49080,30880,49240,31450],'pairApproxRectXYXY':[4024,2208,4184,2778],'finding':'Two slab joints terminate abruptly at global x49152. The upper oblique joint and lower diagonal joint are displaced approximately 100-120 pixels between the two tile halves. The same contour mismatch is present in the DAY sources; bounded RGB matching cannot repair it.','action':'Use four actual upstream DAY common-edge repair natives and shared five-mask geometry contract; do not invent separate festival geometry.'},
 {'id':'C12-C13-BANNER-01','priority':'required','appearances':['festival'],'globalApproxRectXYXY':[49120,32170,49200,32380],'pairApproxRectXYXY':[4064,3498,4144,3708],'finding':'The large white circle on the red hanging cloth has a short duplicated left lobe at the common boundary. Native DAY crop has a single contour; follow the repaired DAY strip and preserve circle silhouette.','action':'Inspect and resolve in the common-edge festival conversion, then inspect exact native return crops.'}],
'otherSegments':'No additional independent object deletion or new boundary displacement was seen in parts 01-02. This does not approve the current common edge, whose part03 and part04 fail.',
'formalAccepted':False,'globalStateModified':False,'nextRequiredEvidence':'Actual complete DAY four-native repair and five-mask contract, followed by festival conversion and full-strip attachment/corner QA.'}
(QA/'review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(QA/'review.json'))
