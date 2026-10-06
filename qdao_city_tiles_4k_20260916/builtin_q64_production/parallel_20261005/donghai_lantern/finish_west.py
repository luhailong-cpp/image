"""Replay exact day ownership masks, bound RGB returns, then insert the day leaf repair.

No image generation, geometry flow, art resampling, state updates or publication.
Every write is restricted to own r08_c11/west-final. Original sources are read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import compose_west as cw

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'r08_c11/west-final'
OUT, QA, FIELDS = DEST/'output', DEST/'qa', DEST/'fields'
PLAN = ROOT/'r08_c11/west-repaired/leaf-conversion/integration-plan.json'
STEP, TOTAL, RADIUS = 18, 24, 256


def smooth(a, radius=12, axis=0):
    pads = [(0, 0)]*a.ndim
    pads[axis] = (radius, radius)
    b = np.pad(a, pads, mode='edge')
    zero = list(b.shape); zero[axis] = 1
    sums = np.concatenate((np.zeros(zero, np.float32), np.cumsum(b, axis=axis, dtype=np.float32)), axis=axis)
    left, right = [slice(None)]*a.ndim, [slice(None)]*a.ndim
    left[axis], right[axis] = slice(None, -2*radius-1), slice(2*radius+1, None)
    return (sums[tuple(right)]-sums[tuple(left)])/(2*radius+1)


def difference_field(a, b):
    difference = np.clip(b.astype(np.float32)-a.astype(np.float32), -72, 72)
    for _ in range(3):
        difference = smooth(smooth(difference, axis=0), axis=1)
    return difference


def weight(distance, radius=RADIUS):
    w = np.clip(1-np.abs(distance)/radius, 0, 1)
    return w*w*(3-2*w)


def field_record(label, metadata, **arrays):
    path = cw.writable(FIELDS/f'{label}.npz')
    np.savez_compressed(path, **arrays)
    return {'id':label, 'field':cw.info(path), **metadata}


def longitudinal_join(base, incoming, alpha, label):
    # Exact transpose makes the generic vertical overlap operation horizontal.
    base, incoming, alpha = base.transpose(1,0,2).copy(), incoming.transpose(1,0,2).copy(), alpha.T
    overlap = alpha.shape[1]
    h, w = base.shape[:2]
    cw.require(base.shape[0] == incoming.shape[0] == alpha.shape[0], label)
    correction = np.clip(difference_field(base[:,-overlap:],incoming[:,:overlap])*.5,-STEP,STEP)
    offsets = np.argmax(alpha>=128,axis=1)
    origin = w-overlap
    x0, x1 = max(0,origin-RADIUS), min(origin+incoming.shape[1],origin+overlap+RADIUS)
    xs = np.arange(x0,x1)
    field = correction[:,np.clip(xs-origin,0,overlap-1)]*weight(xs[None,:]-origin-offsets[:,None])[...,None]
    old_base, old_incoming = base.copy(), incoming.copy()
    bend, nstart = min(x1,w), max(x0,origin)
    base[:,x0:bend] = np.rint(np.clip(base[:,x0:bend].astype(np.float32)+field[:,:bend-x0],0,255)).astype(np.uint8)
    incoming[:,nstart-origin:x1-origin] = np.rint(np.clip(incoming[:,nstart-origin:x1-origin].astype(np.float32)-field[:,nstart-x0:],0,255)).astype(np.uint8)
    bd = base[:,x0:bend].astype(np.int16)-old_base[:,x0:bend].astype(np.int16)
    nd = incoming[:,nstart-origin:x1-origin].astype(np.int16)-old_incoming[:,nstart-origin:x1-origin].astype(np.int16)
    report = field_record(label,{'orientation':'horizontal','overlapPixels':overlap,'radiusPixels':RADIUS,'maximumPerSourceChannelDelta':int(max(np.abs(bd).max(),np.abs(nd).max()))},
        base_delta_rgb=bd.astype(np.int8),incoming_delta_rgb=nd.astype(np.int8),
        base_interval_y=np.array([x0,bend]),incoming_interval_y=np.array([nstart-origin,x1-origin]),
        seam_offsets=offsets,day_alpha=alpha.T)
    result = np.concatenate((base[:,:-overlap],cw.blend(base[:,-overlap:],incoming[:,:overlap],alpha),incoming[:,overlap:]),axis=1)
    return result.transpose(1,0,2), report


def insertion_match(strip, base, alpha, side):
    # Keep the old c10/c11 base fixed. Only the new strip approaches its tone;
    # therefore correction never leaks past the day-authorized insertion rect.
    old = strip.copy()
    overlap = alpha.shape[1]
    origin = 0 if side=='left' else cw.PATCH-overlap
    existing = base[:,cw.X0+origin:cw.X0+origin+overlap]
    correction = np.clip(difference_field(strip[:,origin:origin+overlap],existing),-TOTAL,TOTAL)
    offsets = np.argmax(alpha>=128,axis=1)
    xs = np.arange(cw.PATCH)
    field = correction[:,np.clip(xs-origin,0,overlap-1)]*weight(xs[None,:]-origin-offsets[:,None])[...,None]
    strip = np.rint(np.clip(strip.astype(np.float32)+field,0,255)).astype(np.uint8)
    delta = strip.astype(np.int16)-old.astype(np.int16)
    report = field_record('insert-'+side,{'orientation':'vertical','overlapPixels':overlap,'radiusPixels':RADIUS,'oldBaselineColorChanged':False,'maximumPerSourceChannelDelta':int(np.abs(delta).max())},
        strip_delta_rgb=delta.astype(np.int8),seam_offsets=offsets,day_alpha=alpha)
    return strip, report


def matched_four(base, patches, masks, original):
    strip, reports = patches[0].copy(), []
    for i in range(1,4):
        strip, report = longitudinal_join(strip,patches[i],masks[f'strip-s{i}-s{i+1}'],f'strip-s{i}-s{i+1}')
        reports.append(report)
    for side in ('left','right'):
        strip, report = insertion_match(strip,base,masks['insert-'+side],side)
        reports.append(report)
    result = base.copy()
    result[:,cw.X0:cw.X1] = strip
    result[:,cw.X0:cw.X0+cw.EDGE] = cw.blend(base[:,cw.X0:cw.X0+cw.EDGE],strip[:,:cw.EDGE],masks['insert-left'])
    result[:,cw.X1-cw.EDGE:cw.X1] = cw.blend(strip[:,-cw.EDGE:],base[:,cw.X1-cw.EDGE:cw.X1],masks['insert-right'])
    delta = np.clip(result[:,cw.X0:cw.X1].astype(np.int16)-original[:,cw.X0:cw.X1].astype(np.int16),-TOTAL,TOTAL).astype(np.int8)
    result[:,cw.X0:cw.X1] = (original[:,cw.X0:cw.X1].astype(np.int16)+delta.astype(np.int16)).astype(np.uint8)
    final_field = field_record('four-patch-applied-delta',{'pairRectXYXY':[cw.X0,0,cw.X1,cw.H],'maximumFinalChannelDelta':int(np.abs(delta).max())},delta_rgb=delta)
    return result,reports,final_field


def load_leaf(original):
    plan = cw.read(PLAN)
    for k in ('dayRepairManifest','baseManifest','basePair','exactDayMask','exactDayMaskNpz','prompt'):
        cw.check(plan[k]['file'],plan[k]['sha256'])
    cw.require(np.array_equal(original,cw.rgb(plan['basePair']['file'],(cw.W,cw.H))),'Four-patch replay differs from recorded candidate')
    day = cw.read(plan['dayRepairManifest']['file'])
    cw.require(day['pairRectXYXY']==plan['replacementPairRectXYXY'] and day['sourceCropXYXY']==plan['outputNativeCropXYXY'],'Leaf geometry differs')
    cw.require(day['combinedMask']==plan['exactDayMask'] and day['combinedMaskNpz']==plan['exactDayMaskNpz'],'Leaf mask contract differs')
    native = Path(plan['expectedNativeDestination']); record_path = Path(str(native)+'.generation.json'); record = cw.read(record_path)
    cw.check(native,record['sha256']); cw.check(record['evidence']['toolResultSourcePath'],record['sha256'])
    cw.require(record['resizedAfterGeneration'] is False and record['globalRectXYWH']==plan['globalNativeRectXYWH'],'Leaf source resampled/wrong location')
    for ref,submitted in zip(record['references'],record['submittedParameters']['referenced_image_paths']):
        cw.check(ref['file'],ref['sha256']);cw.require(cw.same(ref['file'],submitted),'Leaf reference order differs')
    cw.require(record['references']==plan['references'],'Leaf references differ from plan')
    cw.require(record['geometryMatchedTo']['sha256']==day['generatedEdit']['sha256'],'Leaf does not bind latest day geometry')
    cw.require(Path(record['prompt']).read_text(encoding='utf-8-sig').strip()==record['submittedParameters']['prompt'].strip(),'Leaf prompt differs')
    alpha = np.asarray(Image.open(plan['exactDayMask']['file'])).copy()
    with np.load(plan['exactDayMaskNpz']['file'],allow_pickle=False) as archive:
        cw.require(set(archive.files)=={'alpha','pair_rect'} and np.array_equal(archive['alpha'],alpha),'Leaf NPZ differs from PNG alpha')
        cw.require(archive['pair_rect'].tolist()==plan['replacementPairRectXYXY'],'Leaf NPZ rectangle differs')
    x0,y0,x1,y1=plan['outputNativeCropXYXY']
    pixels = cw.rgb(native,(1254,1254))[y0:y1,x0:x1].copy()
    cw.require(pixels.shape[:2]==alpha.shape==(400,256),'Wrong leaf crop dimensions')
    return pixels,alpha,plan,{'native':cw.info(native),'record':cw.info(record_path),'plan':cw.info(PLAN),'dayManifest':plan['dayRepairManifest'],'mask':plan['exactDayMask'],'maskNpz':plan['exactDayMaskNpz']}


def integrate_leaf(base,pixels,alpha,plan):
    x0,y0,x1,y1=plan['replacementPairRectXYXY']
    result=base.copy();result[y0:y1,x0:x1]=cw.blend(base[y0:y1,x0:x1],pixels,alpha)
    return result


def extra_qa(result,sources):
    image=Image.fromarray(result);items=[]
    def crop(name,box,**extra):
        items.append(cw.save_image(QA/(name+'.png'),image.crop(box),{'derivedFrom':sources,'pairRectXYXY':list(box),'pixelScale':1,'visualReview':'pending',**extra}))
    # Includes every possible seam position, all correction falloff, and untouched context.
    for side,center in (('left',cw.X0+75),('right',cw.X1-75)):
        for part in range(4):crop(f'attachment-{side}-return-part{part+1:02}',[center-448,part*1024,center+448,(part+1)*1024],coversFullCorrectionReturn=True)
    for i,y in enumerate(cw.STARTS[1:],1):
        overlap=230 if i<3 else 460
        crop(f'longitudinal-{i}-return',[cw.X0,y-RADIUS,cw.X1,min(cw.H,y+overlap+RADIUS)],coversFullCorrectionReturn=True)
    crop('leaf-return-context',[3712,1696,4480,2608])
    crop('leaf-insertion-left',[3936,1920,4032,2384])
    crop('leaf-insertion-right',[4160,1920,4256,2384])
    crop('leaf-insertion-top',[3936,1920,4256,2048])
    crop('leaf-insertion-bottom',[3936,2256,4256,2384])
    return items


def main():
    cw.DEST,cw.OUT,cw.QA,cw.MASKS=DEST,OUT,QA,DEST/'masks'
    for directory in (OUT,QA,FIELDS):directory.mkdir(parents=True,exist_ok=True)
    day,contract,masks,seams=cw.load_day_contract()
    base,baselines,patches,sources=cw.load_inputs(day)
    original=cw.compose(base,patches,masks)
    leaf,leaf_alpha,plan,leaf_info=load_leaf(original)
    tone,reports,final_field=matched_four(base,patches,masks,original)
    result=integrate_leaf(tone,leaf,leaf_alpha,plan)
    cw.require(np.array_equal(result[:,:cw.X0],base[:,:cw.X0]) and np.array_equal(result[:,cw.X1:],base[:,cw.X1:]),'Pixels escaped west repair region')
    # A replay delta relative to the exact uncorrected five-source composition.
    five=integrate_leaf(original,leaf,leaf_alpha,plan)
    delta=result[:,cw.X0:cw.X1].astype(np.int16)-five[:,cw.X0:cw.X1].astype(np.int16)
    cw.require(np.abs(delta).max()<=TOTAL,'Final RGB correction exceeds bound')
    full_field=field_record('five-source-final-applied-delta',{'pairRectXYXY':[cw.X0,0,cw.X1,cw.H],'maximumChannelDelta':int(np.abs(delta).max())},delta_rgb=delta.astype(np.int8))
    dependencies=baselines+sources+[leaf_info['native']]
    common={'derivedFrom':dependencies,'dayGeometryContract':contract,'daySeams':seams,'leafIntegration':leaf_info,'colorCorrection':True,'colorCorrectionField':full_field,'geometryFlow':False,'spatialResampling':False,'formalAccepted':False,'visualReview':'pending'}
    outputs=[]
    for name,pixels,rect in (('pair-r08_c10-c11',result,[0,0,cw.W,cw.H]),('r08_c10',result[:,:cw.H],[0,0,cw.H,cw.H]),('r08_c11',result[:,cw.H:],[cw.H,0,cw.W,cw.H])):
        saved=cw.save_image(OUT/(name+'.png'),pixels,{**common,'pairRectXYXY':rect,'globalOriginXY':list(cw.ORIGIN)})
        cw.require(np.array_equal(cw.rgb(saved['file'],(pixels.shape[1],pixels.shape[0])),pixels),'Saved PNG differs')
        outputs.append({'id':name,**saved})
    preview=cw.save_image(OUT/'preview-1024.png',Image.fromarray(result).resize((1024,512),Image.Resampling.LANCZOS),{'derivedFrom':outputs[:1],'operation':'Downscaled overview only','resized':True,'finalArt':False,'notNativePixelQA':True})
    qa=cw.write_qa(result,outputs)+extra_qa(result,outputs)
    for source in dependencies:cw.check(source['file'],source['sha256'])
    manifest={**common,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':cw.info(__file__),'status':'complete-pixel-candidates-pending-native-visual-review','outputs':outputs,'preview':preview,'qa':qa,'toneOperations':reports,'fourPatchToneField':final_field,'pixelVerification':{'outsideWestRectExactlyIdentical':True,'outsideWestRectChangedPixels':0,'authorizedPairRectXYXY':[cw.X0,0,cw.X1,cw.H],'c11OutsideLocalWestX627ExactlyPreserved':True,'savedPngPixelsMatchComputed':True,'maximumToneChannelDeltaFromUncorrectedFiveSourceComposition':int(np.abs(delta).max())},'leafCrop':plan['outputNativeCropXYXY'],'leafRect':plan['replacementPairRectXYXY'],'exactDayLeafAlpha':True,'sourcePngBytesUnchanged':True,'globalStateModified':False,'wholeCityComplete':False}
    cw.save_json(OUT/'west-final-manifest.json',manifest)
    print(json.dumps({'outputs':outputs,'qaCount':len(qa),'maximumToneChannelDelta':int(np.abs(delta).max()),'manifest':str(OUT/'west-final-manifest.json')},indent=2))


if __name__=='__main__':main()
