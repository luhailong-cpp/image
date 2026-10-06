"""Prepare guide-only native cells with optional west/north external context.

Default hard-band behavior remains available. --soft-context affects guide pixels
only: the first115 neighbor pixels remain native (north wins a shared corner),
and the following115 reference pixels taper into regional context.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, re

import numpy as np
from PIL import Image
from workflow import OUTPUT_ROOT, safe_output, sha256, read_json, write_json, save_image

REPO = Path('D:/work/image')
NATIVE, STEP, HALO, OVERLAP, EXTENDED = 1254, 1024, 115, 230, 4326


def load_native(path, size, expected_sha, label):
    path = Path(path).resolve(strict=True)
    if sha256(path) != expected_sha:
        raise ValueError(f'{label} changed')
    with Image.open(path) as image:
        if image.format != 'PNG' or image.mode not in ('RGB', 'RGBA') or image.size != size:
            raise ValueError(f'{label} must be an RGB/RGBA PNG of size{size}')
        if image.mode == 'RGBA' and image.getextrema()[3] != (255, 255):
            raise ValueError(f'{label} must be opaque')
        image.load()
        return image.convert('RGB')


def native_weights(soft_context):
    weights = np.ones(OVERLAP, dtype=np.float32)
    if soft_context:
        t = np.arange(HALO, dtype=np.float32) / (HALO - 1)
        weights[HALO:] = 1 - t * t * (3 - 2 * t)
    return weights


def prepare(tile_name, row, col, soft_context=False):
    match = re.fullmatch(r'r(\d{2})_c(\d{2})', tile_name)
    if match is None or not all(1 <= int(n) <= 16 for n in match.groups()) or not (1 <= row <= 4 and 1 <= col <= 4):
        raise ValueError('Invalid tile or cell')
    tile = safe_output(OUTPUT_ROOT / tile_name)
    if tile.parent != OUTPUT_ROOT or tile.name != tile_name:
        raise ValueError('Tile output resolves outside the requested tile directory')

    def destination(relative):
        path = safe_output(tile / relative)
        if not path.is_relative_to(tile):
            raise ValueError('Output escapes the requested tile directory')
        return path

    cell = f'r{row:02d}_c{col:02d}'
    target = destination(f'guides/{cell}.layout-only.png')
    pf = destination(f'prompts/{cell}.prompt.txt')
    jf = destination(f'jobs/{cell}.json')
    outputs = [target, pf, jf, destination(f'native/{cell}.png')]
    if any(p.exists() for p in outputs):
        raise FileExistsError(f'Refusing to overwrite existing output for{cell}')
    context_path = tile / 'regional/context.json'
    context = read_json(context_path)
    if not (context.get('westExtended') or context.get('northExtended')):
        raise ValueError('Context must name westExtended and/or northExtended')
    region = tile / 'regional/regional.png'
    region_record = read_json(tile / 'regional/generation.json')
    regional = load_native(region, (NATIVE, NATIVE), region_record['sha256'], 'Regional image')
    x, y = (col - 1) * STEP, (row - 1) * STEP
    guide = regional.resize((EXTENDED, EXTENDED), Image.Resampling.BICUBIC).crop((x, y, x + NATIVE, y + NATIVE))
    bands = []

    def add_band(side, path, expected_sha, size, source_box):
        p = Path(path).resolve(strict=True)
        im = load_native(p, size, expected_sha, f'{side} context')
        orientation = 'left' if side in ('west', 'external_west') else 'top'
        target_box = [0, 0, OVERLAP, NATIVE] if orientation == 'left' else [0, 0, NATIVE, OVERLAP]
        cropped = im.crop(source_box)
        if cropped.size != (target_box[2], target_box[3]):
            raise ValueError('Native band crop does not match target dimensions')
        bands.append((cropped, {'side': side, 'orientation': orientation,
            'file': str(p), 'sha256': expected_sha, 'sourceBox': list(source_box),
            'targetBox': target_box, 'operation': 'integer crop; no native source resize',
            'nativeSourceResampling': 'none'}))

    # Gather left first and top second, matching historical north-last precedence.
    if col == 1:
        west = context.get('westExtended')
        if west:
            add_band('external_west', west['file'], west['sha256'],
                     (EXTENDED, EXTENDED), (4096, y, 4326, y + NATIVE))
    else:
        p = tile / 'native' / f'r{row:02d}_c{col - 1:02d}.png'
        rp = Path(str(p) + '.generation.json')
        if not p.exists() or not rp.exists():
            raise SystemExit(f'WAIT: west neighbor{p}')
        add_band('west', p, read_json(rp)['sha256'], (NATIVE, NATIVE),
                 (STEP, 0, NATIVE, NATIVE))

    if row == 1:
        north = context.get('northExtended')
        if north:
            add_band('external_north', north['file'], north['sha256'],
                     (EXTENDED, EXTENDED), (x, 4096, x + NATIVE, 4326))
    else:
        p = tile / 'native' / f'r{row - 1:02d}_c{col:02d}.png'
        rp = Path(str(p) + '.generation.json')
        if not p.exists() or not rp.exists():
            raise SystemExit(f'WAIT: north neighbor{p}')
        add_band('north', p, read_json(rp)['sha256'], (NATIVE, NATIVE),
                 (0, STEP, NATIVE, NATIVE))
    if not bands:
        raise ValueError('The requested cell has no native neighbor constraint')

    weights = native_weights(soft_context)
    has_left = any(meta['orientation'] == 'left' for _, meta in bands)
    has_top = any(meta['orientation'] == 'top' for _, meta in bands)
    corner = {'priority': 'top/north after left/west', 'overlapExists': has_left and has_top}
    if has_left and has_top:
        left = next(im for im, m in bands if m['orientation'] == 'left')
        top = next(im for im, m in bands if m['orientation'] == 'top')
        diff = np.array(left.crop((0, 0, HALO, HALO)), dtype=np.int16) - np.array(top.crop((0, 0, HALO, HALO)), dtype=np.int16)
        corner.update(nativeSourcesAgreeInSharedFirst115Square=not bool(np.any(diff)),
                      differingPixelCount=int(np.any(diff != 0, axis=2).sum()),
                      maximumAbsoluteChannelDifference=int(np.abs(diff).max()),
                      leftStrictBandOverrideByNorthCore=[0, 0, HALO, HALO],
                      note='Both source corner arrays cannot be claimed exact when they disagree; north is authoritative here.')

    constraints = []
    for band, meta in bands:
        box = meta['targetBox']
        if soft_context:
            alpha = np.broadcast_to(weights[None, :], (NATIVE, OVERLAP)).copy() if meta['orientation'] == 'left' else np.broadcast_to(weights[:, None], (OVERLAP, NATIVE)).copy()
            if meta['orientation'] == 'top' and has_left:
                # Below north's strict first115 rows, preserve west's first115 columns.
                alpha[HALO:, :HALO] = 0
                meta['alphaZeroOverrideTargetBox'] = [0, HALO, HALO, OVERLAP]
            old = np.array(guide.crop(box), dtype=np.float32)
            new = np.array(band, dtype=np.float32)
            composed = np.rint(new * alpha[:, :, None] + old * (1 - alpha[:, :, None])).astype('uint8')
            guide.paste(Image.fromarray(composed), (0, 0))
        else:
            guide.paste(band, (0, 0))
        meta.update(guideOnly=True, compositionMode='soft_context' if soft_context else 'hard_native_band',
                    nativeWeightProfile='guideDerivation.contextProfile.nativeWeightsByNormalIndex',
                    targetNormalAxis='x' if meta['orientation'] == 'left' else 'y')
        constraints.append(meta)
    for band, meta in bands:
        if meta['orientation'] == 'top':
            strict = [0, 0, NATIVE, HALO]
        else:
            # The exact declared region excludes the portion genuinely superseded by north.
            start_y = (HALO if soft_context else OVERLAP) if has_top else 0
            strict = [0, start_y, HALO, NATIVE]
        exact = guide.crop(strict).tobytes() == band.crop(strict).tobytes()
        if not exact:
            raise ValueError('Declared strict native core-reference region lost pixel identity')
        meta.update(guaranteedExactFirst115TargetBox=strict, guaranteedExactFirst115PixelsVerified=True)
        if not soft_context:
            meta['hardBandOverlapNote'] = 'North overwrites the230-square corner when both bands exist; historical behavior retained.'

    side_text = ' and '.join(('left' if m['orientation'] == 'left' else 'top') for _, m in bands)
    if soft_context:
        boundary_instruction = (
            f'The {side_text} neighboring reference band(s) each use first115 pixels as strict native context. '
            'Keep those source grooves, bevels, contours, scale and shadow endpoints exact. The following115 pixels '
            '(indices115..229) are guide-only halo softly transitioned into regional context; complete them coherently, '
            'without reproducing a compositing band as artwork. At a shared corner, the top/north strict source takes precedence. '
            'Never turn guide tone differences, straight compositing bounds, or softened reference edges into walls, steps, '
            'extra paving blocks, foliage edges, new shadows, or broken grooves. '
        )
    else:
        boundary_instruction = (
            f'The first230 pixels at the {side_text} contain native neighboring context; north takes precedence at overlaps. '
            'Preserve the composed native contours, grooves, bevels and shadows at their exact coordinates. '
            'Guide-band tone changes are compositing context, never permission to add walls, steps or extra paving. '
        )
    prompt = (
        'Use case: precise-object-edit. Create one opaque full-bleed native game-map detail square. '
        f'Image1 gives EXACT framing, scale, geometry and object footprints for{tile_name}/{cell}. '
        + boundary_instruction +
        'Reconstruct only the soft interior into crisp real hand-painted detail at matching scale. '
        'Do not move, crop, rotate, enlarge or recompose anything. Image2 is the user-confirmed PRIMARY painting/material '
        'reference: bright, clean, rounded, full-bodied Daoist chibi fantasy, readable smooth bevels and restrained '
        'low-contrast painterly surfaces. Copy no UI, words, floral ornaments, characters, lighting or objects from Image2. '
        'Inventory is determined only by Image1: retain only its existing materials, objects, foliage and shadows. '
        'A stone-only target must remain stone only. No added plants, flowers, gray paving blocks, walls, objects, stains '
        'or cast shadows. Quiet clean stone: no grit, cracks, veins, spotted noise, exaggerated brush patches, blur or '
        'sharpening halos. Keep existing leaves rounded and clean. No new buildings, circles, stairs, medallions, symbols, '
        'characters, frames, labels or watermark. Return only the single native1254-square detail image at highest available fidelity.'
    )
    style = REPO / 'designs/gameplay-ui/04-guild.png'
    if not style.is_file():
        raise FileNotFoundError(style)
    config = read_json(REPO / 'config/image-generation.json')
    if any(p.exists() for p in outputs):
        raise FileExistsError('An output appeared during preparation; refusing overwrite')
    for p in (target, pf, jf):
        destination(p.relative_to(tile)).parent.mkdir(parents=True, exist_ok=True)
    save_image(target, guide)
    pf.write_text(prompt, encoding='utf-8')
    refs = [
        {'path': str(target), 'role': 'Guide-only geometry; native-core references exact within recorded boxes; soft halo context' if soft_context else 'Guide-only geometry with hard native neighbor bands'},
        {'path': str(style), 'role': 'User-confirmed primary painting/material style; copy no UI or added objects'},
    ]
    job = {'tileDir': str(tile), 'cell': cell, 'prompt': prompt, 'promptFile': str(pf), 'references': refs,
        'configSnapshot': config, 'generatedAt': datetime.now(timezone.utc).isoformat(),
        'constraints': constraints, 'submittedParameters': {'model': None, 'quality': None,
            'transparent_background': False, 'referenced_image_paths': [r['path'] for r in refs]},
        'guideDerivation': {'regional': str(region), 'regionalSha256': sha256(region),
            'context': str(context_path), 'contextSha256': sha256(context_path),
            'regionalResampling': 'BICUBIC to4326 for guide only; no guide pixels are final art',
            'guide': str(target), 'guideSha256': sha256(target), 'guideOnly': True,
            'cropInExtended': [x, y, x + NATIVE, y + NATIVE], 'softContext': bool(soft_context),
            'nativeSourceResampling': 'none for every reference band',
            'contextProfile': {'mode': 'smoothstep_halo' if soft_context else 'hard',
                'strictNativeNormalIntervalHalfOpen': [0, HALO],
                'transitionNormalIntervalHalfOpen': [HALO, OVERLAP] if soft_context else None,
                'formula': 'alpha=1 for index<115; otherwise1-smoothstep((index-115)/114), smoothstep(t)=t*t*(3-2*t)' if soft_context else 'alpha=1 for indices0..229',
                'nativeWeightsByNormalIndex': weights.tolist(),
                'regionalWeight': '1-alpha; at band intersections the previous native composition is the base',
                'sourcePixelResampling': 'none', 'imageBlendRounding': 'round-to-nearest uint8'},
            'cornerHandling': corner,
            'finalPixelRestriction': 'All outputs here are guide-only. Final native pixels must come from actual built-in image generation, never this compositing operation.'}}
    write_json(jf, job)
    result = {'job': str(jf), 'promptFile': str(pf), 'references': refs, 'softContext': bool(soft_context)}
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tile')
    parser.add_argument('row', type=int)
    parser.add_argument('col', type=int)
    parser.add_argument('--soft-context', action='store_true', default=False,
                        help='Guide-only smoothstep halo; preserve first115 native pixels, with recorded north corner precedence')
    args = parser.parse_args()
    prepare(args.tile, args.row, args.col, soft_context=args.soft_context)
