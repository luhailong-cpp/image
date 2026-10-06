from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
H=Path(__file__).parent;ROOT=H.parents[2];sys.path.insert(0,str(ROOT/'tools/deps'))
import cv2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def register_on_exterior(context,source,mask,label):
    # Wrong old interior grout is explicitly excluded from registration evidence.
    evidence=np.where(mask[:,:,None],source,context)
    c=cv2.cvtColor(evidence,cv2.COLOR_RGB2GRAY);s=cv2.cvtColor(source,cv2.COLOR_RGB2GRAY)
    flow=cv2.calcOpticalFlowFarneback(c,s,None,.5,4,41,5,7,1.5,0)
    flow=cv2.GaussianBlur(flow,(0,0),3)
    dist,labels=cv2.distanceTransformWithLabels(np.uint8(mask),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    zeros=np.argwhere(~mask);nearest=zeros[labels-1]
    flow*=np.minimum(1,12/np.maximum(np.linalg.norm(flow,axis=2),1e-7))[:,:,None]
    flow*=(1-smooth(dist/96))[:,:,None]
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    if label=='upper':
        # At this return the existing matched grout advances~2px left per row.
        # Trial row719 edge wasx936, while true exterior row720 isx937;
        # shifting the AI side3px right restores the same line tangent.
        w=smooth((yy-656)/64)*(1-smooth((yy-744)/36))*smooth((xx-780)/60)*(1-smooth((xx-1030)/60))
        flow[:,:,0]-=3*w
        flow*=np.minimum(1,12/np.maximum(np.linalg.norm(flow,axis=2),1e-7))[:,:,None]
    aligned=cv2.remap(source,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    diff=context.astype(np.float32)-aligned.astype(np.float32)
    # Extend only the observed exterior residual; the AI-painted new structure itself
    # never contributes the obsolete interior context to the color estimate.
    filled=diff[nearest[:,:,0],nearest[:,:,1]]
    tone=np.clip(cv2.GaussianBlur(filled,(0,0),12),-32,32)*(1-smooth(dist/128))[:,:,None]
    painted=np.clip(np.rint(aligned.astype(float)+tone),0,255).astype(np.uint8)
    merged=np.where(mask[:,:,None],painted,context)
    assert np.array_equal(merged[~mask],context[~mask])
    dxdy,dxdx=np.gradient(flow[:,:,0]);dydy,dydx=np.gradient(flow[:,:,1]);jac=(1+dxdx)*(1+dydy)-dxdy*dydx
    assert np.min(jac[mask])>0,'Folded registration; reject trial.'
    for name,a in [('mask',np.uint8(mask)*255),('flow',flow),('colorCorrection',tone)]:
        p=H/(label+'.'+name+('.png' if name=='mask' else '.npy'))
        Image.fromarray(a).save(p) if name=='mask' else np.save(p,a)
    return merged,dict(label=label,source=ref(H/(label.replace('upper','attempt2').replace('lower','attempt3')+'.png')),
        maxAllowedDisplacementVector=12,actualMaxDisplacementVector=float(np.linalg.norm(flow[mask],axis=1).max()),actualMaxXY=np.max(abs(flow[mask]),axis=0).tolist(),
        maxAllowedColorCorrectionRGB=32,actualMaxColorCorrectionRGB=np.max(abs(tone[mask]),axis=0).tolist(),jacobianMinimum=float(np.min(jac[mask])),foldedPixels=int((jac[mask]<=0).sum()),
        registrationEvidence='Current true exterior only. Editable interior replaced by native AI source before flow estimation, so obsolete broken interior geometry exerts no registration force. Upper return additionally uses a measured3px horizontal native alignment anchor at targety720, derived from the same dark/highlight edges on the unchanged exterior; smooth local fade, no structure synthesized.',
        resampling='native-size bicubic only; no enlargement',fields=[ref(H/(label+'.'+n+('.png' if n=='mask' else '.npy'))) for n in ['mask','flow','colorCorrection']])
def main():
    context=np.array(Image.open(H/'target.png').convert('RGB'))
    a2=np.array(Image.open(H/'attempt2.png').convert('RGB'));a3=np.array(Image.open(H/'attempt3.png').convert('RGB'))
    upper=np.array(Image.open(H/'edit-mask.png'))>0
    upper[:,1127:]=False;upper[:,:627]=False;upper[720:]=False
    first,rec2=register_on_exterior(context,a2,upper,'upper')
    lower=np.zeros((1254,1254),bool)
    # Include the AI-returned intact post contour as registration support, so the final
    # binary cut does not run along a manually approximated silhouette.
    lower[740:1040,627:815]=True
    merged,rec3=register_on_exterior(first,a3,lower,'lower')
    assert np.array_equal(merged[:,:627],context[:,:627]);assert np.array_equal(merged[:,1127:],context[:,1127:])
    p=H/'native-merge-trial.png';Image.fromarray(merged).save(p)
    qa=[]
    def crop(name,box):
        p=H/name;Image.fromarray(merged).crop(box).save(p);qa.append(dict(**ref(p),cropLTRB=box,pixels=[box[2]-box[0],box[3]-box[1]],actuallyViewed=False,nativeScale=1))
    crop('merged-upper-shared.png',[467,240,787,560]);crop('merged-lower-shared.png',[467,750,787,1070])
    crop('merged-return-upper.png',[967,160,1254,740]);crop('merged-return-lower.png',[967,690,1254,1110])
    crop('merged-upper-top-boundary.png',[467,80,1254,260]);crop('merged-bottom-boundary.png',[467,970,1254,1130])
    crop('merged-upper-bottom-boundary.png',[467,640,1254,800])
    crop('return-bottom-micro.png',[850,680,990,760]);crop('return-top-micro.png',[960,135,1127,210])
    crop('merged-column-boundary.png',[607,728,1054,1110])
    crop('merged-internal2048.png',[467,74,1254,234]);crop('merged-internal3072.png',[467,1098,1254,1254])
    write(H/'merge-trial-record.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),kind='two_native_AI_repairs_registered_on_true_exterior_then_binary_mask_merge',input=ref(H/'target.png'),inputCurrentSha256='4adf1d95a12781e56d683977809d555cd018b4621b5b4977afa89c187702c200',output=ref(p),outputPixels=[1254,1254],newTileYOrigin=1894,sharedEdgeX=627,unchangedLeft627=True,unchangedAfterNewX500=True,sourceScale=1,noGeometryFeather=True,passes=[rec2,rec3],qa=qa,productionOutputModified=False,visualReviewPending=True))
    print(json.dumps(dict(file=str(p),passes=[{k:r[k] for k in ['label','actualMaxDisplacementVector','actualMaxXY','actualMaxColorCorrectionRGB']} for r in [rec2,rec3]])))
if __name__=='__main__':main()
