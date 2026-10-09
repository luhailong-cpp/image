"""Preserve native north geometry and correct only local RGB differences."""
from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
import integrate_c15_repairs as j
R=a.ROOT;T=a.TILE;B=T/'repairs/internal-final-v2';P=T/'repairs/north-joint';V=T/'repairs/north-integrated';D=T/'repairs/north-integrated-color-v3';F=D/'fields';Q=D/'qa'
EXPECTED='89d337e9fcaf92c366413cb9c6fc809467be4bd145dbbf239c071af58d96ca45'
assert a.sha(V/'candidate.png')==EXPECTED
meta=a.load_json(V/'manifest.json');base=j.rgb(B/'candidate.png');original=j.rgb(V/'candidate.png');north,ni=a.checked_north();n=np.asarray(north);ep=R/'r09_c16/output/extended-context.png';ne=j.rgb(ep);ns=a.sha(ep)
F.mkdir(parents=True,exist_ok=True)
def smooth(v,n=17,passes=3):
 for _ in range(passes):
  for axis in (0,1):
   pads=[(0,0)]*v.ndim;pads[axis]=(n//2,n//2);p=np.pad(v,pads,mode='reflect');c=np.cumsum(p,axis=axis,dtype=np.float64);c=np.concatenate([np.take(c,[0],axis=axis)*0,c],axis=axis)
   v=(c[n:]-c[:-n])/n if axis==0 else (c[:,n:]-c[:,:-n])/n
 return v.astype(np.float32)
def category(x):
 f=x.astype(np.float32);return np.where((f[...,2]>f[...,0]+15)&(f[...,1]>f[...,0]+5),1,np.where((f[...,0]>f[...,2]+15)&(f[...,0]>f[...,1]+4),2,0))
def field(before,new):
 delta=before.astype(np.float32)-new.astype(np.float32);valid=((category(before)==category(new))&(np.max(np.abs(delta),axis=2)<64)).astype(np.float32)
 den=smooth(valid);v=smooth(delta*valid[:,:,None])/np.maximum(den[:,:,None],.001)
 return np.clip(v,-32,32)
def apply(before,new,alpha,label,linear=False):
 raw=a.blend(before,new,np.rint(alpha*255).astype(np.uint8));f=field(before,new)
 if linear:soft=np.linspace(0,1,alpha.shape[0],dtype=np.float32)[:,None]
 else:
  soft=smooth(alpha,33,2)
  xx=np.minimum(np.arange(alpha.shape[1]),np.arange(alpha.shape[1])[::-1]);yy=np.arange(alpha.shape[0])[::-1]
  ramp=np.minimum(np.clip(xx[None,:]/160,0,1),np.clip(yy[:,None]/160,0,1));ramp=ramp*ramp*(3-2*ramp)
  rf=raw.astype(np.float32);blue=np.clip((rf[:,:,2]-rf[:,:,0]-10)/25,0,1)*np.clip((rf[:,:,1]-rf[:,:,0])/20,0,1)
  soft=soft*(1-blue)+ramp*blue
 corr=(alpha-soft)[:,:,None]*f
 # Fixed patch outer border prevents a newly created rectangular edge.
 gate=np.ones(alpha.shape,np.float32)
 if not linear:
  xx=np.minimum(np.arange(alpha.shape[1]),np.arange(alpha.shape[1])[::-1]);yy=np.arange(alpha.shape[0])[::-1]
  gate*=np.clip(xx[None,:]/20,0,1);gate*=np.clip(yy[:,None]/20,0,1)
 corr*=gate[:,:,None]
 out=np.clip(np.rint(raw.astype(np.float32)+corr),0,255).astype(np.uint8)
 np.savez_compressed(F/(label+'.npz'),field_rgb_f16=f.astype(np.float16),correction_rgb_f16=corr.astype(np.float16),original_alpha_f16=alpha.astype(np.float16),smooth_alpha_f16=np.asarray(soft,dtype=np.float16))
 return raw,out
raw_all=base.copy();image=base.copy();operations=[]
# Root-authorized completion of the original top-row internal difference fields.
authorization=a.load_json(T/'repairs/north-color-scope-authorization.json')
assert authorization['coreRowsAllowed']==[0,800] and authorization['approvedBy']=='root'
prefix=np.zeros((800,4096,3),np.int16);weight=np.ones(800,np.float32)
fade=np.linspace(0,1,101,dtype=np.float32);fade=fade*fade*(3-2*fade);weight[700:800]=1-fade[:100]
prefix_sources=[]
for left in (1,2,3):
 fp=T/'repairs/internal-color-match-v2/fields'/f'vertical_r01_c{left:02d}_c{left+1:02d}.npz'
 with np.load(fp) as saved:
  rect=saved['rect_extended_xywh'];x=int(rect[0])-115;corr=saved['correction_rgb_i16'][115:915]
 prefix[:,x:x+230]=np.rint(corr.astype(np.float32)*weight[:,None,None]).astype(np.int16)
 prefix_sources.append(j.ref(fp))
image[:800]=np.clip(image[:800].astype(np.int16)+prefix,0,255).astype(np.uint8)
np.savez_compressed(F/'prefix-internal-field.npz',correction_rgb_i16=prefix,weight_f16=weight.astype(np.float16))
for name in ('n2','n3'):
 path=P/name;patch,rec=j.valid_patch(path/'edited-native.png');m=a.load_json(path/'input.png.generation.json');x=m['sourceRectXYXY'][0];p=patch[627:].copy();truth=ne[4211:4326,x+115:x+1369];assert np.array_equal(truth,j.rgb(path/'composition-reference.png')[627:742])
 am=np.asarray(Image.open(V/'masks'/(name+'-true-halo.png')),dtype=np.float32)/255
 hraw,hcolor=apply(truth[50:115],p[50:115],am,name+'-halo',True)
 p[:50]=truth[:50];pc=p.copy();p[50:115]=hraw;pc[50:115]=hcolor
 alpha=np.asarray(Image.open(V/'masks'/(name+'-insertion-alpha.png')),dtype=np.float32)/255
 raw_all[:627,x:x+1254]=a.blend(raw_all[:627,x:x+1254],p,np.rint(alpha*255).astype(np.uint8))
 _,out=apply(image[:627,x:x+1254],pc,alpha,name+'-insertion')
 image[:627,x:x+1254]=out
 operations.append(dict(id=name,native=rec,rectCoreXYXY=[x,0,x+1254,627],originalGeometryAlpha=j.ref(V/'masks'/(name+'-insertion-alpha.png')),haloField=j.ref(F/(name+'-halo.npz')),insertionField=j.ref(F/(name+'-insertion.npz'))))
assert np.array_equal(raw_all,original),'Original fixed geometry composition failed to reproduce'
# Match small remaining physical-edge tint only where the adjacent rows share material.
incoming=np.median(image[:3],axis=0).astype(np.float32);target=np.median(n[-3:],axis=0).astype(np.float32)
agreement=(category(incoming)==category(target))&(np.max(np.abs(target-incoming),axis=1)<64)
diff=(target-incoming)*agreement[:,None]
def xsmooth(v):
 for _ in range(2):
  p=np.pad(v,[(8,8)]+[(0,0)]*(v.ndim-1),mode='reflect');c=np.concatenate([np.zeros_like(p[:1]),np.cumsum(p,axis=0,dtype=np.float64)],axis=0);v=(c[17:]-c[:-17])/17
 return v
den=xsmooth(agreement.astype(np.float32));profile=xsmooth(diff)/np.maximum(den[:,None],.001);valid=den>.15
for c in range(3):profile[:,c]=np.interp(np.arange(4096),np.flatnonzero(valid),profile[valid,c])
profile=np.clip(profile,-32,32);fade=(1-np.arange(180,dtype=np.float32)/179)**2
edge=profile[None,:,:]*fade[:,None,None];image[:180]=np.clip(np.rint(image[:180].astype(np.float32)+edge),0,255).astype(np.uint8)
np.savez_compressed(F/'physical-edge.npz',profile_rgb_f16=profile.astype(np.float16),fade_f16=fade.astype(np.float16),material_agreement_u8=agreement.astype(np.uint8))
assert np.array_equal(image[800:],original[800:])
correction=image.astype(np.int16)-original.astype(np.int16);np.savez_compressed(F/'final-correction.npz',correction_rgb_i16=correction,changed_mask_u8=np.any(correction!=0,axis=2).astype(np.uint8))
ext=j.rgb(V/'extended-context.png');oldext=ext.copy();ext[115:4211,115:4211]=image;mask=np.ones((4326,4326),bool);mask[115:4211,115:4211]=False;assert np.array_equal(ext[mask],oldext[mask])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ei=a.save_image(D/'extended-context.png',Image.fromarray(ext));a.ART=D/'candidate.png';a.QA=Q/'assembly';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ext),north);extra=[]
for name,x in [('n2',768),('n3',1792)]:
 probe=np.concatenate([n[-400:,x:x+1254],image[:755,x:x+1254]],0);extra.append(a.save_image(Q/(name+'-full-joint.png'),Image.fromarray(probe)))
for i,x in enumerate([0,1024,2048,2842],1):extra.append(a.save_image(Q/('insertion-bottom-'+str(i)+'.png'),Image.fromarray(image).crop((x,420,x+1254,755))))
for name,x in [('n2-left',768),('n2-n3-overlap',1907),('n3-right',3046)]:extra.append(a.save_image(Q/(name+'-vertical.png'),Image.fromarray(image[:755,max(0,x-180):x+180])))
for k,x in enumerate([909,1933,2957],1):extra.append(a.save_image(Q/f'prefix-transition-{k}.png',Image.fromarray(image[580:930,x-110:x+340])))
assert a.sha(ep)==ns and a.sha(V/'candidate.png')==EXPECTED
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),baseline=j.ref(V/'candidate.png'),baselineManifest=j.ref(V/'manifest.json'),candidate=out,extendedContext=ei,north=ni,northExtended=j.ref(ep),operations=operations,physicalEdgeField=j.ref(F/'physical-edge.npz'),finalCorrection=j.ref(F/'final-correction.npz'),method='Fixed original geometry and2px alpha masks. Same-material normalized17px RGB-difference fields times original-minus-smooth alpha remove only tonal steps. Actual image never spatially filtered or warped. Separate bounded physical-edge color profile fades over180rows.',fieldCap=32,maximumActualTotalCorrection=int(np.abs(correction).max()),belowY627ExactlyPreserved=False,belowY800ExactlyPreserved=True,scopeAuthorization=j.ref(T/'repairs/north-color-scope-authorization.json'),prefixSources=prefix_sources,prefixInternalField=j.ref(F/'prefix-internal-field.npz'),allHaloExactlyPreserved=True,neighbor09Unchanged=True,nativeGeometryUnchanged=True,artImageBlur=False,resampling=False,qa=qa,extraQA=extra,visualReview='pending',formalAccepted=False))
print(out)
