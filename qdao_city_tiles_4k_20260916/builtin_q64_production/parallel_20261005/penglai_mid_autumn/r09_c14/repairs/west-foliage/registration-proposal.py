
from pathlib import Path
import sys, json
from types import SimpleNamespace
import numpy as np
from PIL import Image
BASE=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn')
sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'tools/deps'))
import cv2
from production import sha,deriv,write,now
from native_assemble import register_native,smoothstep
OUT=BASE/'r09_c14/repairs/west-foliage'
def arr(n):return np.array(Image.open(OUT/n).convert('RGB'))
original=arr('edit-target.png');v6=arr('proposed-joint-preview-v6.png');raw=arr('repair-native.png')
size=1254;yy,xx=np.mgrid[:size,:size].astype(np.float32)
# Moving support comes from the actual AI source; using the already locked preview here would produce zero flow.
moving=v6.copy();moving[:,:320]=raw[:,:320]
known=(xx>=160)&(xx<320)&(yy>=300)&(yy<650)
owner=xx>=320
_,flow,tone,base_report=register_native(original,moving,known,owner,['left'],SimpleNamespace(patch=1254,halo=320),max_shift=6.,tone_cap=18.,return_depth=192)
vertical=smoothstep((yy-300)/48)*smoothstep((650-yy)/80)
flow*=vertical[:,:,None];tone*=vertical[:,:,None]
flow[~owner]=0;tone[~owner]=0
pre=None;scale=1.
for _ in range(20):
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1])
 jac=(1+dxu)*(1+dyv)-dyu*dxv
 low=float(jac[owner].min())
 if pre is None:pre=low
 if low>=0.25:break
 flow*=.75;scale*=.75
else:raise RuntimeError('orientation validation failed')
aligned=cv2.remap(moving,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
fixed=np.uint8(np.clip(np.rint(aligned.astype(np.float32)+tone),0,255))
active=owner & (vertical>0) & (xx<512)
result=v6.copy();result[active]=fixed[active]
assert np.array_equal(result[:,:320],original[:,:320])
assert np.array_equal(result[:,512:],v6[:,512:])
assert np.array_equal(result[:300],v6[:300]) and np.array_equal(result[650:],v6[650:])
for name,data in [('proposal-v7.flow.npy',flow),('proposal-v7.colorCorrection.npy',tone)]:np.save(OUT/name,data)
for name,mask in [('proposal-v7.support-mask.png',known),('proposal-v7.apply-mask.png',active)]:
 p=OUT/name;Image.fromarray(mask.astype(np.uint8)*255).save(p);deriv(p,[OUT/'edit-target.png',OUT/'repair-native.png',OUT/'proposed-joint-preview-v6.png'],dict(kind='registration_support_or_application_mask',role=name,nativeScale=1))
p=OUT/'proposed-joint-preview-v7.png';Image.fromarray(result).save(p)
fieldRefs=[dict(file=str(OUT/n),sha256=sha(OUT/n)) for n in ['proposal-v7.flow.npy','proposal-v7.colorCorrection.npy','proposal-v7.support-mask.png','proposal-v7.apply-mask.png']]
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
report=dict(createdAt=now(),kind='targeted_native_registration_of_already_matching_leaf_geometry',baseRegistration=base_report,supportSource='actual old neighbor target x160..319,y300..649 versus corresponding native AI source pixels',movingSource='raw AI left320 support; reviewed v6 right-hand repair pixels',sourceFiles=[dict(file=str(OUT/n),sha256=sha(OUT/n)) for n in ['edit-target.png','repair-native.png','proposed-joint-preview-v6.png']],actualMaxDisplacementVector=float(np.linalg.norm(flow,axis=2).max()),actualMaxDisplacementXY=np.abs(flow).max(axis=(0,1)).tolist(),actualMaxColorCorrectionRGB=np.abs(tone).max(axis=(0,1)).tolist(),maxAllowedDisplacementVector=6,maxAllowedColorCorrectionRGB=18,verticalReturnY=[300,348,570,650],horizontalReturnX=[352,512],jacobianMinimumBeforeFinalBoundarySafety=pre,finalOrientationSafetyScale=scale,jacobianMinimumInAppliedPixels=float(jac[active].min()),foldedAppliedPixels=int((jac[active]<=0).sum()),fields=fieldRefs,helper=dict(file=str(BASE/'native_assemble.py'),sha256=sha(BASE/'native_assemble.py')),script=dict(file=str(Path(__file__).resolve()),sha256=sha(__file__)),fixedNeighborLeft320BitExact=True,rootCandidateChanged=False,sourceUpscaling=False,newStructurePaintedByCode=False,requiresVisualQA=True,formalAccepted=False)
write(OUT/'proposal-v7.registration.json',report)
deriv(p,[OUT/'proposed-joint-preview-v6.png',OUT/'repair-native.png',OUT/'edit-target.png'],dict(kind='bounded_native_leaf_registration_and_color',registrationRecord=str(OUT/'proposal-v7.registration.json'),registrationRecordSha256=sha(OUT/'proposal-v7.registration.json'),fields=fieldRefs,rootCandidateChanged=False,nativeScale=1))
detail=OUT/'upper-detail-v7.png';Image.fromarray(result).crop((200,0,650,700)).save(detail);deriv(detail,[p],dict(kind='native_review_crop',cropLTRB=[200,0,650,700],nativeScale=1))
print(json.dumps(dict(preview=str(p),detail=str(detail),maxShift=report['actualMaxDisplacementVector'],maxColor=report['actualMaxColorCorrectionRGB'],jacobian=report['jacobianMinimumInAppliedPixels'])))

