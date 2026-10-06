from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
source=P/'r09_c13-internal-candidate-v2.png';im=Image.open(source).convert('RGB');base=np.asarray(im,dtype=np.float32);out=base.copy()
rec=json.loads((P/'candidate-record-v2.json').read_text());QA=P/'qa-v3b-targeted';F=P/'fields-v3b-targeted';QA.mkdir(exist_ok=True);F.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
gradmap=np.zeros((4096,4096),np.float32)
for s in rec['nativeSources']:
 n=s['id'];row=int(n[1])-1;col=int(n[2])-1;dx,dy=s['placementShiftXY']
 a=Image.open(s['source']).convert('RGB').transform((1254,1254),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BILINEAR)
 ar=np.asarray(a,dtype=np.float32).mean(axis=2);gy,gx=np.gradient(ar);g=np.hypot(gx,gy)
 gradmap[row*1024:(row+1)*1024,col*1024:(col+1)*1024]=g[115:1139,115:1139]
jobs=[dict(id='wood2048',box=[900,1792,1184,2304],axis='y',seam=2048,material='wood',mode='balanced',support=256),dict(id='wood3072',box=[880,2816,1200,3328],axis='y',seam=3072,material='wood',mode='balanced',support=256),dict(id='pot',box=[768,0,1280,350],axis='x',seam=1024,material='jade',mode='right_only',support=256)]
records=[]
def smooth(v,radius=5):
 k=np.r_[np.arange(1,radius+2),np.arange(radius,0,-1)].astype(float);k/=k.sum()
 return np.stack([np.convolve(np.pad(v[:,c],(radius,radius),mode='edge'),k,'valid') for c in range(3)],axis=1)
for job in jobs:
 x0,y0,x1,y1=job['box'];a=base[y0:y1,x0:x1];h,w=a.shape[:2];yy,xx=np.mgrid[y0:y1,x0:x1]
 coord=yy if job['axis']=='y' else xx;d=coord-job['seam']
 if job['axis']=='y':
  k=job['seam']-y0;before=np.median(a[k-2:k,:,:],axis=0);after=np.median(a[k:k+2,:,:],axis=0)
 else:
  k=job['seam']-x0;before=np.median(a[:,k-9:k-2,:],axis=1);after=np.median(a[:,k+2:k+9,:],axis=1)
 raw=before-after;profile=smooth(raw,2)
 if job['material']=='jade':
  # Compare identical map coordinates, not opposite sides of a curved object.
  aligned=[]
  for n in ['p11','p12']:
   s=next(z for z in rec['nativeSources'] if z['id']==n);dx,dy=s['placementShiftXY']
   ni=Image.open(s['source']).convert('RGB').transform((1254,1254),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BILINEAR)
   ar=np.asarray(ni,dtype=np.float32);nf=np.load(s['fields']['file']);ar+=nf['rgbAdditiveCorrection'];aligned.append(ar)
  aa=aligned[0][:,1024:];bb=aligned[1][:,:230];delta=aa-bb
  good=(aa[:,:,2]/np.maximum(aa[:,:,1],1)>.65)&(bb[:,:,2]/np.maximum(bb[:,:,1],1)>.65)&(aa[:,:,1]/np.maximum(aa[:,:,0],1)>1.6)&(bb[:,:,1]/np.maximum(bb[:,:,0],1)>1.6)&(aa[:,:,0]<145)&(bb[:,:,0]<145)&(np.max(abs(delta),axis=2)<28)
  values=[]
  for gy in range(y0,y1):
   s0=max(0,gy+115-48);s1=min(1254,gy+115+49);g0=good[s0:s1,16:214];d0=delta[s0:s1,16:214]
   values.append(np.median(d0[g0],axis=0) if g0.sum()>100 else np.array([np.nan]*3))
  values=np.asarray(values);t=np.arange(h)
  for c in range(3):
   valid=np.isfinite(values[:,c]);values[:,c]=np.interp(t,t[valid],values[valid,c])
  raw=values;profile=smooth(values,25)
 if job['mode']=='balanced':profile=np.clip(profile,-40,40);direction=np.where(d>=0,.5,-.5)
 else:profile=np.clip(profile,-20,20);direction=(d>=0).astype(float)
 fall=np.where(abs(d)<job['support'],.5+.5*np.cos(np.pi*np.minimum(abs(d),job['support'])/job['support']),0)
 r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 if job['material']=='wood':
  # Preserve gold ornaments and red paper by excluding their distinct hue ratios.
  material=np.clip((r/g-1.22)/.18,0,1)*np.clip((2.30-r/g)/.20,0,1)*np.clip((g/np.maximum(b,1)-1.2)/.3,0,1)*np.clip((r-45)/25,0,1)
  # Continuous broad wood; exclude pale stone/ground.
  material*=np.clip((205-g)/30,0,1)
 else:
  material=np.clip((g/np.maximum(r,1)-1.35)/.4,0,1)*np.clip((b/np.maximum(r,1)-1.1)/.3,0,1)*np.clip((160-r)/40,0,1)
  material*=np.clip((350-yy)/50,0,1)
  # Preserve the entire raised flower ornament, including its outline and volume.
  ornamentProtection=np.maximum(np.clip((1150-xx)/32,0,1),np.clip((140-yy)/32,0,1))
  material*=ornamentProtection
 protect=np.clip((12-gradmap[y0:y1,x0:x1])/8,0,1)
 # Soften rectangle returns without blurring art or ornaments.
 tangent=np.minimum(xx-x0,x1-1-xx) if job['axis']=='y' else np.minimum(yy-y0,y1-1-yy)
 boundary=np.clip(tangent/32,0,1)
 if job['id']=='pot':boundary=np.clip((y1-1-yy)/32,0,1)
 mask=(fall*material*protect*boundary).astype(np.float32)
 pf=profile[None,:,:] if job['axis']=='y' else profile[:,None,:]
 field=np.clip(pf*direction[:,:,None]*mask[:,:,None],-20,20).astype(np.float32)
 out[y0:y1,x0:x1]+=field
 dest=F/(job['id']+'.npz');np.savez_compressed(dest,rgbAdditiveCorrection=field,applicationMask=mask,measuredBoundaryDifferenceRGB=raw,smoothedBoundaryDifferenceRGB=profile,sourceGradientProtection=protect)
 mp=F/(job['id']+'-mask.png');Image.fromarray(np.rint(mask*255).astype('uint8')).save(mp)
 changed=int(np.any(abs(field)>.001,axis=2).sum())
 records.append(dict(**job,actualMaxAbsoluteCorrection=float(abs(field).max()),cap=20,changedPixelCount=changed,sourceNativeHighGradientProtection='full correction at native gradient<=4; zero at>=12; native-source gradients do not mistake assembly tone jump for painted outline',fields=dict(file=str(dest),sha256=sha(dest)),mask=dict(file=str(mp),sha256=sha(mp))))
result=Image.fromarray(np.rint(np.clip(out,0,255)).astype('uint8'));candidate=P/'r09_c13-internal-candidate-v3b.png';result.save(candidate)
qarecords=[]
for job in jobs:
 x0,y0,x1,y1=job['box'];old=im.crop((x0,y0,x1,y1));new=result.crop((x0,y0,x1,y1));w,h=old.size
 sheet=Image.new('RGB',(w*2+12,h+24),'#333333');draw=ImageDraw.Draw(sheet);sheet.paste(old,(0,24));sheet.paste(new,(w+12,24));draw.text((3,4),job['id']+' v2 ORIGINAL',fill='white');draw.text((w+15,4),'v3 LOCAL TONE ONLY',fill='white')
 dest=QA/(job['id']+'-old-new-native.png');sheet.save(dest);qarecords.append(dict(file=str(dest),sha256=sha(dest),scale='1:1',box=job['box'],actuallyViewed=False))
outside=np.ones((4096,4096),bool)
for j in jobs:
 x0,y0,x1,y1=j['box'];outside[y0:y1,x0:x1]=False
manifest=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),file=str(candidate),sha256=sha(candidate),pixels=[4096,4096],derivedFrom=dict(file=str(source),sha256=sha(source),record=str(P/'candidate-record-v2.json')),operation='only three targeted additive RGB correction fields; no geometric operation; no resize; original texture preserved',newGeometricWarp=False,inheritedMaxGeometricWarp=rec['actualMaxAbsoluteShiftPixels'],maximumAllowedRGBAdditiveCorrection=20,jobs=records,unchangedOutsideThreeROIs=bool(np.array_equal(out[outside],base[outside])),qa=qarecords,formalAccepted=False,rootReviewPending=True,sourceFilesModified=False)
(P/'candidate-record-v3b.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(candidate=str(candidate),maxcorrection=max(j['actualMaxAbsoluteCorrection'] for j in records),qa=[x['file'] for x in qarecords]),indent=2))
