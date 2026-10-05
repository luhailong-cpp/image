from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

OUT=Path(__file__).resolve().parent
V1=OUT.parent/'r03_c02-v1'
TASK=OUT.parents[1]
ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
previous=read(V1/'preparation.json')
snapshot=previous['checkpointSnapshot']
fragment=Path(snapshot['fragment']['file'])
assert sha(fragment)==snapshot['fragment']['sha256']=='2b6c3188eaaea9329507903b29ddaa74965db3e6be20a7aaa8c5ea2867467c2f'
global_box=[37773,30605,39027,31859]
tile_box=[909,1933,2163,3187]
with Image.open(fragment) as im:
    im.load();assert im.size==(2278,1139)
    strip=im.convert('RGBA').crop((0,0,1254,230))
context=Image.new('RGBA',(1254,1254),(0,0,0,0))
context.paste(strip,(0,1024));context.save(OUT/'context.png')
assert sha(OUT/'context.png')=='52237b0e541bf8e2b51ed6271b5eb255f98ed5e4b85d46dedc7b778fb9c0c6d6'
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:
    im.load();assert im.size==(6144,6144)
    im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in global_box)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
prompt='''Use case: precise-object-edit / exact terrain outpainting.
Output one fully opaque 1254 by 1254 square game-map crop, exactly the camera, framing and scale of IMAGE 1. This is a close-up of the existing plaza pavement for 五行奇谈, not a complete scene.
IMAGE 1 is the authoritative EDIT TARGET. Its bottom 230 rows, y=1024..1253, are authentic completed native artwork and must remain unchanged. ONLY its transparent upper 1024 rows need newly painted map pixels. There is NO known left strip. Preserve every visible bottom contour, exact width and position of all gray slab insets and ivory/gold dividers, curve tangent, shading and scale. Do not widen or shift the columns. Near y=1024 the six principal gray-inset side contours are at approximately x=154,386,513,757,891,1157: the actual visible native pixels govern the precise endpoints. Continue those exact contours upward from those locations, never substitute the guide's bottom geometry.
IMAGE 2 is the canonical structural layout at exactly these world coordinates, used ONLY for the missing upper area. ESSENTIAL STRUCTURE: a BROAD HORIZONTAL IVORY STONE CROSS-BAND runs across this entire crop around y=700..790, joining the vertical ivory dividers and visibly separating the three upper gray stone inset slabs from the three lower gray inset slabs. It is a substantial warm ivory paving band about 90 pixels deep, with restrained sculpted edges and shadows. Repaint this actual broad cross-band as real continuous ivory stone. DO NOT reduce it to thin dark horizontal seams inside the gray slabs, and DO NOT continue the gray slabs uninterrupted across it. Keep the corresponding upper ivory boundary and the curved vertical divisions shown in image 2. Generate crisp new native painted surfaces; never copy enlarged blurry guide pixels.
IMAGE 3 is the user-approved PRIMARY STYLE reference only: bright clean rounded full Q/chibi Daoist fantasy handpainting, calm smooth ivory stone, restrained warm gold bevels and neutral slate insets. Do not import the UI, lettering, characters, icons, props or frame.
Preserve the entire image-1 bottom strip as closely as possible and solve the missing geometry ABOVE it. The alpha boundary y=1024 is not a physical object: do not put any new transverse joint, bevel, panel, shadow or straight material border at that height. The real broad horizontal cross-band belongs around y=700..790, NOT at the alpha boundary. Quiet surfaces, no new marble veins, cracks, speckles, mottled polygon texture or grunge. No buildings, foliage, figures, ornaments, text, watermark, collage or border. No zoom, rotation, crop shift, rescaling or camera change. Return only the exact opaque terrain crop with newly rendered upper-region detail at the highest visual finish available through the host.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
roles=['edit target: original bottom230 native pixels ONLY; top1024 transparent missing','canonical structural layout ONLY; broad ivory cross-band around y700..790 must be repainted','primary user-approved rendering style ONLY; no UI or characters imported']
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r03_c02','version':'v2','tile':'r08_c10','globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'knownPixels':1254*230,'missingPixels':1254*1024,'knownRegionLTRB':[0,1024,1254,1254],'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json')})
write('preparation.json',{'previousAttemptReview':info(V1/'visual-review.json'),'previousAttemptNative':info(V1/'native.png'),'previousNativeIsAuthoritative':False,'previousNativeSubmitted':False,'frozenCheckpointSnapshot':snapshot,'nativeInputs':[info(fragment)],'references':[{**info(p),'role':r} for p,r in zip(refs,roles)],'master':info(master),'sourceFragmentCropLTRB':[0,0,1254,230],'contextPasteXY':[0,1024],'nativeScale':1,'guidePixelsAllowedInFinal':False,'globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'targetedCorrection':'Restore broad ivory cross-band y700..790 and preserve actual bottom contour endpoints','otherTaskFilesModified':False})
write('context.png.generation.json',{'file':str(OUT/'context.png'),'sha256':sha(OUT/'context.png'),'derivedFrom':[info(fragment)],'operation':'Exact original-native crop [0,0,1254,230] pasted at [0,1024] on transparent1254 square. No resize.','newModelCalls':0})
write('layout-reference-only.png.generation.json',{'file':str(OUT/'layout-reference-only.png'),'sha256':sha(OUT/'layout-reference-only.png'),'derivedFrom':[info(master)],'operation':'Reference-only BICUBIC sample at same world coordinates. Pixels forbidden in final artwork.','sourceCropLTRB':[v*3/32 for v in global_box],'newModelCalls':0})
write('capability-evidence.json',{'sameProductionBatch':True,'taskCapabilityEvidence':info(TASK/'model-capability.json'),'taskCapabilitySnapshot':read(TASK/'model-capability.json'),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'actualModel':None,'actualQuality':None})
print(json.dumps({'out':str(OUT),'knownBottomPixels':1254*230,'missingUpperPixels':1254*1024,'contextSameAsOriginal':True}))
