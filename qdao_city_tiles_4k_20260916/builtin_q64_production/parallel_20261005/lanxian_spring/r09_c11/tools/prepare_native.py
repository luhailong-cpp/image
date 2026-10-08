"""Prepare one guide-only crop and a job compatible with ../../tools/register_job.py."""
from __future__ import annotations

import argparse
import json
import numpy as np
from PIL import Image

from common import (TILE, REPO, NATIVE, CORE, HALO, OVERLAP, EXTENDED,
                    WEST, WEST_SHA, now, sha, read, write, info, load_png,
                    load_native, load_west)


def prepare(row, col, description):
    if not 1 <= row <= 4 or not 1 <= col <= 4:
        raise ValueError('row and col must be 1..4')
    if not description.strip():
        raise ValueError('--description must describe this actual viewed crop')
    cell = f'r{row:02d}_c{col:02d}'
    if (TILE / 'native' / f'{cell}.png').exists():
        raise ValueError(f'Refusing to prepare an already registered native cell: {cell}')
    job_path = TILE / 'jobs' / f'{cell}.json'
    target = TILE / 'guides' / f'{cell}.layout-only.png'
    prompt_path = TILE / 'prompts' / f'{cell}.prompt.txt'
    if any(path.exists() for path in (job_path, target, prompt_path)):
        raise ValueError(f'Prepared inputs already exist for {cell}; inspect them rather than overwrite evidence')

    # Gather and validate every dependency before writing anything. Requiring
    # both predecessors permits diagonal wavefront parallelism without races.
    neighbors = []
    if col > 1:
        image, source = load_native(row, col - 1)
        neighbors.append(('west', image, source, [CORE, 0, NATIVE, NATIVE], [0, 0, OVERLAP, NATIVE]))
    if row > 1:
        image, source = load_native(row - 1, col)
        neighbors.append(('north', image, source, [0, CORE, NATIVE, NATIVE], [0, 0, NATIVE, OVERLAP]))
    west = load_west() if col == 1 else None
    regional = TILE / 'regional/shared-region1254.png'
    region = load_png(regional, (NATIVE, NATIVE))
    style = REPO / 'designs/gameplay-ui/04-guild.png'
    style_info = info(style)
    config = read(REPO / 'config/image-generation.json')
    x, y = (col - 1) * CORE, (row - 1) * CORE
    master = region.resize((EXTENDED, EXTENDED), Image.Resampling.BICUBIC)
    guide = master.crop((x, y, x + NATIVE, y + NATIVE))
    occupied = np.zeros((NATIVE, NATIVE), dtype=bool)
    constraints = []

    def apply(side, image, source, source_box, target_box):
        fragment = image.crop(source_box)
        tx0, ty0, tx1, ty1 = target_box
        old = np.asarray(guide.crop(target_box)).astype(np.int16)
        incoming = np.asarray(fragment).astype(np.int16)
        overlap = occupied[ty0:ty1, tx0:tx1]
        diff = incoming - old
        collision = {'pixelsWithEarlierNativeContext': int(overlap.sum()),
                     'disagreeingPixels': int((np.any(diff != 0, axis=2) & overlap).sum()),
                     'meanAbsoluteRGBDifference': float(np.abs(diff[overlap]).mean()) if overlap.any() else 0.0,
                     'resolution': 'later priority source owns intersecting guide pixels; no blending'}
        guide.paste(fragment, (tx0, ty0))
        occupied[ty0:ty1, tx0:tx1] = True
        constraints.append({'side': side, 'source': source, 'sourceCrop': source_box,
                            'targetBox': target_box, 'resized': False,
                            'cornerConflict': collision})

    for side, image, source, source_box, target_box in neighbors:
        apply(side, image, source, source_box, target_box)
    if west is not None:
        apply('external_west', west, {'file': str(WEST), 'sha256': WEST_SHA},
              [4096, y, 4326, y + NATIVE], [0, 0, OVERLAP, NATIVE])
    # Compare sources a second time, preventing preparation against a concurrent
    # replacement. Every guide source is read-only and the job is immutable.
    for constraint in constraints:
        source = constraint['source']
        if sha(source['file']) != source['sha256']:
            raise ValueError('A native context source changed during preparation')
    sides = [constraint['side'] for constraint in constraints]
    bands = []
    bands.append('the first 230 pixels on the left')
    if row > 1:
        bands.append('the first 230 pixels at the top')
    prompt = (
        f'Use case: precise-object-edit. Produce one opaque full-bleed native 1254 by 1254 game-map detail square '
        f'for the original Daoist chibi game 五行奇谈, patch {cell} of shared structural tile r09_c11. '
        'Use exactly Image 1 framing, scale and coordinates. This shared geometry will be reused for daytime and '
        'Spring Festival appearances. Image 1 is a soft regional layout guide with genuine native neighbor '
        f'pixels in {" and ".join(bands)}. Preserve the shown edge-strip colors, endpoints, contours, '
        f'paving joints and silhouettes, connecting them naturally into the interior. The {"x=230 and y=230" if row > 1 else "x=230"} guide '
        'paste boundaries are not physical scene edges: do not invent a vertical or horizontal stripe, wall, '
        'ledge, border or doubled contour there. Reconstruct the soft remaining interior into crisp original '
        'painted detail at the same mapped scale. Do not zoom, pan, rotate, reframe, stretch or redesign anything. '
        f'Content actually visible in this crop: {description.strip()} '
        'Only render those visible elements and their existing continuations. Preserve all route widths, '
        'height transitions, water and shore boundaries, tree footprints, shadows and structural geometry. '
        'Do not import features from another part of the region. Image 2 is the user-confirmed primary '
        'painting and material style: bright clean rounded full-bodied Daoist chibi fantasy, polished delicate '
        'hand-painted materials, soft dimensional highlights, crisp quiet contours and restrained surface '
        'variation. Use no UI or text from Image 2. Keep stone stone-colored, foliage green, water turquoise '
        'blue and existing surface colors as shown. Add no festival decorations, buildings, planters, trees, '
        'lanterns, stairs, circles, medallions, objects, characters, text, frames or watermarks. No photographic '
        'texture, plastic look, gritty noise, excessive marbling, cracks, speckles, blur or sharpening halos. '
        'Output only the target native square at highest available visual fidelity.'
    )
    refs = [
        {'path': str(target), 'role': 'Guide only: mapped composition plus unscaled native neighbor constraints'},
        {'path': str(style), 'role': 'Confirmed primary painting/material style; copy no UI or text', 'sha256': style_info['sha256']},
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    guide.save(target)
    prompt_path.write_text(prompt + '\n', encoding='utf-8')
    job = {
        'schemaVersion': 1, 'tileDir': str(TILE), 'cell': cell, 'promptFile': str(prompt_path),
        'references': refs, 'configSnapshot': config, 'preparedAt': now(),
        'descriptionFromActualCropReview': description.strip(), 'constraints': constraints,
        'constraintPriorityLowToHigh': ['internal_west', 'north', 'external_west'],
        'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False,
                                'referenced_image_paths': [ref['path'] for ref in refs]},
        'guideDerivation': {'regional': info(regional), 'guide': info(target), 'guideOnly': True,
                            'regionalResampling': 'BICUBIC 1254 to 4326 for guide only; never final art',
                            'cropInExtended': [x, y, x + NATIVE, y + NATIVE],
                            'nativeSize': NATIVE, 'coreSize': CORE, 'halo': HALO,
                            'sharedDaySpringGeometry': True},
        'qa': {'referenceImagesMustBeViewedBeforeSubmission': True, 'nativeOutputPending': True,
               'accepted': False, 'formalAccepted': False},
    }
    write(job_path, job)
    print(json.dumps({'job': str(job_path), 'promptFile': str(prompt_path),
                      'references': refs, 'constraints': sides}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('row', type=int)
    parser.add_argument('col', type=int)
    parser.add_argument('--description', required=True, help='Accurate content of this viewed crop only')
    args = parser.parse_args()
    try:
        prepare(args.row, args.col, args.description)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'error: {error}\n')
