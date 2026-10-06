"""Integrate the single WEST-LEAF-01 edit at native scale, preserving the exterior."""
from pathlib import Path
import json
import shutil
import numpy as np
from PIL import Image
import assembly as n

ROOT = Path(__file__).resolve().parent
REPAIR = ROOT / 'r08_c11/repairs/west-leaf-01'
QA = REPAIR / 'qa'
MASKS = REPAIR / 'masks'
RAW = Path('C:/Users/luyua/.codex/generated_images/01a10baf-971a-7563-ab28-dc817d78eefa/exec-9e80168d-6d1b-46d6-9b79-ad8e2dc958df.png')
PATCH = REPAIR / 'edited-native.png'
INPUT = REPAIR / 'input.png'
STYLE = Path('D:/work/image/designs/gameplay-ui/04-guild.png')
RECT = (3968, 1952, 4224, 2352)
CROP = (3469, 1543, 4723, 2797)
OVERLAP = 48


def rgb(path, size):
    with Image.open(path) as im:
        im.load()
        n.require(im.size == size and im.format == 'PNG', f'Wrong native dimensions/format: {path}')
        n.require(im.mode in ('RGB', 'RGBA'), 'Unexpected mode')
        if im.mode == 'RGBA':
            n.require(im.getextrema()[3] == (255, 255), 'Unexpected transparency')
        return np.asarray(im.convert('RGB')).copy()


def file_ref(path):
    return {'file': str(path), 'sha256': n.sha(path)}


def save_mask(label, a, b, transpose, invert):
    aa, bb = (a.transpose(1, 0, 2), b.transpose(1, 0, 2)) if transpose else (a, b)
    # Search the inner 44 of 48 pixels so the outside contour is exactly zero.
    path = n.load_seam_function()(aa[:, 2:-2], bb[:, 2:-2]) + 2
    n.require(np.all(np.abs(np.diff(path)) <= 1), 'Discontinuous minimum-error path')
    alpha = n.seam_alpha(path, width=OVERLAP)
    if invert:
        alpha = 255 - alpha
    if transpose:
        alpha = alpha.T
    png = n.save_image(MASKS / f'{label}.png', Image.fromarray(alpha))
    npz = n.writable(MASKS / f'{label}.npz')
    np.savez_compressed(npz, alpha=alpha, seam=path)
    error = np.abs(aa.astype(np.int16) - bb.astype(np.int16)).mean(axis=2)
    info = {'name': label, 'mask': png, 'npz': file_ref(npz),
            'overlapPixels': OVERLAP, 'searchPixelRange': [2, 46],
            'transitionPartialPixels': 2, 'transpose': transpose, 'invert': invert,
            'pathRange': [int(path.min()), int(path.max())],
            'meanAbsoluteRgbDifferenceOnPath': n.statistics(error[np.arange(len(path)), path]),
            'metricsMeaning': 'Diagnostic only, never visual acceptance.'}
    n.save_json(MASKS / f'{label}.json', info)
    return alpha, info


def main():
    provenance_path = REPAIR / 'replaced-tiles.provenance.json'
    provenance = n.load_json(provenance_path)
    baselines = provenance['currentOutputsBeforeRepair']
    for ref in baselines:
        n.require(n.sha(ref['file']) == ref['sha256'], 'Baseline has changed; refusing overwrite/rerun')
    pair = np.concatenate([rgb(Path(ref['file']), (4096, 4096)) for ref in baselines], axis=1)
    original_input = rgb(INPUT, (1254, 1254))
    n.require(np.array_equal(pair[CROP[1]:CROP[3], CROP[0]:CROP[2]], original_input), 'Input is not exact current pair crop')
    edited = rgb(RAW, (1254, 1254))
    shutil.copy2(RAW, n.writable(PATCH))
    n.require(n.sha(PATCH) == n.sha(RAW), 'Raw-to-canonical copy changed pixels or bytes')
    prompt = REPAIR / 'prompt.txt'
    config = n.load_json(Path('D:/work/image/config/image-generation.json'))
    generation = {**file_ref(PATCH), 'width': 1254, 'height': 1254, 'format': 'PNG',
        'generatedAt': '2026-10-05T23:05:30Z', 'submittedAt': '2026-10-05T23:04:37Z',
        'timestampMeaning': 'locally observed submission and tool completion',
        'tool': 'image_gen.imagegen', 'route': 'builtin', 'configSnapshot': config,
        'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False,
                               'referenced_image_paths': [str(INPUT), str(STYLE)]},
        'actualModel': None, 'actualQuality': None,
        'unverifiedReason': 'Host managed; tool exposes no model/quality selectors or returned evidence.',
        'evidence': {'toolResultSourcePath': str(RAW), 'toolResultSha256': n.sha(RAW),
                     'singleCallSucceeded': True, 'referencesActuallyViewedBeforeCall': True},
        'prompt': str(prompt), 'promptSha256': n.sha(prompt),
        'references': [{**file_ref(INPUT), 'role': 'edit target, exact current native pair crop',
                        'sourceRecord': str(INPUT) + '.generation.json'},
                       {**file_ref(STYLE), 'role': 'confirmed painting/material/finish style only'}],
        'resizedAfterGeneration': False, 'finalArtUpscaled': False,
        'issue': 'WEST-LEAF-01', 'editTargetInInputApproxXYXY': [611, 517, 651, 737]}
    n.save_json(Path(str(PATCH) + '.generation.json'), generation)
    x0, y0, x1, y1 = RECT
    baseline = pair[y0:y1, x0:x1].copy()
    incoming = edited[y0-CROP[1]:y1-CROP[1], x0-CROP[0]:x1-CROP[0]].copy()
    alpha = np.full(baseline.shape[:2], 255, dtype=np.uint8)
    masks = []
    for name, sl, transpose, invert in [
        ('left', (slice(None), slice(0, OVERLAP)), False, False),
        ('right', (slice(None), slice(-OVERLAP, None)), False, True),
        ('top', (slice(0, OVERLAP), slice(None)), True, False),
        ('bottom', (slice(-OVERLAP, None), slice(None)), True, True),
    ]:
        a, b = (incoming[sl], baseline[sl]) if invert else (baseline[sl], incoming[sl])
        part, info = save_mask(name, a, b, transpose, invert)
        alpha[sl] = np.minimum(alpha[sl], part)
        masks.append(info)
    n.require(all(np.all(edge == 0) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])), 'Outside mask contour must be exactly zero')
    n.require(set(np.unique(alpha)) <= {0, 64, 191, 255}, 'Unexpected blend weights')
    combined = n.save_image(MASKS / 'combined.png', Image.fromarray(alpha))
    np.savez_compressed(n.writable(MASKS / 'combined.npz'), alpha=alpha, pair_rect=np.asarray(RECT))
    result = pair.copy()
    result[y0:y1, x0:x1] = n.blend(baseline, incoming, alpha)
    exterior = np.ones(pair.shape[:2], dtype=bool)
    exterior[y0:y1, x0:x1] = False
    changed = np.any(result != pair, axis=2)
    n.require(np.array_equal(result[exterior], pair[exterior]), 'Pixels outside approved ROI changed')
    n.require(not np.any(changed[y0:y1, x0:x1] & (alpha == 0)), 'Zero-mask pixel changed')
    # Save exact baseline SHA and the text provenance before replacing canonical tiles.
    for ref in baselines:
        n.require(n.sha(ref['file']) == ref['sha256'], 'Concurrent baseline mutation')
    outputs = []
    for i, ref in enumerate(baselines):
        p = Path(ref['file'])
        array = result[:, i*4096:(i+1)*4096]
        saved = n.save_image(p, Image.fromarray(array))
        n.require(np.array_equal(rgb(p, (4096, 4096)), array), 'Saved PNG differs from native composition')
        outputs.append({**saved, 'tile': ref['tile']})
    qa_entries = []
    boxes = {
        'repair-context': (3712, 1696, 4480, 2608),
        'repair-native': RECT,
        'insertion-left': (3936, 1920, 4032, 2384),
        'insertion-right': (4160, 1920, 4256, 2384),
        'insertion-top': (3936, 1920, 4256, 2048),
        'insertion-bottom': (3936, 2256, 4256, 2384),
    }
    for name, box in boxes.items():
        x, y, xx, yy = box
        info = n.save_image(QA / f'{name}.png', Image.fromarray(result[y:yy, x:xx]))
        qa_entries.append({**info, 'pairRectXYXY': list(box), 'nativePixelScale': '1:1',
                           'pixelCoverage': 'every pixel in stated rectangle, no scaling'})
    band = result[:, 3968:4224]
    sheet = np.concatenate([band[i*1024:(i+1)*1024] for i in range(4)], axis=1)
    qa_entries.append({**n.save_image(QA / 'common-edge-full.png', Image.fromarray(sheet)),
        'pairRectXYXY': [3968, 0, 4224, 4096], 'nativePixelScale': '1:1',
        'layout': 'Four 256x1024 pieces placed left to right; y ranges 0..1024,1024..2048,2048..3072,3072..4096',
        'pixelCoverage': 'all 1048576 pixels of the complete 256x4096 band exactly once'})
    manifest = {'createdAt': n.utc_now(), 'issue': 'WEST-LEAF-01',
        'historicalBaseline': baselines, 'historicalBaselineAvailableAsCurrentPixels': False,
        'historicalProvenance': file_ref(provenance_path),
        'previousIntegrationManifest': file_ref(Path(provenance['previousIntegrationManifest'])),
        'nativeInput': file_ref(INPUT), 'inputRecord': file_ref(Path(str(INPUT) + '.generation.json')),
        'generatedEdit': file_ref(PATCH), 'generationRecord': file_ref(Path(str(PATCH) + '.generation.json')),
        'pairRectXYXY': list(RECT), 'globalRectXYXY': [x0+36864, y0+28672, x1+36864, y1+28672],
        'sourceCropXYXY': [x0-CROP[0], y0-CROP[1], x1-CROP[0], y1-CROP[1]],
        'overlapEachSidePixels': OVERLAP, 'transitionPartialPixels': 2,
        'composition': 'Per-side minimum-error monotonic seam, corner intersection by minimum alpha; one integer blend.',
        'masks': masks, 'combinedMask': combined, 'combinedMaskNpz': file_ref(MASKS / 'combined.npz'),
        'noUpscaling': True, 'registration': False, 'colorCorrection': False, 'structureBlur': False,
        'outsideRepairRectPixelEquality': True, 'outsideRepairRectChangedPixelCount': int(changed[exterior].sum()),
        'insideRepairRectChangedPixelCount': int(changed[y0:y1, x0:x1].sum()),
        'savedPngPixelsExactlyMatchComposition': True, 'oldTileImageBackupsCreated': False,
        'outputs': outputs, 'qa': qa_entries, 'formalAccepted': False, 'wholeCityAccepted': False,
        'script': file_ref(Path(__file__)), 'seamHelper': file_ref(n.HELPER),
        'diagnosticsNotVisualAcceptance': True}
    n.save_json(ROOT / 'tiles/west-leaf-repair-manifest.json', manifest)
    print(json.dumps({'outputs': outputs, 'outsideChangedPixels': 0,
                      'insideChangedPixels': manifest['insideRepairRectChangedPixelCount'], 'qaCount': len(qa_entries)}))


if __name__ == '__main__':
    main()
