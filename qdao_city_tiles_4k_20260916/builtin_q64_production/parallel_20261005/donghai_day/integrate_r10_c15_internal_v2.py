from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/internal-integrated-v2';Q=D/'qa';M=D/'masks'
S=T/'repairs/color-match/candidate.png';BASE='a047f7b73c7890e6c0bf75e0d99c822508424e75ab091d12f1ca3814146003e5'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE
base=j.rgb(S);image=base.copy();P=T/'repairs/internal-wall';patch,ev=j.valid_patch(P/'edited-native.png');meta=a.load_json(P/'input.png.generation.json');box=meta['sourceRectXYXY']
assert j.raw(j.cut(base,box))==meta['rawSourceRGBSha256'] and np.array_equal(j.cut(base,box),j.rgb(P/'input.png'))
j.insert(image,patch,box,16,'wall-strip',rects=[[676,2940,1510,4096]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]) and np.array_equal(image[:700],base[:700])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/color-match/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=image
exinfo=a.save_image(D/'extended-context.png',Image.fromarray(ex));mask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK))
a.QA=Q/'assembly';a.ART=D/'candidate.png';north,ni=a.checked_north();qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),north)
extras=[]
for name,b in [('wall-full',[640,2890,1580,4096]),('wall-top',[650,2880,1570,3220]),('wall-bottom',[650,3870,1570,4096]),('wall-left',[650,2910,950,4096]),('wall-right',[1280,2910,1560,4096])]:
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(image,b))),sourceRectXYXY=b,resized=False))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=exinfo,nativeRepair=ev,sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256'],seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mask,qa=qa,insertionQA=extras,north700Unchanged=True,nativeSourcesUnchanged=True,imageResampling=False,imageBlur=False,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
