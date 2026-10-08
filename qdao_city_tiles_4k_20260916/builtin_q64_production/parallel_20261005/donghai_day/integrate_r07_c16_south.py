from pathlib import Path
import sys,uuid,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import assembly_r07_c16 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/south-integrated';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa';S=T/'output/r07_c16.png';BASE='2dbf08054591651fb62f3477ef79926f2d7696f773eaf26b5f8f1b18d886a06a'
if '--anchor-only' in sys.argv:
 D=T/'repairs/south-anchor-only';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
if '--anchored-ai' in sys.argv:
 D=T/'repairs/south-anchored-ai';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
if '--thin' in sys.argv:
 D=T/'repairs/south-thin';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
if '--protect-wood' in sys.argv:
 D=T/'repairs/south-final';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
SO=R/'r08_c16/output/r08_c16.png';SS='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de';SX=R/'r08_c16/output/extended-context.png';XS='0055b578b51057e9c05d6ca050bd83d84c20aae92bc72cd47d424610b6e02689'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
assert a.sha(S)==BASE and a.sha(SO)==SS and a.sha(SX)==XS
base=j.rgb(S);south=j.rgb(SO);sx=j.rgb(SX);pair=np.concatenate([base,south],axis=0);P=T/'repairs/south-rope'
if '--anchored-ai' in sys.argv:P=T/'repairs/south-rope-anchored'
if '--thin' in sys.argv:P=T/'repairs/south-rope-thin'
patch,e=j.valid_patch(P/'edited-native.png');meta=a.load_json(P/'input.png.generation.json');expected=j.cut(pair,meta['sourceRectInPairXYXY']).copy()
if '--anchored-ai' in sys.argv:expected[512:627]=sx[:115,1365:2619]
assert j.raw(expected)==meta['rawSourceRGBSha256'] and np.array_equal(expected,j.rgb(P/'input.png'))
assert np.array_equal(sx[115:4211,115:4211],south)
anchor=sx[:115,1365:2619].copy();north=patch[:627].copy()
if '--anchor-only' in sys.argv:
 north=base[3469:4096,1250:2504].copy();e={'operation':'actual source-native top rows to authoritative neighboring north halo; generated repair discarded for this candidate','baselineSource':j.ref(S)}
joined=j.join([north,anchor],[0,512],'horizontal',1250,3469,'north-to-final-south-halo')
joined[-16:]=anchor[-16:]
eligibility=None;protection=None
if '--protect-wood' in sys.argv:
 poly=[(0,400),(204,267),(214,230),(260,181),(315,144),(355,150),(400,169),(449,208),(477,260),(474,308),(460,352),(420,386),(386,405),(358,420),(338,445),(295,471),(0,640)]
 protected=Image.new('L',(1254,627));ImageDraw.Draw(protected).polygon(poly,fill=255);protected=protected.filter(ImageFilter.MaxFilter(7));eligibility=255-np.asarray(protected)
 protection=dict(a.save_image(M/'original-wood-protection.png',protected),polygonLocalXY=poly,dilationPixels=3,purpose='Keep original occluding wood cap and diagonal spar pixels; only rope/water may change')
image=base.copy();j.insert(image,joined,[1250,3469,2504,4096],96,'south-rope',eligibility=eligibility,rects=meta['intendedRepairRectsXYXY'])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0])
assert a.sha(SO)==SS and a.sha(SX)==XS
out=a.save_image(D/'candidate.png',Image.fromarray(image));old=a.load_json(T/'output/assembly-manifest.json');ex=j.rgb(T/'output/extended-context.png');assert a.sha(T/'output/extended-context.png')==old['extendedContext']['sha256']
ex[115:4211,115:4211]=image;ex[4211:,115:4211]=south[:115]
ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));mask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK));a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south))
extras=[]
for name,box in [('rope-insertion',[1420,3469,2210,4096]),('rope-joint',[1480,3800,2200,4400])]:
 arr=image if name=='rope-insertion' else np.concatenate([image,south],axis=0)
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(arr,box))),sourceRectXYXY=box,resized=False,visualReview='pending'))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=ei,immutableSouth=j.ref(SO),immutableSouthExtended=j.ref(SX),nativeRepair=e,sourceROIValidated=True,originalWoodProtection=protection,anchor=dict(source=j.ref(SX),sourceRectXYXY=[1365,0,2619,115],targetR07RectXYXY=[1250,3981,2504,4096],actualCoreTransitionViewed=True,spatialResampling=False,rawRGBSha256=j.raw(anchor),last16RowsForcedExactBeforeInsertion=True),seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=mask,qa=qa,insertionQA=extras,sourceNativeFilesUnchanged=True,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
