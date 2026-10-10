from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/north-right-integrated';Q=D/'qa';M=D/'masks'
S=T/'repairs/east-integrated/candidate.png';BASE='e27d76d08c9725bdca0525b45faa8d6ee3f1c2388bfd29e99507559d2450897f'
N=R/'r09_c15/output/r09_c15.png';NS='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE and a.sha(N)==NS
base=j.rgb(S);north=j.rgb(N);image=base.copy();P=T/'repairs/north-right-joint';patch,ev=j.valid_patch(P/'edited-native.png');meta=a.load_json(P/'input.png.generation.json')
raw=np.concatenate([north[-627:,2842:],base[:627,2842:]],axis=0)
assert j.raw(raw)==meta['rawSourceRGBSha256'] and np.array_equal(raw,j.rgb(P/'input.png'))
j.insert(image,patch[627:],[2842,0,4096,627],32,'north-right',rects=[[3180,0,4096,627]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]) and np.array_equal(image[627:],base[627:])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/east-integrated/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=image
exinfo=a.save_image(D/'extended-context.png',Image.fromarray(ex));mask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK))
a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(north))
extras=[];pair=np.concatenate([north,image],axis=0)
for name,b in [('north-right-wide',[2842,3796,4096,4566]),('north-right-joint',[3100,3976,4096,4296])]:
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(pair,b))),sourceRectInNorthPair=b,resized=False))
for name,b in [('north-right-left-insertion',[3060,0,3350,727]),('north-right-bottom-insertion',[3100,490,4096,727])]:
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(image,b))),sourceRectXYXY=b,resized=False))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=exinfo,nativeRepair=ev,immutableNorth=j.ref(N),sourceROIValidated=True,sourceRectXYXY=meta['sourceRectXYXY'],rawSourceRGBSha256=meta['rawSourceRGBSha256'],seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mask,qa=qa,insertionQA=extras,y627AndBelowUnchanged=True,east627BelowY700RawRGBSha256=j.raw(image[700:,3469:]),nativeSourcesUnchanged=True,imageResampling=False,imageBlur=False,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q),east627BelowY700RawRGBSha256=j.raw(image[700:,3469:]))))
