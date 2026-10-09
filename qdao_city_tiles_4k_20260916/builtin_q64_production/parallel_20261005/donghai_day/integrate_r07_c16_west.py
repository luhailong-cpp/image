from pathlib import Path
import sys,json,uuid
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
R=Path(__file__).resolve().parent;T=R/'r07_c16';P=T/'repairs/west-only-joint';D=T/'repairs/west-upper-integrated';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa';S=T/'repairs/integrated-south-v2/candidate.png'
if '--three' in sys.argv:D=T/'repairs/west-upper-three';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);Q=D/'qa'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image;j.M=M;j.Q=Q;j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json;j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
bind=a.load_json(P/'source-bindings.json');W=Path(bind['westFile']);assert a.sha(W)==bind['westSha256'];assert a.sha(S)=='3f5be4ea2f6cb9e54121761646fc0b0c218af12738fa7493c198a1f4b9944bc2'
west=j.rgb(W);base=j.rgb(S);pair=np.concatenate([west,base],axis=1);patches=[];entries=[]
starts=[0,1024,1982] if '--three' in sys.argv else [0,1024]
for i in range(1,len(starts)+1):
 arr,e=j.valid_patch(P/f's{i}.png');meta=a.load_json(P/f's{i}-input.png.generation.json');box=meta['sourceRectInPairXYXY'];rawcrop=j.cut(pair,box).copy();assert j.raw(rawcrop)==meta['rawSourceRGBSha256']
 guide=rawcrop.copy()
 if i>1:
  ov=starts[i-2]+1254-starts[i-1];guide[:ov,627:]=patches[-1][-ov:,627:]
 assert np.array_equal(guide,j.rgb(P/f's{i}-input.png'));patches.append(arr);e.update(rawSourceROIValidated=True,inputRecord=j.ref(P/f's{i}-input.png.generation.json'));entries.append(e)
strip=j.join([patches[0][:1090,627:]]+[p[:,627:] for p in patches[1:]],starts,'horizontal',0,0,'upper-west-joint');end=starts[-1]+1254
image=base.copy();j.insert(image,strip,[0,0,627,end],128,'upper-west-only',rects=[[0,0,627,end]])
assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0]);assert a.sha(W)==bind['westSha256']
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=j.rgb(T/'repairs/integrated-south-v2/extended-context.png');ex[115:4211,115:4211]=image;ex[115:4211,:115]=west[:,-115:];ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));a.QA=Q/'assembly';a.ART=D/'candidate.png';south=Image.open(R/'r08_c16/output/r08_c16.png').convert('RGB');qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),south)
def band(arr,orient):
 if orient=='vertical':
  out=Image.new('RGB',(arr.shape[1]*4,1024))
  for k in range(4):out.paste(Image.fromarray(arr[k*1024:(k+1)*1024]),(k*arr.shape[1],0))
  return out
extras=[]
for name,arr,box in [('west-common-full',np.concatenate([west[:,-128:],image[:,:128]],axis=1),None),('east-insertion-full',image[:,435:755],[435,0,755,4096])]:extras.append(dict(a.save_image(Q/(name+'.png'),band(arr,'vertical')),sourceRectXYXY=box,resized=False,visualReview='pending'))
for name,box in [('upper-left-join',[3968,250,4396,900]),('timber-underside',[3968,930,4396,1310]),('upper-overlap',[4096,950,4723,1350]),('post-waterline',[3968,1580,4723,2160]),('bottom-insertion',[0,end-258,790,min(4096,end+132)])]:
 arr=image if name=='bottom-insertion' else np.concatenate([west,image],axis=1);extras.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(j.cut(arr,box))),sourceRectXYXY=box,resized=False,visualReview='pending'))
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(S),candidate=out,extendedContext=ei,west=j.ref(W),westStatus=bind['westStatus'],formalWestBound=False,immutableWest=True,finalSourceROIValidationStillRequired=True,nativeRepairs=entries,sourceNativeCropsXYXY=[[627,0,1254,1090]]+[[627,0,1254,1254] for p in patches[1:]],joinOverlapPixels=[66]+[starts[k-1]+1254-starts[k] for k in range(2,len(starts))],reasonForNarrowerFirstOverlap='Use s2 corrected underside at global y1100, keeping native s1 above and s2 below without resampling.',seams=j.SEAMS,insertions=j.INSERTIONS,unionMask=a.save_image(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK)),outsideInsertionExactlyPreserved=True,southExactlyPreserved=bool(np.array_equal(image[3300:],base[3300:])),qa=qa,insertionQA=extras,formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(candidate=out,qa=str(Q))))
