"""Exact native-overlap comparison sheets for c13 row 4; no final pixels changed."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
TILE = ROOT / 'r08_c13'
OUT = TILE / 'qa' / 'row4-native-overlaps'
OUT.mkdir(parents=True, exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source(c):
    path = TILE / 'native' / f'r04_c{c:02}.png'
    record = json.loads(Path(str(path) + '.generation.json').read_text(encoding='utf-8-sig'))
    im = Image.open(path).convert('RGB')
    assert im.size == (1254, 1254) and sha(path) == record['sha256']
    return path, im

items = []
for c in range(1, 4):
    left_path, left = source(c)
    right_path, right = source(c + 1)
    # Side-by-side duplicate views of the very same global 230-pixel overlap.
    sheet = Image.new('RGB', (460, 1254))
    sheet.paste(left.crop((1024, 0, 1254, 1254)), (0, 0))
    sheet.paste(right.crop((0, 0, 230, 1254)), (230, 0))
    path = OUT / f'c{c:02}-c{c+1:02}-same-global-overlap.png'
    sheet.save(path)
    item = {'file': str(path), 'sha256': sha(path), 'pixels': [460, 1254],
            'operation': 'two exact unscaled crops, side by side for native comparison; not an assembled seam',
            'derivedFrom': [
                {'file': str(left_path), 'sha256': sha(left_path), 'cropXYXY': [1024, 0, 1254, 1254], 'pasteXY': [0, 0]},
                {'file': str(right_path), 'sha256': sha(right_path), 'cropXYXY': [0, 0, 230, 1254], 'pasteXY': [230, 0]}],
            'finalArt': False, 'resized': False}
    Path(str(path) + '.generation.json').write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
    items.append(item)
(OUT / 'manifest.json').write_text(json.dumps({'scope': 'all 3 native row4 internal overlaps, before shared DAY alpha assembly', 'sheets': items}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'sheets': [i['file'] for i in items]}))
