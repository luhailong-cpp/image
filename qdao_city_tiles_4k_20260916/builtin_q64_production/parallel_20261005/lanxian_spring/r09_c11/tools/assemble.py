"""Assemble immutable native pixels and expose every join for subsequent review.

This is deliberately a transparent hard-cut baseline. It applies zero geometric
shift, zero RGB correction and zero blending. Later bounded seam repairs require
their own masks, limits and provenance instead of silently altering this result.
"""
from __future__ import annotations

import argparse
import json
import re
import numpy as np
from PIL import Image

from common import (TILE, NATIVE, CORE, HALO, OVERLAP, EXTENDED, WEST,
                    WEST_SHA, now, sha, write, info, load_native, load_west)


def ownership(index):
    start = 0 if index == 0 else HALO
    end = NATIVE if index == 3 else HALO + CORE
    return start, end, index * CORE + start


def difference(a, b):
    delta = np.asarray(a).astype(np.int16) - np.asarray(b).astype(np.int16)
    return {'pixelsCompared': int(delta.shape[0] * delta.shape[1]),
            'equalPixels': int(np.all(delta == 0, axis=2).sum()),
            'meanAbsoluteRGB': [float(value) for value in np.abs(delta).mean(axis=(0, 1))],
            'maxAbsoluteRGB': [int(value) for value in np.abs(delta).max(axis=(0, 1))]}


def save_qa(output, core, west):
    directory = output / 'qa'
    directory.mkdir()
    records = []
    width = 160
    for axis in ('vertical', 'horizontal'):
        for boundary in range(1, 4):
            for segment in range(4):
                position, start = boundary * CORE, segment * CORE
                box = ([position - width, start, position + width, start + CORE]
                       if axis == 'vertical' else
                       [start, position - width, start + CORE, position + width])
                path = directory / f'{axis}_{position}_segment{segment + 1:02d}_1to1.png'
                core.crop(box).save(path)
                records.append({**info(path), 'kind': 'internal_seam', 'axis': axis,
                                'coreBox': box, 'resized': False, 'viewed': False})
    for row in range(1, 4):
        for col in range(1, 4):
            x, y = col * CORE, row * CORE
            box = [x - width, y - width, x + width, y + width]
            path = directory / f'junction_{x}_{y}_1to1.png'
            core.crop(box).save(path)
            records.append({**info(path), 'kind': 'internal_junction', 'coreBox': box,
                            'resized': False, 'viewed': False})
    for segment in range(4):
        y = segment * CORE
        # Last 160 pixels of the neighbor's 4096 core immediately precede our
        # first 160 core pixels in world coordinates. No halo is duplicated.
        west_box = [HALO + 4096 - width, HALO + y, HALO + 4096, HALO + y + CORE]
        east_box = [0, y, width, y + CORE]
        sheet = Image.new('RGB', (width * 2, CORE))
        sheet.paste(west.crop(west_box), (0, 0))
        sheet.paste(core.crop(east_box), (width, 0))
        path = directory / f'west_external_segment{segment + 1:02d}_1to1.png'
        sheet.save(path)
        records.append({**info(path), 'kind': 'external_west_seam', 'resized': False,
                        'westSourceBoxInExtended': west_box, 'ownCoreBox': east_box,
                        'seamXInSheet': width, 'viewed': False})
    for name, box in (
        ('northwest', [0, 0, 320, 320]),
        ('northeast', [3776, 0, 4096, 320]),
        ('southwest', [0, 3776, 320, 4096]),
        ('southeast', [3776, 3776, 4096, 4096]),
    ):
        path = directory / f'outer_corner_{name}_1to1.png'
        core.crop(box).save(path)
        records.append({**info(path), 'kind': 'outer_corner', 'coreBox': box,
                        'resized': False, 'viewed': False})
    return records


def assemble(output_name):
    if not re.fullmatch(r'[a-z][a-z0-9_-]*', output_name):
        raise ValueError('--output-name must be a simple lowercase directory name')
    output = TILE / output_name
    if output.exists():
        raise ValueError(f'Refusing to overwrite an existing candidate: {output}')
    arrays, images, sources = {}, {}, []
    for row in range(4):
        for col in range(4):
            image, source = load_native(row + 1, col + 1)
            images[(row, col)] = image
            arrays[(row, col)] = np.asarray(image)
            sources.append(source)
    west = load_west()
    canvas = Image.new('RGB', (EXTENDED, EXTENDED))
    owners = np.zeros((EXTENDED, EXTENDED), dtype=np.uint8)
    coverage = np.zeros((EXTENDED, EXTENDED), dtype=np.uint8)
    placements = []
    for row in range(4):
        for col in range(4):
            x0, x1, dx = ownership(col)
            y0, y1, dy = ownership(row)
            source_box = [x0, y0, x1, y1]
            canvas.paste(images[(row, col)].crop(source_box), (dx, dy))
            owner = row * 4 + col + 1
            owners[dy:dy + y1 - y0, dx:dx + x1 - x0] = owner
            coverage[dy:dy + y1 - y0, dx:dx + x1 - x0] += 1
            placements.append({'patchId': f'r{row + 1:02d}_c{col + 1:02d}',
                               'sourceCrop': source_box, 'destinationXY': [dx, dy],
                               'ownerLabel': owner, 'resized': False})
    if not np.all(coverage == 1):
        raise ValueError('Hard-cut placement failed exact once-only full coverage')
    # Only the exterior west halo belongs to the previous tile. The current
    # core is entirely from its native sources; do not silently replace the
    # first 115 core pixels with another tile's generated halo.
    west_halo_box = [4096, 0, 4096 + HALO, EXTENDED]
    canvas.paste(west.crop(west_halo_box), (0, 0))
    owners[:, :HALO] = 255
    candidate = np.asarray(canvas)
    if not np.array_equal(candidate[:, :HALO], np.asarray(west)[:, 4096:4096 + HALO]):
        raise ValueError('External west halo is not byte equal')
    # Verify every output pixel against its recorded original native owner.
    for placement in placements:
        index = placement['ownerLabel'] - 1
        row, col = divmod(index, 4)
        x0, y0, x1, y1 = placement['sourceCrop']
        dx, dy = placement['destinationXY']
        owned = owners[dy:dy + y1 - y0, dx:dx + x1 - x0] == index + 1
        actual = candidate[dy:dy + y1 - y0, dx:dx + x1 - x0]
        raw = arrays[(row, col)][y0:y1, x0:x1]
        if not np.array_equal(actual[owned], raw[owned]):
            raise ValueError(f'Pixels differ from declared native owner: {placement["patchId"]}')
    metrics = []
    for row in range(4):
        for col in range(4):
            a = arrays[(row, col)]
            if col < 3:
                metrics.append({'axis': 'vertical', 'source': f'r{row + 1:02d}_c{col + 1:02d}',
                                'neighbor': f'r{row + 1:02d}_c{col + 2:02d}',
                                'raw230pxOverlap': difference(a[:, CORE:], arrays[(row, col + 1)][:, :OVERLAP])})
            if row < 3:
                metrics.append({'axis': 'horizontal', 'source': f'r{row + 1:02d}_c{col + 1:02d}',
                                'neighbor': f'r{row + 2:02d}_c{col + 1:02d}',
                                'raw230pxOverlap': difference(a[CORE:], arrays[(row + 1, col)][:OVERLAP])})
    for source in sources:
        if sha(source['file']) != source['sha256'] or sha(source['generationRecord']['file']) != source['generationRecord']['sha256']:
            raise ValueError('A source or source record changed during assembly')
    if sha(WEST) != WEST_SHA:
        raise ValueError('West source changed during assembly')
    output.mkdir()
    core = canvas.crop((HALO, HALO, HALO + 4096, HALO + 4096))
    extended_path, core_path = output / 'extended4326.png', output / 'core4096.png'
    canvas.save(extended_path)
    core.save(core_path)
    owner_path = output / 'native-owner-mask4326.png'
    Image.fromarray(owners).save(owner_path)
    qa = save_qa(output, core, west)
    manifest = {
        'schemaVersion': 1, 'tile': 'r09_c11', 'appearance': 'shared_day_spring_structure',
        'createdAtUtc': now(), 'status': 'hard_cut_candidate_pending_visual_review',
        'script': info(__file__), 'sources': sources, 'placements': placements,
        'westSource': {'file': str(WEST), 'sha256': WEST_SHA, 'sourceCropForFixedHalo': west_halo_box},
        'geometry': {'nativePatchSize': NATIVE, 'corePerPatch': CORE, 'halo': HALO,
                     'grid': [4, 4], 'coreOutput': [4096, 4096], 'extendedOutput': [EXTENDED, EXTENDED],
                     'coreBoxInExtended': [HALO, HALO, 4211, 4211]},
        'parameters': {'method': 'core ownership hard-cut plus exact exterior west halo',
                       'integerTranslationMax': 0, 'actualTranslation': 0,
                       'colorCorrectionMaxPerChannel': 0, 'blendWidth': 0,
                       'resizeOperations': 0, 'blurOperations': 0},
        'verification': {'sourcesUnchanged': True, 'everyPixelEqualsItsRecordedSource': True,
                         'fixedWestHaloByteEqual': True, 'fullCoverage': True,
                         'rawNativeOverlapMetrics': metrics,
                         'west230OverlapMetric': difference(candidate[:, :OVERLAP], np.asarray(west)[:, 4096:4326])},
        'outputs': {'core': info(core_path), 'extended': info(extended_path),
                    'ownerMask': {**info(owner_path), 'labels': '1..16 row-major natives; 255 west selected-v2 source'}},
        'qa': qa, 'qaStatus': 'pending', 'qaAccepted': False, 'formalAccepted': False,
        'clientAccepted': False, 'completeTileCount': 0, 'qualifiedComplete4KCandidate': False,
        'unresolved': ['Review all 24 internal seam segments, 9 internal junctions, 4 west segments and outer corners.',
                       'Pixel coverage and numerical metrics do not establish visual seam quality.',
                       'North/east/south exterior neighbors are absent; those joins remain pending.',
                       'Validate shared geometry/navigation against the regional contract before selection.'],
    }
    write(output / 'assembly.json', manifest)
    print(json.dumps({'manifest': str(output / 'assembly.json'), 'core': str(core_path),
                      'qaImages': len(qa), 'accepted': False}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-name', default='assembly_hardcut')
    args = parser.parse_args()
    try:
        assemble(args.output_name)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'error: {error}\n')
