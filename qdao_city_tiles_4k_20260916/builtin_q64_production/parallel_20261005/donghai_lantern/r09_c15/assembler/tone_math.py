from pathlib import Path
import numpy as np
import shared_math as shared
FIELDS=None
RADIUS=256
STEP_LIMIT=18
TOTAL_LIMIT=24

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
