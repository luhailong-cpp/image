from pathlib import Path
import numpy as np,json,hashlib,datetime
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
REPORT=json.loads((OUT/'overlap-diagnostics.json').read_text())
FIELDS=OUT/'fields-v2';QA=OUT/'qa-v2';FIELDS.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
names=[f'p{r}{c}' for r in range(1,5) for c in range(1,5)]
assert not REPORT['missingPatches']
UNSAFE={('p22','p32'):'ornamental cap mismatch handled by hard source ownership below cap; no color or feather on this edge'}
NOFEATHER={('p11','p12'),('p22','p32')}
arrays={};orig={};shifts={};grad={}
for name in names:
 p=ROOT/'native'/(name+'.png');im=Image.open(p).convert('RGB');orig[name]=np.asarray(im,dtype=np.float32)
 shift=np.asarray(REPORT['boundedPatchPlacementSuggestions'][name]);assert abs(shift).max()<=4
 shifts[name]=shift.tolist()
 if name=='p11':assert np.all(shift==0);warped=im
 else:warped=im.transform(im.size,Image.Transform.AFFINE,(1,0,-float(shift[0]),0,1,-float(shift[1])),Image.Resampling.BILINEAR)
 arrays[name]=np.asarray(warped,dtype=np.float32)
 gy,gx=np.gradient(arrays[name].mean(axis=2));grad[name]=np.hypot(gx,gy)

# Local robust RGB offsets only near already-matching overlap structures. No source blur.
fields={n:np.zeros((1254,1254,3),dtype=np.float32) for n in names}
denom={n:np.zeros((1254,1254),dtype=np.float32) for n in names}
profiles=[]
yy,xx=np.mgrid[:1254,:1254]
for e in REPORT['pairs']:
 a,b=e['a'],e['b'];axis=e['axis']
 if (a,b) in UNSAFE:continue
 if axis=='horizontal':aa=arrays[a][:,1024:];bb=arrays[b][:,:230];ga=grad[a][:,1024:];gb=grad[b][:,:230]
 else:aa=arrays[a][1024:];bb=arrays[b][:230];ga=grad[a][1024:];gb=grad[b][:230]
 points=np.arange(0,1254,64);values=[];counts=[]
 for v in points:
  lo=max(0,v-96);hi=min(1254,v+97)
  if axis=='horizontal':da=aa[lo:hi,83:147];db=bb[lo:hi,83:147];gga=ga[lo:hi,83:147];ggb=gb[lo:hi,83:147]
  else:da=aa[83:147,lo:hi];db=bb[83:147,lo:hi];gga=ga[83:147,lo:hi];ggb=gb[83:147,lo:hi]
  diff=da-db;good=(gga<3)&(ggb<3)&(np.max(abs(diff),axis=2)<24)
  counts.append(int(good.sum()));values.append(np.median(diff[good],axis=0) if good.sum()>60 else np.zeros(3))
 values=np.asarray(values);profile=np.stack([np.interp(np.arange(1254),points,values[:,k]) for k in range(3)],axis=1)
 factorA=0 if a=='p11' else -.5;factorB=1 if a=='p11' else .5
 for n,center,factor in [(a,1139,factorA),(b,115,factorB)]:
  dist=abs((xx if axis=='horizontal' else yy)-center);w=np.maximum(0,1-dist/160)**2
  pf=profile[:,None,:] if axis=='horizontal' else profile[None,:,:]
  fields[n]+=factor*pf*w[:,:,None];denom[n]+=w
 profiles.append(dict(a=a,b=b,axis=axis,coordinates=points.tolist(),medianDifferenceAminusB=values.tolist(),validSampleCounts=counts,correctionSupportPixels=160,maximumAbsoluteRequestedRGB=float(abs(values).max())))
for n in names:
 fields[n]/=np.maximum(1,denom[n])[:,:,None];np.clip(fields[n],-8,8,out=fields[n])
 if n=='p11':fields[n][:]=0
for a,b in UNSAFE:
 axis=next(e['axis'] for e in REPORT['pairs'] if e['a']==a and e['b']==b)
 for n,center in [(a,1139),(b,115)]:fields[n][abs((xx if axis=='horizontal' else yy)-center)<=160]=0
corrected={n:np.clip(arrays[n]+fields[n],0,255) for n in names}

# Narrow32px texture feather, explicitly disabled at unmatched ornaments and strong contours.
wx={n:((xx>=115)&(xx<1139)).astype(np.float32) for n in names}
wy={n:((yy>=115)&(yy<1139)).astype(np.float32) for n in names}
blendReports=[]
for e in REPORT['pairs']:
 a,b=e['a'],e['b'];axis=e['axis'];unsafe=(a,b) in NOFEATHER
 if axis=='horizontal':aa=corrected[a][:,1123:1155];bb=corrected[b][:,99:131];ga=grad[a][:,1123:1155];gb=grad[b][:,99:131]
 else:aa=corrected[a][1123:1155,:];bb=corrected[b][99:131,:];ga=grad[a][1123:1155,:];gb=grad[b][99:131,:]
 gate=(ga<3)&(gb<3)&(np.max(abs(aa-bb),axis=2)<20)
 if unsafe:gate[:]=False
 ramp=(np.arange(32)+.5)/32
 if axis=='horizontal':
  wx[a][:,1123:1155]=np.where(gate,1-ramp[None,:],wx[a][:,1123:1155]);wx[b][:,99:131]=np.where(gate,ramp[None,:],wx[b][:,99:131])
 else:
  wy[a][1123:1155,:]=np.where(gate,1-ramp[:,None],wy[a][1123:1155,:]);wy[b][99:131,:]=np.where(gate,ramp[:,None],wy[b][99:131,:])
 blendReports.append(dict(a=a,b=b,axis=axis,textureBlendPixelCount=int(gate.sum()),totalSupportPixelCount=int(gate.size),widthPixels=32,disabledReason=UNSAFE.get((a,b))))

# Exact native ownership route: p22 supplies its whole plain lamp cap;
# p32 supplies red ring below cap and body, retaining complete body motifs.
# Every routed pixel exists in both original230px overlaps; no content synthesis.
ownershipCut=np.interp(np.arange(1254),[0,260,300,575,620,1253],[115,115,150,150,115,115])
wy['p22'][1024:1254,:]=(np.arange(230)[:,None]<ownershipCut[None,:]).astype(np.float32)
wy['p32'][:230,:]=(np.arange(230)[:,None]>=ownershipCut[None,:]).astype(np.float32)
ownership=dict(pair=['p22','p32'],method='hard native pixel ownership without feather',overlapSize=[1254,230],coordinateSpace='p32 native overlap XY; p22 sample Y=1024+overlapY',knotsXY=[[0,115],[260,115],[300,150],[575,150],[620,115],[1253,115]],rule='p22 owns y<cut(x);p32 owns y>=cut(x)',nominalGlobalSeamY=2048,maximumRouteExcursionPixels=35,featurePolicy='exclude p32 upper disk and cap gold scrolls whole; retain p32 body motifs starting around y200; p22halo supports routed y1174<1254',actualVisualAcceptancePending=True)
save(OUT/'lamp-ownership-cut-v2.json',ownership)

total=np.zeros((4096,4096,3),np.float32);weight=np.zeros((4096,4096),np.float32);records=[]
for n in names:
 row=int(n[1])-1;col=int(n[2])-1;ox=col*1024-115;oy=row*1024-115
 x0=max(0,ox);x1=min(4096,ox+1254);y0=max(0,oy);y1=min(4096,oy+1254)
 sx=slice(x0-ox,x1-ox);sy=slice(y0-oy,y1-oy);mask=wx[n]*wy[n]
 total[y0:y1,x0:x1]+=corrected[n][sy,sx]*mask[sy,sx,None];weight[y0:y1,x0:x1]+=mask[sy,sx]
 flow=np.empty((1254,1254,2),np.float32);flow[:,:,0]=-shifts[n][0];flow[:,:,1]=-shifts[n][1]
 fp=FIELDS/(n+'-fields.npz');np.savez_compressed(fp,backwardSamplingDisplacementXY=flow,rgbAdditiveCorrection=fields[n],assemblyWeightMask=mask)
 mp=FIELDS/(n+'-assembly-mask.png');Image.fromarray(np.rint(mask*255).astype('uint8')).save(mp)
 records.append(dict(id=n,source=str(ROOT/'native'/(n+'.png')),sourceSha256=sha(ROOT/'native'/(n+'.png')),pixels=[1254,1254],placementShiftXY=shifts[n],backwardSampleShiftXY=[-x for x in shifts[n]],sourceResampling='none' if n=='p11' else 'bilinear subpixel translation at original native scale',maximumAbsoluteRGBOffset=float(abs(fields[n]).max()),fields=dict(file=str(fp),sha256=sha(fp)),maskPreview=dict(file=str(mp),sha256=sha(mp))))
assert weight.min()>0
candidate=Image.fromarray(np.clip(np.rint(total/weight[:,:,None]),0,255).astype('uint8'))
p=OUT/'r09_c13-internal-candidate-v2.png';candidate.save(p)
base=Image.new('RGB',(4096,4096))
for n in names:base.paste(Image.fromarray(orig[n].astype('uint8')).crop((115,115,1139,1139)),((int(n[2])-1)*1024,(int(n[1])-1)*1024))
qa=[]
for axis in ['x','y']:
 for v in [1024,2048,3072]:
  crop=candidate.crop((v-128,0,v+128,4096)) if axis=='x' else candidate.crop((0,v-128,4096,v+128)).transpose(Image.Transpose.ROTATE_90)
  sheet=Image.new('RGB',(1024,1048),'#333333');draw=ImageDraw.Draw(sheet)
  for i in range(4):sheet.paste(crop.crop((0,i*1024,256,(i+1)*1024)),(i*256,24));draw.text((i*256+2,4),f'{axis}{v} part{i+1} native',fill='white')
  dest=QA/f'{axis}{v}-full-native.png';sheet.save(dest);qa.append(dict(file=str(dest),sha256=sha(dest),scale='1:1',scope=f'full4096 {axis} seam +/-128px',actuallyViewed=False))
sheet=Image.new('RGB',(1152,1224),'#333333');draw=ImageDraw.Draw(sheet)
for r,y in enumerate([1024,2048,3072]):
 for c,x in enumerate([1024,2048,3072]):
  sheet.paste(candidate.crop((x-192,y-192,x+192,y+192)),(c*384,r*408+24));draw.text((c*384+3,r*408+4),f'junction {x},{y} native',fill='white')
dest=QA/'nine-intersections-native.png';sheet.save(dest);qa.append(dict(file=str(dest),sha256=sha(dest),scale='1:1',scope='all9 intersections384square',actuallyViewed=False))
small=candidate.resize((1254,1254),Image.Resampling.LANCZOS);small.save(OUT/'internal-candidate-preview-v2.png')
save(OUT/'candidate-record-v2.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),file=str(p),sha256=sha(p),pixels=[4096,4096],role='internal-seam candidate only; source ownership ornaments require visual acceptance; external c12 not repaired',nativeSources=records,diagnosticsSha256=sha(OUT/'overlap-diagnostics.json'),hardShiftBoundPixels=4,preferredShiftBoundPixels=2,actualMaxAbsoluteShiftPixels=max(abs(v) for s in shifts.values() for v in s),anchor='p11 fixed; every col1 x=0',colorRule='robust local median RGB on low-gradient matching overlap pixels; linear profile interpolation;160px quadratic spatial taper;offset cap8/255; no blur;lamp cap edge excluded',colorProfiles=profiles,featherRule='32px total only both source gradients<3 and maxRGBdiff<20; all strong contours hard cut;pot/lamp ornament edges disabled',blendReports=blendReports,ownershipCut=ownership,weightSumBeforeNormalization=[float(weight.min()),float(weight.max())],knownUnresolved=['source ownership lamp mask contour return points and minor tone differences require visual inspection','externalc12 not repaired'],sourceUpscaling=False,rootFilesModified=False,formalAccepted=False,clientAccepted=False,qa=qa))
print(json.dumps(dict(file=str(p),pixels=candidate.size,actualMaxShift=max(abs(v) for s in shifts.values() for v in s),knownUnresolved=len(UNSAFE),qaBoards=len(qa)),indent=2))
