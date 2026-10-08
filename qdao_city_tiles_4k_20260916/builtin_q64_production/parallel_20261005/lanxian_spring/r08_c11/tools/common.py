"""Strict selected-neighbor and native checks for bottom-to-top r08_c11."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

TILE = Path(__file__).resolve().parents[1]
ROOT = TILE.parent
REPO = Path('D:/work/image')
NATIVE, CORE, HALO, OVERLAP, EXTENDED = 1254, 1024, 115, 230, 4326
NEIGHBORS = {
    'west': ROOT / 'r08_c10/selected-v2/delivery.manifest.json',
    'south': ROOT / 'r09_c11/selected/delivery.manifest.json',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def info(path):
    return {'file': str(path), 'sha256': sha(path)}


def load_png(path, dimensions):
    with Image.open(path) as image:
        image.load()
        if image.format != 'PNG' or image.size != dimensions:
            raise ValueError(f'Expected opaque PNG {dimensions}: {path}; got {image.format} {image.size}')
        if 'A' in image.getbands() and image.getchannel('A').getextrema() != (255, 255):
            raise ValueError(f'Non-opaque source: {path}')
        return image.convert('RGB')


def load_native(row, col):
    if not 1 <= row <= 4 or not 1 <= col <= 4:
        raise ValueError('Native row and col must be 1..4')
    cell = f'r{row:02d}_c{col:02d}'
    path = TILE / 'native' / f'{cell}.png'
    record = path.with_name(path.name + '.generation.json')
    if not path.is_file() or not record.is_file():
        raise ValueError(f'WAIT: registered west/south native dependency absent: {cell}')
    digest = sha(path)
    if read(record).get('sha256') != digest:
        raise ValueError(f'Native SHA differs from generation record: {cell}')
    return load_png(path, (NATIVE, NATIVE)), {
        'patchId': cell, 'file': str(path), 'sha256': digest,
        'generationRecord': info(record), 'sourceNativeSize': [NATIVE, NATIVE], 'resized': False,
    }


def load_selected(side):
    manifest = NEIGHBORS[side]
    if not manifest.is_file():
        raise ValueError(f'WAIT: selected {side} delivery manifest absent: {manifest}; no hardcut fallback')
    metadata = read(manifest)
    expected_tile = {'west': 'r08_c10', 'south': 'r09_c11'}[side]
    if metadata.get('tile') != expected_tile:
        raise ValueError(f'{side} selected manifest identifies the wrong tile')
    if metadata.get('qualifiedComplete4KCandidate') is not True:
        raise ValueError(f'WAIT: {side} source is not a selected qualified complete 4K candidate')
    expected = (manifest.parent / 'extended4326.png').resolve()
    outputs = metadata.get('outputs', {})
    entries = list(outputs.values()) if isinstance(outputs, dict) else outputs
    matches = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw = entry.get('file') or entry.get('path')
        if not raw:
            continue
        path = Path(raw)
        path = (manifest.parent / path).resolve() if not path.is_absolute() else path.resolve()
        if path == expected:
            matches.append(entry)
    if len(matches) != 1 or not matches[0].get('sha256'):
        raise ValueError(f'{side} manifest must identify exactly its selected extended4326.png with SHA')
    digest = sha(expected)
    if digest != matches[0]['sha256']:
        raise ValueError(f'Selected {side} source image SHA does not match delivery manifest')
    image = load_png(expected, (EXTENDED, EXTENDED))
    return image, {'side': side, 'file': str(expected), 'sha256': digest,
                   'deliveryManifest': info(manifest), 'qualifiedComplete4KCandidate': True,
                   'formalAccepted': metadata.get('formalAccepted', False), 'resized': False}


def load_neighbors():
    images, sources = {}, {}
    for side in ('west', 'south'):
        images[side], sources[side] = load_selected(side)
    check_boundary_pin(sources, create=False)
    return images, sources


def check_boundary_pin(sources, create=False):
    path = TILE / 'jobs/boundary-pin.json'
    identities = {side: {'file': value['file'], 'sha256': value['sha256'],
                         'deliveryManifest': value['deliveryManifest']} for side, value in sources.items()}
    if path.exists():
        if read(path)['sources'] != identities:
            raise ValueError('Selected west/south source changed since this native batch was pinned; review before continuing')
    elif create:
        write(path, {'createdAt': now(), 'sources': identities,
                     'purpose': 'Immutable selected source identities shared by all 16 native jobs'})


def unchanged(sources):
    values = sources.values() if isinstance(sources, dict) else sources
    for source in values:
        if sha(source['file']) != source['sha256']:
            raise ValueError('Image source changed during operation')
        for key in ('deliveryManifest', 'generationRecord'):
            if key in source and sha(source[key]['file']) != source[key]['sha256']:
                raise ValueError(f'Source {key} changed during operation')


def differences(a, b):
    a, b = np.asarray(a).astype(np.int16), np.asarray(b).astype(np.int16)
    if a.shape != b.shape:
        raise ValueError('Cannot compare differently shaped corner sources')
    delta = a - b
    mismatch = np.any(delta != 0, axis=2)
    ys, xs = np.where(mismatch)
    return {'size': [int(a.shape[1]), int(a.shape[0])], 'pixelCount': int(mismatch.size),
            'differingPixels': int(mismatch.sum()), 'byteEqual': bool(not mismatch.any()),
            'meanAbsoluteRGB': np.abs(delta).mean(axis=(0, 1)).tolist(),
            'maxAbsoluteRGB': np.abs(delta).max(axis=(0, 1)).tolist(),
            'differenceBoundingBox': [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if mismatch.any() else None}


def corner_image(west, south, owner):
    """Resolve guide context without modifying, blending, or equating its sources."""
    if owner == 'west':
        return west.copy()
    if owner == 'south':
        return south.copy()
    if owner == 'core-split':
        if west.size != (OVERLAP, OVERLAP) or south.size != west.size:
            raise ValueError('core-split applies only to the native 230 by 230 guide corner')
        chosen = south.copy()
        chosen.paste(west.crop((0, 0, OVERLAP, HALO)), (0, 0))
        return chosen
    raise ValueError('Unknown corner owner')


def analyze_corner(directory, name, west, south, sources, owner=None, reason=None,
                   allow_core_split=False):
    """Always expose both original corners before resolving any disagreement."""
    directory.mkdir(parents=True, exist_ok=True)
    metric = differences(west, south)
    sheet = Image.new('RGB', (west.width * 2 + 16, west.height + 24), '#eeeeee')
    ImageDraw.Draw(sheet).text((0, 4), 'WEST', fill='black')
    ImageDraw.Draw(sheet).text((west.width + 16, 4), 'SOUTH', fill='black')
    sheet.paste(west, (0, 24)); sheet.paste(south, (west.width + 16, 24))
    contact = directory / f'{name}.corner-sources-1to1.png'
    sheet.save(contact)
    allowed = ['west', 'south'] + (['core-split'] if allow_core_split else [])
    if owner is not None and owner not in allowed:
        raise ValueError(f'Corner owner must be one of {allowed}')
    if owner == 'core-split' and west.size != (OVERLAP, OVERLAP):
        raise ValueError('core-split is a 230-pixel guide policy, never an exterior halo policy')
    explicit = owner in allowed and bool(reason and reason.strip())
    record = {'createdAt': now(), 'metric': metric, 'sources': sources, 'contact': info(contact),
              'contactResized': False, 'ownerRequested': owner, 'reason': reason,
              'explicitDecisionProvided': explicit, 'bothSourcesAssertedEqual': metric['byteEqual'],
              'selection': owner if explicit else ('identical' if metric['byteEqual'] else None),
              'allowedOwners': allowed, 'visualReviewStillRequired': True,
              'decisionIsVisualAcceptance': False}
    if explicit:
        chosen = corner_image(west, south, owner)
        chosen_path = directory / f'{name}.corner-selected-context-1to1.png'
        chosen.save(chosen_path)
        record['selectedContext'] = {**info(chosen_path), 'resized': False}
        record['sourceOwnerRectsInCorner'] = (
            [{'owner': 'west', 'box': [0, 0, OVERLAP, HALO]},
             {'owner': 'south', 'box': [0, HALO, OVERLAP, OVERLAP]}]
            if owner == 'core-split' else
            [{'owner': owner, 'box': [0, 0, west.width, west.height]}])
        if owner == 'core-split':
            record['guideOnly'] = True
            record['knownLimitation'] = ('Source ownership preserves west core above the boundary and south '
                'core below it, but may expose a visible contour or tone step. This is not seam acceptance.')
    write(directory / f'{name}.corner-analysis.json', record)
    return record


def require_corner_decision(record):
    if not record['metric']['byteEqual'] and not record['explicitDecisionProvided']:
        options = '|'.join(record.get('allowedOwners', ['west', 'south']))
        raise ValueError(f'Corner sources disagree. View the saved 1:1 contact and explicitly pass --corner-owner {options} and --corner-reason; no default overwrite')
    return record['selection'] if record['selection'] != 'identical' else 'west'
