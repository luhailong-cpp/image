from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
T=O.parent.parent
S=O.parent/'candidate-v4/candidate1254.png'
C=json.loads((T/'regional/context.json').read_text())
N=Path(C['northCore']['file'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def raw(a):return hashlib.sha256(a.tobytes()).hexdigest()
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
a=np.array(Image.open(S).convert('RGB'));n=np.array(Image.open(N).convert('RGB'))
assert sha(S)=='3ad00fa37e398ad9983a36f210d5b8d6c7f996edd8b1819a23b7de5cc734fb7e'
assert sha(N)==C['northCore']['sha256']
assert np.array_equal(a[:115],n[3981:4096,909:2163])
# Five actual quiet stone-face windows; deliberately exclude the visible slot
# cap and left bevel where source geometry creates misleading RGB differences.
windows=[(890,905),(905,920),(920,935),(983,990),(990,996)]
samples=[]
for x0,x1 in windows:
 nr=n[4093:4096,909+x0:909+x1];sr=a[115:118,x0:x1]
 delta=np.median(nr,axis=(0,1))-np.median(sr,axis=(0,1))
 samples.append({'nativeXHalfOpen':[x0,x1],'northBoxXYXY':[909+x0,4093,909+x1,4096],'southBoxXYXY':[x0,115,x1,118],'northMedianRgb':np.median(nr,axis=(0,1)).tolist(),'southMedianRgb':np.median(sr,axis=(0,1)).tolist(),'deltaRgb':delta.tolist(),'northRawRGBSha256':raw(nr),'southRawRGBSha256':raw(sr)})
centers=np.array([(x0+x1-1)/2 for x0,x1 in windows]);values=np.array([x['deltaRgb'] for x in samples])
# Cubic smoothstep interpolation affects only numeric delta coefficients, not
# artwork pixels. No image blur, neighborhood filtering, shift or resampling.
x=np.arange(1254);yy,xx=np.mgrid[:1254,:1254]
curves=np.repeat(values[:1],len(x),axis=0)
for i in range(len(centers)-1):
 use=(x>=centers[i])&(x<centers[i+1]);t=smooth((x[use]-centers[i])/(centers[i+1]-centers[i]));curves[use]=values[i]*(1-t[:,None])+values[i+1]*t[:,None]
curves[x>=centers[-1]]=values[-1]
curves=np.clip(curves,[-6,-7,-8],[6,7,8])
alpha=smooth((xx-882)/10)*smooth((1002-xx)/7)*(1-smooth((yy-115)/135))
alpha[yy<115]=0
# Strict material gating: no green pixels, brown wood or dark slot pixels.
rgb=a.astype(np.float64);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
material=smooth((r-227)/17)*smooth((g-187)/19)*smooth((b-156)/17)
material*=((g-r)<0)&((r-g)<44)&((g-b)<39)
alpha*=material
# Do not hide the unresolved northern slot-cap contour in the color solution.
exclude=Image.new('L',(1254,1254));polygon=[(934,115),(982,115),(982,157),(968,170),(942,155),(923,176),(916,187),(908,184),(918,160),(932,142)]
ImageDraw.Draw(exclude).polygon(polygon,fill=255)
ex=np.array(exclude)>0
distance=np.full(alpha.shape,np.inf)
for i,(x0,y0) in enumerate(polygon):
 x1,y1=polygon[(i+1)%len(polygon)];vx=x1-x0;vy=y1-y0
 t=np.clip(((xx-x0)*vx+(yy-y0)*vy)/(vx*vx+vy*vy),0,1)
 distance=np.minimum(distance,np.hypot(xx-(x0+t*vx),yy-(y0+t*vy)))
distance[ex]=0
alpha*=smooth(distance/7)
field=alpha[:,:,None]*curves[None,:,:]
limit=np.array([6,7,8]);assert np.all(np.abs(field)<=limit)
out=np.clip(np.rint(rgb+field),0,255).astype(np.uint8)
changed=np.any(out!=a,axis=2);delta=out.astype(np.int16)-a.astype(np.int16)
assert np.array_equal(out[:115],a[:115]) and np.array_equal(out[400:],a[400:])
assert not np.any(changed & (g>=r))
assert not np.any(changed & ex)
assert not np.any(changed & ((xx<882)|(xx>=1002)|(yy<115)|(yy>=250)))
assert np.all(np.abs(delta)<=limit)
Image.fromarray(out).save(O/'candidate1254.png')
Image.fromarray(np.uint8(changed)*255).save(O/'changed-mask.png')
Image.fromarray(np.uint8(np.rint(alpha*255))).save(O/'stone-alpha.png')
exclude.save(O/'excluded-slot-contour-mask.png')
np.savez_compressed(O/'stone-rgb-field.npz',rgb_delta_float32=field.astype(np.float32),rgb_delta_applied_int16=delta,alpha=alpha.astype(np.float32),changed_mask=changed,excluded_slot_mask=ex,dx=np.zeros_like(alpha,dtype=np.float32),dy=np.zeros_like(alpha,dtype=np.float32),channel_limits=limit)
board=Image.new('RGB',(1254,512));board.paste(Image.fromarray(n).crop((909,3840,2163,4096)),(0,0));board.paste(Image.fromarray(out).crop((0,115,1254,371)),(0,256));board.save(O/'north1254x512.png')
board.crop((680,186,1010,386)).save(O/'stone330x200.png')
Image.fromarray(out).crop((840,65,1030,260)).save(O/'after-native-stone190x195.png')
Image.fromarray(out).crop((870,115,1010,290)).save(O/'field-boundary140x175.png')
qa=[]
for name in ['north1254x512.png','stone330x200.png','after-native-stone190x195.png','field-boundary140x175.png']:
 p=O/name;im=Image.open(p).convert('RGB');qa.append({**ref(p),'width':im.width,'height':im.height,'rawRGBSha256':raw(np.array(im)),'actuallyViewed':False})
ys,xs=np.where(changed)
merge={'requiredBaseImage':ref(S),'activeMask':ref(O/'changed-mask.png'),'activeMaskSourcePixelsRawRGBSha256':raw(a[changed]),'field':ref(O/'stone-rgb-field.npz'),'operation':'At each changed_mask pixel, assert final top candidate RGB equals requiredBaseImage RGB exactly, then add rgb_delta_applied_int16. Fail on any mismatch; no fallback blending or silent overwrite.','recipe':ref(Path(__file__))}
meta={'createdAt':datetime.now(timezone.utc).isoformat(),'tool':'local_native_processing','aiInvocation':False,'operation':'Bounded material-only numerical additive RGB field; no image blur, geometry change, resampling or new drawing.','source':ref(S),'trueNorth':ref(N),'northSourceCropForStrict115XYXY':[909,3981,2163,4096],'samples':samples,'channelLimits':[6,7,8],'actualAppliedMinRgb':delta.min((0,1)).tolist(),'actualAppliedMaxRgb':delta.max((0,1)).tolist(),'changedPixelCount':int(changed.sum()),'changedBoundsHalfOpen':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'depthFade':'numeric cubic smoothstep y115..250 to zero','xFade':'numeric cubic smoothstep x882..892 and x995..1002','slotContourExclusionPolygon':polygon,'strictTop115Exact':True,'bottomRows400PlusExact':True,'greenMaterialChangedPixelCount':0,'excludedSlotContourChangedPixelCount':0,'geometryDxDyZero':True,'noArtworkBlur':True,'output':ref(O/'candidate1254.png'),'mergeContract':merge,'technicalArtifacts':[{'role':'selected local stone color alpha',**ref(O/'stone-alpha.png')},{'role':'applied stone material support mask',**ref(O/'changed-mask.png')},{'role':'explicit protected slot-contour exclusion',**ref(O/'excluded-slot-contour-mask.png')},{'role':'numeric color field and zero geometry fields',**ref(O/'stone-rgb-field.npz')},{'role':'reproducible local color recipe',**ref(Path(__file__))}],'qa':qa,'requiresFurtherReview':True,'wholeNorthSeamAccepted':False,'knownUnresolvedObservation':'Slot cap at native x~950..977 across y115 remains a visible contour/shading-shape disagreement. It is explicitly protected rather than hidden by a large color correction. Root/top must inspect this shape separately.'}
(O/'processing.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:meta[k] for k in ['changedPixelCount','changedBoundsHalfOpen','actualAppliedMinRgb','actualAppliedMaxRgb','output','wholeNorthSeamAccepted']},indent=2))
