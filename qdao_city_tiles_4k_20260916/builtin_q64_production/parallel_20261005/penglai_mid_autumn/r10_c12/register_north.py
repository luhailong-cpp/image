from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from production import ROOT as TASK,read,write,sha,now,deriv
sys.path.insert(0,str(TASK/'tools/deps'))
import cv2
import numpy as np
from PIL import Image
ROOT=TASK/'r10_c12';OUT=ROOT/'output';QA=ROOT/'qa/north-registered'
OUT.mkdir(exist_ok=True);QA.mkdir(parents=True,exist_ok=True)

def main():
    base=ROOT/'assembly-registered/r10_c12-candidate.png';ext=ROOT/'assembly-registered/r10_c12-extended.png'
    north=Path(read(TASK/'handoff.json')['baselineCandidates'][2]['file'])
    old=np.array(Image.open(north).convert('RGB'));original=np.array(Image.open(base).convert('RGB'))
    source=np.array(Image.open(ext).convert('RGB'))[:435,115:4211]
    context=source.copy();context[:115]=old[-115:]
    flow0=cv2.calcOpticalFlowFarneback(cv2.cvtColor(context,cv2.COLOR_RGB2GRAY),cv2.cvtColor(source,cv2.COLOR_RGB2GRAY),None,.5,4,51,5,7,1.5,0)
    anchor=np.median(flow0[80:106],axis=0)
    anchor=cv2.GaussianBlur(anchor[None],(0,0),3)[0]
    norms=np.linalg.norm(anchor,axis=1,keepdims=True);anchor*=np.minimum(1,6/np.maximum(norms,1e-6))
    yy,xx=np.mgrid[:435,:4096].astype(np.float32)
    fade=np.clip((256-(yy-115))/256,0,1);fade=fade*fade*(3-2*fade)
    flow=anchor[None]*fade[:,:,None]
    aligned=cv2.remap(source,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    delta=np.median(old[-24:].astype(float)-aligned[91:115].astype(float),axis=0)
    delta=cv2.GaussianBlur(delta[None].astype(np.float32),(0,0),12)[0]
    correction=np.clip(delta,-24,24)[None]*fade[:,:,None]
    corrected=np.uint8(np.clip(np.rint(aligned.astype(float)+correction),0,255))
    result=original.copy();result[:256]=corrected[115:371]
    assert np.array_equal(result[256:],original[256:])
    dst=OUT/'r10_c12.png';Image.fromarray(result).save(dst)
    fields={}
    for name,arr in [('flow',flow[115:371]),('colorCorrection',correction[115:371])]:
        f=OUT/(name+'.npy');np.save(f,arr);fields[name]=dict(file=str(f),sha256=sha(f))
    mask=OUT/'mask.png';Image.fromarray(np.full((256,4096),255,np.uint8)).save(mask);fields['mask']=dict(file=str(mask),sha256=sha(mask))
    operation=dict(kind='limited_registration_on_actual_northern_support',geometrySource=str(ext),oldNeighborUnchanged=True,unchangedAfterNewTileY=256,sourcePixelScale=1,sourceUpscaling=False,resampling='bicubic limited subpixel remap of existing native pixels',maximumAllowedVectorPixels=6,actualMaximumVectorPixels=float(np.linalg.norm(flow[115:371],axis=2).max()),toneClampRGB=24,actualMaxToneRGB=np.abs(correction[115:371]).max(axis=(0,1)).tolist(),anchorEstimation='median native old-only support rows80:106, Gaussian3 horizontally; smoothly extend to new256px then zero',fields=fields)
    deriv(dst,[base,ext,north],operation);g=read(str(dst)+'.generation.json');g.update(productionPixels=True,formalAccepted=False);write(str(dst)+'.generation.json',g)
    qa=[]
    joint=np.concatenate([old[-160:],result[:160]],axis=0)
    for name,array in [('north-full',joint),('return-y256',result[96:416])]:
        im=Image.fromarray(array);sheet=Image.new('RGB',(1024,1280))
        for k in range(4):sheet.paste(im.crop((1024*k,0,1024*(k+1),320)),(0,320*k))
        p=QA/(name+'.png');sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),scale=1,actuallyViewed=False))
    sheet=Image.new('RGB',(960,480))
    for k,x in enumerate([1024,2048,3072]):sheet.paste(Image.fromarray(np.concatenate([old[-160:,x-160:x+160],result[:320,x-160:x+160]],axis=0)),(320*k,0))
    p=QA/'junctions.png';sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),scale=1,actuallyViewed=False))
    write(OUT/'manifest.json',dict(createdAt=now(),tile='r10_c12',file=str(dst),sha256=sha(dst),pixels=[4096,4096],globalPixelRectXYWH=[45056,36864,4096,4096],completePixelCoverage=True,northSource=str(north),northSourceSha256=sha(north),operation=operation,qa=qa,formalAccepted=False,navigationVerified=False,clientVerified=False,status='complete_native_candidate_pending_northern_registration_QA'))
    Image.fromarray(result).resize((1254,1254),Image.Resampling.LANCZOS).save(ROOT/'current-preview.png');deriv(ROOT/'current-preview.png',[dst],dict(kind='preview_downsample_only',scale='1254/4096'))
    print(str(dst))
if __name__=='__main__':main()
