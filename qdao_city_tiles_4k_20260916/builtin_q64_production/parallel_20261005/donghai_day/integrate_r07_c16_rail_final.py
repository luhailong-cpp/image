"""Finish the upper tile's rail only; all three neighboring tiles stay fixed."""
from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
import repair_r07_c16_rail_edge as p
R=p.R;T=p.T;B=T/'repairs/final-west-joint';D=T/'repairs/final-rail-v1';Q=D/'qa';M=D/'masks'/('run-'+uuid.uuid4().hex[:8])
N=p.D/'south-boundary';S=B/'candidate.png'
for f,s in p.EXPECTED.items():assert a.sha(f)==s
base=j.rgb(S);west=j.rgb(p.W);south=j.rgb(p.SO);southwest=j.rgb(p.SW)
raw=np.concatenate([np.concatenate([west[3428:,-76:],base[3428:,:1178]],1),np.concatenate([southwest[:586,-76:],south[:586,:1178]],1)],0)
meta=a.load_json(N/'input.png.generation.json');assert j.raw(raw)==meta['rawSourceRGBSha256']
native,entry=j.valid_patch(N/'edited-native.png');assert raw.shape==native.shape==(1254,1254,3)
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
image=base.copy();box=[0,3912,627,4096];crop=native[484:668,76:703].copy()
j.insert(image,crop,box,48,'native-rail',rects=[box])
before=image.copy();h=184;w=627;above=image[-h:,:w].astype(np.float32);below=south[:12,:w].astype(np.float32)
def smooth(x,n=9):
 return np.stack([np.convolve(np.pad(x[:,c],(n//2,n//2),mode='edge'),np.ones(n)/n,mode='valid') for c in range(3)],1)
def warm(x):return np.clip((x[...,0]-x[...,2]+25)/70,0,1)
wa=warm(above);wb=warm(below);fields=[];support=[]
for k in (0,1):
 va=(wa[-7:]>.85) if k else (wa[-7:]<.15);vb=(wb>.85) if k else (wb<.15)
 good=(va.sum(0)>=4)&(vb.sum(0)>=7);delta=np.zeros((w,3),np.float32)
 for x in np.flatnonzero(good):delta[x]=np.median(below[:,x][vb[:,x]],axis=0)-np.median(above[-7:,x][va[:,x]],axis=0)
 assert good.any();xp=np.flatnonzero(good)
 for c in range(3):delta[:,c]=np.interp(np.arange(w),xp,delta[xp,c])
 fields.append(smooth(np.clip(delta,-80,80)));support.append(good)
yweight=np.clip((np.arange(h)-16)/(h-17),0,1);yweight=yweight*yweight*(3-2*yweight)
xweight=np.clip((w-1-np.arange(w))/44,0,1);xweight=xweight*xweight*(3-2*xweight)
field=(fields[0][None,:,:]*(1-wa[:,:,None])+fields[1][None,:,:]*wa[:,:,None])*yweight[:,None,None]*xweight[None,:,None]
# Preserve the reviewed west joint exactly at x=0, with a short continuous fade.
leftweight=np.clip(np.arange(w)/40,0,1);leftweight=leftweight*leftweight*(3-2*leftweight);field*=leftweight[None,:,None]
image[-h:,:w]=np.clip(np.rint(above+field),0,255).astype(np.uint8)
M.mkdir(parents=True,exist_ok=True);np.savez_compressed(M/'boundary-difference.npz',field_rgb=field.astype(np.float16),warm_support=support[1],blue_support=support[0])
assert np.array_equal(image[:,627:],base[:,627:]) and np.array_equal(image[:3912],base[:3912])
ex=j.rgb(B/'extended-context.png');ex[115:4211,115:4211]=image
out=a.save_image(D/'candidate.png',Image.fromarray(image));ei=a.save_image(D/'extended-context.png',Image.fromarray(ex))
a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south))
extras=[]
def save(name,arr,rect=None):extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(arr)),sourceRectXYXY=rect,resized=False,visualReview='pending'))
pair=np.concatenate([np.concatenate([west,image],1),np.concatenate([southwest[:512],south[:512]],1)],0)
save('four-way-corner',pair[3584:4608,3584:4608],[3584,3584,4608,4608])
save('south-rail-close',np.concatenate([image[-300:,:760],south[:200,:760]],0))
save('rail-east-insertion',image[3860:4096,435:820],[435,3860,820,4096])
save('rail-top-insertion',image[3850:4040,:790],[0,3850,790,4040])
for name,arr in [('west-common-full',np.concatenate([west[:,-128:],image[:,:128]],1)),('east-insertion-full',image[:,435:755])]:save(name,np.concatenate([arr[k*1024:(k+1)*1024] for k in range(4)],1))
for f,s in p.EXPECTED.items():assert a.sha(f)==s
old=a.load_json(B/'manifest.json')
a.save_json(D/'manifest.json',{**old,'createdAtUtc':a.utc_now(),'baseline':j.ref(S),'baselineManifest':j.ref(B/'manifest.json'),'candidate':out,'extendedContext':ei,'nativeRepairs':old['nativeRepairs']+[dict(entry,sourceROIValidated=True,inputRecord=j.ref(N/'input.png.generation.json'))],'priorInsertionQA':old['insertionQA'],'insertionQA':extras,'qa':qa,'finalRailRepairRectXYXY':box,'colorCorrection':dict(file=str(M/'boundary-difference.npz'),sha256=a.sha(M/'boundary-difference.npz'),maximumAbsoluteChannelDelta=float(np.abs(field).max()),maximumBound=80,method='Same-material adjacent edge median RGB differences; unsupported columns interpolated; nine-column smoothing of differences only; continuous warm confidence; cubic fades into upper tile; original west and x>=627 preserved.'),'railInsertions':j.INSERTIONS,'railSeams':j.SEAMS,'allColumnsFrom627ExactlyPreserved':True,'immutableNeighbors':True,'imageBlur':False,'shapeWarp':False,'visualReview':'pending'})
print(json.dumps(out))
