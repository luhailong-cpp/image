from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/east-integrated';Q=D/'qa';M=D/'masks'
S=T/'repairs/north-integrated-v2/candidate.png';BASE='56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7'
E=R/'r10_c16/repairs/north-integrated-color-v3/candidate.png';ES='38f9ab047e8dccca8e49e2db392465f42d9447b5edcf4b2aa4d9432ea94304a4'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE and a.sha(E)==ES
base=j.rgb(S);east=j.rgb(E);image=base.copy();P=T/'repairs/east-guide-joint';patch,ev=j.valid_patch(P/'edited-native.png');meta=a.load_json(P/'input.png.generation.json')
raw=np.concatenate([base[2842:,3340:],east[2842:,:498]],axis=1)
assert j.raw(raw)==meta['rawSourceRGBSha256'] and np.array_equal(raw,j.rgb(P/'input.png'))
j.insert(image,patch[:,:756],[3340,2842,4096,4096],32,'east-guide',rects=[[3780,3300,4096,4096]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]) and np.array_equal(image[:3300],base[:3300])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/north-integrated-v2/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=image
exinfo=a.save_image(D/'extended-context.png',Image.fromarray(ex));mask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK))
a.QA=Q/'assembly';a.ART=D/'candidate.png';north,ni=a.checked_north();qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),north)
extras=[];pair=np.concatenate([image,east],axis=1)
for name,b in [('east-wall',[3600,2842,4500,4096]),('east-top',[3670,3150,4380,3520]),('east-left',[3670,3250,3920,4096]),('east-guide-detail',[3910,3450,4080,4096]),('east-join',[4000,3000,4192,4096])]:
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(pair,b))),sourceRectInEastPair=b,resized=False))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=exinfo,nativeRepair=ev,immutableEast=j.ref(E),sourceROIValidated=True,sourceRectXYXY=meta['sourceRectXYXY'],rawSourceRGBSha256=meta['rawSourceRGBSha256'],seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mask,qa=qa,insertionQA=extras,nativeSourcesUnchanged=True,imageResampling=False,imageBlur=False,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
