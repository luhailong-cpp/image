"""Prepare native jobs in order r04 -> r01, west -> east within each row."""
from __future__ import annotations
import argparse
import json
from PIL import Image
from common import (TILE, REPO, NATIVE, CORE, HALO, OVERLAP, EXTENDED,
                    now, info, read, write, load_png, load_native, load_neighbors,
                    check_boundary_pin, unchanged, analyze_corner, require_corner_decision,
                    corner_image)


def prepare(row, col, description='', corner_owner=None, corner_reason=None, analyze_only=False):
    if not 1 <= row <= 4 or not 1 <= col <= 4:
        raise ValueError('row and col must be 1..4')
    cell = f'r{row:02d}_c{col:02d}'
    job_path = TILE / 'jobs' / f'{cell}.json'
    guide_path = TILE / 'guides' / f'{cell}.layout-only.png'
    prompt_path = TILE / 'prompts' / f'{cell}.prompt.txt'
    if (TILE / 'native' / f'{cell}.png').exists():
        raise ValueError(f'Refusing to re-prepare registered native: {cell}')
    if any(path.exists() for path in (job_path, guide_path, prompt_path)):
        raise ValueError(f'Prepared inputs exist: {cell}; do not overwrite generation evidence')
    if not analyze_only and not description.strip():
        raise ValueError('--description must describe the actual viewed crop')
    # Neither a hard-cut preview nor the old west-only guide can stand in for
    # the selected southern neighbor. This check precedes every cell.
    boundaries, boundary_sources = load_neighbors()
    x, y = (col - 1) * CORE, (row - 1) * CORE
    if col == 1:
        west_image = boundaries['west']
        west_source = boundary_sources['west']
        west_box = [4096, y, 4326, y + NATIVE]
        west_kind = 'external_west'
    else:
        west_image, west_source = load_native(row, col - 1)
        west_box = [CORE, 0, NATIVE, NATIVE]
        west_kind = 'internal_west'
    if row == 4:
        south_image = boundaries['south']
        south_source = boundary_sources['south']
        south_box = [x, 0, x + NATIVE, OVERLAP]
        south_kind = 'external_south'
    else:
        south_image, south_source = load_native(row + 1, col)
        south_box = [0, 0, NATIVE, OVERLAP]
        south_kind = 'internal_south'
    west = west_image.crop(west_box)
    south = south_image.crop(south_box)
    corner = analyze_corner(TILE / 'jobs' / cell, cell,
                            west.crop((0, CORE, OVERLAP, NATIVE)),
                            south.crop((0, 0, OVERLAP, OVERLAP)),
                            {'west': {'source': west_source, 'sourceCrop': west_box,
                                      'cornerInFragment': [0, CORE, OVERLAP, NATIVE]},
                             'south': {'source': south_source, 'sourceCrop': south_box,
                                       'cornerInFragment': [0, 0, OVERLAP, OVERLAP]}},
                            corner_owner, corner_reason, allow_core_split=True)
    corner['coordinateMapping'] = {
        'cornerBoxInNative': [0, CORE, OVERLAP, NATIVE],
        'cornerBoxInTileExtended': [x, y + CORE, x + OVERLAP, y + NATIVE],
        'splitYInNative': CORE + HALO if corner_owner == 'core-split' else None,
        'splitYInTileExtended': y + CORE + HALO if corner_owner == 'core-split' else None,
    }
    if corner_owner == 'core-split' and row == 4 and col == 1:
        policy = read(TILE / 'corner-source-ownership.json')
        expected = [{'targetExtendedLTRB': [0, 4096, 230, 4211], 'source': 'west'},
                    {'targetExtendedLTRB': [0, 4211, 230, 4326], 'source': 'south'}]
        actual = [{k: entry[k] for k in ('targetExtendedLTRB', 'source')}
                  for entry in policy['cornerGuideOwnerRects']]
        if actual != expected or policy['splitYInTargetExtended'] != y + CORE + HALO:
            raise ValueError('Native core-split differs from current regional guide corner ownership')
        corner['regionalGuideOwnershipPolicy'] = info(TILE / 'corner-source-ownership.json')
        corner['regionalGuideCoordinateAgreement'] = True
    write(TILE / 'jobs' / cell / f'{cell}.corner-analysis.json', corner)
    if analyze_only:
        print(json.dumps({'cell': cell, 'analysisOnly': True,
                          'corner': corner, 'jobCreated': False}, ensure_ascii=False))
        return
    selected_owner = require_corner_decision(corner)
    regional = TILE / 'regional/shared-region1254.png'
    region = load_png(regional, (NATIVE, NATIVE))
    # Upsampling is confined to this layout guide and explicitly forbidden in
    # production assembly. Actual native overlap fragments are pasted 1:1.
    guide = region.resize((EXTENDED, EXTENDED), Image.Resampling.BICUBIC).crop((x, y, x + NATIVE, y + NATIVE))
    guide.paste(west, (0, 0)); guide.paste(south, (0, CORE))
    guide.paste(corner_image(west.crop((0, CORE, OVERLAP, NATIVE)),
                            south.crop((0, 0, OVERLAP, OVERLAP)), selected_owner), (0, CORE))
    style = REPO / 'designs/gameplay-ui/04-guild.png'
    style_info = info(style)
    config = read(REPO / 'config/image-generation.json')
    unchanged(boundary_sources)
    unchanged([west_source, south_source])
    constraints = [
        {'side': west_kind, 'source': west_source, 'sourceCrop': west_box,
         'targetBox': [0, 0, OVERLAP, NATIVE], 'resized': False,
         'cornerOwnership': corner.get('sourceOwnerRectsInCorner'),
         'fullCornerOwnedByThisSource': selected_owner == 'west'},
        {'side': south_kind, 'source': south_source, 'sourceCrop': south_box,
         'targetBox': [0, CORE, NATIVE, NATIVE], 'resized': False,
         'cornerOwnership': corner.get('sourceOwnerRectsInCorner'),
         'fullCornerOwnedByThisSource': selected_owner == 'south'},
    ]
    prompt = (
        f'Use case: precise-object-edit. Create one opaque native 1254 by 1254 game-map patch {cell} '
        'for the original Daoist chibi game 五行奇谈, shared structural tile r08_c11. '
        'Use exactly Image 1 framing, coordinates, scale and all visible object silhouettes. '
        'This is one common geometry for daytime and Spring Festival appearances. '
        'Image 1 is a soft composition guide with real unscaled native neighbor context in the first '
        '230 pixels on the LEFT and the last 230 pixels at the BOTTOM. Their southwest intersection '
        f'uses the explicitly recorded {selected_owner} context ownership. '
        'For core-split, the upper 115 rows of that intersection use west and the lower 115 use south; '
        'the dividing line is native y=1139. A visible cut or leaf step there is a guide-source '
        'disagreement, not a physical feature to copy. Preserve the committed west core context '
        'at native x<115 and y<1139, and committed south core context at native y>=1139 and x>=115. '
        'Within the new patch core, connect the existing neighbor contours smoothly at those boundaries '
        'without adding a duplicate contour or changing the committed neighbor geometry. '
        'Keep the left and bottom edge endpoints, colors, shadows and contour positions. The x=230 and '
        'y=1024 guide paste boundaries are not physical edges: do not turn them into a stripe, rectangle, '
        'ledge, false wall or duplicate contour. Resolve the soft interior into clean original native '
        'painting at the same mapping. Do not zoom, pan, rotate, stretch, reframe or redesign. '
        f'Actual visible crop content: {description.strip()} '
        'Only render those visible elements and their continuations. Preserve existing navigation '
        'space, route widths, shoreline, tree/planter footprints and structure. '
        'Image 2 is the user-confirmed PRIMARY painting and material style: bright clean rounded '
        'full-bodied Daoist chibi, delicate polished hand-painted materials, quiet soft dimensional '
        'highlights, clear contours, restrained texture. Copy no UI or text. '
        'Keep all existing material colors as shown, including any existing seasonal colors in the '
        'native context. Do not add decorations or invent additional objects. Where water appears, '
        'preserve the existing size, count and density of painted reflection shapes; better clarity '
        'does not mean adding caustic meshes, thin bright veins or more ripples. '
        'No extra buildings, trees, planters, lanterns, stairs, medallions, characters, text, frames '
        'or watermarks. No gritty noise, photographic texture, plastic look, cracks, speckles, blur '
        'or sharpening halos. Return only the target native square with the highest available visual fidelity.'
    )
    refs = [{'path': str(guide_path), 'role': 'Layout guide only with unscaled west and south native constraints; resolved corner is explicit'},
            {'path': str(style), 'role': 'User-confirmed primary painting/material style; no UI copied', 'sha256': style_info['sha256']}]
    check_boundary_pin(boundary_sources, create=True)
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    guide.save(guide_path)
    prompt_path.write_text(prompt + '\n', encoding='utf-8')
    job = {'schemaVersion': 1, 'tileDir': str(TILE), 'cell': cell, 'preparedAt': now(),
           'generationOrder': 'rows 4,3,2,1; columns 1,2,3,4; west plus south dependencies',
           'promptFile': str(prompt_path), 'references': refs, 'configSnapshot': config,
           'descriptionFromActualCropReview': description.strip(), 'boundarySources': boundary_sources,
           'constraints': constraints, 'southwestCornerDecision': corner,
           'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False,
                                   'referenced_image_paths': [ref['path'] for ref in refs]},
           'guideDerivation': {'regional': info(regional), 'guide': info(guide_path), 'guideOnly': True,
                              'regionalResampling': 'BICUBIC 1254 to 4326 for guide only; never final art',
                              'cropInExtended': [x, y, x + NATIVE, y + NATIVE],
                              'nativeSize': NATIVE, 'coreSize': CORE, 'halo': HALO},
           'qa': {'referencesAndCornerMustBeViewedBeforeSubmission': True,
                  'nativeOutputPending': True, 'accepted': False, 'formalAccepted': False}}
    write(job_path, job)
    print(json.dumps({'job': str(job_path), 'promptFile': str(prompt_path),
                      'references': refs, 'cornerOwner': selected_owner}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('row', type=int)
    parser.add_argument('col', type=int)
    parser.add_argument('--description', default='')
    parser.add_argument('--corner-owner', choices=['west', 'south', 'core-split'])
    parser.add_argument('--corner-reason')
    parser.add_argument('--analyze-only', action='store_true')
    args = parser.parse_args()
    try:
        prepare(args.row, args.col, args.description, args.corner_owner, args.corner_reason, args.analyze_only)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'error: {error}\n')
