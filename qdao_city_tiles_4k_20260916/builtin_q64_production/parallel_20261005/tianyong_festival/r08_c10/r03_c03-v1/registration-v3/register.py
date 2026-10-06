"""Bounded horizontal landmark registration of existing native stone contours.

No AI call; no scale change. Only writes beside this script. Source context
owns every already-known pixel. Coordinates are local to the 1254px patch.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
SRC = OUT.parent
ROOT = next(p for p in SRC.parents if (p / 'config/image-generation.json').is_file())
sys.path.insert(0, str(ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor'))
import cv2

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p): return {'file': str(p), 'sha256': sha(p)}
def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)
def write_json(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

# Signed derivative landmarks measured from 9-row averages, sigma 1.5.
names = ['left_gray_to_ivory','first_ivory_to_gray','second_gray_to_ivory',
         'slim_ivory_to_channel','channel_to_broad_ivory',
         'broad_ivory_to_frame','frame_to_cloudpanel']
sample_y = np.array([1032.,1136.])
native_x = np.array([[153,269,507,632,701,896,926],
                     [150,267,504,629,699,895,930]], dtype=float)
target_x = np.array([[134,265,506,634,719,903,935],
                     [138,265,504,631,716,901,937]], dtype=float)
windows = [(125,180,1),(240,300,-1),(480,545,1),(615,665,-1),
           (675,740,1),(870,935,-1),(910,960,1)]

raw = np.array(Image.open(SRC/'native.png').convert('RGB'))
current = SRC.parent/'current/v005'
current_record = json.loads((current/'assembly.json').read_text())
current_origin = current_record['tileLocalLTRB'][:2]
current_image = Image.open(current/'r08_c10-fragment.png').convert('RGBA')
assert sha(current/'r08_c10-fragment.png') == current_record['fragment']['sha256']
crop = [1933-current_origin[0],1933-current_origin[1],3187-current_origin[0],3187-current_origin[1]]
context = np.array(current_image.crop(crop))
assert raw.shape == (1254,1254,3) and context.shape == (1254,1254,4)
known = context[:,:,3] == 255
target = context[:,:,:3]
H,W = raw.shape[:2]
flow = np.zeros((H,W,2),np.float32)
amplitudes = native_x-target_x  # inverse source sampling at target positions
slope = (amplitudes[1]-amplitudes[0])/104.
target_slope = (target_x[1]-target_x[0])/104.
xx = np.arange(W,dtype=float)

for y in range(800,H):
    # Constant target x in the earlier new region; target landmark trajectories
    # are extrapolated only near/inside the known overlap.
    tx = target_x[0] + (y-1032)*target_slope
    if y < 1032:
        t=(y-800)/232.
        # Hermite: zero starting value/slope, measured value/slope at y1032.
        d=(-2*t**3+3*t**2)*amplitudes[0] + (t**3-t**2)*232*slope
    else:
        d=amplitudes[0]+(y-1032)*slope
    d=np.clip(d,-20,20)
    xp=np.r_[0.,tx,1024.]
    fp=np.r_[0.,d,0.]
    # Smooth monotone-by-segment interpolation of inverse displacement.
    for i in range(len(xp)-1):
        select=(xx>=xp[i]) & (xx<xp[i+1])
        f=smooth((xx[select]-xp[i])/(xp[i+1]-xp[i]))
        flow[y,select,0]=fp[i]+(fp[i+1]-fp[i])*f

yy0,xx0=np.mgrid[:H,:W].astype(np.float32)
# New left neighbor: a2px existing upper vertical contour offset at its top
# corner; change only the missing continuation above that known strip.
left_peak=np.where(xx0<=142,smooth(xx0/142),1-smooth((xx0-142)/88))
left_peak=np.where(xx0<230,left_peak,0)
top_ramp=smooth((yy0-260)/137)
flow[:,:,0] += -2*left_peak*top_ramp*(yy0<800)
# The upper edge of the existing horizontal cross-band is10px higher in the
# fixed left neighbor, while its lower edge is already at the same y783.
# This is inverse vertical sampling, positive dy moves output geometry up.
up_y=np.where(yy0<=684,smooth((yy0-560)/124),1-smooth((yy0-684)/99))
up_x=1-smooth((xx0-230)/390)
flow[:,:,1]=10*up_x*up_y
assert np.abs(flow[:,:,0]).max() <= 20.0001
assert np.abs(flow[:,:,1]).max() <= 10.0001
assert np.count_nonzero(flow[:,1024:]) == 0
yy,xxg=np.mgrid[:H,:W].astype(np.float32)
aligned=cv2.remap(raw,xxg+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,
                  borderMode=cv2.BORDER_REPLICATE)

# Estimate low-frequency RGB correction from flat existing stone faces only.
# No edge/dark-gap intensity is allowed to drive surface tone.
gray=target.astype(np.float32).mean(2)
g1=np.gradient(gray)
g2=np.gradient(aligned.astype(np.float32).mean(2))
flat=(np.hypot(*g1)<6) & (np.hypot(*g2)<6) & known
delta=np.clip(target.astype(np.float32)-aligned.astype(np.float32),-12,12)
def weighted_profile(delta,valid,axis,sigma):
    num=(delta*valid[:,:,None]).sum(axis=axis)
    den=valid.sum(axis=axis).astype(np.float32)
    if axis==0:
        num=cv2.GaussianBlur(num[None,:,:],(0,0),sigmaX=sigma,sigmaY=1)[0]
        den=cv2.GaussianBlur(den[None,:],(0,0),sigmaX=sigma,sigmaY=1)[0]
    else:
        num=cv2.GaussianBlur(num[:,None,:],(0,0),sigmaX=1,sigmaY=sigma)[:,0]
        den=cv2.GaussianBlur(den[:,None],(0,0),sigmaX=1,sigmaY=sigma)[:,0]
    return np.clip(num/np.maximum(den[:,None],1e-4),-12,12)
bottom=weighted_profile(delta[1024:1088],flat[1024:1088],0,12)
right=weighted_profile(delta[:,1024:1088],flat[:,1024:1088],1,12)
left=weighted_profile(delta[:,166:230],flat[:,166:230],1,12)
top=weighted_profile(delta[397:461],flat[397:461] & (np.arange(W)[None,:]<230),0,12)
wb=smooth((yy-800)/224)
wr=smooth((xxg-900)/124)
wl=(1-smooth((xxg-230)/180))*smooth((yy-320)/77)
wt=smooth((yy-260)/137)*(1-smooth((xxg-166)/64))
den=np.maximum(wb+wr+wl+wt,1)
tone=(bottom[None,:,:]*wb[:,:,None]+right[:,None,:]*wr[:,:,None]+left[:,None,:]*wl[:,:,None]+top[None,:,:]*wt[:,:,None])/den[:,:,None]
tone=np.clip(tone,-12,12).astype(np.float32)
corrected=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
joined=corrected.copy()
joined[known]=target[known]
assert np.array_equal(joined[known],target[known])
assert np.array_equal(joined[(yy<260)&(xxg<900)&~known],raw[(yy<260)&(xxg<900)&~known])

OUT.mkdir(exist_ok=True)
qa=OUT/'qa';qa.mkdir(exist_ok=True)
np.save(OUT/'horizontal-field.npy',flow)
np.save(OUT/'tone.npy',tone)
Image.fromarray(context).save(OUT/'context-v005.png')
Image.fromarray((~known).astype(np.uint8)*255).save(OUT/'source-ownership-mask.png')
Image.fromarray(aligned).save(OUT/'aligned-native.png')
Image.fromarray(joined).save(OUT/'joined.png')

k=np.exp(-np.arange(-5,6,dtype=float)**2/(2*1.5**2));k/=k.sum()
def edges(im,y):
    row=im[max(0,y-4):min(H,y+5)].astype(float).mean((0,2))
    grad=np.gradient(np.convolve(row,k,'same'))
    values=[]
    for x0,x1,sign in windows:
        loc=int(x0+np.argmax(grad[x0:x1]*sign))
        v=grad*sign
        denominator=v[loc-1]-2*v[loc]+v[loc+1]
        refine=0.5*(v[loc-1]-v[loc+1])/denominator if abs(denominator)>1e-8 else 0
        values.append(float(loc+np.clip(refine,-.5,.5)))
    return np.array(values)
residual=[]
for y in [1032,1056,1088,1136]:
    n=edges(raw,y);t=edges(target,y);a=edges(aligned,y)
    residual.append({'y':y,'nativeX':n.tolist(),'contextX':t.tolist(),
                     'alignedX':a.tolist(),'alignedMinusContextPx':(a-t).tolist()})
traces=[]
for y in range(850,1101,4):
    traces.append({'y':y,'finalX':edges(joined,y).tolist()})
contours={'method':'9-row mean intensity, 1D Gaussian sigma1.5 then signed strongest gradient in fixed windows; quadratic peak refinement. Not full registration proof.',
          'names':names,'windows':windows,'residualsInKnownComparisonBand':residual,
          'joinedContourTraces':traces,
          'maxAbsComparisonResidualPx':float(max(abs(z) for r in residual for z in r['alignedMinusContextPx']))}
write_json(OUT/'contour-residuals.json',contours)

# All QA crops retain original source pixels without scale changes.
im=Image.fromarray(joined)
for name,box in [
    ('lower-return-1254x454',(0,800,1254,1254)),
    ('bottom-contact-1254x224',(0,912,1254,1136)),
    ('right-return-354x1254',(900,0,1254,1254)),
    ('corner-return-390x354',(864,900,1254,1254)),
    ('first-band-return-240x454',(80,800,320,1254)),
    ('broad-band-return-350x454',(610,800,960,1254)),
    ('left-return-400x1254',(0,0,400,1254)),
    ('left-cross-band-return-650x350',(0,550,650,900)),
    ('upper-left-corner-400x300',(0,260,400,560)),
    ('upper-right-corner-354x350',(900,0,1254,350))]:
    im.crop(box).save(qa/(name+'.png'))
board=Image.new('RGB',(1254,3*230),(255,0,255))
for i,a in enumerate([target,aligned,joined]):
    board.paste(Image.fromarray(a).crop((0,1024,1254,1254)),(0,i*230))
board.save(qa/'context-aligned-final-known-band.png')
manifest=[]
for p in qa.glob('*.png'):
    with Image.open(p) as image:
        manifest.append({**info(p),'pixels':list(image.size),'nativePixelScale':1})
write_json(qa/'manifest.json',manifest)

record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'operation':'Landmark-controlled horizontal inverse sampling of already corresponding stone contours, flat-surface RGB correction, exact context ownership. No AI call or enlargement.',
 'sourceFiles':[info(SRC/'native.png'),info(current/'r08_c10-fragment.png')],
 'contextCropFromCurrent':crop,'contextReference':info(OUT/'context-v005.png'),'currentAssembly':info(current/'assembly.json'),
 'request':info(SRC/'request.json'),'output':info(OUT/'joined.png'),
 'nativePixels':[W,H],'allowedMaxHorizontalShiftPx':20,'actualMaxHorizontalShiftPx':float(np.abs(flow[:,:,0]).max()),
 'allowedMaxVerticalShiftPx':10,'actualMaxVerticalShiftPx':float(np.abs(flow[:,:,1]).max()),'rightRegionX1024PlusShiftPx':0,
 'inverseSamplingDefinition':'sample native at (targetX + fieldX, targetY + fieldY); positive field means output structure moves left/up',
 'controlNames':names,'anchorY':sample_y.tolist(),'targetX':target_x.tolist(),'nativeX':native_x.tolist(),
 'transition':'Horizontal: Hermite y800..1032, measured ending derivative, smoothstep x segments. Left top corner adds2px horizontal inverse correction with y260..397 ramp. Vertical: existing cross-band top at684 samples source694, lower783 fixed; smooth y560..684..783, x230..620 taper. Right x>=1024 field0. No optical flow.',
 'allowedToneMaxRGB':12,'actualToneMaxRGB':np.abs(tone).max(axis=(0,1)).tolist(),
 'toneEstimation':'Known flat faces (gradient magnitude<6) in bottom/right/left/top known64px strips; bounded12/255 RGB deltas, weighted profiles Gaussian sigma12; broad smooth extension into new area only.',
 'resampling':'OpenCV INTER_CUBIC, no resize, dimensions unchanged',
 'allKnownPixelsUnchanged':bool(np.array_equal(joined[known],target[known])),
 'knownPixels':int(known.sum()),'fields':[info(OUT/x) for x in ['horizontal-field.npy','tone.npy','source-ownership-mask.png']],
 'contourResiduals':info(OUT/'contour-residuals.json'),'qa':info(qa/'manifest.json'),'script':info(Path(__file__)),
 'localAccepted':False,'formalAccepted':False,'requiresVisualReview':True,'scope':'one1254 native patch only, no complete4K or city acceptance'}
write_json(OUT/'assembly.json',record)
write_json(OUT/'joined.png.generation.json',{'file':str(OUT/'joined.png'),'sha256':sha(OUT/'joined.png'),'derivedFrom':record['sourceFiles'],'assembly':info(OUT/'assembly.json'),'newModelCalls':0,'operation':record['operation']})
print(json.dumps({'output':record['output'],'maxShift':record['actualMaxHorizontalShiftPx'],'residualMax':contours['maxAbsComparisonResidualPx'],'localAccepted':False}))
