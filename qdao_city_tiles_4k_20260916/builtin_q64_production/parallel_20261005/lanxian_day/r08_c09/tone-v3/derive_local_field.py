"""Remove the visually confirmed spurious y3072 RGB correction locally.

No image filtering, resampling, warping, or geometry synthesis. Reconstruct the
affected band from candidate source plus the attenuated stored correction field.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

O = Path(__file__).resolve().parent
T = O.parent
V2 = T / 'tone-v2'
Q = O / 'qa'
Q.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):
    return {'file': str(p), 'sha256': sha(p)}

src_path = T / 'candidate/extended4326.png'
v2_path = V2 / 'extended4326.png'
field_path = V2 / 'y3072-correction.npy'
assert sha(src_path) == 'bfc3ccdd8bc4fafa4d2123af125adcbb7d0587485497e1dacde86586b7d4d18a'
assert sha(v2_path) == '2442528dfc63149279a441a6597796340c81a8a357a765f5fc2a59d411a5b407'
assert sha(field_path) == 'af861f64d438cca791974f020ab717af0b50a45f0201519c91f9d35a44cf482d'
src = np.array(Image.open(src_path).convert('RGB'))
v2 = np.array(Image.open(v2_path).convert('RGB'))
field = np.load(field_path)
assert field.shape == (384, 4326, 3)
ys = slice(3072 + 115 - 192, 3072 + 115 + 192)
reconstructed = np.rint(np.clip(src[ys].astype(np.float32) + field, 0, 255)).astype(np.uint8)
assert np.array_equal(reconstructed, v2[ys]), 'Band must contain only this stored pass'

# Pixel centers in core coordinates. Zero undo outside [1024,1600]; full
# undo on [1152,1472]. Cubic smoothstep has zero endpoint derivatives.
x = np.arange(4326, dtype=np.float32) - 115
rise = np.clip((x - 1024) / 128, 0, 1)
fall = np.clip((1600 - x) / 128, 0, 1)
rise = rise * rise * (3 - 2 * rise)
fall = fall * fall * (3 - 2 * fall)
undo = np.minimum(rise, fall).astype(np.float32)
mask = np.broadcast_to(undo[None, :], field.shape[:2]).copy()
adjustment = (-field * mask[:, :, None]).astype(np.float32)
v3_field = field + adjustment
v3 = v2.copy()
v3[ys] = np.rint(np.clip(src[ys].astype(np.float32) + v3_field, 0, 255)).astype(np.uint8)
changed = np.any(v3 != v2, axis=2)
yc, xc = np.where(changed)
assert np.array_equal(v3[ys, 115 + 1152:115 + 1473], src[ys, 115 + 1152:115 + 1473])
core = v3[115:4211,115:4211]
v2_core = v2[115:4211,115:4211]
assert np.array_equal(core[:,:320], v2_core[:,:320])
assert np.array_equal(core[:,3776:], v2_core[:,3776:])
assert not changed[:ys.start].any() and not changed[ys.stop:].any()
assert not changed[:, :115+1024].any() and not changed[:,115+1601:].any()

np.save(O / 'y3072-undo-mask.npy', mask)
np.save(O / 'y3072-field-adjustment.npy', adjustment)
np.save(O / 'y3072-correction.npy', v3_field)
Image.fromarray(np.rint(mask * 255).astype(np.uint8)).save(O / 'y3072-undo-mask.png')
Image.fromarray(v3).save(O / 'extended4326.png')
Image.fromarray(core).save(O / 'core4096.png')

checks = []
for name, box in [
    ('horizontal_y3072_part2_v2_v3', (1024, 2944, 2048, 3200)),
    ('horizontal_y3072_full_field_v2_v3', (1024, 2880, 2048, 3264)),
    ('intersection_r3_c1_v2_v3', (768, 2816, 1280, 3328)),
    ('horizontal_y3072_part2_candidate_v3', (1024, 2944, 2048, 3200)),
]:
    before = Image.fromarray(src[115:4211,115:4211] if 'candidate' in name else v2_core).crop(box)
    after = Image.fromarray(core).crop(box)
    board = Image.new('RGB', (before.width, before.height * 2))
    board.paste(before, (0, 0))
    board.paste(after, (0, before.height))
    p = Q / f'{name}.png'
    board.save(p)
    checks.append({'id': name, **rec(p), 'sourceBoxCoreXYXY': box,
        'sourceBoxWholeCityXYXY': [box[0]+32768, box[1]+28672, box[2]+32768, box[3]+28672],
        'layout': 'before_top_after_bottom', 'pixels': board.size,
        'operation': 'integer crop and paste', 'resampling': 'none'})

report = {
    'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
    'purpose': 'Remove visually confirmed new vertical tone stripe in tone-v2 near core x1304 across y3072.',
    'sources': {'candidateExtended': rec(src_path), 'toneV2Extended': rec(v2_path),
                'toneV2Core': rec(V2/'core4096.png'), 'y3072Field': rec(field_path)},
    'operation': 'Reconstruct only the y3072 band from original candidate source plus stored RGB field multiplied by (1-undo). No raster filtering, blur, geometric change, or resampling.',
    'maskDefinition': {
        'coordinateConvention': 'half-open boxes; x is integer core pixel coordinate; array field y0 corresponds core y2880; field x0 corresponds core x-115',
        'arrayShape': list(mask.shape), 'fieldBoxCoreXYXY': [-115,2880,4211,3264],
        'undoSupportCoreXYXY': [1025,2880,1600,3264],
        'undoPlateauXInclusive': [1152,1472], 'taperIntervalsX': [[1024,1152],[1472,1600]],
        'formula': 'undo=min(smoothstep(clamp((x-1024)/128)),smoothstep(clamp((1600-x)/128))); smoothstep(t)=t*t*(3-2*t)',
        'maskNpy': rec(O/'y3072-undo-mask.npy'), 'maskPngVisualization': rec(O/'y3072-undo-mask.png')},
    'adjustmentField': rec(O/'y3072-field-adjustment.npy'),
    'replacementY3072Field': rec(O/'y3072-correction.npy'),
    'maxAbsoluteFieldAdjustmentRGB': np.abs(adjustment).max(axis=(0,1)).tolist(),
    'maxActualPixelChangeFromV2RGB': np.abs(v3.astype(np.int16)-v2.astype(np.int16)).max(axis=(0,1)).tolist(),
    'changedPixelCount': int(changed.sum()),
    'actualChangedBoxCoreXYXY': [int(xc.min())-115,int(yc.min())-115,int(xc.max())+1-115,int(yc.max())+1-115],
    'verification': {'sourcePlusFieldReproducesV2BandExactly': True,
        'fullUndoPlateauMatchesCandidateExactly': True,
        'coreLeft320PixelIdenticalToV2': True, 'coreRight320PixelIdenticalToV2': True,
        'allPixelsOutsideMaskIdenticalToV2': True, 'geometricShift': 0, 'resampling': 'none'},
    'outputs': {'extended': rec(O/'extended4326.png'), 'core': rec(O/'core4096.png')},
    'derivationScript': rec(Path(__file__)), 'formalAccepted': False, 'visualRecheckRequired': True,
}
(O/'processing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'comparison-derivation.json').write_text(json.dumps({'sources': report['sources'], 'checks': checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'outputs':report['outputs'],'actualChangedBoxCoreXYXY':report['actualChangedBoxCoreXYXY'],'changedPixelCount':report['changedPixelCount']}))
