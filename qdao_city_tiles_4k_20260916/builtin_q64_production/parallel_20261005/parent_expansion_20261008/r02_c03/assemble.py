from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
req=read(R/'request.json')
context=np.array(Image.open(R/'context.png').convert('RGBA'))
native=np.array(Image.open(R/'native.png').convert('RGB'))
repair=np.array(Image.open(R/'surface-repair/native.png').convert('RGB'))
assert context.shape==(1254,1254,4) and native.shape==repair.shape==(1254,1254,3)
missing=context[:,:,3]==0
assert int(missing.sum())==813056 and np.all(np.isin(context[:,:,3],[0,255]))
y,x=np.mgrid[:1254,:1254]

# Only native regenerated surface pixels inside the gold face are used. No
# contour is painted procedurally and no image is scaled, warped, or blurred.
u=x-(95+0.38*y)
def ramp(v,lo,hi,feather):
    return np.clip(np.minimum((v-lo)/feather,(hi-v)/feather),0,1)
surface=np.maximum(ramp(u,-59,59,9)*ramp(y+0.34*(x-220),250,397,14),
                   ramp(u,-59,59,9)*ramp(y+0.34*(x-380),635,821,14))
surface_byte=np.rint(surface*255).astype(np.uint8)
base=native.astype(np.uint32);fixed=repair.astype(np.uint32)
corrected=((base*(255-surface_byte[:,:,None])+fixed*surface_byte[:,:,None]+127)//255).astype(np.uint8)

# The source has exactly this rectangular missing area. Blend only into at
# most 32 existing pixels surrounding it. Hole interiors stay at 1:1 native.
expected=(x<1024)&(y>=230)&(y<1024)
assert np.array_equal(missing,expected)
distance=np.hypot(np.maximum(x-1023,0),np.maximum(np.maximum(230-y,y-1023),0))
weight=np.rint(np.clip(1-distance/32,0,1)*255).astype(np.uint8)
weight[missing]=255
# One pre-existing rectangular white-trim step lies42px below the hole.
# Reuse this call's continuous native trim in a tight return repair; no new
# geometry is drawn by code, and the surrounding original context is retained.
step_weight=np.rint(ramp(x,194,368,18)*ramp(y,1028,1111,18)*255).astype(np.uint8)
weight=np.maximum(weight,step_weight)
old=context[:,:,:3].astype(np.uint32)
joined=((old*(255-weight[:,:,None])+corrected.astype(np.uint32)*weight[:,:,None]+127)//255).astype(np.uint8)
assert np.array_equal(joined[weight==0],context[:,:,:3][weight==0])
assert np.array_equal(joined[missing],corrected[missing])

sources=[{'file':str(R/f),'sha256':sha(R/f),'generationRecord':str(R/(f+'.generation.json'))} for f in ['context.png','native.png','surface-repair/native.png']]
def save(name,array,operation,extra=None):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.fromarray(array);im.save(p)
    rec={'file':str(p),'sha256':sha(p),'createdAt':datetime.now(timezone.utc).isoformat(),
         'width':im.width,'height':im.height,'format':'PNG','derivedFrom':sources,'operation':operation,
         'nativeScale':1,'upscaled':False,'formalAccepted':False}
    if extra: rec.update(extra)
    Path(str(p)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'file':str(p),'sha256':rec['sha256'],'generationRecord':str(p)+'.generation.json'}
surface_ref=save('surface-mask.png',surface_byte,'Analytic mask selects only two AI-regenerated surface corrections; 9/14px opacity transition; no image blurring.')
weight_ref=save('join-mask.png',weight,'Native missing-region mask plus at most32px return transition, and a separately recorded194,1028,368,1111 trim repair with18px transition.')
joined_ref=save('joined.png',joined,'Native1:1 gap fill using generated detail, two AI surface-only corrections,32px texture returns and a tight pre-existing trim-step repair with18px transition; no scaling, geometric registration or blur.',{'windowTileLocalLTRB':req['windowTileLocalLTRB'],'newNativeCoveragePixels':int(missing.sum())})
patch_ref=save('newfilled-patch.png',np.dstack([corrected,weight]),'RGBA native patch to alpha-composite at exact tile-local window; alpha255 covers original missing region and limited alpha surrounds existing returns.',{'windowTileLocalLTRB':req['windowTileLocalLTRB'],'newNativeCoveragePixels':int(missing.sum()),'applicationRule':'RGBA alpha composite over the EXACT bound source context; do not paste full opaque square or overwrite child selection.'})

qa=[]
regions={'top-left':[0,166,420,300],'top-center':[360,166,780,300],'top-right':[720,166,1100,300],
         'bottom-left':[0,960,420,1100],'bottom-center':[360,960,780,1100],'bottom-right':[720,960,1100,1100],
         'right-upper':[960,166,1100,486],'right-center':[960,450,1100,770],'right-lower':[960,730,1100,1100],
         'surface-upper':[120,250,355,425],'surface-middle':[275,620,520,840],
         'old-trim-step-return':[160,1000,410,1140]}
for name,box in regions.items():
    x0,y0,x1,y1=box
    ref=save('qa/'+name+'.png',joined[y0:y1,x0:x1],'Native1:1 final joined crop, no resizing.',{'contextCropLTRB':box})
    qa.append(dict(ref,name=name,contextCropLTRB=box,actuallyViewed=False))
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'assembled_pending_native_visual_review','tile':'r08_c10','patch':'r02_c03',
    'sourceSelection':req['sourceSelection'],'sourceParts':req['parts'],'windowTileLocalLTRB':req['windowTileLocalLTRB'],'outputs':{'joined':joined_ref,'patch':patch_ref},
    'inputContext':sources[0],'nativeSources':sources[1:],'newNativeCoveragePixelsAgainstBoundSource':int(missing.sum()),
    'newCoverageContextLTRB':[0,230,1024,1024],'globalNewCoverageTileLocalLTRB':[1933,1139,2957,1933],
    'coverageMustBeDeduplicatedAgainstOtherParentPatches':True,'newCompleteTileCount':0,'formalAccepted':False,'wholeCityComplete':False,'childSelectionModified':False,
    'joinMask':weight_ref,'surfaceCorrectionMask':surface_ref,'geometricRegistration':{'applied':False,'maxDisplacementPixels':0,'resampling':'none','reason':'Diagnostic sharp-edge shift minima bottom/right atdy0; diagonal top ambiguity does not establish a rigid displacement. Inspect final returns before any correction.'},
    'textureFeatherPixels':32,'additionalKnownReturnRepair':{'issue':'Pre-existing rectangular white trim jump nearcontext230,1066','maskSupportLTRB':[194,1028,368,1111],'featherPixels':18,'source':'Original native generation continuous trim; no additional generation.'},
    'imageBlurApplied':False,'changedKnownPixels':int((np.any(joined!=context[:,:,:3],axis=2)&~missing).sum()),
    'knownPixelsUnchangedOutsideMask':True,'qa':qa,'limitations':['Left edge borders another missing parent patch and is not accepted against a neighboring final patch yet.','Only this local native patch and three existing return sides are reviewed; not whole4K internal QA.']}
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(R/'joined.png'),'newPixels':int(missing.sum()),'qaCrops':len(qa)}))
