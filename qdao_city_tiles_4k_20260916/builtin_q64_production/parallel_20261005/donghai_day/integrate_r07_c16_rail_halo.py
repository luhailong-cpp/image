"""Native rail stitch into the exact lower neighbor's existing upper halo."""
from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
import repair_r07_c16_rail_edge as p
R=p.R;T=p.T;B=T/'repairs/final-west-joint';D=T/'repairs/final-rail-v2';Q=D/'qa';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);N=p.D/'halo-stitch';S=B/'candidate.png'
for f,s in p.EXPECTED.items():assert a.sha(f)==s
base=j.rgb(S);prepared=j.rgb(N/'prepared-upper-candidate.png');west=j.rgb(p.W);south=j.rgb(p.SO);southwest=j.rgb(p.SW)
raw=j.rgb(N/'original-crop.png');meta=a.load_json(N/'input.png.generation.json');assert j.raw(raw)==meta['rawSourceRGBSha256'];assert np.array_equal(raw[:668,76:],prepared[3428:,:1178])
assert np.array_equal(prepared[:,780:],base[:,780:]) and np.array_equal(prepared[:3981],base[:3981])
native,entry=j.valid_patch(N/'edited-native.png')
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
image=prepared.copy();box=[0,3928,780,4090];j.insert(image,native[500:662,76:856],box,24,'native-rail-halo-stitch',rects=[box])
assert np.array_equal(image[:,780:],base[:,780:]) and np.array_equal(image[:3928],base[:3928])
ex=j.rgb(B/'extended-context.png');ex[115:4211,115:4211]=image
out=a.save_image(D/'candidate.png',Image.fromarray(image));ei=a.save_image(D/'extended-context.png',Image.fromarray(ex))
a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south));extras=[]
def save(name,arr,rect=None):extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(arr)),sourceRectXYXY=rect,resized=False,visualReview='pending'))
pair=np.concatenate([np.concatenate([west,image],1),np.concatenate([southwest[:512],south[:512]],1)],0)
save('four-way-corner',pair[3584:4608,3584:4608],[3584,3584,4608,4608])
save('south-rail-close',np.concatenate([image[-300:,:930],south[:200,:930]],0))
save('rail-east-insertion',image[3860:4096,435:950],[435,3860,950,4096])
save('rail-top-insertion',image[3850:4096,:900],[0,3850,900,4096])
for name,arr in [('west-common-full',np.concatenate([west[:,-128:],image[:,:128]],1)),('east-insertion-full',image[:,435:820])]:save(name,np.concatenate([arr[k*1024:(k+1)*1024] for k in range(4)],1))
for f,s in p.EXPECTED.items():assert a.sha(f)==s
old=a.load_json(B/'manifest.json');diff=np.any(base!=image,axis=2);ys,xs=np.where(diff)
a.save_json(D/'manifest.json',{**old,'createdAtUtc':a.utc_now(),'baseline':j.ref(S),'baselineManifest':j.ref(B/'manifest.json'),'candidate':out,'extendedContext':ei,'nativeRepairs':old['nativeRepairs']+[dict(entry,sourceROIValidated=True,inputRecord=j.ref(N/'input.png.generation.json'))],'priorInsertionQA':old['insertionQA'],'insertionQA':extras,'qa':qa,'finalRailRepairRectXYXY':box,'haloSelection':dict(preparedCandidate=j.ref(N/'prepared-upper-candidate.png'),source=j.ref(p.SO.parent/'extended-context.png'),sourceRectXYXY=[115,0,895,115],sameCoordinatePlacementCoreXYXY=[0,3981,780,4096],recipe=j.ref(R/'probe_r07_c16_rail_halo.py'),fields=j.ref(p.D/'south-boundary/halo-DP-probe-fields.npz')),'actualChangedRectXYXY':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'railInsertions':j.INSERTIONS,'railSeams':j.SEAMS,'allColumnsFrom627ExactlyPreserved':False,'allColumnsFrom780ExactlyPreserved':True,'immutableNeighbors':True,'imageBlur':False,'shapeWarp':False,'visualReview':'pending'})
print(json.dumps(out))
