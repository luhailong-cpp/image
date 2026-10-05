"""Prepare layout-only guides for a new frontier tile with native north/west context."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, re
from PIL import Image
from workflow import OUTPUT_ROOT, safe_output, sha256, read_json, write_json

REPO = Path('D:/work/image')

def prepare(tile_name, row, col):
    if not re.fullmatch(r'r\d{2}_c\d{2}', tile_name) or not (1 <= row <= 4 and 1 <= col <= 4):
        raise ValueError('Invalid tile or cell')
    tile = safe_output(OUTPUT_ROOT / tile_name)
    cell = f'r{row:02d}_c{col:02d}'
    if (tile / 'native' / f'{cell}.png').exists():
        raise FileExistsError(cell)
    context = read_json(tile / 'regional/context.json')
    region = tile / 'regional/regional.png'
    region_record = read_json(tile / 'regional/generation.json')
    if sha256(region) != region_record['sha256']:
        raise ValueError('Regional image has changed')
    guide = Image.open(region).convert('RGB').resize((4326,4326), Image.Resampling.BICUBIC)
    x, y = (col - 1) * 1024, (row - 1) * 1024
    guide = guide.crop((x,y,x+1254,y+1254))
    constraints = []
    if col == 1:
        west = context['westExtended']
        p = Path(west['file'])
        if sha256(p) != west['sha256']:
            raise ValueError('External west context changed')
        im = Image.open(p).convert('RGB')
        if im.size != (4326,4326):
            raise ValueError('West must include native exterior halo')
        guide.paste(im.crop((4096,y,4326,y+1254)),(0,0))
        constraints.append({'side':'external_west','file':str(p),'sha256':west['sha256'],
            'sourceBox':[4096,y,4326,y+1254],'targetBox':[0,0,230,1254]})
    for r, c, side in [(row,col-1,'west'),(row-1,col,'north')]:
        if not r or not c:
            continue
        p = tile / 'native' / f'r{r:02d}_c{c:02d}.png'
        rp = Path(str(p) + '.generation.json')
        if not p.exists() or not rp.exists():
            raise SystemExit(f'WAIT: {side} neighbor {p}')
        record = read_json(rp)
        if sha256(p) != record['sha256']:
            raise ValueError('Native neighbor changed')
        im = Image.open(p).convert('RGB')
        box = (1024,0,1254,1254) if side == 'west' else (0,1024,1254,1254)
        guide.paste(im.crop(box),(0,0))
        constraints.append({'side':side,'file':str(p),'sha256':record['sha256'],
            'sourceBox':list(box),'targetBox':[0,0,230,1254] if side == 'west' else [0,0,1254,230]})
    target = safe_output(tile/'guides'/f'{cell}.layout-only.png')
    guide.save(target)
    bands = 'first 230 pixels on the left' + (' and first 230 pixels at the top' if row > 1 else '')
    prompt = (
        f'Use case: precise-object-edit. Create one opaque full-bleed native game-map detail square. '
        f'Image 1 gives the EXACT target framing, scale, geometry, and object footprint for {tile_name}/{cell}; '
        f'its {bands} contain true native neighboring art. Preserve these bands and every crossing groove, '
        'bevel, contour and shadow at their exact coordinates. Reconstruct ONLY the soft interior into crisp real '
        'hand-painted detail with matching scale. Do not move, crop, rotate, enlarge or recompose anything. '
        'Image 2 is the user-confirmed PRIMARY painting/material reference: bright, clean, rounded, full-bodied '
        'Daoist chibi fantasy, smooth readable bevels and restrained low-contrast painterly surfaces. '
        'Copy no UI, words, floral border ornaments, characters, lighting or objects from Image 2 into the map. '
        'Inventory is determined only by Image 1. Keep existing ivory stone, cream trim, warm shallow risers, '
        'gray paving, planter and foliage exactly where visible. If a target contains stone only, return STONE ONLY '
        'with no added plant, flower, object, stain or cast shadow. Quiet clean stone: no grit, cracks, veins, '
        'spotted noise, exaggerated brush patches, blur or sharpening halos. Keep all existing leaves rounded '
        'and clean if foliage is present. No new buildings, circles, stairs, medallions, symbols, characters, '
        'frames, labels or watermark. Return only the single native 1254-square detail image, highest available fidelity.'
    )
    pf = safe_output(tile/'prompts'/f'{cell}.prompt.txt');pf.write_text(prompt,encoding='utf-8')
    refs = [{'path':str(target),'role':'Guide-only target geometry with exact native neighbor bands; coordinates invariant'},
            {'path':str(REPO/'designs/gameplay-ui/04-guild.png'),'role':'User-confirmed primary painting/material style; copy no UI or added objects'}]
    job = {'tileDir':str(tile),'cell':cell,'prompt':prompt,'promptFile':str(pf),'references':refs,
        'configSnapshot':read_json(REPO/'config/image-generation.json'),
        'generatedAt':datetime.now(timezone.utc).isoformat(),'constraints':constraints,
        'submittedParameters':{'model':None,'quality':None,'transparent_background':False,
            'referenced_image_paths':[r['path'] for r in refs]},
        'guideDerivation':{'regional':str(region),'regionalSha256':sha256(region),
            'regionalResampling':'BICUBIC4326 for guide only; no guide pixels in final art',
            'guide':str(target),'guideSha256':sha256(target),'guideOnly':True,
            'cropInExtended':[x,y,x+1254,y+1254]}}
    jf = safe_output(tile/'jobs'/f'{cell}.json');write_json(jf,job)
    print(json.dumps({'job':str(jf),'promptFile':str(pf),'references':refs}))

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('row',type=int);p.add_argument('col',type=int)
    a=p.parse_args();prepare(a.tile,a.row,a.col)
