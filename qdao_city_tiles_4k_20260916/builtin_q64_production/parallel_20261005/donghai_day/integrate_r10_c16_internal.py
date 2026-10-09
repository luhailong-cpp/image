from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
import integrate_c15_repairs as j
R=a.ROOT;T=a.TILE;B=T/'repairs/internal-color-match';N=T/'repairs/internal-bucket';D=T/'repairs/internal-final';Q=D/'qa';M=D/'masks'/('run-'+uuid.uuid4().hex[:8])
assert a.sha(a.ART)=='76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7'
assert a.sha(B/'candidate.png')=='83bda970e93c68ad09a5eb6fe76b432b3fc343b16e0515bda0659261608ca0f4'
base=j.rgb(B/'candidate.png');raw=j.rgb(a.ART);arr,e=j.valid_patch(N/'edited-native.png');meta=a.load_json(N/'input.png.generation.json');box=meta['sourceRectXYXY'];assert j.raw(j.cut(base,box))==meta['rawSourceRGBSha256']
eligible=np.asarray(Image.open(N/'water-only-eligibility.png').convert('L'));assert a.sha(N/'water-only-eligibility.png')==meta['eligibility']['sha256']
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
im=base.copy();j.insert(im,arr,box,24,'bucket-water',eligible,[[1020,704,1390,1055]])
assert np.array_equal(im[:700],raw[:700]);assert np.array_equal(im[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0])
ext=j.rgb(B/'extended-context.png');origex=j.rgb(a.OUT/'extended-context.png');ext[115:4211,115:4211]=im
halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False;assert np.array_equal(ext[halo],origex[halo])
out=a.save_image(D/'candidate.png',Image.fromarray(im));ex=a.save_image(D/'extended-context.png',Image.fromarray(ext));a.QA=Q;a.ART=D/'candidate.png';north,ni=a.checked_north();qa=a.write_qa(Image.fromarray(im),Image.fromarray(ext),north)
extra=a.save_image(Q/'bucket-native-detail.png',Image.fromarray(j.cut(im,box)))
diff=im.astype(np.int16)-raw.astype(np.int16);fp=D/'fields/final-correction.npz';fp.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(fp,correction_rgb_i16=diff,changed_mask_u8=np.any(diff!=0,axis=2).astype(np.uint8))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),candidate=out,extendedContext=ex,baseline=dict(file=str(T/'output/r10_c16.png'),sha256='76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7'),colorCandidate=j.ref(B/'candidate.png'),colorManifest=j.ref(B/'manifest.json'),nativeRepair=dict(e,inputRecord=j.ref(N/'input.png.generation.json'),rawSourceROIValidated=True,eligible=j.ref(N/'water-only-eligibility.png')),insertions=j.INSERTIONS,seams=j.SEAMS,bucketAlpha=j.ref(M/'bucket-water-insertion-alpha.png'),finalCorrection=j.ref(fp),northCore700ExactlyPreserved=True,allHaloExactlyPreserved=True,northCorrection=False,canonicalOutputUnchanged=True,imageBlur=False,geometryWarp=False,resampling=False,qa=qa,extraQA=[extra],visualReview='pending-internal-scope-only',formalAccepted=False))
print(json.dumps(out))
