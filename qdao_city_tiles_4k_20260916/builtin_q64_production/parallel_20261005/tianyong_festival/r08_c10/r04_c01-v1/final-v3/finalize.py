from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
expected='8b8519ad0e04df77272a33da2917aef665c37e2599a63d906519465c9ab3a2f5'
assert sha(O/'r04_c01-joined.png')==expected==sha(P/'corner-repair-v2/joined.png')
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'image':info(O/'r04_c01-joined.png'),'localVisualAccepted':True,'acceptanceScope':'1254 native r04_c01 local patch plus all four return strips, applied together against verified source checkpoint','formalAccepted':False,'countsAsComplete4096Tile':False,'geometryAndNavigationAcceptance':False,'joinedIntoCurrent':False,'reviewer':'/root/audit_native_pipeline','independentReviewer':'/root/audit_native_pipeline/registration_visual_audit','independentConclusion':'已实际查看corner-repair-v2的qa-corner与前后对照：原先白边凸点/7行骤降已消失，回接曲率连续；白边宽度没有局部鼓包、收窄或双影，圆角与暗倒角自然衔接。此前已通过的底部、右侧、上部与暖中板结论可保持。final-v3与corner-v2 joined同字节SHA，本1254局部补片及return可接。','evidence':[info(O/n) for n in ['r04_c01-joined.png','qa-left-return.png','qa-right-return.png','qa-bottom-return.png','qa-upper-overlap.png','qa-left-corner.png','qa-bottom-corners.png','measurements.json']]+[info(P/'corner-repair-v2/qa-corner.png'),info(P/'corner-repair-v2/qa-before-beside-after.png')],'knownInheritedSourceIssues':['左c09来源条窗口y115横向色阶','左c09/r09c09来源条窗口y1139横向色阶','c09上游来源是WIP，不等同正式整块验收'],'checks':{'nativeDimensions':[1254,1254],'nativeScale':1,'upscaled':False,'layoutReferencePixelsInFinal':False,'maxBottomContourResidual':1,'maxLeftHighlightEndpointResidual':1,'maxMainHorizontalRegistration':24,'maxMicroCornerAIRegistration':21.89199447631836,'verticalRegistration':0,'maxSummedMechanicalColorField':12,'sourceROIStillMatchesFrozenCurrent':True,'outerNativePixelsExact':True,'newRectangularMaterialSeamObserved':False,'newDoubleEdgesObserved':False,'newWidthJumpOrCurvatureWaveObserved':False}}
write(O/'visual-review.json',review)
m=read(O/'manifest.json');m['pendingIndependentVisualReview']=False;m['localVisualAccepted']=True;m['visualReview']=info(O/'visual-review.json');write(O/'manifest.json',m)
g=read(O/'generation-chain.json');g['selected']=['repaired-v1 upper warm slab','shifted-curve-v2 native shifted lower complete paired contours, bounded mechanical alignment','left-repair-v1 AI-painted material and small continuous outer highlight shape, bounded native remap in corner-repair-v2'];g['standaloneLeftRepairRejectedGeometryButSelectedMicroRegion']='The whole generation was not used: only the reviewed surface material and original-scale small white-highlight shape were selected.';g['rejectedAsStandalone'][-1]='left-repair-v1 whole image altered geometry outside hole; only local material and aligned micro highlight selected';write(O/'generation-chain.json',g)
for p in O.glob('*.png.generation.json'):
 d=read(p);d['manifest']=info(O/'manifest.json');d['pendingVisualReview']=False;d['localVisualAccepted']=True;d['formalAccepted']=False;d['selectionEvidence']=info(P/'corner-repair-v2/parameters.json');write(p,d)
for folder in [P/'corner-repair-v1',P/'corner-repair-v2']:
 for p in folder.glob('*.png'):
  write(p.with_name(p.name+'.generation.json'),{'file':str(p),'sha256':sha(p),'derivedAtUtc':datetime.now(timezone.utc).isoformat(),'generatedAt':None,'newModelCalls':0,'actualModel':None,'actualQuality':None,'operation':'Native-sized selected AI highlight, bounded horizontal remap or QA crop; no procedural redraw','sources':[info(P/'left-repair-v1/native.png.generation.json'),info(P/'final-v2/r04_c01-joined.png.generation.json')],'parameters':info(folder/'parameters.json'),'formalAccepted':False,'localVisualAccepted':folder.name=='corner-repair-v2','review':info(O/'visual-review.json')})
for folder,reason in [('final-v1','Left white highlight retained a7px last-bright-row jump; superseded'),('final-v2','Left white highlight retained a7px last-bright-row jump; superseded'),('corner-repair-v1','Smooth but residual3px in original lower anchor; refined to≤1px in v2')]:
 write(P/folder/'superseded.json',{'localVisualAccepted':False,'reason':reason,'replacement':info(O/'r04_c01-joined.png'),'replacementReview':info(O/'visual-review.json')})
for p in O.glob('*.png'):
 with Image.open(p) as im:im.verify()
for item in [m['joined'],m['core']]+[v['asset'] for v in m['patches']]:assert sha(item['file'])==item['sha256']
write(O/'result.json',{'status':'local-patch-and-return-strips-ready','joined':info(O/'r04_c01-joined.png'),'manifest':info(O/'manifest.json'),'review':info(O/'visual-review.json'),'generationChain':info(O/'generation-chain.json'),'localVisualAccepted':True,'formalAccepted':False,'joinedIntoCurrent':False,'allWritesConfinedTo':str(P),'newBuiltinGenerationsInR04C01':7,'actualModel':None,'actualQuality':None})
print(json.dumps({'result':info(O/'result.json'),'joined':info(O/'r04_c01-joined.png'),'localVisualAccepted':True,'formalAccepted':False},ensure_ascii=False))
