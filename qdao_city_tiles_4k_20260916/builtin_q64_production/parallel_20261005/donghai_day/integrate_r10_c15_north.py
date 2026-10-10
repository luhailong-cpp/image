from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/north-integrated';Q=D/'qa';M=D/'masks'
S=T/'repairs/internal-integrated-v2/candidate.png';BASE='af95055c00efcb511e8a19e157fa8ec62d885eeaff0d98f83a5471139b1b1bfa'
N=R/'r09_c15/output/r09_c15.png';NS='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff';NX=N.parent/'extended-context.png';NXS='a1e579822cdc65b66be7549715388b7adb6b9feab17451c851a00fb5a8bd074f'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE and a.sha(N)==NS and a.sha(NX)==NXS
base=j.rgb(S);north=j.rgb(N);nex=j.rgb(NX);assert np.array_equal(nex[115:4211,115:4211],north)
initial=j.rgb(T/'output/r10_c15.png');assert np.array_equal(initial[:700],base[:700])
patches=[];sources=[]
for name,x0 in [('n2',896),('n3-narrow',2048)]:
 p=T/'repairs/north-joint'/name;arr,e=j.valid_patch(p/'edited-native.png');meta=a.load_json(p/'input.png.generation.json');box=meta['sourceRectXYXY'];assert box==[x0,-627,x0+1254,627]
 raw=np.concatenate([north[-627:,x0:x0+1254],initial[:627,x0:x0+1254]],axis=0)
 assert j.raw(raw)==meta['rawBeforeJointRGBSha256']
 for item in meta['sources']:assert a.sha(item['file'])==item['sha256']
 anchor=nex[4211:4326,x0+115:x0+1369].copy();repair=arr[627:].copy()
 joined=j.join([anchor,repair[64:]],[0,64],'horizontal',x0,0,name+'-to-real-north-halo')
 assert joined.shape==(627,1254,3) and np.array_equal(joined[:64],anchor[:64])
 patches.append(joined);e.update(sourceROIValidated=True,sourceRectXYXY=box,rawBeforeJointRGBSha256=meta['rawBeforeJointRGBSha256'],trueNorthSouthHaloSourceRect=[x0+115,4211,x0+1369,4326],exactNorthHaloFirstCoreRows=64);sources.append(e)
strip=j.join(patches,[0,1152],'vertical',896,0,'north-pair')
image=base.copy();j.insert(image,strip,[896,0,3302,627],80,'north-joint',rects=[[896,0,3302,627]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]) and np.array_equal(image[627:],base[627:])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/internal-integrated-v2/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=image;ex[:115,115:4211]=north[-115:]
ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));mask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK));a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(north))
extras=[];pair=np.concatenate([north,image],axis=0)
for name,b in [('north-left-insertion',[750,0,1110,707]),('north-middle-insertion',[1920,0,2250,707]),('north-right-insertion',[3090,0,3430,707]),('north-bottom-left',[800,450,2054,710]),('north-bottom-right',[2054,450,3308,710])]:
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(image,b))),sourceRectXYXY=b,resized=False))
for i,x in enumerate([0,1024,2048,2842],1):
 b=[x,3796,x+1254,4566];extras.append(dict(a.save_image(Q/f'north-wide-{i}.png',Image.fromarray(j.cut(pair,b))),sourceRectInNorthPair=b,resized=False))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=ei,nativeRepairs=sources,immutableNorth=j.ref(N),immutableNorthExtended=j.ref(NX),seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mask,qa=qa,insertionQA=extras,coreY627AndBelowUnchanged=True,nativeSourcesUnchanged=True,imageResampling=False,imageBlur=False,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
