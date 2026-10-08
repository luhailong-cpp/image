from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;T=R/'r08_c16';Q=T/'qa/assembly'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
candidate=T/'output/r08_c16.png'
assert sha(candidate)=='8c6871e74071f25997e4263bc21518f8b151a97c1b3408546e288f01867c3115'
names=['overview-preview-1024','corner-nw','corner-ne','corner-sw','corner-se','west-c15-c16-common-edge-full']
record={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actualVisualInspection':True,'candidateSha256':sha(candidate),'formalAccepted':False,'overallResult':'needs-repair','tileCorners':'pass for standalone corner material continuity; common-edge geometry assessed separately','westCommonEdge':'fail: upper blue canopy versus timber framing and several hull/rail endpoints are discontinuous','overviewFindings':['mast horizontal shade bands','vertical jagged color junction in blue hull/wood hull','right water vertical texture seam'],'nextWork':'close_joint14 handles west structure joint; fill16_left supplies interior repairs; no downstream full-tile binding until stable repaired output','sheets':[{'file':str(Q/f'{n}.png'),'sha256':sha(Q/f'{n}.png'),'nativePixelQA':not n.startswith('overview')} for n in names]}
(T/'qa/root-external-initial-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Initial c16 external findings recorded; not accepted.')
