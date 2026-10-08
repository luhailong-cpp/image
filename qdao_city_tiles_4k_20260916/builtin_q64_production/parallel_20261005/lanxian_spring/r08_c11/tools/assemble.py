"""Native hard-cut baseline with selected west and south exterior halo pixels.

No resize, warp, tone adjustment, feathering, or automatic acceptance. The
southwest halo intersection requires an explicit source decision if unequal.
"""
from __future__ import annotations
import argparse
import json
import re
import numpy as np
from PIL import Image
from common import (TILE, NATIVE, CORE, HALO, OVERLAP, EXTENDED, now, info,
                    write, load_native, load_neighbors, unchanged, differences,
                    analyze_corner, require_corner_decision)


def ownership(index):
    if not 0 <= index <= 3:
        raise ValueError('Ownership index must be 0..3')
    start = 0 if index == 0 else HALO
    end = NATIVE if index == 3 else HALO + CORE
    return start, end, index * CORE + start


def external_halo_fragments(neighbors):
    return (neighbors['west'].crop((4096, 0, 4211, EXTENDED)),
            neighbors['south'].crop((0, HALO, EXTENDED, OVERLAP)))


def place_external_halos(canvas, owners, west_halo, south_halo, owner):
    """Only replace exterior halos. The 4096 core remains native-owned."""
    if owner not in ('west', 'south'):
        raise ValueError('Resolved southwest halo owner must be west or south')
    bottom = HALO + 4096
    if owner == 'west':
        canvas.paste(south_halo, (0, bottom))
        owners[bottom:] = 254
        canvas.paste(west_halo, (0, 0))
        owners[:, :HALO] = 255
    else:
        canvas.paste(west_halo, (0, 0))
        owners[:, :HALO] = 255
        canvas.paste(south_halo, (0, bottom))
        owners[bottom:] = 254


def save_qa(output, core, neighbors):
    directory = output / 'qa'
    directory.mkdir()
    records, width = [], 160
    for axis in ('vertical', 'horizontal'):
        for boundary in range(1, 4):
            for segment in range(4):
                position, start = boundary * CORE, segment * CORE
                box = ([position-width, start, position+width, start+CORE]
                       if axis == 'vertical' else
                       [start, position-width, start+CORE, position+width])
                path = directory / f'{axis}_{position}_segment{segment+1:02d}_1to1.png'
                core.crop(box).save(path)
                records.append({**info(path), 'kind': 'internal_seam', 'axis': axis,
                                'coreBox': box, 'resized': False, 'viewed': False})
    for row in range(1, 4):
        for col in range(1, 4):
            x, y = col*CORE, row*CORE
            box = [x-width, y-width, x+width, y+width]
            path = directory / f'junction_{x}_{y}_1to1.png'
            core.crop(box).save(path)
            records.append({**info(path), 'kind': 'internal_junction', 'coreBox': box,
                            'resized': False, 'viewed': False})
    for segment in range(4):
        start = segment * CORE
        west_box = [4211-width, HALO+start, 4211, HALO+start+CORE]
        own_box = [0, start, width, start+CORE]
        sheet = Image.new('RGB', (width*2, CORE))
        sheet.paste(neighbors['west'].crop(west_box), (0, 0))
        sheet.paste(core.crop(own_box), (width, 0))
        path = directory / f'west_external_segment{segment+1:02d}_1to1.png'
        sheet.save(path)
        records.append({**info(path), 'kind': 'external_west_seam', 'resized': False,
                        'sourceBoxInExtended': west_box, 'ownCoreBox': own_box,
                        'seamXInSheet': width, 'viewed': False})
        south_box = [HALO+start, HALO, HALO+start+CORE, HALO+width]
        own_box = [start, 4096-width, start+CORE, 4096]
        sheet = Image.new('RGB', (CORE, width*2))
        sheet.paste(core.crop(own_box), (0, 0))
        sheet.paste(neighbors['south'].crop(south_box), (0, width))
        path = directory / f'south_external_segment{segment+1:02d}_1to1.png'
        sheet.save(path)
        records.append({**info(path), 'kind': 'external_south_seam', 'resized': False,
                        'sourceBoxInExtended': south_box, 'ownCoreBox': own_box,
                        'seamYInSheet': width, 'viewed': False})
    for name, box in (
        ('northwest', [0, 0, 320, 320]), ('northeast', [3776, 0, 4096, 320]),
        ('southwest', [0, 3776, 320, 4096]), ('southeast', [3776, 3776, 4096, 4096]),
    ):
        path = directory / f'outer_corner_{name}_1to1.png'
        core.crop(box).save(path)
        records.append({**info(path), 'kind': 'outer_corner', 'coreBox': box,
                        'resized': False, 'viewed': False})
    return records


def assemble(output_name, corner_owner=None, corner_reason=None, analyze_only=False):
    if not re.fullmatch(r'[a-z][a-z0-9_-]*', output_name):
        raise ValueError('--output-name must be a simple lowercase directory name')
    output = TILE / output_name
    if output.exists():
        raise ValueError(f'Refusing to overwrite an existing candidate: {output}')
    # This must fail before writing anything if the southern selected candidate
    # is absent, unqualified, or no longer matches its immutable batch pin.
    neighbors, boundary_sources = load_neighbors()
    west_halo, south_halo = external_halo_fragments(neighbors)
    corner = analyze_corner(
        TILE / 'jobs/assembly', 'southwest-exterior-halo',
        west_halo.crop((0, 4211, HALO, EXTENDED)),
        south_halo.crop((0, 0, HALO, HALO)),
        {'west': {'source': boundary_sources['west'], 'sourceCrop': [4096, 4211, 4211, 4326]},
         'south': {'source': boundary_sources['south'], 'sourceCrop': [0, 115, 115, 230]}},
        corner_owner, corner_reason)
    if analyze_only:
        print(json.dumps({'analysisOnly': True, 'corner': corner, 'candidateCreated': False}, ensure_ascii=False))
        return
    if not corner['explicitDecisionProvided']:
        raise ValueError('Exterior southwest 115 by 115 halo requires its own explicit '
                         '--corner-owner west|south and --corner-reason after viewing its contact; '
                         'a native core-split guide choice does not select this halo owner')
    owner = require_corner_decision(corner)
    arrays, images, sources = {}, {}, []
    for row in range(4):
        for col in range(4):
            image, source = load_native(row+1, col+1)
            images[(row, col)], arrays[(row, col)] = image, np.asarray(image)
            sources.append(source)
    canvas = Image.new('RGB', (EXTENDED, EXTENDED))
    owners = np.zeros((EXTENDED, EXTENDED), np.uint8)
    coverage = np.zeros((EXTENDED, EXTENDED), np.uint8)
    placements = []
    for row in range(4):
        for col in range(4):
            x0, x1, dx = ownership(col)
            y0, y1, dy = ownership(row)
            box, label = [x0, y0, x1, y1], row*4+col+1
            canvas.paste(images[(row, col)].crop(box), (dx, dy))
            owners[dy:dy+y1-y0, dx:dx+x1-x0] = label
            coverage[dy:dy+y1-y0, dx:dx+x1-x0] += 1
            placements.append({'patchId': f'r{row+1:02d}_c{col+1:02d}', 'sourceCrop': box,
                               'destinationXY': [dx, dy], 'ownerLabel': label, 'resized': False})
    if not np.all(coverage == 1):
        raise ValueError('Hard-cut placement did not cover every pixel exactly once')
    place_external_halos(canvas, owners, west_halo, south_halo, owner)
    candidate = np.asarray(canvas)
    west_expected, south_expected = np.asarray(west_halo), np.asarray(south_halo)
    west_mask, south_mask = owners[:, :HALO] == 255, owners[4211:] == 254
    if not np.array_equal(candidate[:, :HALO][west_mask], west_expected[west_mask]):
        raise ValueError('West-owned exterior halo differs from selected west source')
    if not np.array_equal(candidate[4211:][south_mask], south_expected[south_mask]):
        raise ValueError('South-owned exterior halo differs from selected south source')
    if not np.all((owners[HALO:4211, HALO:4211] >= 1) & (owners[HALO:4211, HALO:4211] <= 16)):
        raise ValueError('External neighbor pixels entered this tile core')
    for placement in placements:
        label = placement['ownerLabel']
        row, col = divmod(label-1, 4)
        x0, y0, x1, y1 = placement['sourceCrop']
        dx, dy = placement['destinationXY']
        owned = owners[dy:dy+y1-y0, dx:dx+x1-x0] == label
        actual = candidate[dy:dy+y1-y0, dx:dx+x1-x0]
        raw = arrays[(row, col)][y0:y1, x0:x1]
        if not np.array_equal(actual[owned], raw[owned]):
            raise ValueError(f'Pixels differ from native owner: {placement["patchId"]}')
    overlap_metrics = []
    for row in range(4):
        for col in range(4):
            raw = arrays[(row, col)]
            if col < 3:
                overlap_metrics.append({'axis': 'vertical', 'row': row+1, 'leftColumn': col+1,
                    'raw230Overlap': differences(raw[:, CORE:], arrays[(row, col+1)][:, :OVERLAP])})
            if row < 3:
                overlap_metrics.append({'axis': 'horizontal', 'topRow': row+1, 'column': col+1,
                    'raw230Overlap': differences(raw[CORE:], arrays[(row+1, col)][:OVERLAP])})
    unchanged(sources)
    unchanged(boundary_sources)
    output.mkdir()
    core = canvas.crop((HALO, HALO, 4211, 4211))
    cp, ep, op = output/'core4096.png', output/'extended4326.png', output/'native-owner-mask4326.png'
    core.save(cp); canvas.save(ep); Image.fromarray(owners).save(op)
    qa = save_qa(output, core, neighbors)
    manifest = {
        'schemaVersion': 1, 'tile': 'r08_c11', 'appearance': 'shared_day_spring_structure',
        'createdAtUtc': now(), 'status': 'hard_cut_candidate_pending_visual_review',
        'script': info(__file__), 'sources': sources, 'placements': placements,
        'boundarySources': boundary_sources, 'southwestExteriorHaloDecision': corner,
        'exteriorHaloDecisionIndependentOfNativeGuideCorner': True,
        'geometry': {'nativePatchSize': NATIVE, 'corePerPatch': CORE, 'halo': HALO, 'grid': [4, 4],
                     'coreOutput': [4096, 4096], 'extendedOutput': [EXTENDED, EXTENDED],
                     'coreBoxInExtended': [HALO, HALO, 4211, 4211]},
        'parameters': {'method': 'core ownership hard-cut plus selected west and south exterior halos',
                       'integerTranslationMax': 0, 'actualTranslation': 0, 'colorCorrectionMaxPerChannel': 0,
                       'blendWidth': 0, 'resizeOperations': 0, 'blurOperations': 0,
                       'westHaloSourceCrop': [4096, 0, 4211, EXTENDED],
                       'southHaloSourceCrop': [0, HALO, EXTENDED, OVERLAP]},
        'verification': {'sourcesUnchanged': True, 'fullCoverage': True,
                         'everyPixelEqualsItsRecordedSource': True, 'coreOnlyNativeOwned': True,
                         'eachExteriorHaloEqualsItsOwnerSource': True,
                         'westExteriorHaloFullByteEqual': bool(np.array_equal(candidate[:, :HALO], west_expected)),
                         'southExteriorHaloFullByteEqual': bool(np.array_equal(candidate[4211:], south_expected)),
                         'rawNativeOverlapMetrics': overlap_metrics,
                         'west230OverlapMetric': differences(candidate[:, :OVERLAP], np.asarray(neighbors['west'])[:, 4096:4326]),
                         'south230OverlapMetric': differences(candidate[4096:], np.asarray(neighbors['south'])[:OVERLAP])},
        'outputs': {'core': info(cp), 'extended': info(ep),
                    'ownerMask': {**info(op), 'labels': '1..16 row-major natives; 254 selected south; 255 selected west'}},
        'qa': qa, 'qaStatus': 'pending', 'qaAccepted': False, 'formalAccepted': False,
        'clientAccepted': False, 'completeTileCount': 0, 'qualifiedComplete4KCandidate': False,
        'unresolved': ['Review all 24 internal seams, 9 junctions, 4 west seams, 4 south seams, and 4 outer corners at 1:1.',
                       'Pixel coverage and numerical metrics do not establish visual seam quality.',
                       'North/east exterior neighbors and shared navigation remain pending.',
                       'Review the southwest diagonal 115 by 115 halo against selected r09_c10; neither immediate neighbor owns that diagonal core.',
                       'The explicit southwest halo source choice does not make disagreeing source pixels equal.']}
    write(output/'assembly.json', manifest)
    for path in (cp, ep):
        write(str(path)+'.generation.json', {'file': str(path), **info(path), 'newGeneration': False,
            'actualModel': None, 'actualQuality': None, 'derivedFrom': sources+list(boundary_sources.values()),
            'assembly': info(output/'assembly.json'), 'operation': 'Unresampled source-pixel hard-cut ownership',
            'formalAccepted': False})
    print(json.dumps({'manifest': str(output/'assembly.json'), 'core': str(cp),
                      'qaImages': len(qa), 'accepted': False}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-name', default='assembly_hardcut')
    parser.add_argument('--corner-owner', choices=['west', 'south'])
    parser.add_argument('--corner-reason')
    parser.add_argument('--analyze-only', action='store_true')
    args = parser.parse_args()
    try:
        assemble(args.output_name, args.corner_owner, args.corner_reason, args.analyze_only)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'error: {error}\n')
