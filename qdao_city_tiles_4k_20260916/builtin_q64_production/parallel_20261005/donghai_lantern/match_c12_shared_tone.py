"""Bounded RGB matching of native, already drawn overlap pixels.

Uses the exact day seam masks; changes color only. No displacement, artwork
filter, resizing, texture generation or registration. Full applied integer
correction fields and source hashes are retained for inspection and replay.
"""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import assemble_c12_shared as shared

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'r08_c12/tone-assembly/output'
QA = OUT.parent / 'qa'
FIELDS = OUT.parent / 'fields'
RADIUS = 256
STEP_LIMIT = 18
TOTAL_LIMIT = 24

def smooth_box(a, radius, axis):
    pads = [(0, 0)] * a.ndim
    pads[axis] = (radius, radius)
    b = np.pad(a, pads, mode='edge')
    zero = list(b.shape); zero[axis] = 1
    sums = np.concatenate((np.zeros(zero, np.float32), np.cumsum(b, axis=axis, dtype=np.float32)), axis=axis)
    left = [slice(None)] * a.ndim; right = left.copy()
    width = radius * 2 + 1
    left[axis] = slice(None, -width); right[axis] = slice(width, None)
    return (sums[tuple(right)] - sums[tuple(left)]) / width

def append(base, incoming, alpha, label, orientation):
    # All joins are calculated in vertical orientation; transposition is exact.
    if orientation == 'horizontal':
        base, incoming, alpha = base.transpose(1, 0, 2), incoming.transpose(1, 0, 2), alpha.T
    h, w = base.shape[:2]
    left = base[:, -230:].astype(np.float32)
    right = incoming[:, :230].astype(np.float32)
    difference = np.clip(right - left, -72, 72)
    # Smooth the correction field, never the underlying artwork.
    for _ in range(3):
        difference = smooth_box(smooth_box(difference, 16, 0), 16, 1)
    correction = np.clip(difference * .5, -STEP_LIMIT, STEP_LIMIT)
    offsets = np.argmax(alpha >= 128, axis=1).astype(np.int32)
    origin = w - 230
    x0, x1 = max(0, origin - RADIUS), min(w + 1024, origin + 230 + RADIUS)
    xs = np.arange(x0, x1)
    distance = np.abs(xs[None, :] - (origin + offsets[:, None]))
    weights = np.clip(1 - distance / RADIUS, 0, 1)
    weights = weights * weights * (3 - 2 * weights)
    field = correction[:, np.clip(xs - origin, 0, 229)] * weights[:, :, None]
    old_base, old_new = base.copy(), incoming.copy()
    # x coordinates are in the combined image. Each source approaches the
    # midpoint appearance in the overlap then returns smoothly to original RGB.
    base_start, base_end = x0, min(x1, w)
    new_start, new_end = max(x0, origin), min(x1, origin + incoming.shape[1])
    base[:, base_start:base_end] = np.rint(np.clip(base[:, base_start:base_end].astype(np.float32) + field[:, :base_end-x0], 0, 255)).astype(np.uint8)
    incoming[:, new_start-origin:new_end-origin] = np.rint(np.clip(incoming[:, new_start-origin:new_end-origin].astype(np.float32) - field[:, new_start-x0:new_end-x0], 0, 255)).astype(np.uint8)
    base_delta = base[:, base_start:base_end].astype(np.int16) - old_base[:, base_start:base_end].astype(np.int16)
    new_delta = incoming[:, new_start-origin:new_end-origin].astype(np.int16) - old_new[:, new_start-origin:new_end-origin].astype(np.int16)
    assert max(np.abs(base_delta).max(), np.abs(new_delta).max()) <= STEP_LIMIT
    f = FIELDS / f'{label}.npz'
    np.savez_compressed(f, base_delta_rgb=base_delta.astype(np.int8), incoming_delta_rgb=new_delta.astype(np.int8),
                        base_interval_x=np.array([base_start, base_end]), incoming_interval_x=np.array([new_start-origin, new_end-origin]),
                        seam_offsets=offsets, orientation=np.array(orientation))
    result = np.concatenate((base[:, :-230], shared.blend(base[:, -230:], incoming[:, :230], alpha), incoming[:, 230:]), axis=1)
    if orientation == 'horizontal': result = result.transpose(1, 0, 2)
    report = {'id': label, 'orientation': orientation, 'radiusFromDaySeamPixels': RADIUS, 'perStepLimitRGB': STEP_LIMIT,
              'actualMaximumCorrectionRGB': int(max(np.abs(base_delta).max(), np.abs(new_delta).max())),
              'correctionField': {'file': str(f), 'sha256': shared.sha(f)}, 'geometricDisplacement': 0, 'artworkResampled': False,
              'correctionFieldSmoothing': 'Three radius16 box passes per axis, applied to RGB difference only; not image blur'}
    return result, report

def main():
    OUT.mkdir(parents=True, exist_ok=True); QA.mkdir(parents=True, exist_ok=True); FIELDS.mkdir(parents=True, exist_ok=True)
    arrays, day, sources, day_manifest, manifest_hash = shared.validate_inputs()
    masks, mask_evidence = shared.load_day_masks(day_manifest)
    day_replay, _ = shared.assemble(day, masks)
    expected_day = shared.load_rgb(day_manifest['extendedContext']['file'], day_manifest['extendedContext']['sha256'], (4326,4326))
    shared.require(np.array_equal(day_replay, expected_day), 'Exact day mask pixel replay failed')
    del day, day_replay, expected_day
    original, _ = shared.assemble(arrays, masks)
    source_manifest_path = ROOT/'r08_c12/shared-assembly/output/shared-assembly-manifest.json'
    source_manifest = shared.read(source_manifest_path)
    baseline = shared.load_rgb(source_manifest['extendedContext']['file'], source_manifest['extendedContext']['sha256'], (4326,4326))
    shared.require(np.array_equal(original, baseline), 'Saved shared assembly is not the exact baseline for tonal correction')
    del baseline
    rows, reports = [], []
    for row in range(1, 5):
        combined = arrays[row, 1].copy()
        for column in range(2, 5):
            label = f'vertical_r{row:02}_c{column-1:02}_c{column:02}'
            combined, report = append(combined, arrays[row, column].copy(), masks[label], label, 'vertical'); reports.append(report)
        rows.append(combined)
    combined = rows[0]
    for row in range(2, 5):
        label = f'horizontal_r{row-1:02}_r{row:02}'
        combined, report = append(combined, rows[row-1], masks[label], label, 'horizontal'); reports.append(report)
    delta = np.clip(combined.astype(np.int16)-original.astype(np.int16), -TOTAL_LIMIT, TOTAL_LIMIT).astype(np.int8)
    combined = (original.astype(np.int16) + delta.astype(np.int16)).astype(np.uint8)
    support = np.zeros((4326,4326), dtype=bool)
    # The seam is within each 230-wide overlap; the field extends at most256
    # pixels beyond it. Keep an explicit conservative support for verification.
    for boundary in (1024,2048,3072):
        support[:,boundary-RADIUS:boundary+230+RADIUS] = True
        support[boundary-RADIUS:boundary+230+RADIUS,:] = True
    shared.require(not np.any(delta[~support]), 'Tone changed pixels outside local seam support')
    actual_mask = np.any(delta != 0, axis=2)
    mask_path = FIELDS/'final-applied-delta-mask.png'
    Image.fromarray(actual_mask.astype(np.uint8)*255).save(mask_path)
    f = FIELDS / 'final-applied-delta-rgb.npz'; np.savez_compressed(f, delta_rgb=delta)
    assert np.array_equal(combined.astype(np.int16), original.astype(np.int16) + delta.astype(np.int16))
    shared.OUT, shared.QA = OUT, QA
    helper = shared.load_helpers()
    common = {'operation':'Bounded additive RGB matching along exact shared day seams', 'derivedFrom':sources,
              'dayMasks':mask_evidence, 'dayManifest':{'file':str(shared.DAY_MANIFEST), 'sha256':manifest_hash},
              'artResampled':False, 'artUpscaled':False, 'imageBlur':False, 'geometricDisplacementPixels':0,
              'completePixelCandidate':True, 'finalArt':False, 'formalAccepted':False,
              'maximumFinalChannelChange':int(np.abs(delta).max()), 'finalAppliedCorrectionField':{'file':str(f),'sha256':shared.sha(f)},
              'perStepChannelLimit':STEP_LIMIT, 'maximumPermittedFinalChannelChange':TOTAL_LIMIT,
              'actualCorrectionMask':{'file':str(mask_path),'sha256':shared.sha(mask_path)},
              'outsideLocalSeamSupportPixelIdentical':True, 'dayReplayPixelIdentical':True,
              'sharedBaselineManifest':{'file':str(source_manifest_path),'sha256':shared.sha(source_manifest_path)},
              'operations':reports, 'visualReview':'pending'}
    ext = Image.fromarray(combined); core = ext.crop((115,115,4211,4211))
    extended = helper.save_image(OUT/'extended-context.png', ext, {**common,'globalRectXYWH':[44941,28557,4326,4326]})
    candidate = helper.save_image(OUT/'r08_c12.png', core, {**common,'globalRectXYWH':[45056,28672,4096,4096]})
    preview = helper.save_image(OUT/'preview-1024.png', core.resize((1024,1024),Image.Resampling.LANCZOS),
                                {'operation':'Downscaled overview only','derivedFrom':[candidate],'finalArt':False,'notNativePixelQA':True})
    west, west_info = helper.load_west()
    qa = helper.export_qa(core,candidate,west,west_info)
    # +/-448 includes maximum day-path offset115 + correction radius256 and returns.
    for axis in ('x','y'):
        for boundary in (1024,2048,3072):
            for part in range(4):
                box = (boundary-448,part*1024,boundary+448,(part+1)*1024) if axis=='x' else (part*1024,boundary-448,(part+1)*1024,boundary+448)
                qa.append(helper.save_image(QA/f'{axis}{boundary}-return-part{part+1:02}.png',core.crop(box),
                    {'operation':'Native exact crop of full correction-and-return band','derivedFrom':[candidate],
                     'sourceCropXYXY':list(box),'resized':False,'finalArt':False,'coversFullCorrectionSupport':True}))
    manifest={**common,'candidate':candidate,'extendedContext':extended,'preview':preview,'qa':qa,
              'westSource':west_info,'stateFilesModified':False,
              'qaCoverage':{'internalFullLength256Bands':6,'internalFullLength896Bands':6,'returnBandSegments':24,
                            'internalJunctions':9,'tileCorners':4,'westCommonEdgeLength':4096,'allVisualReviewPending':True},
              'changedPixels':int(np.any(delta!=0,axis=2).sum()), 'script':{'file':str(Path(__file__)),'sha256':shared.sha(__file__)}}
    for source in sources:
        shared.require(shared.sha(source['file']) == source['sha256'], 'Native source changed during tone export')
    shared.require(shared.sha(shared.DAY_MANIFEST) == manifest_hash, 'Day manifest changed during tone export')
    saved = shared.load_rgb(extended['file'], extended['sha256'], (4326,4326))
    shared.require(np.array_equal(saved.astype(np.int16), original.astype(np.int16)+delta.astype(np.int16)), 'Saved tone field replay failed')
    manifest['savedExtendedPixelsExactlyEqualBaselinePlusRecordedDelta'] = True
    helper.atomic_write(OUT/'tone-assembly-manifest.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'candidate':candidate,'maximumFinalChannelChange':int(np.abs(delta).max()),'qaImages':len(qa)},indent=2))

if __name__=='__main__': main()
