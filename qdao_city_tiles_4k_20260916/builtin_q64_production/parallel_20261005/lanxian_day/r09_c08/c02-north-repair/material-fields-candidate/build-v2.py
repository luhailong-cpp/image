from pathlib import Path
from PIL import Image
import hashlib,json,sys,numpy as np
from datetime import datetime,timezone
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day');T=ROOT/'r09_c08';R=T/'c02-north-repair';D=R/'material-fields-candidate'/'v2';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(z):
 z=np.clip(z,0,1);return z*z*(3-2*z)
src=R/'candidate-v4/candidate1254.png';a=np.array(Image.open(src).convert('RGB'));z=a.astype(np.float32);ctx=json.loads((T/'regional/context.json').read_text());npth=Path(ctx['northCore']['file']);n=Image.open(npth).convert('RGB');nt=np.array(n.crop((909,3981,2163,4096)))
assert np.array_equal(a[:115],nt)
up=np.median(nt[-2:].astype(np.float32),axis=0);lo=np.median(z[115:117],axis=0);diff=up-lo
Y,X=np.mgrid[:1254,:1254]
Rr,Gg,Bb=z[...,0],z[...,1],z[...,2]
orange=smooth((Rr-Bb-35)/35)*smooth((Gg-Bb-25)/30)*smooth((Rr-150)/50)
orange*=1-smooth((X-392)/25);orange*=((X<430)&(Y>=115)&(Y<300))
leaf=smooth((Gg-np.maximum(Rr,Bb)+5)/17)
leaf*=smooth((X-996)/12)*(1-smooth((X-1119)/20));leaf*=((X>=990)&(X<1139)&(Y>=115)&(Y<270))
leaf*=1-smooth((Y-175)/95)
orange*=1-smooth((Y-165)/135)
# Fit a robust source-relative seam field from actual true-north rows to actual south rows.
# Strong contour columns are excluded from fitting; field is filled across them.
def fit_field(alpha,lo_x,hi_x,limits,refchannel):
 boundary=alpha[115]
 grad=np.max(np.abs(np.gradient(up,axis=0)),axis=1)+np.max(np.abs(np.gradient(lo,axis=0)),axis=1)
 valid=(boundary>.65)&(np.arange(1254)>=lo_x)&(np.arange(1254)<hi_x)&(grad<22)
 if lo_x==140:
  valid &= np.max(np.abs(diff),axis=1)<=15
  valid[150:195]=False;valid[285:336]=False
 inds=np.flatnonzero(valid);assert len(inds)>20
 ratios=np.zeros((1254,3),np.float32)
 for c in range(3):
  ratio=diff[:,c]/np.maximum(lo[:,refchannel],32)
  values=np.interp(np.arange(1254),inds,ratio[inds]).astype(np.float32)
  values=cv2.medianBlur(values[None],5)[0]
  ratios[:,c]=values
 field=np.zeros_like(z)
 for yy in range(115,300):
  # Smooth the correction field only; never convolve image pixels.
  depth=yy-115;sigma=max(6,.35*depth) if lo_x==140 else max(2,.20*depth)
  row=cv2.GaussianBlur(ratios[None],(0,0),sigmaX=sigma,sigmaY=0)[0]
  field[yy]=np.clip(row*np.maximum(z[yy,:,refchannel,None],32),-np.array(limits),np.array(limits))*alpha[yy,:,None]
 return field,ratios,valid,diff[valid]
of,orat,oval,od=fit_field(orange,140,415,[12,16,16],1)
lf,lrat,lval,ld=fit_field(leaf,1008,1119,[20,24,16],1)
field=of+lf;f=np.rint(np.clip(z+field,0,255)).astype(np.uint8)
assert np.array_equal(f[:115],a[:115]);assert np.array_equal(f[400:],a[400:]);assert np.array_equal(f[:,1139:],a[:,1139:])
changed=np.any(f!=a,axis=-1);assert not np.any(changed&(orange==0)&(leaf==0));assert not np.any((orange>0)&(leaf>0))
Image.fromarray(f).save(D/'candidate1254.png')
for name,arr in [('orange-alpha',orange),('leaf-alpha',leaf),('changed-mask',changed.astype(float))]:Image.fromarray(np.rint(np.clip(arr,0,1)*255).astype(np.uint8)).save(D/(name+'.png'))
np.savez_compressed(D/'fields.npz',rgb_field=field,orange_rgb_field=of,leaf_rgb_field=lf,orange_alpha=orange,leaf_alpha=leaf,source_pixels=a,orange_valid_columns=oval,leaf_valid_columns=lval,orange_relative_reference=orat,leaf_relative_reference=lrat,reference_north_last2=nt[-2:],reference_south_first2=a[115:117])
j=Image.new('RGB',(1254,512));j.paste(n.crop((909,3840,2163,4096)),(0,0));j.paste(Image.fromarray(f).crop((0,115,1254,371)),(0,256));j.save(D/'north1254x512.png')
for name,box in [('orange',[0,216,430,356]),('leaves',[990,206,1254,346]),('stone-unchanged',[870,186,1010,386])]:j.crop(box).save(D/(name+'.png'))
stats=[]
for name,alpha,fi,limits,valid,deltas in [('orange',orange,of,[12,16,16],oval,od),('leaf',leaf,lf,[20,24,16],lval,ld)]:
 ys,xs=np.where(alpha>0);stats.append({'material':name,'alphaBoxXYXY':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'activePixels':int(np.sum(alpha>0)),'limit':limits,'actualFloatMin':fi.min(axis=(0,1)).tolist(),'actualFloatMax':fi.max(axis=(0,1)).tolist(),'validReferenceColumns':np.flatnonzero(valid).tolist(),'referenceDeltaQuantiles':np.quantile(deltas,[0,.1,.5,.9,1],axis=0).tolist()})
def ref(p,role):return {'file':str(p),'sha256':sha(p),'role':role}
m={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'operation':'Material-limited bounded RGB correction only, no geometry or AI invocation','status':'candidate_requires_actual_review_not_adopted','source':ref(src,'Exact candidate-v4 baseline; no write to original candidate'),'trueNorth':ref(npth,'Real north4096 original; last115 x909..2162 direct native crop'),'referenceRule':'median north last2 versus actual v4 south first2; contour columns excluded, 5column median on relative RGB deltas; field-only Gaussian horizontal smoothing orange sigma=max(6,.35*depth), leaf sigma=max(2,.20*depth); orange high-gloss contours150..194 and285..335 and reference |delta|>15 excluded; source green channel modulates local brightness','materials':stats,'alphaRule':'Smooth continuous material confidence, spatial ROI and depth fade; orange y165..300, leaf y175..270; leaf x996..1008 fade-in and1119..1139 fade-out preserve strict east','geometryChanged':False,'imageBlur':False,'unchangedNorthRows0To114':True,'unchangedRows400To1253':True,'unchangedEastColumns1139To1253':True,'stoneAndWoodModified':False,'mergeRule':'Apply recorded RGB delta only where future source pixel equals saved source_pixels at affected pixel; reject any changed-mask collision. Do not merge with newer geometry/source silently.','unhandledKnownRegions':['Dark brown inner tree/soil at x0..145 north boundary remains visibly different and is excluded from orange material mask.','Wood x430..870 and stone x870..1010 are untouched and handled independently.'],'technicalArtifacts':[ref(D/f,role) for f,role in [('orange-alpha.png','Selected candidate orange continuous alpha'),('leaf-alpha.png','Selected candidate leaf continuous alpha'),('changed-mask.png','Exact changed pixel support mask'),('fields.npz','Exact float RGB fields, alpha, fit columns and baseline pixels for collision-safe merge')]],'outputs':[ref(D/f,'QA or candidate image') for f in ['candidate1254.png','north1254x512.png','orange.png','leaves.png','stone-unchanged.png']],'formalAccepted':False}
(D/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(stats))
