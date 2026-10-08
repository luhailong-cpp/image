from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np, json, hashlib, datetime
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
OUT=ROOT/'r09_c08/canopy-repair/candidate-v1'
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
south=base.copy();south[115:320]=patch[627:832]
roi=np.zeros((1254,1254),bool);roi[115:320,:650]=True
oldleaf=green(base)&roi
newleaf=green(south)&roi
union=oldleaf|newleaf
# Two-pixel margin captures anti-aliased leaf outlines; binary copy, no feather or blur.
replacement=np.array(Image.fromarray(union.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)))>0
replacement &= roi
# Estimate per-column color offset using authentic northern leaf pixels against generated northern counterparts.
true_ref=north[4080:4096,1933:3187].astype(np.int16)
ai_ref=patch[611:627].astype(np.int16)
valid=green(true_ref)&green(ai_ref)
valid[:,650:]=False
delta=np.full((1254,3),np.nan,np.float32)
for x in range(650):
 v=valid[:,x]
 if v.sum()>=4: delta[x]=np.median((true_ref-ai_ref)[v,x],axis=0)
good=np.where(np.isfinite(delta[:,0]))[0]
assert len(good)>100
for k in range(3):
 delta[:,k]=np.interp(np.arange(1254),good,delta[good,k])
 # Smooth only the numeric correction field, never image pixels.
 delta[:,k]=np.convolve(np.pad(delta[:,k],(8,8),mode='edge'),np.ones(17)/17,mode='valid')
limits=np.array([16,40,16],np.float32)
delta=np.clip(delta,-limits,limits)
t=np.clip((np.arange(1254)-115)/205,0,1)
taper=1-(3*t*t-2*t*t*t)
taper[:115]=0;taper[320:]=0
requested=np.rint(taper[:,None,None]*delta[None,:,:]).astype(np.int16)
correctionmask=newleaf.copy()
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
np.savez_compressed(OUT/'rgb-fields.npz',requested_delta_rgb=requested,actual_delta_rgb=actual,column_delta_rgb=delta,taper_y=taper)
join=np.concatenate((north[3840:4096,1933:3187],out[115:371]),axis=0)
Image.fromarray(join).save(OUT/'qa-real-north1254x512.png')
Image.fromarray(out[:420,:700]).save(OUT/'qa-canopy-mask-surround700x420.png')
Image.fromarray(out[90:350,600:760]).save(OUT/'qa-right-mask-edge160x260.png')
Image.fromarray(out[270:380,:650]).save(OUT/'qa-bottom-mask-edge650x110.png')
j=join.astype(np.int16);stats={}
for name,x0,x1 in [('canopy',0,625),('left',0,150),('middle',150,350),('bright',350,515),('outer',515,625),('ground',650,1254)]:
 d=j[256,x0:x1]-j[255,x0:x1]
 stats[name]={'meanSignedRGBJump':d.mean(axis=0).tolist(),'meanAbsoluteChannelJump':float(np.abs(d).mean()),'maximumAbsoluteChannelJump':int(np.abs(d).max())}
manifest={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'candidate_only_pending_root_review_not_ingested','operation':'Native integer crop/patch with bounded per-channel RGB leaf correction. No new AI call, no image resampling, no image blur, no geometric transform.','sourceNativeImages':{'baseRejectedAttempt04':info(BASE),'newBridgeBuiltin':info(PATCH),'authenticNorthCore':info(NORTH),'authenticEastNative':info(EAST)},'pixelMappings':[{'source':'newBridgeBuiltin','sourceBox':[0,627,650,832],'destinationBox':[0,115,650,320],'maskedBy':'replacement-mask.png'},{'source':'authenticNorthCore','sourceBox':[1933,3981,3187,4096],'destinationBox':[0,0,1254,115]},{'source':'authenticEastNative','sourceBox':[115,115,230,1254],'destinationBox':[1139,115,1254,1254]}],'replacementMask':{'logic':'Union of original and new canopy green pixels, 2px binary outline margin, intersected with x0..649/y115..319','greenPredicate':'G>R+12 and G>B+12 and G>35','pixelCount':int(replacement.sum()),'outsideNativeHaloAndMaskPixelIdentityVerified':True},'rgbCorrection':{'onlyNewGreenLeafPixels':True,'maskPixelCount':int(correctionmask.sum()),'limitPerChannelRGB':[16,40,16],'actualMinPerChannelRGB':actual[correctionmask].min(axis=0).tolist(),'actualMaxPerChannelRGB':actual[correctionmask].max(axis=0).tolist(),'referenceTrueNorthBox':[1933,4080,3187,4096],'referenceGeneratedBoardBox':[0,611,1254,627],'fieldEstimation':'Per-column median authentic minus generated north RGB over green intersection; min4 valid rows; interpolate unsupported columns; 17-column moving average of numeric field only; clip per channel.','taper':'1-smoothstep((cell_y-115)/205), zero outside y115..319','noImageBlur':True,'fields':'rgb-fields.npz'},'unchangedNorthAndEastPixelIdentityVerified':True,'boundaryStatisticsDiagnosticOnly':stats,'knownUnresolvedGeometry':'Near cell x574..590, y115..116 right silhouette protrudes relative to actual north. No geometry edit applied.','outputFiles':{},'actualModel':None,'actualQuality':None,'generationParameters':'No generation call performed by this derivation; actual AI submission evidence remains bridge.receipt01.json and attempt04 records.','formalAccepted':False,'clientValidated':False,'visualReviewPending':True}
for p in sorted(OUT.iterdir()):
 if p.is_file():manifest['outputFiles'][p.name]={**info(p)}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'manifestSha256':sha(OUT/'manifest.json'),'candidate':info(OUT/'candidate1254.png'),'statistics':stats},ensure_ascii=False))

