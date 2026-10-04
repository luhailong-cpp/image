from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
root=Path(__file__).parents[2]
work=root/'run-contact-revision-20261004/SE/07-v8'
source=work/'native.png';reference=root/'run-contact-revision-20261004/SE/07-v7/native.png'
# Manually read from 50px coordinate-grid review, using head, pelvic belt and weapon grip details; never sole.
anchors=[
 ('head-forehead-jewel',[756,524],[733,512]),
 ('pelvis-belt-flower',[658,816],[644,763]),
 ('weapon-lower-hand-grip',[523,836],[520,785]),
 ('weapon-upper-hand-grip',[835,663],[800,628]),
 ('head-left-hair-gem',[577,424],[575,422]),
]
src=np.array([a[1] for a in anchors],float);dst=np.array([a[2] for a in anchors],float)
cx=src.mean(0);cy=dst.mean(0);x=src-cx;y=dst-cy
u,s,vt=np.linalg.svd(x.T@y);rot=u@vt
scale=s.sum()/(x*x).sum();offset=cy-scale*cx@rot
forward=np.eye(3);forward[:2,:2]=scale*rot.T;forward[:2,2]=offset
inverse=np.linalg.inv(forward);pred=scale*src@rot+offset
residual=np.linalg.norm(pred-dst,axis=1)
im=Image.open(source).convert('RGBA');im.transform(im.size,Image.Transform.AFFINE,tuple(inverse[:2].ravel()),Image.Resampling.BICUBIC).save(work/'registered.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof={'source':source.relative_to(root).as_posix(),'sourceSha256':sha(source),'reference':reference.relative_to(root).as_posix(),'referenceSha256':sha(reference),'purpose':'Remove global generation composition enlargement of an already independently drawn pose; does not create an extra pose or align soles.','anchorSource':'Manually read from SE/anchor-review.jpg50px coordinate grid; approximate visual detail centers.','anchors':[{'name':a[0],'sourceXY':a[1],'referenceXY':a[2],'residualPx':float(e)}for a,e in zip(anchors,residual)],'transform':'similarity scale+rotation+translation only','uniformScale':float(scale),'forwardMatrix':forward.tolist(),'rmsResidualPx':float(np.sqrt((residual**2).mean())),'footAnchorsUsed':False,'sourcePoseCount':1,'outputPoseCount':1,'output':'registered.png'}
(work/'registration.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
rec=json.loads(Path(str(source)+'.generation.json').read_text())
rec.update(file=(work/'registered.png').relative_to(root).as_posix(),sha256=sha(work/'registered.png'),derivedFrom={'file':source.relative_to(root).as_posix(),'sha256':sha(source),'generationRecord':Path(str(source)+'.generation.json').relative_to(root).as_posix()},nativeEvidence={'historicalFile':source.relative_to(root).as_posix(),'sha256':sha(source),'size':list(im.size),'mode':im.mode,'generationRecord':Path(str(source)+'.generation.json').relative_to(root).as_posix(),'recordSHA256':sha(Path(str(source)+'.generation.json'))},operation='Single independently AI-drawn pose registration using5 head/pelvis/weapon anchors; no foot anchor and no duplicated frame.',registrationRecord=(work/'registration.json').relative_to(root).as_posix())
Path(str(work/'registered.png')+'.generation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'scale':float(scale),'rms':proof['rmsResidualPx'],'output':str(work/'registered.png')}))
