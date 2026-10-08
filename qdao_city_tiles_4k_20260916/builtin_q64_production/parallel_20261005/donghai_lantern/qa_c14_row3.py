"""Exact native overlap comparisons for c14 row3; QA derivatives only."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
TILE = ROOT / 'r08_c14'
OUT = TILE / 'qa/row3-native-overlaps'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def source(r, c):
    path = TILE / 'native' / f'r{r:02}_c{c:02}.png'
    record = json.loads(Path(str(path) + '.generation.json').read_text(encoding='utf-8-sig'))
    image = Image.open(path).convert('RGB')
    assert image.size == (1254, 1254) and sha(path) == record['sha256']
    return path, image

def save(name, specs, size):
    sheet = Image.new('RGB', size)
    origins = []
    for r, c, rect, dest in specs:
        path, image = source(r, c)
        sheet.paste(image.crop(rect), dest)
        origins.append({'file': str(path), 'sha256': sha(path), 'cropXYXY': list(rect), 'pasteXY': list(dest)})
    path = OUT / name
    sheet.save(path)
    item = {'file': str(path), 'sha256': sha(path), 'pixels': list(size),
            'operation': 'two exact unscaled crops of same global overlap for comparison; not assembled seam',
            'derivedFrom': origins, 'finalArt': False, 'resized': False}
    Path(str(path)+'.generation.json').write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
    return item

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for c in range(1, 4):
        items.append(save(f'c{c:02}-c{c+1:02}-same-global-overlap.png',
                          [(3,c,(1024,0,1254,1254),(0,0)),(3,c+1,(0,0,230,1254),(230,0))], (460,1254)))
    for c in range(1, 5):
        items.append(save(f'north-c{c:02}-same-global-overlap.png',
                          [(2,c,(0,1024,1254,1254),(0,0)),(3,c,(0,0,1254,230),(0,230))], (1254,460)))
    manifest = {'scope': 'all 3 native row3 internal overlaps and 4 north overlaps before shared DAY alpha assembly', 'sheets': items}
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'sheets': [item['file'] for item in items]}))

if __name__ == '__main__': main()
