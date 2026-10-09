"""Build reviewed straight-timber candidate; immutable historical candidates remain sources."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import integrate_r07_c15 as i
sys.path.insert(0,str(i.D/'python-deps'))
import cv2
a=i.a; D=i.D; F=D/'south-straight'; O=D/'straight-integrated'
BASE=D/'refined/candidate.png'; EXPECTED='965caba9070b2a41daa9b2c2b1e5ec1d292bfa3970965fe89d4f6ebb2ace3a40'

def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)

def material(p):
 p=p.astype(np.float32); warm=smooth((p[:,:,0]-p[:,:,2]+12)/52)
 return np.stack([warm,1-warm],axis=2)

def edge_color(p,raw,halo,label):
 """Sample corresponding materials in known halo; filter only RGB differences."""
 h,w=p.shape[:2];mp=material(raw[926:956]);mh=material(halo[85:115]);delta=halo[85:115].astype(np.float32)-raw[926:956].astype(np.float32)
 fields=[];samples=[];xx=np.arange(w)
 for k in range(2):
  wt=mp[:,:,k]*mh[:,:,k];den=wt.sum(axis=0);num=(delta*wt[:,:,None]).sum(axis=0)
  valid=den>12;v=np.zeros((w,3),np.float32)
  if np.any(valid):
   for c in range(3):v[:,c]=np.interp(xx,xx[valid],num[valid,c]/den[valid])
  v=cv2.GaussianBlur(v[None],(9,1),0)[0];fields.append(np.clip(v,-24,24));samples.append(int(valid.sum()))
 weights=material(raw[:h]);field=sum(weights[:,:,k,None]*fields[k][None] for k in range(2))
 fade=smooth((np.arange(h)-776)/180)[:,None,None];field*=fade
 corrected=np.clip(np.rint(p.astype(np.float32)+field),0,255).astype(np.uint8)
 # Exact known boundary with a short, geometry-aligned transition; never alter south.
 z=smooth(np.linspace(0,1,16,dtype=np.float32))[:,None,None]
 corrected[940:956]=np.rint(corrected[940:956]*(1-z)+halo[99:115]*z).astype(np.uint8)
 a.save_image(O/'sources'/f'{label}-upper.png',Image.fromarray(corrected))
 fp=a.writable(O/'fields'/f'{label}-boundary-color.npz');np.savez_compressed(fp,delta_rgb_f16=field.astype(np.float16),material_column_delta=np.stack(fields),fade_f16=fade.astype(np.float16))
 return corrected,{'id':label,'field':i.ref(fp),'capPerChannel':24,'fadeRowsLocal':[776,956],'sampleRowsLocal':[926,956],'horizontalDifferenceSmoothing':9,'continuousMaterialWeights':True,'validColumnCounts':samples,'artBlur':False,'haloTransitionRows':[940,956]}

def panel(im):
 p,m=i.valid_patch(i.T/'repairs/panel-notch-ai','panel-notch-native')
 b=[430,2970,790,3160];old=i.cut(im,b).copy();new=p[b[1]-2600:b[3]-2600,b[0]:b[2]].copy()
 x=np.arange(b[0],b[2])[None,:];y=np.arange(b[1],b[3])[:,None]
 line=3039+0.35*(x-575)
 ax=smooth((x-430)/120)*smooth((790-x)/120)
 ay=smooth((52-np.abs(y-line))/25)
 alpha=ax*ay
 im[b[1]:b[3],b[0]:b[2]]=np.rint(old*(1-alpha[:,:,None])+new*alpha[:,:,None]).astype(np.uint8)
 fp=a.writable(O/'fields/panel-contour-alpha.npz');np.savez_compressed(fp,alpha_f16=alpha.astype(np.float16),rect_xyxy=b)
 return {'source':i.ref(i.T/'repairs/panel-notch-ai/edited-native.png'),'rect':b,'alpha':i.ref(fp),'method':'Existing native contour with 120px continuous x transition and 25px y feather; no spatial resampling','sourceRecord':i.ref(i.T/'repairs/panel-notch-ai/edited-native.png.generation.json')}

def main():
 assert a.sha(BASE)==EXPECTED and a.sha(i.SOUTH)==i.SOUTH_SHA and a.sha(i.SEX)==i.SEX_SHA
 i.M=O/'masks';i.Q=O/'qa';i.SEAMS.clear();i.INSERTIONS.clear();i.SOURCES.clear();i.GLOBAL[:]=0
 im=i.rgb(BASE);before=im.copy();sex=i.rgb(i.SEX);south=i.rgb(i.SOUTH)
 sourceinfo=[];patches=[];color=[]
 for n,x in [('s2',1024),('s3',2048),('s4-clean-cloth',2842)]:
  native,meta=i.valid_patch(F/n,n)
  if n=='s2':up=i.rgb(F/n/'halo-upper-probe.png');raw=native
  elif n=='s3':
   up=i.rgb(F/n/'affine-final-upper.png')
   with np.load(F/n/'affine-final-map.npz') as z:
    keys=list(z.keys());mx=z['mx'] if 'mx' in keys else z[keys[0]];my=z['my'] if 'my' in keys else z[keys[1]]
   raw=cv2.remap(native,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
  else:up=i.rgb(F/n/'native-final-upper.png');raw=native
  assert up.shape==(956,1254,3)
  if n!='s2':up,cm=edge_color(up,raw,sex[:115,115+x:115+x+1254],n);color.append(cm)
  patches.append(up[230:956])
  sourceinfo.append({'id':n,'native':i.ref(F/n/'edited-native.png'),'inputMeta':i.ref(F/n/'input.png.generation.json')})
 joined=i.join(patches,[0,1024,1818],3370,'straight-south')
 joined[-1]=sex[114,1139:4211]
 i.insert(im,joined,[1024,3370,4096,4096],110,'straight-south',boundary_full=('right','bottom'))
 im[-1,1024:]=sex[114,1139:4211]
 pi=panel(im)
 assert np.array_equal(im[:3236,3469:],before[:3236,3469:])
 assert np.array_equal(im[-1],sex[114,115:4211])
 ex=i.rgb(D/'refined/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],before)
 ex[115:4211,115:4211]=im
 ci=a.save_image(O/'candidate.png',Image.fromarray(im));ei=a.save_image(O/'extended-context.png',Image.fromarray(ex))
 a.ART=O/'candidate.png';a.QA=O/'qa/assembly';qa=a.write_qa(Image.fromarray(im),Image.fromarray(ex),Image.fromarray(south));extras=i.extra_qa(im,south)
 for j,x in enumerate([0,1024,2048,2842],1):
  p=np.concatenate([im[3370:4096,x:x+1254],south[:200,x:x+1254]],axis=0);a.save_image(O/f'qa/full-south-{j}.png',Image.fromarray(p))
 a.save_image(O/'qa/panel-contour-detail.png',Image.fromarray(im[2970:3160,430:790]));a.save_image(O/'qa/panel-context.png',Image.fromarray(im[2870:3260,250:1000]))
 for tag,b in [('south-top',[1024,3270,4096,3470]),('south-left',[924,3370,1224,4096])]:a.save_image(O/f'qa/{tag}.png',Image.fromarray(i.cut(im,b)))
 proofs=[]
 for f in sorted((O/'qa/assembly').glob('*.png')):
  old=D/'refined/qa/assembly'/f.name
  if old.exists() and a.sha(old)==a.sha(f):proofs.append({'name':f.name,'sha256':a.sha(f),'sameAsRefined':True})
 a.save_json(O/'manifest.json',{'createdAtUtc':a.utc_now(),'input':i.ref(BASE),'inputManifest':i.ref(D/'refined/manifest.json'),'candidate':ci,'extendedContext':ei,'south':i.ref(i.SOUTH),'southExtended':i.ref(i.SEX),'nativeSources':i.SOURCES,'sourceInfo':sourceinfo,'boundaryColor':color,'seams':i.SEAMS,'insertions':i.INSERTIONS,'panel':pi,'eastUpperPixelProof':{'rect':[3469,0,4096,3236],'baselineSha256':EXPECTED,'RGBSha256':i.raw(im[:3236,3469:]),'equal':True},'unchangedQA':proofs,'southUnchanged':True,'lastRowExactAuthoritativeHalo':True,'imageBlur':False,'spatialRegistration':'S3 single horizontal affine scale 1.00990099009901 offset -16.584158415841614; map recorded; S4 final native AI geometry','registrationRecord':i.ref(F/'s3/affine-final-record.json'),'registrationMap':i.ref(F/'s3/affine-final-map.npz'),'s4AnchorRecord':i.ref(F/'s4-clean-cloth/native-final-record.json'),'qa':qa,'insertionQA':extras,'script':i.ref(__file__),'visualReview':'pending','formalAccepted':False})
 a.save_json(D/'refined/root-rejection.json',{'candidateSha256':EXPECTED,'passed':False,'reviewer':'root','receivedFromParent':True,'findings':['S1 barrel and dark wall continuous.','S2 x1650..1780 y4000..4080 board ends soft or doubled.','S3 main beam right edge and wood grain visibly wavy from nonlinear registration.','S4 canopy frame formed a large S-shaped dogleg and attached to the gray rope anchor instead of remaining straight behind the main beam.'],'resolutionCandidate':str(O/'candidate.png')})
 print(json.dumps({'candidate':ci,'unchangedQACount':len(proofs),'eastUpperUnchanged':True}))
if __name__=='__main__':main()
