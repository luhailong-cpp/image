from pathlib import Path
import json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/integrated-southwest-v3';P=T/'repairs/south-west-joint-masked';B=T/'repairs/west-upper-three';S=B/'candidate.png';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa';SO=R/'r08_c16/output/r08_c16.png'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
assert a.sha(S)=='4104373b3faa477b95d4ec6b9df3cf29a25e49d8593d6def8ad60c123957830f';assert a.sha(SO)=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
base=j.rgb(S);south=j.rgb(SO);pair=np.concatenate([base,south],axis=0);meta=a.load_json(P/'input.png.generation.json');box=meta['sourceRectXYXY'];assert j.raw(j.cut(pair,box))==meta['rawUnmodifiedCropRGBSha256'];patch,e=j.valid_patch(P/'edited-native.png')
image=base.copy();j.insert(image,patch[:627],[443,3469,1697,4096],64,'south-mast-masked',rects=[[790,3910,1400,4096]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]);assert np.array_equal(image[:,1400:],base[:,1400:]);assert a.sha(SO)=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(B/'extended-context.png');ex[115:4211,115:4211]=image;ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south))
extras=[];pair=np.concatenate([image,south],axis=0)
for name,box in [('mast-joint',[700,3830,1460,4270]),('mast-top-insertion',[710,3810,1480,4110]),('mast-left-insertion',[710,3830,1020,4220]),('mast-right-insertion',[1260,3850,1490,4220]),('rope-spar-current',[1320,3469,2210,4096])]:extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(pair,box))),sourceRectXYXY=box,resized=False,visualReview='pending'))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),baselineManifest=j.ref(B/'manifest.json'),candidate=out,extendedContext=ei,nativeRepair=e,inputRecord=j.ref(P/'input.png.generation.json'),rawSourceROIValidated=True,immutableSouth=j.ref(SO),sourceRectInPairXYXY=meta['sourceRectXYXY'],intendedROI=[790,3910,1400,4096],maskHole=[853,3994,1328,4096],rightPaddingRationale='Extend insertion search to1400 so all reconstructed hole to1328 is included; all original rope/spar at x>=1400 retained exactly. Input uses prior reviewed spar repair and raw ROI was validated.',southOriginalPixelsCopied=False,seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK)),outsideInsertionExactlyPreserved=True,qa=qa,insertionQA=extras,westStatus='upper candidate source only; lower joint pending stable r07c15',formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
