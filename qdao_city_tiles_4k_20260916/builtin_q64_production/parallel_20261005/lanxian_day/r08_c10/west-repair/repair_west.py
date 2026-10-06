"""Bounded repair of c10's internal guide artifact; never shift its external west edge."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
TILE = ROOT / 'r08_c10'
OWN = TILE / 'west-repair'
OUT = OWN / 'v1'
VENDOR = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
sys.path.insert(0, str(VENDOR))
import cv2

def safe(path):
    p = Path(path).resolve()
    if not p.is_relative_to(OWN):
        raise ValueError(f'Outside assigned output: {p}')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ref(p):
    return {'file': str(Path(p).resolve()), 'sha256': sha(p)}

def write(p, value):
    safe(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)

def box_of(mask):
    y, x = np.where(mask)
    return [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)] if x.size else None

source = TILE / 'candidate/extended4326.png'
source_core = TILE / 'candidate/core4096.png'
assert sha(source_core) == '1a2bb992de62dce69c9e77fb7ad0163aa7fa96f402156e8f8268ff8a09ccdd0f'
base = np.asarray(Image.open(source)).copy()
assert base.shape == (4326,4326,3)
assert np.array_equal(base[115:4211,115:4211], np.asarray(Image.open(source_core)))
out = base.copy()

# Pull-map displacement at the artificial guide line. Each value is an explicit
# bounded trial inferred from the reviewed edge profiles, not a global offset.
features = [
    dict(id='G01_upper', x=115, y=295, dy=1.25, plateau=14, radius=32),
    dict(id='G01_lower', x=115, y=409, dy=2.0, plateau=16, radius=36),
    dict(id='G02_upper', x=115, y=1362, dy=-4.5, plateau=24, radius=52),
    dict(id='G02_lower', x=115, y=1832, dy=4.0, plateau=22, radius=48),
    dict(id='G03_upper', x=115, y=2519, dy=1.25, plateau=12, radius=24),
    dict(id='G03_lower', x=115, y=2575, dy=2.75, plateau=12, radius=24),
    dict(id='G05_upper', x=121, y=3618, dy=2.0, plateau=18, radius=42),
    dict(id='G05_lower', x=121, y=3742, dy=2.0, plateau=18, radius=38),
]
# All deterministic changes stop before corex196, leaving the other agent's
# corex200..290 repair and root/source's corex>=512 area disjoint.
x0, x1 = 230, 311
yy, xx = np.mgrid[0:4326, x0:x1].astype(np.float32)
corex, corey = xx-115, yy-115
dy = np.zeros(xx.shape, np.float32)
for f in features:
    wx = np.where(corex >= f['x'], 1-smooth((corex-f['x'])/(196-f['x'])), 0)
    wy = 1-smooth((np.abs(corey-f['y'])-f['plateau'])/(f['radius']-f['plateau']))
    dy += f['dy']*wx*wy
assert np.abs(dy).max() <= 10
warped = cv2.remap(base, xx, yy+dy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
out[:,x0:x1] = np.where((dy != 0)[...,None], warped, base[:,x0:x1])
pre_tone = out[:,x0:x1].copy()

# Additive color field only: derive from quiet faces adjacent to the internal
# artifact, excluding strong vertical detail edges. Smooth the field, not art.
left = out[:,223:230].astype(np.float32).mean(1)
right = out[:,230:237].astype(np.float32).mean(1)
raw = left-right
leftgy = np.max(np.abs(np.gradient(left, axis=0)), axis=1)
rightgy = np.max(np.abs(np.gradient(right, axis=0)), axis=1)
valid = ((leftgy < 8) & (rightgy < 8) & (np.max(np.abs(raw), axis=1) < 40)).astype(np.float32)
weight = cv2.GaussianBlur(valid[:,None], (1,0), sigmaX=0, sigmaY=24).reshape(-1)
field = np.zeros((4326,3),np.float32)
for c in range(3):
    numerator = cv2.GaussianBlur((raw[:,c]*valid)[:,None], (1,0), sigmaX=0, sigmaY=24).reshape(-1)
    field[:,c] = numerator / np.maximum(weight,1e-6)
field = np.clip(field, -12, 12)
wy = smooth((np.arange(4326)-115)/24) * (1-smooth((np.arange(4326)-(115+3016))/56))
wx = 1-smooth((np.arange(x0,x1)-230)/(311-230))
tone = field[:,None,:]*wy[:,None,None]*wx[None,:,None]
out[:,x0:x1] = np.clip(np.rint(pre_tone.astype(np.float32)+tone),0,255).astype(np.uint8)
assert np.abs(out[:,x0:x1].astype(np.int16)-pre_tone.astype(np.int16)).max() <= 12

# AI patches are copied at the SAME native pixel coordinates. Eight-pixel alpha
# transition is explicitly recorded; no patch is resized or geometrically moved.
ai_file = OWN / 'native/r04_c01.png'
ai = np.asarray(Image.open(ai_file))
original_native = np.asarray(Image.open(TILE / 'native/r04_c01.png'))
assert ai.shape == original_native.shape == (1254,1254,3)
ai_boxes = [dict(id='G04_junction', nativeBox=[165,300,300,430]),
            dict(id='G06_leaf_rail', nativeBox=[165,990,305,1254])]
alpha_full = np.zeros((4326,4326),np.float32)
for b in ai_boxes:
    ax0,ay0,ax1,ay1 = b['nativeBox']
    py,px = np.mgrid[ay0:ay1,ax0:ax1]
    alpha = (smooth((px-ax0)/8)*smooth((ax1-1-px)/8)*
             smooth((py-ay0)/8)*smooth((ay1-1-py)/8)).astype(np.float32)
    ey0,ey1 = 3072+ay0,3072+ay1
    b['extendedBox'] = [ax0,ey0,ax1,ey1]
    b['coreBox'] = [ax0-115,ey0-115,ax1-115,ey1-115]
    b['alphaTransitionPixels'] = 8
    before = out[ey0:ey1,ax0:ax1].astype(np.float32)
    after = ai[ay0:ay1,ax0:ax1].astype(np.float32)
    out[ey0:ey1,ax0:ax1] = np.clip(np.rint(before*(1-alpha[...,None])+after*alpha[...,None]),0,255).astype(np.uint8)
    alpha_full[ey0:ey1,ax0:ax1] = alpha

changed = np.any(out != base,axis=2)
assert not changed[:,:115].any()  # exterior halo and actual corewest border fixed
assert not changed[:,311:].any()
assert not changed[115+1090:115+1210,115+200:115+291].any()
core = out[115:4211,115:4211]
Image.fromarray(out).save(safe(OUT/'extended4326.png'))
Image.fromarray(core).save(safe(OUT/'core4096.png'))
Image.fromarray(core).resize((1024,1024),Image.Resampling.LANCZOS).save(safe(OUT/'preview1024.png'))
Image.fromarray((changed*255).astype(np.uint8)).save(safe(OUT/'changed-mask.png'))
Image.fromarray(np.rint(alpha_full*255).astype(np.uint8)).save(safe(OUT/'ai-alpha-mask.png'))
geom_mask=np.zeros(changed.shape,np.uint8);geom_mask[:,x0:x1]=(dy!=0)*255
Image.fromarray(geom_mask).save(safe(OUT/'geometry-mask.png'))
tone_mask=np.zeros(changed.shape,np.uint8);tone_mask[:,x0:x1]=np.rint(np.max(np.abs(tone),axis=2)/12*255).astype(np.uint8)
Image.fromarray(tone_mask).save(safe(OUT/'tone-mask.png'))
np.savez_compressed(safe(OUT/'flow-correction.npz'),extendedStripXYXY=[x0,0,x1,4326],flowX=np.zeros_like(dy),flowY=dy,toneRGB=tone,aiAlpha=alpha_full)
bbox=box_of(changed);bx0,by0,bx1,by1=bbox
np.savez_compressed(safe(OUT/'delta.npz'),extendedBoxXYXY=bbox,deltaRGB=out[by0:by1,bx0:bx1].astype(np.int16)-base[by0:by1,bx0:bx1].astype(np.int16),changedMask=changed[by0:by1,bx0:bx1],sourceSha256=sha(source))

qa=[]
def saveqa(name,image,meta):
    p=safe(OUT/'qa'/f'{name}.png');image.save(p);qa.append(dict(ref(p),pixels=list(image.size),resampling='none; integer crop/paste',**meta))
base_core=base[115:4211,115:4211]
west=np.asarray(Image.open(ROOT/'r08_c09/selected/core4096.png'))
for n in range(4):
    y0,y1=n*1024,(n+1)*1024
    saveqa(f'guide_part{n+1}_before_after',Image.fromarray(np.concatenate([base_core[y0:y1,:256],core[y0:y1,:256]],axis=1)),dict(coreYRange=[y0,y1],layout='before left256; after right256'))
    saveqa(f'external_west_part{n+1}',Image.fromarray(np.concatenate([west[y0:y1,-256:],core[y0:y1,:256]],axis=1)),dict(coreYRange=[y0,y1],layout='west256 left; repairedtarget256 right; trueseamx256, guideartifactx371'))
for label,box in [('nw',[0,0,512,512]),('ne',[3584,0,4096,512]),('sw',[0,3584,512,4096]),('se',[3584,3584,4096,4096])]:
    ax0,ay0,ax1,ay1=box;saveqa('corner_'+label,Image.fromarray(core[ay0:ay1,ax0:ax1]),dict(coreBox=box))
for label,box in [('r4_junction',[16,3240,240,3408]),('r4_orange_rail',[40,3576,224,3816]),('r4_foliage',[16,3896,240,4096])]:
    ax0,ay0,ax1,ay1=box;saveqa(label+'_before_after',Image.fromarray(np.concatenate([base_core[ay0:ay1,ax0:ax1],core[ay0:ay1,ax0:ax1]],axis=1)),dict(coreBox=box,layout='before left; after right'))
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Local internal guide-boundary registration, bounded additive RGB correction, and two same-coordinate AI repair patches','source':ref(source),'sourceCore':ref(source_core),'outputs':{k:ref(OUT/f) for k,f in [('extended','extended4326.png'),('core','core4096.png'),('preview','preview1024.png')]},'sourceUnmodified':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'parameters':{'features':features,'pullMapping':'sourceY=outputY+flowY; sourceX=outputX','coreXFadeZero':196,'geometricDisplacementCap':10,'interpolation':'OpenCV INTER_CUBIC','nativeEnlargement':False,'additiveToneCapRGB':12,'toneFieldSmoothingSigmaY':24,'noUnderlyingRasterBlur':True,'AIpatches':ai_boxes,'AIpatchResizeOrWarp':False,'AIpatchAlphaBoundaryBlending':True},'actual':{'maxAbsFlowPixels':float(np.abs(dy).max()),'maxAbsToneFieldRGB':np.max(np.abs(tone),axis=(0,1)).tolist(),'maxActualAdditiveRGB':np.max(np.abs(out[:,x0:x1].astype(np.int16)-pre_tone.astype(np.int16)),axis=(0,1)).tolist(),'changedPixels':int(changed.sum()),'changedExtendedBox':bbox,'trueWestEdgeAndExteriorHaloPixelIdentical':bool(np.array_equal(out[:,:116],base[:,:116])),'allCoreX196AndGreaterPixelIdentical':bool(np.array_equal(out[:,311:],base[:,311:])),'relayROIUntouched':True,'east230PixelIdentical':bool(np.array_equal(out[:,-230:],base[:,-230:]))},'AI':{'file':ref(ai_file),'generationRecord':ref(OWN/'native/r04_c01.png.generation.json'),'actualModel':None,'actualQuality':None,'sourceGeometryAuthoring':'AI fixes absent/truncated local contours; color/flow pass does not pretend to recreate them.','selection':'Only two bounded source-native patches used; all other AI output pixels discarded from composition.'},'evidence':{k:ref(OUT/f) for k,f in [('flowAndCorrection','flow-correction.npz'),('delta','delta.npz'),('changedMask','changed-mask.png'),('AIalphaMask','ai-alpha-mask.png'),('geometryMask','geometry-mask.png'),('toneMask','tone-mask.png')]},'qa':qa,'script':ref(Path(__file__)),'resamplingDeclaration':'Original4326 dimensions maintained with no enlargement. Bounded existing-geometry subpixel remap occurs only where flow is nonzero. AI patches are copied at identical native coordinates with8px recorded alpha boundary blending, never resized. Preview alone is downsampled.','reviewStatus':'pending_actual_before_after_visual_review'}
# The AI pass is not an additive-tone correction; report its change separately.
manifest['actual']['maxActualAdditiveRGB']=np.max(np.abs(np.clip(np.rint(pre_tone.astype(np.float32)+tone),0,255).astype(np.int16)-pre_tone.astype(np.int16)),axis=(0,1)).tolist()
write(OUT/'processing.json',manifest)
print(json.dumps({'outputs':manifest['outputs'],'actual':manifest['actual'],'qaCount':len(qa)}))
