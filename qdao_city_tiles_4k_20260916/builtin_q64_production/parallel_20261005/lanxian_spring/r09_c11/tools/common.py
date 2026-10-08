"""Shared strict source checks for r09_c11 native production."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

TILE = Path(__file__).resolve().parents[1]
ROOT = TILE.parent
REPO = Path('D:/work/image')
NATIVE, CORE, HALO, OVERLAP, EXTENDED = 1254, 1024, 115, 230, 4326
WEST = ROOT / 'r09_c10/selected-v2/extended4326.png'
WEST_SHA = '3532108ee8d5eab3f85bee5abb83924e5df41c2a1126b08554a6c754d0bd917d'


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
            raise ValueError(f'Expected PNG {dimensions}, got {image.format} {image.size}: {path}')
        if 'A' in image.getbands() and image.getchannel('A').getextrema() != (255, 255):
            raise ValueError(f'Expected opaque pixels: {path}')
        return image.convert('RGB')


def load_native(row, col):
    cell = f'r{row:02d}_c{col:02d}'
    path = TILE / 'native' / f'{cell}.png'
    record = path.with_name(path.name + '.generation.json')
    if not path.is_file() or not record.is_file():
        raise ValueError(f'WAIT: registered native dependency is absent: {cell}')
    metadata = read(record)
    digest = sha(path)
    if metadata.get('sha256') != digest:
        raise ValueError(f'Native SHA differs from generation record: {cell}')
    image = load_png(path, (NATIVE, NATIVE))
    return image, {'patchId': cell, 'file': str(path), 'sha256': digest,
                   'generationRecord': info(record), 'sourceNativeSize': [NATIVE, NATIVE],
                   'resized': False}


def load_west():
    if sha(WEST) != WEST_SHA:
        raise ValueError('Pinned selected-v2 west source changed; review/re-pin explicitly before continuing')
    return load_png(WEST, (EXTENDED, EXTENDED))
