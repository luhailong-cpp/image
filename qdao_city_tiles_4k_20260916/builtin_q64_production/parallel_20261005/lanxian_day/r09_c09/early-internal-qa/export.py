from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

out = Path(__file__).resolve().parent
tile = out.parent
assert tile.name == 'r09_c09'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
canvas = Image.new('RGB', (4096, 3072))
sources = []
for row in range(1, 4):
    for col in range(1, 5):
        p = tile / 'native' / f'r{row:02d}_c{col:02d}.png'
        gp = Path(str(p) + '.generation.json')
        g = json.loads(gp.read_text(encoding='utf-8-sig'))
        assert sha(p) == g['sha256']
        im = Image.open(p)
        assert im.size == (1254, 1254) and im.mode == 'RGB'
        dx, dy = (col - 1) * 1024, (row - 1) * 1024
        canvas.paste(im.crop((115, 115, 1139, 1139)), (dx, dy))
        sources.append({'cell': f'r{row:02d}_c{col:02d}', 'file': str(p), 'sha256': sha(p),
                        'generationRecord': str(gp), 'generationRecordSha256': sha(gp),
                        'sourceBox': [115, 115, 1139, 1139], 'targetCoreBox': [dx, dy, dx+1024, dy+1024]})
checks = []
def save(name, box, kind, seam):
    p = out / (name + '.png')
    if p.exists(): raise FileExistsError(p)
    im = canvas.crop(box)
    im.save(p)
    mappings = []
    for source in sources:
        sbox = source['targetCoreBox']
        x0, y0 = max(box[0], sbox[0]), max(box[1], sbox[1])
        x1, y1 = min(box[2], sbox[2]), min(box[3], sbox[3])
        if x1 <= x0 or y1 <= y0: continue
        mappings.append({'file': source['file'], 'sha256': source['sha256'],
                         'sourceBox': [115+x0-sbox[0], 115+y0-sbox[1], 115+x1-sbox[0], 115+y1-sbox[1]],
                         'destinationXY': [x0-box[0], y0-box[1]], 'targetCoreBox': [x0, y0, x1, y1]})
    checks.append({'name': name, 'file': str(p), 'sha256': sha(p), 'pixels': list(im.size),
                   'decodedRgbSha256': hashlib.sha256(im.tobytes()).hexdigest(), 'targetCoreBox': box,
                   'kind': kind, 'seamCoordinate': seam, 'pixelMappings': mappings,
                   'operation': 'Integer native-core crop and paste; no resizing, feathering, corrections or generated pixels',
                   'resampling': 'none', 'actualViewed': False})
for row in [1, 2]:
    for col in range(4):
        x, y = col*1024, row*1024
        save(f'horizontal_r{row}_c{col+1}', [x, y-128, x+1024, y+128], 'horizontal_core_seam', y)
        y += 115
        save(f'guide_horizontal_r{row+1}_c{col+1}', [x, y-64, x+1024, y+64], 'horizontal_guide_inner_edge', y)
for row in range(3):
    for seam in range(1, 4):
        x, y = seam*1024, row*1024
        save(f'vertical_r{row+1}_c{seam}', [x-128, y, x+128, y+1024], 'vertical_core_seam', x)
for row in [1, 2]:
    for col in [1, 2, 3]:
        x, y = col*1024, row*1024
        save(f'intersection_r{row}_c{col}', [x-256, y-256, x+256, y+256], 'four_native_cell_intersection', [x,y])
assert len(checks) == 31
manifest = {'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(), 'tile': 'r09_c09',
            'sources': sources, 'temporaryUnsavedCanvasPixels': [4096,3072],
            'temporaryCanvasDecodedRgbSha256': hashlib.sha256(canvas.tobytes()).hexdigest(),
            'partialOnly': True, 'isComplete4KCandidate': False, 'formalAccepted': False,
            'checks': checks, 'status': 'pending_actual_original_pixel_views',
            'scope': {'horizontalCoreSeams':8, 'horizontalGuideInnerEdges':8, 'verticalCoreSeams':9, 'intersections':6, 'total':31}}
mp = out / 'manifest.json'
assert not mp.exists()
mp.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps({'manifest':str(mp), 'sha256':sha(mp), 'checks':len(checks)}))
