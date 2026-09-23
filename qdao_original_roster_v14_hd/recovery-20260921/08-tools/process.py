"""08 only: deterministic cleanup/alignment; creates no animation poses."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
GEN = RECOVERY / '08-generation'
OUT = RECOVERY / '08-delivery-preview' / 'processed'
CONFIG = RECOVERY.parents[1] / 'config/image-generation.json'
DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def bbox(image, threshold=0):
    y, x = np.where(np.asarray(image)[:, :, 3] > threshold)
    if not len(x):
        raise ValueError('Empty image')
    return [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1]

def anchor(image):
    y, x = np.where(np.asarray(image)[:, :, 3] > 8)
    top, height = int(y.min()), int(y.max() - y.min())
    return float(np.median(x[y < top + max(1, int(height * .42))])), int(y.max())

def process(attempt):
    source = (GEN / attempt).resolve()
    if source.parent != GEN.resolve():
        raise ValueError('Attempt must be one direct child of 08-generation')
    rawpath, reqpath, recpath = [source / x for x in ('raw.png', 'request.json', 'receipt.json')]
    request, receipt = read(reqpath), read(recpath)
    prompt = (source / 'prompt.txt').read_text(encoding='utf-8-sig')
    params = request.get('parameters', request.get('actual_request', {}))
    if prompt != params['prompt']:
        raise ValueError('Prompt does not match submitted request')
    slot = request['slot'].removesuffix('.png')
    pieces = slot.split('/')
    if not (len(pieces) in (2, 3) and pieces[0] in ('idle', 'walk') and pieces[1] in DIRS):
        raise ValueError('Invalid slot in request')
    if pieces[0] == 'walk' and (len(pieces) != 3 or not 1 <= int(pieces[2]) <= 16):
        raise ValueError('Invalid walk frame')
    with Image.open(rawpath) as raw:
        size, mode, fmt = list(raw.size), raw.mode, raw.format
        if min(size) < 1024 or mode != 'RGBA':
            raise ValueError('Need native >=1024 RGBA with actual transparent alpha')
        a = np.array(raw)
    if a[:, :, 3].min() != 0:
        raise ValueError('No transparent alpha background')
    cleanup_count = int(np.count_nonzero((a[:, :, 3] > 0) & (a[:, :, 3] <= 8)))
    a[:, :, 3][a[:, :, 3] <= 8] = 0
    cleaned = Image.fromarray(a)
    b = bbox(cleaned)
    if b[0] == 0 or b[1] == 0 or b[2] == size[0] or b[3] == size[1]:
        raise ValueError('Real subject touches source edge; regenerate')
    factor = 1024 / max(size) * .88
    if factor > 1:
        raise ValueError('Upscaling prohibited')
    normalized = cleaned.resize(tuple(round(v * factor) for v in size), Image.Resampling.LANCZOS)
    ax, ay = anchor(normalized)
    delta = [round(512 - ax), 942 - ay]
    b = bbox(normalized)
    moved = [b[0] + delta[0], b[1] + delta[1], b[2] + delta[0], b[3] + delta[1]]
    if min(moved[:2]) < 1 or max(moved[2:]) > 1023:
        raise ValueError('Aligned subject would be clipped: ' + str(moved))
    final = Image.new('RGBA', (1024, 1024))
    final.paste(normalized, tuple(delta))
    dest = OUT / attempt
    if (dest / 'source.json').exists():
        old = read(dest / 'source.json')
        if old['raw']['sha256'] != sha(rawpath) or old['request']['sha256'] != sha(reqpath):
            raise ValueError('Immutable attempt input changed; use a new attempt name')
    dest.mkdir(parents=True, exist_ok=True)
    stages = []
    for name, im in [('cleaned', cleaned), ('normalized', normalized), ('frame', final)]:
        p = dest / (name + '.png'); im.save(p)
        stages.append({'file': str(p), 'sha256': sha(p), 'size': list(im.size)})
    qa = []
    for name, color in [('light', (240, 238, 228)), ('dark', (30, 38, 46))]:
        canvas = Image.new('RGB', final.size, color); canvas.paste(final, (0, 0), final)
        path = dest / ('qa-' + name + '.png'); canvas.save(path)
        qa.append({'file': str(path), 'sha256': sha(path), 'operation': 'preview_alpha_composite_only', 'derivedFrom': stages[-1]})
    record = {'schema': 'qdao-08-derived-frame-v1', 'attempt': attempt, 'slot': slot,
      'processedAt': datetime.now(timezone.utc).isoformat(), 'raw': {'file': str(rawpath), 'sha256': sha(rawpath), 'size': size, 'mode': mode, 'format': fmt},
      'request': {'file': str(reqpath), 'sha256': sha(reqpath)}, 'receipt': {'file': str(recpath), 'sha256': sha(recpath)},
      'operation': {'alpha_zero_at_or_below': 8, 'pixels_cleaned': cleanup_count, 'preserved_rgb_and_other_alpha_before_resizing': True, 'whole_cell_scale': factor, 'common_scale': .88, 'translation_px': delta, 'pose_synthesis': False},
      'anchor_px': list(anchor(final)), 'bbox_px': bbox(final), 'stages': stages, 'qa': qa, 'output_sha256': sha(dest / 'frame.png'),
      'reproduction_script': {'file': str(Path(__file__)), 'sha256': sha(__file__)},
      'visual_review': 'pending', 'client_validation': False}
    write(dest / 'source.json', record)
    config = request.get('configSnapshot', read(CONFIG))
    generation = {'file': str(rawpath), 'sha256': sha(rawpath), 'generatedAt': receipt.get('completedAt'), 'requestedAt': request.get('startedAt'),
      'width': size[0], 'height': size[1], 'format': fmt, 'tool': request.get('tool'), 'route': 'builtin', 'configSnapshot': config,
      'configSnapshotEvidence': 'request' if 'configSnapshot' in request else 'archive_time_config_not_preserved_in_request',
      'submittedParameters': request.get('submittedParameters', {'model': None, 'quality': None}),
      'actualModel': receipt.get('actualModel'), 'actualQuality': receipt.get('actualQuality'),
      'unverifiedReason': receipt.get('unverifiedReason', 'host-managed; tool did not disclose model or quality'),
      'prompt': {'file': str(source / 'prompt.txt'), 'sha256': sha(source / 'prompt.txt')},
      'references': [{'file': p, 'sha256': sha(p) if Path(p).is_file() else None} for p in params.get('referenced_image_paths', [])],
      'evidence': [record['request'], record['receipt']], 'historical_source_files_unchanged': True}
    write(dest / 'raw.png.generation.json', generation)
    write(dest / 'frame.png.generation.json', {'file': str(dest / 'frame.png'), 'sha256': record['output_sha256'], 'derivedFrom': {'file': str(rawpath), 'sha256': sha(rawpath), 'generationRecord': str(dest / 'raw.png.generation.json')}, 'operation': record['operation']})
    return {'attempt': attempt, 'slot': slot, 'size': size, 'anchor': record['anchor_px'], 'alpha_cleaned': cleanup_count, 'output': str(dest / 'frame.png'), 'visual_review': 'pending'}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--attempt', required=True)
    args = p.parse_args(); attempts = [v.name for v in GEN.iterdir() if v.is_dir() and (v / 'raw.png').is_file() and (v / 'receipt.json').is_file()] if args.attempt == 'all' else [args.attempt]
    errors = []
    for attempt in sorted(attempts):
        try: print(json.dumps(process(attempt), ensure_ascii=False))
        except Exception as exc:
            errors.append({'attempt': attempt, 'error': str(exc)})
            print(json.dumps(errors[-1], ensure_ascii=False))
    if errors:
        sys.exit(1)
