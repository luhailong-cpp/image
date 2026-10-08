"""Record shared_edge's actual 23-image native review; this does not accept tiles."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'r08_c13/west-final'
M=DEST/'output/west-final-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
m=json.loads(M.read_text(encoding='utf-8'))
assert len(m['qa'])==23
for e in m['outputs']+m['qa']:assert sha(e['file'])==e['sha256']
native=[]
for i in range(1,5):
 p=ROOT/f'r08_c13/repairs/west-common-edge/native/s{i}.png';r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'));assert sha(p)==r['sha256']
 assert Image.open(p).size==(1254,1254)
 native.append({**info(p),'record':info(str(p)+'.generation.json'),'actualView':'builtin generation result displayed at native size','geometryReference':r['geometryMatchedTo'],'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'finding':'Same DAY geometry and material identities retained under established warm festival rendering. The DAY s3 paving interruption remains a shared-source issue, recorded separately.'})
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'shared_edge','status':'shared-source-paving-repair-required','candidateOutputs':m['outputs'],'assemblyManifest':info(M),'nativeGenerationReview':native,
 'scope':{'actuallyViewedNativeQaImages':23,'completeCommonEdgePixels':4096,'commonEdgeContextWidth':512,'completeLeftAndRightAttachmentPixels':4096,'attachmentContextWidth':896,'longitudinalCorrectionReturns':3,'corners':4,'topBottomFullStripReturns':2,'targetedKnownDefectCrops':2,'resizedForInspection':False,'viewDetail':'original'},
 'evidence':[{'file':e['file'],'sha256':e['sha256'],'pixels':e['pixels'],'pairRectXYXY':e['pairRectXYXY'],'actualView':True,'viewDetail':'original'} for e in m['qa']],
 'passedScope':['Former straight common-boundary material stripe has been removed.','Red cloth white-circle duplication has been removed; circle is single and continuous.','Wood post, rope twists, wheel/fasteners and red banner have continuous contours.','The full left/right insertion attachments and all three horizontal repair-source transitions show no new clipped object, double edge or straight tone stripe.','Four strip attachment corners and full top/bottom edge returns were inspected; no local cut observed. North/south neighboring tiles are not supplied, so outer map seam QA is not implied.'],
 'remainingFindings':[{'id':'C12-C13-PAVING-JOINT-02','priority':'required','origin':'Inherited from actual DAY repaired s3 source, not caused by festival masks or RGB correction','globalApproxRectXYXY':[48945,30820,49340,31120],'pairApproxRectXYXY':[3889,2148,4284,2448],'finding':'The former 100-120px slab-joint displacement is now covered by pale/purple mottling. Two parallel diagonal joints still terminate separately in the stone surface instead of connecting as one plausible slab boundary. Top joint stops around the shared x coordinate; lower joint starts left of it at a lower y. Current candidate is visually improved but cannot claim this geometry defect resolved.','evidence':['old-paving-offset-focus.png','common-edge-return-part03.png','longitudinal-2-return.png'],'requiredAction':'Obtain a corrected DAY source and exact shared local insertion mask, then convert appearance and apply the same geometry. Do not independently invent a divergent festival-only slab layout.'}],
 'pixelVerification':m['pixelVerification'],'formalAccepted':False,'globalStateModified':False,'clientAcceptance':False,'northSouthOuterNeighborsReviewed':False}
(DEST/'qa/review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':info(DEST/'qa/review.json'),'outputs':m['outputs'],'status':report['status']},indent=2))
