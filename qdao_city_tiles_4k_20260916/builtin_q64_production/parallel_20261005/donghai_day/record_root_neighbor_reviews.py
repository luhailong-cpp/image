from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
T=R/'r09_c15';P=T/'output/r09_c15.png';C=T/'repairs/color-match/candidate.png'
assert sha(P)=='45a82a7b24818094fdb8a0b5ee6f3dd3ca554e2c01eff2c862de9184afa8bf66'
assert sha(C)=='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
def sheets(q,names):return [{'file':str(q/f'{n}.png'),'sha256':sha(q/f'{n}.png'),'nativePixelQA':not n.startswith('overview')}for n in names]
base={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actualVisualInspection':True,'formalAccepted':False}
write(T/'qa/root-external-initial-review.json',{**base,'candidateSha256':sha(P),'result':'pass for four corners and full north common edge only','limitations':'Internal seams failed initial review and are repaired separately; east neighbor is incomplete.','sheets':sheets(T/'qa/assembly',['overview-preview-1024','corner-nw','corner-ne','corner-sw','corner-se','north-r08-r09-common-edge-full'])})
old=np.asarray(Image.open(P));new=np.asarray(Image.open(C));assert np.array_equal(old[:128],new[:128])
write(T/'repairs/color-match/root-independent-review.json',{**base,'candidateSha256':sha(C),'result':'pass for targeted final review; may commit this candidate','observations':['No artificial cross-grain jagged step remains in the checked main timber pilings.','Submerged rear piling retains continuous material and contact highlight.','Water and pilings at horizontal y3072 join smoothly; shadow shapes remain intact.','North128 native rows remain exactly equal to the already-reviewed initial candidate.'],'north128PixelIdentityVerified':True,'sheets':sheets(T/'repairs/color-match/qa',['overview-preview-1024','internal-vertical-x2048-full','internal-horizontal-y3072-full']),'limitations':['Other final internal sheets were actually reviewed by producing agent.','No whole-city/client/navigation acceptance.']})
T=R/'r07_c15';P=T/'output/r07_c15.png';assert sha(P)=='3d6784d05e08447095081e0a2c425a1d11b2f7c461a7ff1dd74d9efa7644ea13'
names=['overview-preview-1024','south-r07-r08-common-edge-full']+[f'internal-{axis}-{coord}{x}-full'for axis,coord in [('vertical','x'),('horizontal','y')]for x in [1024,2048,3072]]+[f'intersection-x{x}-y{y}'for x in [1024,2048,3072]for y in [1024,2048,3072]]+[f'corner-{x}'for x in ['nw','ne','sw','se']]
write(T/'qa/root-initial-review.json',{**base,'candidateSha256':sha(P),'result':'needs repair','observations':['Horizontal y2048: multiple abrupt piling and water color steps.','Vertical water boundaries x2048/x3072 continue toward y3072.','Blue pane has mismatched reflection below y3072.','Horizontal y1024 and nearby plank surfaces show smaller tonal steps.','South common edge has disconnected barrel/cabin-roof/canopy geometry requiring upper-side repair.','Four standalone corner crops contain intact materials; this does not imply cross-tile acceptance.'],'sheets':sheets(T/'qa/assembly',names)})
plan=json.loads((T/'plan.json').read_text(encoding='utf-8'));plan['status']='complete-native-candidate-under-seam-repair';plan['geometryStatus']='local structure reviewed; native geometry preserved except documented unresolved south boundary joins';write(T/'plan.json',plan)
print('Recorded root actual visual reviews and exact north edge identity.')
