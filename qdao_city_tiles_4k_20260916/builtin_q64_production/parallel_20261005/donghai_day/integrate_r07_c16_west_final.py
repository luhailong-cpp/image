"""Integrate four native west joints only after final c15 source identity checks."""
from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j

R=Path(__file__).resolve().parent;T=R/'r07_c16';P=T/'repairs/west-only-joint'
D=T/'repairs/final-west-joint';B=T/'repairs/south-joint-color-v4';S=B/'candidate.png'
E=T/'repairs/integrated-south-v2/candidate.png';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
SO=R/'r08_c16/output/r08_c16.png';SW=R/'r08_c15/output/r08_c15.png'
EXPECTED={S:'098911dc49894dc80236dea0f8617660be97f1f1c0f1e17097b73cec718af6aa',E:'3f5be4ea2f6cb9e54121761646fc0b0c218af12738fa7493c198a1f4b9944bc2',SO:'3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de',SW:'70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'}
for p,s in EXPECTED.items():assert a.sha(p)==s
bind=a.load_json(P/'source-bindings.json');assert bind['westStatus']=='stable-reviewed-source' and bind['formalWestBound'] is True
W=Path(bind['westFile']);assert W.name=='r07_c15.png' and a.sha(W)==bind['westSha256']
pn=a.load_json(T/'plan.json')['neighbors']['west'];assert pn['bindingStatus']=='bound' and pn['sha256']==a.sha(W)
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
west=j.rgb(W);base=j.rgb(S);east_input=j.rgb(E);south=j.rgb(SO);southwest=j.rgb(SW)
assert np.array_equal(base[:,:627],j.rgb(T/'repairs/west-upper-three/candidate.png')[:,:627])
pair=np.concatenate([west,east_input],axis=1)
pair=np.concatenate([pair,np.concatenate([southwest[:118],south[:118]],axis=1)],axis=0)
starts=[0,1024,1982,2960];patches=[];entries=[]
for i,start in enumerate(starts,1):
 pf=P/'final-source' if i==4 and (P/'final-source/s4.png').exists() else P
 arr,e=j.valid_patch(pf/f's{i}.png');meta=a.load_json(pf/f's{i}-input.png.generation.json');box=meta['sourceRectInPairXYXY']
 assert box==[3469,start,4723,start+1254]
 rawcrop=j.cut(pair,box).copy();assert j.raw(rawcrop)==meta['rawSourceRGBSha256'],f'Final western source ROI changed for s{i}; do not consume stale native patch.'
 guide=rawcrop.copy()
 if i>1:
  overlap=starts[i-2]+1254-start;guide[:overlap,627:]=patches[-1][-overlap:,627:]
 assert np.array_equal(guide,j.rgb(pf/f's{i}-input.png'))
 patches.append(arr);e.update(rawSourceROIValidatedAgainstFinalNeighbor=True,inputRecord=j.ref(pf/f's{i}-input.png.generation.json'),finalNeighbor=j.ref(W),sourceRectInPairXYXY=box);entries.append(e)
strip=j.join([patches[0][:1090,627:],patches[1][:,627:],patches[2][:,627:],patches[3][:1136,627:]],starts,'horizontal',0,0,'final-west-joint')
assert strip.shape==(4096,627,3)
image=base.copy();j.insert(image,strip,[0,0,627,4096],128,'final-west-only',rects=[[0,0,627,4096]])
assert np.array_equal(image[:,627:],base[:,627:])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(B/'extended-context.png');ex[115:4211,115:4211]=image
wx=W.parent/'extended-context.png';wex=j.rgb(wx);assert np.array_equal(wex[115:4211,115:4211],west)
ex[:,:115]=wex[:,4096:4211]
ex[4211:,:115]=southwest[:115,-115:]
assert np.array_equal(ex[4211:,115:4211],south[:115])
ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south))
def band(arr):
 result=Image.new('RGB',(arr.shape[1]*4,1024))
 for k in range(4):result.paste(Image.fromarray(arr[k*1024:(k+1)*1024]),(k*arr.shape[1],0))
 return result
extras=[]
for name,arr,box in [('west-common-full',np.concatenate([west[:,-128:],image[:,:128]],axis=1),None),('east-insertion-full',image[:,435:755],[435,0,755,4096])]:extras.append(dict(a.save_image(Q/(name+'.png'),band(arr)),sourceRectXYXY=box,resized=False,visualReview='pending'))
finalpair=np.concatenate([np.concatenate([west,image],axis=1),np.concatenate([southwest[:512],south[:512]],axis=1)],axis=0)
for name,box in [('upper-left-join',[3968,250,4396,900]),('timber-underside',[3968,930,4396,1310]),('upper-overlap',[4096,950,4723,1350]),('post-waterline',[3968,1580,4723,2160]),('lower-overlap',[3968,2800,4886,3300]),('four-way-corner',[3584,3584,4608,4608]),('west-bottom-insertion',[435,3584,850,4096])]:
 arr=image if name=='west-bottom-insertion' else finalpair
 extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(arr,box))),sourceRectXYXY=box,resized=False,visualReview='pending'))
for p,s in EXPECTED.items():assert a.sha(p)==s
assert a.sha(W)==bind['westSha256']
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),baselineManifest=j.ref(B/'manifest.json'),candidate=out,extendedContext=ei,west=j.ref(W),westExtended=j.ref(wx),south=j.ref(SO),southwest=j.ref(SW),formalWestBound=True,immutableNeighbors=True,nativeRepairs=entries,finalNeighborRawROIValidation=True,nativeRightCropsXYXY=[[627,0,1254,1090],[627,0,1254,1254],[627,0,1254,1254],[627,0,1254,1136]],joinOverlapPixels=[66,296,276],s4ActualLowerContextRows=[1136,1254],s4LowerNeighborArtInserted=False,seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK)),outsideInsertionExactlyPreserved=True,allColumnsFrom627ExactlyPreserved=True,resampling=False,imageBlur=False,shapeWarp=False,qa=qa,insertionQA=extras,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
