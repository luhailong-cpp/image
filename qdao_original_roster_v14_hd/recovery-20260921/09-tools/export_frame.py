"""Export one native RGBA 09 pose into an isolated direction, pending visual review."""
import argparse
import hashlib
import importlib.util
import io
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image
from common import (DELIVERY, GENERATION, PACKAGE, CHARACTER, DIRS, claim_lock, inside,
                    immutable_bytes, immutable_json, read_json, require, sha, utc_now)

FRAME = 1024
COMMON_SCALE = .88
ROOT = (512, 942)


def vendor(name):
    path = PACKAGE / 'tools/vendor' / (name + '.py')
    spec = importlib.util.spec_from_file_location('bamboo_' + name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result, path


def pixel_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def alpha_axis(image):
    alpha = np.asarray(image)[:, :, 3]
    ys, xs = np.where(alpha > 8)
    require(len(xs) > 0, 'Empty visible frame')
    top = int(ys.min())
    height = int(ys.max()) - top
    return float(np.median(xs[ys < top + max(1, int(height * .42))])), int(ys.max())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--direction', choices=DIRS, required=True)
    parser.add_argument('--kind', choices=('walk', 'idle'), default='walk')
    parser.add_argument('--frame', type=int, choices=range(1, 17))
    parser.add_argument('--variant', help='Optional non-overwriting review variant below the direction workspace')
    parser.add_argument('--chroma-profile', choices=('standard', 'none'), default='none',
                        help='standard: project magenta100/150 + despill4/12; none: preserve native RGBA')
    args = parser.parse_args()
    require(not args.variant or re.fullmatch(r'[A-Za-z0-9_-]+', args.variant), 'Invalid review variant name')
    require(args.kind != 'walk' or args.frame is not None, 'walk requires --frame 1..16')
    require(args.kind != 'idle' or args.frame is None, 'idle is independent and must not specify --frame')
    archive = inside(args.archive, GENERATION, 'Archive')
    raw = archive / 'raw.png'
    generation_path = archive / 'generation.json'
    generation = read_json(generation_path)
    require(generation['sha256'] == sha(raw), 'Archived raw SHA differs from generation record')
    require(generation.get('route') == 'builtin' and generation.get('paidApiCalls') == 0, 'Need archived built-in result')
    with Image.open(raw) as image:
        require(image.format == 'PNG', 'Require original PNG')
        require(args.chroma_profile == 'standard' or image.mode == 'RGBA', 'none requires actual native RGBA PNG')
        require(min(image.size) >= 1024, 'Native single-frame dimensions must both be at least 1024')
        original_mode = image.mode
        native = image.convert('RGBA')
    a = np.asarray(native)[:, :, 3]
    require(args.chroma_profile == 'standard' or (int(a.min()) == 0 and int(a.max()) == 255),
            'none requires genuine transparent background and opaque subject')
    tool_bindings = []
    if args.chroma_profile == 'standard':
        keyer, keyer_path = vendor('generate2dsprite')
        edge, edge_path = vendor('edge_despill')
        tool_bindings = [{'path': str(p), 'sha256': sha(p)} for p in (keyer_path, edge_path)]
        keyed = keyer.remove_bg_magenta(native, 100, 150)
    else:
        keyed = native.copy()
    ka = np.asarray(keyed)[:, :, 3]
    boundary_max = max(int(ka[0].max()), int(ka[-1].max()), int(ka[:, 0].max()), int(ka[:, -1].max()))
    require(boundary_max <= 8, 'Visible original subject touches canvas boundary; regenerate this pose')
    factor = FRAME / max(native.size) * COMMON_SCALE
    require(factor <= 1, 'Upscaling is forbidden')
    normalized_size = tuple(round(v * factor) for v in native.size)
    normalized = keyed.resize(normalized_size, Image.Resampling.LANCZOS)
    if args.chroma_profile == 'standard':
        cleaned, cleanup = edge.despill(normalized, radius=4, reference_radius=12)
    else:
        cleaned, cleanup = normalized.copy(), {'mode': 'native-rgba-preserved', 'changed_pixels': 0}
    ax, ay = alpha_axis(cleaned)
    delta = (round(ROOT[0] - ax), ROOT[1] - ay)
    bbox = cleaned.getchannel('A').getbbox()
    require(bbox is not None, 'Empty normalized image')
    moved = (bbox[0] + delta[0], bbox[1] + delta[1], bbox[2] + delta[0], bbox[3] + delta[1])
    require(min(moved[:2]) >= 1 and max(moved[2:]) <= FRAME - 1,
            'Integer alignment would clip alpha pixels; regenerate rather than silently crop: ' + str(moved))
    final = Image.new('RGBA', (FRAME, FRAME), (0, 0, 0, 0))
    final.paste(cleaned, delta)
    anchor = alpha_axis(final)
    require(abs(anchor[0] - ROOT[0]) <= .5 and anchor[1] == ROOT[1], 'Final foot/body anchor does not match contract')
    relative = f'walk/{args.direction}/{args.frame:02d}.png' if args.kind == 'walk' else f'idle/{args.direction}.png'
    direction_root = DELIVERY / 'work' / args.direction
    if args.variant:
        direction_root = direction_root / 'variants' / args.variant
    runtime = direction_root / 'runtime'
    output = runtime / relative
    source_path = direction_root / 'sources' / (relative + '.json')
    require(not output.exists() and not source_path.exists(), 'Slot already exists; preserve selected pose and use a separate revision')
    lock = claim_lock(direction_root / '.export.lock')
    try:
        # One unique source per slot across all direction records. Direction lock avoids shared JSON writes.
        for existing in (DELIVERY / 'work').glob('*/sources/**/*.json'):
            other = read_json(existing)
            require(other.get('source', {}).get('sha256') != generation['sha256'],
                    'The same raw image is already assigned to another action slot: ' + str(existing))
        buffer = io.BytesIO()
        final.save(buffer, format='PNG')
        output_bytes = buffer.getvalue()
        output_sha = hashlib.sha256(output_bytes).hexdigest()
        operation = {'name': 'whole_cell_downsample_and_integer_foot_alignment',
                     'commonScale': COMMON_SCALE, 'wholeCellScale': factor,
                     'normalizedSize': list(normalized_size), 'translationPx': list(delta),
                     'footAnchorPx': list(ROOT), 'anchorAfterPx': list(anchor),
                     'horizontalAxis': 'upper_body_alpha_median_42_percent',
                     'alphaThresholdForAnchorOnly': 8, 'resampler': 'LANCZOS',
                     'chromaProfile': args.chroma_profile,
                     'chromaKey': args.chroma_profile == 'standard',
                     'chromaThresholds': [100, 150] if args.chroma_profile == 'standard' else None,
                     'despill': args.chroma_profile == 'standard',
                     'despillRadius': 4 if args.chroma_profile == 'standard' else 0,
                     'despillReferenceRadius': 12 if args.chroma_profile == 'standard' else 0,
                     'alphaCleanup': False, 'cleanupReport': cleanup,
                     'processingTools': tool_bindings,
                     'perSubjectBboxScaling': False, 'mirrored': False, 'poseInterpolated': False}
        record = {'schemaVersion': 1, 'character': CHARACTER, 'kind': args.kind,
                  'direction': args.direction, 'frame': args.frame if args.kind == 'walk' else None,
                  'output': str(output), 'outputRelative': relative, 'outputSha256': output_sha,
                  'nativeSize': list(native.size), 'originalMode': original_mode, 'outputSize': [FRAME, FRAME],
                  'source': {'path': str(raw), 'sha256': generation['sha256'],
                             'generationRecord': str(generation_path), 'generationRecordSha256': sha(generation_path)},
                  'operation': operation, 'sourceBoundaryAlphaMax': boundary_max,
                  'stageRgbaPixelSha256': {name: pixel_sha(im) for name, im in
                                          [('native', native), ('keyed', keyed), ('normalized', normalized),
                                           ('cleaned', cleaned), ('final', final)]},
                  'outputAlphaBounds': list(final.getchannel('A').getbbox()),
                  'exportedAt': utc_now(), 'visualReview': 'pending', 'canPublish': False,
                  'reviewNotes': 'Color-key processing is recorded when explicitly selected; all edges, gait and identity remain pending visual review.'}
        derived = {'schemaVersion': 1, 'file': str(output), 'sha256': output_sha,
                   'width': FRAME, 'height': FRAME, 'format': 'PNG', 'route': 'derived_no_model_call',
                   'generatedAt': generation['generatedAt'], 'exportedAt': record['exportedAt'],
                   'actualModel': generation['actualModel'], 'actualQuality': generation['actualQuality'],
                   'configSnapshot': generation['configSnapshot'],
                   'submittedParameters': generation['submittedParameters'],
                   'unverifiedReason': generation['unverifiedReason'],
                   'derivedFrom': record['source'], 'operation': operation,
                   'visualReview': 'pending', 'canPublish': False}
        immutable_bytes(output, output_bytes)
        immutable_json(source_path, record)
        immutable_json(output.with_name(output.name + '.generation.json'), derived)
        print(json.dumps({'output': str(output), 'sha256': output_sha,
                          'sourceRecord': str(source_path), 'anchor': list(anchor),
                          'status': 'exported_pending_visual_review'}, ensure_ascii=False))
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
