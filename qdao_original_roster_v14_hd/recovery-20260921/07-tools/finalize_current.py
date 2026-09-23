"""Export07 native single frames, keeping one genuine raw plus textual provenance.
Latest user instruction retains new raw; no processing/rollback image copies are made.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
OUT = HERE / 'candidate' / '07_moon_shadow_assassin_girl'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def now():
    return datetime.now(timezone.utc).isoformat()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def metrics(im):
    a = np.asarray(im.getchannel('A'))
    yy, xx = np.where(a > 8)
    require(len(xx), 'Empty silhouette')
    top, bottom = int(yy.min()), int(yy.max())
    height = bottom - top + 1
    axis = float(np.median(xx[yy < top + int(height * .42)]))
    widths = []
    for y in range(top + int(height * .18), top + int(height * .42)):
        xs = np.where(a[y] > 8)[0]
        if len(xs):
            widths.append(int(xs[-1] - xs[0] + 1))
    return {'size': list(im.size), 'alpha_min': int(a.min()), 'alpha_max': int(a.max()),
            'bbox_alpha_gt8': [int(xx.min()), top, int(xx.max()) + 1, bottom + 1],
            'subject_height': height, 'axis': [axis, bottom],
            'headBandWidth95': float(np.percentile(widths, 95)),
            'alpha_boundary_touched': bool(any(np.any(edge) for edge in (a[0], a[-1], a[:, 0], a[:, -1]))),
            'body_scale': float(np.sqrt(np.count_nonzero(a[:, im.width//4:3*im.width//4])/(im.width*im.height)))}

def historical_bindings(paths):
    ledgers = [read(p) for p in HERE.glob('cleanup-*.json')]
    lookup = {}
    def walk(value):
        if isinstance(value, dict):
            if value.get('path') and value.get('sha256'):
                lookup[str(value['path']).replace('\\', '/').lower()] = value
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    for ledger in ledgers:
        walk(ledger)
    rows = []
    for raw_path in paths:
        p = Path(raw_path)
        old = lookup.get(str(p).replace('\\', '/').lower())
        rows.append({'pathAtGeneration': str(p), 'sha256': sha(p) if p.is_file() else old.get('sha256') if old else None,
                     'bindingEvidence': 'current_file_at_export' if p.is_file() else 'user_authorized_cleanup_ledger' if old else 'not_available',
                     'imagePresentAtExport': p.is_file(), 'historicalReferenceOnly': not p.is_file()})
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--source', type=Path, help='Actual returned native PNG or retained unique in-progress raw')
    parser.add_argument('--replace', action='store_true', help='Replace current slot without image backup per2026-09-23 user policy')
    parser.add_argument('--head-reference', type=Path, help='Optional diagnostic whole-frame scale to current same-direction idle PNG')
    parser.add_argument('--canvas-scale', type=float, default=1.0, help='Optional additional whole-native-canvas uniform reduction, 0 < value <= 1; never pose synthesis')
    args = parser.parse_args()
    require(0 < args.canvas_scale <= 1, 'Canvas scale must be in (0,1]')
    require(not args.head_reference or args.canvas_scale == 1, 'Choose canvas reduction or head-reference calibration, not both')
    require(re.fullmatch(r'[A-Za-z0-9_-]+', args.attempt), 'Invalid attempt')
    match = re.match(r'^(idle|walk)-(N|NE|E|SE|S|SW|W|NW)(?:-(\d{2}))?-', args.attempt)
    require(match, 'Attempt must identify action/direction/frame')
    kind, direction, number = match.groups()
    frame = int(number) if number else None
    require(kind == 'idle' or frame is not None and 1 <= frame <= 16, 'Invalid frame')
    slot = f'walk/{direction}/{frame:02d}.png' if kind == 'walk' else f'idle/{direction}.png'
    folder = RECOVERY / '07-generation' / args.attempt
    request_path, result_path = folder / 'request.json', folder / 'result.json'
    request, result = read(request_path), read(result_path)
    submitted = next((request[k] for k in ('arguments', 'actual_request', 'submittedArguments') if isinstance(request.get(k), dict)), None)
    require(submitted and isinstance(submitted.get('prompt'), str), 'Exact request prompt required')
    returned_path = result.get('original_generated_file') or result.get('rawPath') or result.get('raw_path')
    if not returned_path:
        hint = result.get('output_hint') or (result.get('tool_output') or {}).get('output_hint')
        found = re.search(r'as (.+?\.png) by default', hint or '')
        if found:
            returned_path = found.group(1)
    source = args.source or Path(returned_path or '')
    if not source.is_file() and (folder / 'raw.png').is_file():
        source = folder / 'raw.png'
    require(source.is_file(), 'Use --source actual existing native PNG')
    source = source.resolve()
    source_sha = sha(source)
    evidence = json.dumps(result, ensure_ascii=False).replace('\\\\', '/').replace('\\', '/').lower()
    if str(source).replace('\\', '/').lower() not in evidence:
        recorded = [result.get(k) for k in ('raw_sha256', 'rawSha256', 'sha256')]
        old_receipt = HERE / 'archives' / args.attempt / 'generation-receipt.json'
        if old_receipt.is_file():
            recorded.append(read(old_receipt).get('rawSha256'))
        require(source_sha in recorded, 'Source needs actual tool path or previously measured SHA binding')
    with Image.open(source) as native:
        require(native.format == 'PNG' and native.mode == 'RGBA' and min(native.size) >= 1024,
                'Native complete single-frame PNG must be RGBA and >=1024 on both axes')
        im = native.copy()
    raw_metrics = metrics(im)
    require(raw_metrics['alpha_min'] == 0 and raw_metrics['alpha_max'] == 255, 'Native background must already have transparency')
    retained_raw = folder / 'raw.png'
    if retained_raw.is_file():
        require(sha(retained_raw) == source_sha, 'Existing native raw differs; choose another attempt')
    elif source != retained_raw.resolve():
        shutil.copy2(source, retained_raw)
    require(sha(retained_raw) == source_sha, 'Native raw copy SHA mismatch')
    actual_model = next((result[k] for k in ('actualModel','actual_model') if isinstance(result.get(k), str) and result[k]), None)
    actual_quality = next((result[k] for k in ('actualQuality','actual_quality') if isinstance(result.get(k), str) and result[k]), None)
    refs = historical_bindings(submitted.get('referenced_image_paths', []))
    observed_at = result.get('completedAt') or result.get('receivedAt')
    raw_record = {'file': str(retained_raw), 'sha256': source_sha, 'nativeMetrics': raw_metrics,
                  'originalGeneratedPath': str(source), 'originalRetained': True,
                  'actualModel': actual_model, 'actualQuality': actual_quality,
                  'configSnapshot': request.get('configSnapshot') or request.get('config_snapshot'),
                  'submittedParameters': request.get('submittedParameters', {'model':None,'quality':None}),
                  'generatedAt': observed_at, 'generatedAtScope': 'observed_tool_return_time' if observed_at else 'not_disclosed',
                  'requestEvidence': {'path': str(request_path), 'sha256': sha(request_path)},
                  'resultEvidence': {'path': str(result_path), 'sha256': sha(result_path)},
                  'exactPrompt': submitted['prompt'], 'referenceBindings': refs,
                  'retentionPolicy': 'latest_user_instruction_retain_genuine_new_raw_and_textual_generation_evidence'}
    Path(str(retained_raw)+'.generation.json').write_text(json.dumps(raw_record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    pixels = np.array(im)
    a = pixels[:, :, 3]
    strong = Image.fromarray(np.where(a > 8, 255, 0).astype(np.uint8))
    near = np.asarray(strong.filter(ImageFilter.MaxFilter(7))) > 0
    remote = (a > 0) & (a <= 8) & ~near
    transparent_near = np.asarray(Image.fromarray(a).filter(ImageFilter.MinFilter(7))) == 0
    hi, lo = pixels[:, :, :3].max(2).astype(int), pixels[:, :, :3].min(2).astype(int)
    fringe = (a > 0) & (a <= 8) & transparent_near & (hi > 220) & (lo < 32) & (hi-lo > 180)
    a[remote | fringe] = 0
    clean = Image.fromarray(pixels, 'RGBA')
    require(not metrics(clean)['alpha_boundary_touched'], 'Source touches boundary after limited alpha cleanup')
    canvas_factor = 1024 / max(clean.size)
    factor, calibration = canvas_factor * args.canvas_scale, None
    if args.head_reference:
        require(args.head_reference.resolve() == (OUT / f'idle/{direction}.png').resolve(), 'Use current same-direction independent idle')
        with Image.open(args.head_reference) as ref:
            target = metrics(ref)['headBandWidth95']
        measured = metrics(clean)['headBandWidth95']
        factor = target / measured
        require(factor <= 1, 'No enlargement of native artwork')
        calibration = {'kind': 'diagnostic_per_frame_uniform_scale_not_original_common_scale_contract',
                       'reference': str(args.head_reference.resolve()), 'referenceSha256': sha(args.head_reference),
                       'targetWidth': target, 'nativeWidth': measured, 'method': 'alpha>8;18..42%height;95thpercentile_row_span'}
    resized = clean.resize(tuple(round(v * factor) for v in clean.size), Image.Resampling.LANCZOS)
    sized = metrics(resized)
    shift = [round(512 - sized['axis'][0]), 942 - sized['axis'][1]]
    box = resized.getchannel('A').getbbox()
    bounds = [box[0]+shift[0], box[1]+shift[1], box[2]+shift[0], box[3]+shift[1]]
    require(min(bounds[:2]) >= 1 and max(bounds[2:]) <= 1023, f'Would clip complete figure {bounds}; regenerate margins')
    destination = OUT / slot
    require(not destination.exists() or args.replace, 'Slot already exists; use explicit --replace')
    output = Image.new('RGBA', (1024, 1024))
    output.paste(resized, tuple(shift))
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.save(destination)
    meta = {'character': '07_moon_shadow_assassin_girl', 'attempt': args.attempt, 'slot': slot,
            'status': 'candidate_pending_visual_review', 'exportedAt': now(), 'outputSha256': sha(destination),
            'derivedFrom': {'path': str(retained_raw), 'sha256': source_sha, 'historicalPathOnly': False,
                            'generationRecord': str(retained_raw)+'.generation.json',
                            'runtimeDependency': False, 'verificationDependency': True, 'nativeVerifiedBeforeExport': True},
            'sourceImageRetention': {'status': 'retained_genuine_raw_per_latest_user_instruction',
                                     'policy': 'latest_user_instruction_retain_genuine_new_raw_and_textual_generation_evidence',
                                     'sourcePathIsRuntimeDependency': False},
            'requestEvidence': {'path': str(request_path), 'sha256': sha(request_path)},
            'resultEvidence': {'path': str(result_path), 'sha256': sha(result_path)},
            'exactPrompt': submitted['prompt'], 'referenceBindings': refs,
            'generatedAt': observed_at, 'generatedAtScope': 'observed_tool_return_time' if observed_at else 'not_disclosed', 'startedAt': request.get('startedAt'),
            'actualModel': actual_model, 'actualQuality': actual_quality,
            'unverifiedReason': 'host-managed; actual model/quality not disclosed by tool' if not actual_model else None,
            'configSnapshot': request.get('configSnapshot'), 'submittedParameters': request.get('submittedParameters', {'model':None,'quality':None}),
            'nativeMetrics': raw_metrics, 'outputMetrics': metrics(output), 'wholeCanvasScale': factor,
            'commonScale': factor/canvas_factor, 'scaleCalibration': calibration, 'translationPx': shift,
            'requestedCanvasScale': args.canvas_scale,
            'anchorTarget': [512,942], 'removedLowAlphaPixels': int((remote|fringe).sum()),
            'alphaPolicy': 'Only remote/near-transparent extreme-saturation alpha<=8; source RGB and alpha>8 unchanged before uniform resize',
            'operation': 'limited_alpha_cleanup_then_complete_frame_uniform_downsample_and_integer_alignment;no_pose_synthesis',
            'generationCalls': 1, 'paidApiCalls': 0, 'formalApproval': False, 'clientIntegration': False}
    Path(str(destination)+'.generation.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest = folder / 'current-export.json'
    manifest.write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(destination), 'sha256': meta['outputSha256'], 'nativeSha256': source_sha,
                      'native': im.size, 'height': meta['outputMetrics']['subject_height'],
                      'retainedNativeRaw': str(retained_raw), 'status': meta['status']}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'status':'failed', 'error':str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
