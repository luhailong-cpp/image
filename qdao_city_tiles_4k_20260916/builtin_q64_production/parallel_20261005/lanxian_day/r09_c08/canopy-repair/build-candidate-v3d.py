from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, json, hashlib, datetime
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
OUT=ROOT/'r09_c08/canopy-repair/candidate-v3d'
BASE=Path('C:/Users/luyua/.codex/generated_images/01a11ab8-70d6-73e3-98b9-8233e86c8e74/exec-a3258e86-b156-4704-ac9d-90d9bfb10410.png')
PATCH=Path('C:/Users/luyua/.codex/generated_images/01a10baf-7a48-7811-ba55-23983983a89d/exec-1496dc29-aaaf-417f-9b76-03827f6b1428.png')
NORTH=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_day/triple_r08_c06_c08/output_v2/r08_c08.png')
EAST=ROOT/'r09_c08/native/r01_c04.png'
if not OUT.is_relative_to(ROOT): raise RuntimeError('Outside root')
if OUT.exists(): raise RuntimeError('Refuse overwrite')
OUT.mkdir()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(a): return hashlib.sha256(a.tobytes()).hexdigest()
def info(p): return {'file':str(p),'sha256':sha(p)}
def green(a):
 a=a.astype(np.int16)
 return (a[:,:,1]>a[:,:,0]+12)&(a[:,:,1]>a[:,:,2]+12)&(a[:,:,1]>35)
base=np.array(Image.open(BASE).convert('RGB')); patch=np.array(Image.open(PATCH).convert('RGB')); north=np.array(Image.open(NORTH).convert('RGB')); east=np.array(Image.open(EAST).convert('RGB'))
assert base.shape==patch.shape==east.shape==(1254,1254,3)
# Native board y627 maps to original cell y115. No resampling.
south=base.copy();south[115:350]=patch[627:862]
# Bounded 0..2px integer source-row registration only around the tiny right silhouette protrusion.
xs=np.arange(1254);ys=np.arange(1254)
def smooth01(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
xweight=smooth01((xs-540)/20)*(1-smooth01((xs-600)/25))
yweight=1-smooth01((ys-117)/18)
yweight[ys<115]=0;yweight[ys>=135]=0
geom_dy=np.rint(2*yweight[:,None]*xweight[None,:]).astype(np.int16)
geom_active=geom_dy>0
cy,cx=np.where(geom_active)
south[cy,cx]=patch[cy+512+geom_dy[cy,cx],cx]
roi=np.zeros((1254,1254),bool);roi[115:310,:640]=True
def leafconfidence(arr):
 cs=arr.astype(np.float32)
 c=np.clip((cs[:,:,1]-np.maximum(cs[:,:,0],cs[:,:,2])+6)/18,0,1)
 return c*c*(3-2*c)
newconf=leafconfidence(south);oldconf=leafconfidence(base)
# Strong foliage silhouette, not near-neutral color confidence; preserve a continuous exterior contour.
outer=(green(south)|green(base))&roi
closed=Image.fromarray(outer.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(5))
padded=Image.new('L',(1258,1258),0);padded.paste(closed,(2,2))
ImageDraw.floodfill(padded,(0,0),128)
replacement=np.array(padded)[2:-2,2:-2]!=128
restriction=np.zeros_like(replacement);restriction[115:312,:640]=True
replacement &= restriction
# Local native copy margin clears old left-edge silhouette fragments; no color processing of adjacent ground.
leftmargin=np.array(Image.fromarray(replacement.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(25)))>0
leftscope=np.zeros_like(replacement);leftscope[155:235,:105]=True
left_outline_addition=leftmargin&leftscope&~replacement
replacement |= left_outline_addition
lower_edge=np.full(1254,115,np.int16)
for x in range(640):
 rows=np.where(replacement[:,x])[0]
 if len(rows):lower_edge[x]=int(rows.max())+1
leaf_alpha=newconf.copy();leaf_alpha[~replacement]=0
# Estimate per-column color offset using authentic northern leaf pixels against generated northern counterparts.
true_ref=north[4094:4096,1933:3187].astype(np.int16)
ai_ref=south[115:117].astype(np.int16)
valid=green(true_ref)&green(ai_ref)
valid[:,640:]=False
delta=np.full((1254,3),np.nan,np.float32)
for x in range(640):
 v=valid[:,x]
 if v.sum()>=1: delta[x]=np.median((true_ref-ai_ref)[v,x],axis=0)
good=np.where(np.isfinite(delta[:,0]))[0]
assert len(good)>100
for k in range(3):
 delta[:,k]=np.interp(np.arange(1254),good,delta[good,k])
 # Smooth only the numeric correction field, never image pixels.
 dpad=np.pad(delta[:,k],(2,2),mode='edge')
 delta[:,k]=np.median(np.lib.stride_tricks.sliding_window_view(dpad,5),axis=1)
 delta[:,k]=np.convolve(np.pad(delta[:,k],(1,1),mode='edge'),np.ones(3)/3,mode='valid')
limits=np.array([32,64,32],np.float32)
delta=np.clip(delta,-limits,limits)
t=np.clip((np.arange(1254)-180)/170,0,1)
taper=1-(3*t*t-2*t*t*t)
taper[:115]=0;taper[350:]=0
# Extend boundary color correction as a two-dimensional numeric field. No source artwork is blurred.
reference_luma=np.maximum(south[115:117,:,1].astype(np.float32).mean(axis=0),32)
relative_delta=delta/reference_luma[:,None]
requested=np.zeros((1254,1254,3),np.int16)
for y in range(115,350):
 sigma=max(0.65,(y-115)*0.22)
 radius=max(2,int(np.ceil(sigma*3)))
 k=np.arange(-radius,radius+1,dtype=np.float32);k=np.exp(-0.5*(k/sigma)**2);k/=k.sum()
 sm=np.stack([np.convolve(np.pad(relative_delta[:,ch],(radius,radius),mode='edge'),k,mode='valid') for ch in range(3)],axis=1)
 # Scale offset by local leaf luminance to avoid darkening lower shadow leaves with a bright-leaf absolute correction.
 row=sm*south[y,:,1,None].astype(np.float32)*taper[y]*leaf_alpha[y,:,None]
 requested[y]=np.rint(np.clip(row,-limits,limits)).astype(np.int16)
correctionmask=leaf_alpha>0
requested[~correctionmask]=0
corrected=np.clip(south.astype(np.int16)+requested,0,255).astype(np.uint8)
actual=corrected.astype(np.int16)-south.astype(np.int16)
out=base.copy();out[replacement]=corrected[replacement]
# Exact native neighbor evidence; north has corner priority.
out[115:,1139:]=east[115:,115:230]
out[:115]=north[3981:4096,1933:3187]
assert np.array_equal(out[:115],north[3981:4096,1933:3187])
assert np.array_equal(out[115:,1139:],east[115:,115:230])
outside=(~replacement);outside[:115]=False;outside[115:,1139:]=False
assert np.array_equal(out[outside],base[outside])
Image.fromarray(out).save(OUT/'candidate1254.png')
Image.fromarray(replacement.astype(np.uint8)*255).save(OUT/'replacement-mask.png')
Image.fromarray(correctionmask.astype(np.uint8)*255).save(OUT/'rgb-correction-mask.png')
Image.fromarray(np.rint(leaf_alpha*255).astype(np.uint8)).save(OUT/'rgb-continuous-alpha.png')
Image.fromarray((geom_active&replacement).astype(np.uint8)*255).save(OUT/'geometry-mask.png')
Image.fromarray(left_outline_addition.astype(np.uint8)*255).save(OUT/'left-outline-extra-native-copy-mask.png')
np.savez_compressed(OUT/'rgb-fields.npz',requested_delta_rgb=requested,actual_delta_rgb=actual,column_delta_rgb=delta,taper_y=taper,geometry_source_dy=geom_dy,geometry_active_mask=geom_active&replacement,continuous_leaf_alpha=leaf_alpha,whole_crown_lower_edge=lower_edge,relative_boundary_delta_rgb=relative_delta,left_outline_addition=left_outline_addition)
join=np.concatenate((north[3840:4096,1933:3187],out[115:371]),axis=0)
Image.fromarray(join).save(OUT/'qa-real-north1254x512.png')
Image.fromarray(out[:420,:700]).save(OUT/'qa-canopy-mask-surround700x420.png')
Image.fromarray(out[90:380,600:760]).save(OUT/'qa-right-mask-edge160x290.png')
Image.fromarray(out[300:420,:700]).save(OUT/'qa-bottom-mask-edge700x120.png')
j=join.astype(np.int16);stats={}
for name,x0,x1 in [('canopy',0,625),('left',0,150),('middle',150,350),('bright',350,515),('outer',515,625),('ground',650,1254)]:
 d=j[256,x0:x1]-j[255,x0:x1]
 stats[name]={'meanSignedRGBJump':d.mean(axis=0).tolist(),'meanAbsoluteChannelJump':float(np.abs(d).mean()),'maximumAbsoluteChannelJump':int(np.abs(d).max())}
manifest={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'candidate_only_pending_root_review_not_ingested','operation':'Native integer crop/patch with bounded per-channel RGB leaf correction. No new AI call, no image scaling or blur. Bounded integer source-row registration 0..2px near the right canopy outline only.','sourceNativeImages':{'baseRejectedAttempt04':info(BASE),'newBridgeBuiltin':info(PATCH),'authenticNorthCore':info(NORTH),'authenticEastNative':info(EAST)},'pixelMappings':[{'source':'newBridgeBuiltin','sourceBox':[0,627,640,824],'destinationBox':[0,115,640,312],'maskedBy':'replacement-mask.png'},{'source':'authenticNorthCore','sourceBox':[1933,3981,3187,4096],'destinationBox':[0,0,1254,115]},{'source':'authenticEastNative','sourceBox':[115,115,230,1254],'destinationBox':[1139,115,1254,1254]}],'geometricRegistration':{'source':'newBridgeBuiltin','maximumSourceOffsetXY':[0,2],'sourceCoordinates':'patch x=cell x, patch y=cell y+512+geometry_source_dy','supportBoxCellXYXY':[540,115,625,135],'xWeight':'smoothstep((x-540)/20) * (1-smoothstep((x-600)/25))','yWeight':'1-smoothstep((y-117)/18), zero outside115..134','integerSampling':'round-to-nearest offset, exact source pixels, no interpolation','appliedOnlyInReplacementMask':True,'appliedPixelCount':int((geom_active&replacement).sum())},'replacementMask':{'logic':'Continuous filled whole-crown exterior from strong original/new foliage union (G>R+12,G>B+12,G>35); binary7px morphological closure bridges small foliage gaps,2px outline margin preserves native antialias; external flood fill closes interior holes. No per-column extension. Restrictx0..639/y115..311; lower trunk, gray block and flowerbed excluded.','leftEdgeAdditionalNativeCopy':{'scopeCellXYXY':[0,155,105,235],'maximumOutlineExpansionPixels':12,'mask':'left-outline-extra-native-copy-mask.png','pixelCount':int(left_outline_addition.sum()),'reason':'Remove isolated old green fragments and white holes at crop-left leaf silhouette by copying complete new native boundary and adjacent background.'},'alphaForColorOnly':'smoothstep(clamp((G-max(R,B)+6)/18,0,1)); continuous real-valued leaf confidence, zero outside rectangle','pixelCount':int(replacement.sum()),'outsideNativeHaloAndMaskPixelIdentityVerified':True},'rgbCorrection':{'onlyNewGreenLeafPixels':'Continuous leaf alpha including anti-alias transition; no hard predicate correction edge','maskPixelCount':int(correctionmask.sum()),'limitPerChannelRGB':[32,64,32],'actualMinPerChannelRGB':actual[correctionmask].min(axis=0).tolist(),'actualMaxPerChannelRGB':actual[correctionmask].max(axis=0).tolist(),'referenceTrueNorthBox':[1933,4094,3187,4096],'referenceActualSouthCellBox':[0,115,1254,117],'referenceActualSouthUsesRegisteredNativePatch':True,'fieldEstimation':'Per-column median authentic north final2 rows minus actual registered south first2 rows over green intersection; min1 valid row; interpolate unsupported columns; 5-column median then3-column mean of numeric correction field only; clip per channel.','spatialField':'Boundary column RGB offsets divided by source boundary mean G (floor32); row-wise Gaussian smoothing of numeric relative-color field, sigma=max(0.65,0.22*(cell_y-115)); then scaled by local source G, continuous leaf alpha and vertical taper; clamped per pixel/channel. Image pixels are never blurred.','taper':'Full correction weight y115..180, then1-smoothstep((cell_y-180)/170), zero outside y115..349; multiply by continuous leaf alpha','noImageBlur':True,'fields':'rgb-fields.npz'},'unchangedNorthAndEastPixelIdentityVerified':True,'boundaryStatisticsDiagnosticOnly':stats,'knownGeometryTarget':'Previous right silhouette protrusion near cell x574..590/y115..116 targeted by maximum2px integer source-row shift; pending actual visual review, not automatically accepted.','outputFiles':{},'actualModel':None,'actualQuality':None,'generationParameters':'No generation call performed by this derivation; actual AI submission evidence remains bridge.receipt01.json and attempt04 records.','formalAccepted':False,'clientValidated':False,'visualReviewPending':True}
for p in sorted(OUT.iterdir()):
 if p.is_file():manifest['outputFiles'][p.name]={**info(p)}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'manifestSha256':sha(OUT/'manifest.json'),'candidate':info(OUT/'candidate1254.png'),'statistics':stats},ensure_ascii=False))

