from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TILE = ROOT / 'r09_c09'
OUT = Path(__file__).resolve().parent
assert ROOT.name == 'lanxian_day' and TILE.is_relative_to(ROOT)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rgbsha(im):
    return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def native(row, col):
    p = TILE / 'native' / f'r{row:02d}_c{col:02d}.png'
    r = read(Path(str(p) + '.generation.json'))
    assert sha(p) == r['sha256']
    im = Image.open(p).convert('RGB')
    assert im.size == (1254, 1254)
    return im, {'file': str(p), 'sha256': r['sha256'], 'generationRecord': str(p) + '.generation.json'}

def selected(name):
    d = read(ROOT / name / 'selected/delivery.manifest.json')
    m = d['outputs']['core']
    p = Path(m['file'])
    assert sha(p) == m['sha256']
    im = Image.open(p).convert('RGB')
    assert im.size == (4096, 4096)
    return im, {'file': str(p), 'sha256': m['sha256']}

def mapping(meta, sourcebox, targetbox):
    return dict(meta, sourceBoxXYXY=list(sourcebox), targetBoxXYXY=list(targetbox), resampling='none')

exports = []
def save(name, im, maps, **more):
    p = OUT / name
    assert not p.exists()
    im.save(p)
    exports.append({'file': str(p), 'sha256': sha(p), 'pixels': list(im.size),
                    'rawRGBSha256': rgbsha(im), 'mapping': maps, 'resampling': 'none', **more})
    return {'file': str(p), 'sha256': sha(p), 'rawRGBSha256': rgbsha(im)}

top = Image.new('RGB', (4096, 1024))
topmaps = []
for col in range(1, 5):
    im, m = native(1, col)
    box = (115, 115, 1139, 1139)
    dx = (col - 1) * 1024
    top.paste(im.crop(box), (dx, 0))
    topmaps.append(mapping(m, box, (dx, 0, dx + 1024, 1024)))
topmeta = save('top-row-core4096x1024.png', top, topmaps,
               role='QA-only partial top row; not a complete tile or delivery candidate', notVisualScope=True)
north, nm = selected('r08_c09')
east, em = selected('r09_c10')
for col in range(1, 5):
    x = (col - 1) * 1024
    im = Image.new('RGB', (1024, 512))
    im.paste(north.crop((x, 3840, x + 1024, 4096)), (0, 0))
    im.paste(top.crop((x, 0, x + 1024, 256)), (0, 256))
    save(f'external-north-part{col}.png', im,
         [mapping(nm, (x, 3840, x + 1024, 4096), (0, 0, 1024, 256)),
          mapping(topmeta, (x, 0, x + 1024, 256), (0, 256, 1024, 512))],
         scope='external_north', targetCoreBox=[x, 0, x + 1024, 256], seamInBoardY=256)
    box = (x, 51, x + 1024, 179)
    save(f'guide-north-part{col}.png', top.crop(box),
         [mapping(topmeta, box, (0, 0, 1024, 128))],
         scope='guide_north_y115', targetCoreBox=list(box), boundaryInBoardY=64)
for row in range(1, 4):
    src, sm = native(row, 4)
    y = (row - 1) * 1024
    im = Image.new('RGB', (512, 1024))
    im.paste(src.crop((883, 115, 1139, 1139)), (0, 0))
    im.paste(east.crop((0, y, 256, y + 1024)), (256, 0))
    save(f'external-east-part{row}.png', im,
         [mapping(sm, (883, 115, 1139, 1139), (0, 0, 256, 1024)),
          mapping(em, (0, y, 256, y + 1024), (256, 0, 512, 1024))],
         scope='external_east', targetCoreBox=[3840, y, 4096, y + 1024], seamInBoardX=256)
    save(f'guide-east-part{row}.png', src.crop((960, 115, 1088, 1139)),
         [mapping(sm, (960, 115, 1088, 1139), (0, 0, 128, 1024))],
         scope='guide_east_x3981', targetCoreBox=[3917, y, 4045, y + 1024], boundaryInBoardX=64)
box = (3584, 0, 4096, 512)
save('corner-northeast512.png', top.crop(box),
     [mapping(topmeta, box, (0, 0, 512, 512))],
     scope='own_northeast_corner', targetCoreBox=list(box))
manifest = {'schemaVersion': 1, 'tile': 'r09_c09', 'createdAt': datetime.now(timezone.utc).isoformat(),
            'purpose': 'Early partial-tile QA only; no final delivery or acceptance implied.',
            'scopeCount': 15, 'exports': exports,
            'missingScope': 'Fourth-row east edge and guide band not included; later full-tile QA required.'}
p = OUT / 'derivation.json'
assert not p.exists()
p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'manifest': str(p), 'sha256': sha(p), 'visualScopeCount': 15, 'exportCount': len(exports)}))
