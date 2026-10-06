"""Prepare c10 layout-only inputs with SHA-bound native overlap constraints."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import argparse, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
TILE = ROOT / 'r08_c10'
REPO = Path('D:/work/image')
NATIVE, CORE, PADDED, OVERLAP = 1254, 1024, 4326, 230

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def prepare(row, col):
    assert 1 <= row <= 4 and 1 <= col <= 4
    cell = f'r{row:02d}_c{col:02d}'
    assert not (TILE / 'native' / f'{cell}.png').exists(), cell
    for sub in ('guides', 'prompts', 'jobs', 'native'):
        (TILE / sub).mkdir(parents=True, exist_ok=True)
    neighbors = []
    for r, c, side in [(row, col - 1, 'west'), (row - 1, col, 'north')]:
        if r and c:
            path = TILE / 'native' / f'r{r:02d}_c{c:02d}.png'
            record = Path(str(path) + '.generation.json')
            if not path.exists() or not record.exists():
                raise SystemExit(f'WAIT: {side} neighbor {path}')
            if read(record)['sha256'] != sha(path):
                raise SystemExit(f'ERROR: {side} neighbor hash mismatch {path}')
            neighbors.append((side, path, record))
    region = TILE / 'regional' / 'native.png'
    master = Image.open(region).convert('RGB').resize((PADDED, PADDED), Image.Resampling.BICUBIC)
    x, y = (col - 1) * CORE, (row - 1) * CORE
    guide = master.crop((x, y, x + NATIVE, y + NATIVE))
    constraints = []
    for side, path, record in neighbors:
        with Image.open(path) as im:
            assert im.size == (NATIVE, NATIVE)
            if side == 'west':
                guide.paste(im.convert('RGB').crop((CORE, 0, NATIVE, NATIVE)), (0, 0))
                box = [0, 0, OVERLAP, NATIVE]
            else:
                guide.paste(im.convert('RGB').crop((0, CORE, NATIVE, NATIVE)), (0, 0))
                box = [0, 0, NATIVE, OVERLAP]
        constraints.append({'side': side, 'file': str(path), 'sha256': sha(path),
                            'generationRecord': str(record), 'generationRecordSha256': sha(record), 'targetBox': box})
    if col == 1:
        west = TILE / 'guides' / 'spring-c09-east-overlap-230x4326.png'
        with Image.open(west) as im:
            assert im.size == (OVERLAP, PADDED)
            guide.paste(im.convert('RGB').crop((0, y, OVERLAP, y + NATIVE)), (0, 0))
        constraints.append({'side': 'external_west', 'file': str(west), 'sha256': sha(west),
                            'sourceCrop': [0, y, OVERLAP, y + NATIVE], 'targetBox': [0, 0, OVERLAP, NATIVE],
                            'priority': 'exact c09 shared source across full 230px'})
    target = TILE / 'guides' / f'{cell}.layout-only.png'
    guide.save(target)
    bands = 'the first 230px on the left'
    if row > 1:
        bands += ' and the first 230px at the top'
    seam = (' The x=230 vertical boundary in Image 1 is a layout-guide paste boundary, NOT a physical edge. Keep the exact left 230px shared strip in place but reconstruct smooth scene continuity immediately beyond it; do not duplicate or preserve a long vertical border, pale stripe or false ledge at x=230. Continue real paving joints and curved trim across that boundary at the exact existing endpoints.' if col == 1 else '')
    prompt = (f'Use case: precise-object-edit. Create one opaque full-bleed native 1254 by 1254 game-map detail square in exactly Image 1 framing. This is {cell} within the already planned r08_c10 Spring Festival town-plaza tile, not a new scene. Image 1 is a layout guide with true native neighbor pixels in {bands}. Preserve these edge-strip coordinates, colors, scale and geometry; smoothly connect every visible groove, bevel, leaf outline and shadow. Reconstruct the soft remaining interior into crisp real hand-painted detail at this same mapped scale. Do not shift, magnify, rotate, crop or redesign the composition.' + seam + ' Image 2 is the user-confirmed PRIMARY painting and material style: clean bright rounded full-bodied Daoist chibi fantasy, polished delicate hand-painted materials, quiet clean stone, clear contours, soft dimensional highlights, restrained surface variation; no photographic or plastic look. Copy no UI or text. Preserve the shown ivory stone paving and curved trim routes, red-and-warm-gold Spring Festival planter and railing where present, green tree and shrub footprints, shadows, height and walkway geometry. Fine rounded bevels and crisp joints without gritty texture, cracks, speckles, excessive marbling, blur or sharpening halos. Add no new circles, medallions, stairs, buildings, objects, characters, frames, labels or watermark. Return the single target square only, retaining every coordinate in the native 1254-square framing, with the highest available visual fidelity.')
    prompt_file = TILE / 'prompts' / f'{cell}.prompt.txt'
    prompt_file.write_text(prompt, encoding='utf-8')
    refs = [
        {'path': str(target), 'role': 'Layout only plus exact native neighbor strips; edge coordinates are invariant; guide paste boundary is not scene geometry'},
        {'path': str(REPO / 'designs/gameplay-ui/04-guild.png'), 'role': 'User-confirmed primary painting/material style, no UI copied'}]
    job = {'tileDir': str(TILE), 'cell': cell, 'promptFile': str(prompt_file), 'references': refs,
           'configSnapshot': read(REPO / 'config/image-generation.json'),
           'preparedAt': datetime.now(timezone.utc).isoformat(), 'constraints': constraints,
           'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False,
                                   'referenced_image_paths': [ref['path'] for ref in refs]},
           'guideDerivation': {'regional': str(region), 'regionalSha256': sha(region),
                               'regionalResampling': 'BICUBIC to 4326 only for guide; forbidden in final pixels',
                               'guide': str(target), 'guideSha256': sha(target), 'guideOnly': True,
                               'cropInExtended': [x, y, x + NATIVE, y + NATIVE]}}
    job_file = TILE / 'jobs' / f'{cell}.json'
    write(job_file, job)
    print(json.dumps({'job': str(job_file), 'promptFile': str(prompt_file), 'references': refs,
                      'constraints': [c['side'] for c in constraints]}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('row', type=int)
    parser.add_argument('col', type=int)
    args = parser.parse_args()
    prepare(args.row, args.col)
