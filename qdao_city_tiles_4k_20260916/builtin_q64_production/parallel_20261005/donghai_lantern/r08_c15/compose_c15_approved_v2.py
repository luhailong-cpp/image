"""Compose the pinned approved c15 repair chain; --check never writes pixels.

Nineteen festival natives, five joins and fifteen ordered insertions use OWN
frozen DAY alpha snapshots. DAY RGB fields are evidence only. --build writes an
immutable approved-sync candidate, including the real right halo, raw exact-mask
baseline, bounded festival difference fields and original-pixel QA crops.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import replay_c15_consolidated as r

T = Path(__file__).resolve().parent
OWN = T.parent
B = T / 'repairs/consolidated-sync'
D = T / 'repairs/approved-sync'
CONTRACT = T / 'source-contract-v2/source-contract.json'
CONTRACT_SHA = 'c6d301c1602ce7e237ddaf46ed45984e5273ee5e6b7f61eb4504181e5a39a2af'
BASE_MANIFEST = T / 'tone-assembly/output/tone-assembly-manifest.json'
BASE_SHA = '4d1b561d1ab579903d17d9697d0b1566d5bc77f6e2915a4f7cee7bcb3ca9d060'
EXTENDED_SHA = '3ceb57fa7bdf8adb3aa7ac3c4413f82bb6b2f24abfd077b9e5a142705c1e56b0'
LIMIT = 24
IDS = [
    'wood-horizontal-s1', 'wood-horizontal-s2', 'wood-horizontal-s3', 'wood-horizontal-s4',
    'wood-right-w1', 'wood-right-w2', 'a-left-cross', 'b-right-cross', 'c-left-bottom',
    'd-right-bottom', 'e-hull-waterline', 'f-lantern-blueboard', 'right-upper',
    'right-lower', 'g-left-insertion', 'roof', 'left-insertion',
    'water-left-horizontal', 'right-halo-finish',
]
OP_IDS = [
    'wood-horizontal', 'wood-right', 'water-a-left-cross', 'water-b-right-cross',
    'water-c-left-bottom', 'water-d-right-bottom', 'e-hull-waterline',
    'f-lantern-blueboard', 'right-insertion-finish', 'water-seams-g-left-insertion',
    'root-finishing-roof', 'root-finishing-left-insertion', 'water-left-horizontal',
    'roof-full-end', 'east-hull-through-halo',
]
JOIN_IDS = ['wood-horizontal-1-2', 'wood-horizontal-2-3', 'wood-horizontal-3-4',
            'wood-right-1-2', 'right-insertion-finish-1-2']
sha, read, ref, need, cut, blend = r.sha, r.read, r.ref, r.need, r.cut, r.blend


def now():
    return datetime.now(timezone.utc).isoformat()


def verify(entry):
    path = Path(entry['file'])
    need(path.is_file() and sha(path) == entry['sha256'], 'Hash mismatch: ' + str(path))


def write_json(path, value):
    path = Path(path).resolve()
    need(path.is_relative_to(T.resolve()), 'JSON write outside own c15')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def save_image(path, pixels, metadata):
    path = Path(path).resolve()
    need(path.is_relative_to(D.resolve()), 'Image write outside approved-sync')
    need(not path.exists(), 'Immutable image already exists: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    image = pixels if isinstance(pixels, Image.Image) else Image.fromarray(pixels)
    image.save(path)
    with Image.open(path) as saved:
        need(np.array_equal(np.asarray(saved), np.asarray(image)), 'Saved PNG pixels differ')
    info = {**ref(path), 'pixels': list(image.size)}
    sidecar = Path(str(path) + '.generation.json')
    write_json(sidecar, {
        **info, 'createdAtUtc': now(), 'generatedByAI': False,
        'actualModel': None, 'actualQuality': None, 'artResampled': False,
        'formalAccepted': False, **metadata,
    })
    return {**info, 'generationRecord': ref(sidecar)}


def raw_evidence(path, record):
    raw = Path(record['evidence']['toolResultSourcePath'])
    need(record['evidence']['toolResultSha256'] == record['sha256'], 'Tool digest mismatch')
    if raw.is_file():
        need(sha(raw) == record['sha256'], 'Tool result changed')
        return {**ref(raw), 'cacheAvailable': True}
    audit_path = OWN / 'audit/duplicate-cache-cleanup.json'
    need(audit_path.is_file(), 'Missing raw result has no cleanup evidence')
    entries = [e for e in read(audit_path)['entries']
               if Path(e['nativeFile']).resolve() == path.resolve()
               and Path(e['originalToolResultSourcePath']).resolve() == raw.resolve()]
    need(len(entries) == 1, 'Missing unique raw cleanup proof')
    entry = entries[0]
    need(entry['status'] == 'deleted' and entry['verifiedCacheSha256'] ==
         entry['retainedNativeSha256AfterDeletion'] == record['sha256'], 'Invalid cleanup proof')
    return {'file': str(raw), 'sha256': record['sha256'], 'cacheAvailable': False,
            'cleanupEvidence': ref(audit_path), 'retainedNative': ref(path)}


def validate():
    need(sha(CONTRACT) == CONTRACT_SHA, 'Pinned approved-chain contract changed')
    contract = read(CONTRACT)
    need(contract['revision'] == 2 and contract['nativeSourceCount'] == 19
         and contract['nativeReferenceCount'] == 20, 'Wrong approved source catalog')
    need([e['id'] for e in contract['nativeSources']] == IDS, 'Native source order changed')
    need([e['id'] for e in contract['joinOperations']] == JOIN_IDS, 'Join order changed')
    need([e['id'] for e in contract['insertionOperations']] == OP_IDS, 'Insertion order changed')
    proof = contract['dayReplay']
    for key in ('historicalBasePNGByteIdentical', 'historicalExtendedPNGByteIdentical',
                'approvedCorePixelIdentical', 'approvedExtendedPixelIdentical',
                'currentOutputPixelIdentical', 'currentExtendedPixelIdentical', 'approvedUnionPixelIdentical'):
        need(proof[key] is True, 'Missing pinned DAY replay proof: ' + key)
    snapshots = {}
    for entry in contract['maskAndColorFieldSnapshots']:
        authority, snapshot = entry['authority'], entry['snapshot']
        need(authority['sha256'] == snapshot['sha256'], 'Snapshot changed authority bytes')
        need(Path(snapshot['file']).resolve().is_relative_to((T / 'source-contract-v2').resolve()),
             'Frozen mask/field is outside own snapshot directory')
        verify(snapshot)
        snapshots[(authority['file'], authority['sha256'])] = snapshot
    for entry in contract['joinOperations']:
        for key in ('maskPng', 'maskNpz', 'localColorMatch'):
            need((entry[key]['file'], entry[key]['sha256']) in snapshots,
                 'Join evidence lacks frozen snapshot: ' + entry['id'])
    for entry in contract['insertionOperations']:
        for key in ('alpha', 'colorField'):
            need((entry[key]['file'], entry[key]['sha256']) in snapshots,
                 'Insertion evidence lacks frozen snapshot: ' + entry['id'])
    for key in ('dayGeometrySnapshot', 'dayExtendedSnapshot'):
        verify(contract[key]['snapshot'])
        need(contract[key]['authority']['sha256'] == contract[key]['snapshot']['sha256'],
             'Frozen DAY candidate identity differs')

    bm = read(BASE_MANIFEST)
    bi, exi = bm['candidate'], bm['extendedContext']
    need(bi['sha256'] == BASE_SHA and exi['sha256'] == EXTENDED_SHA, 'Unexpected festival baseline')
    for entry in (bi, exi):
        verify(entry)
        verify({'file': entry['sidecar'], 'sha256': entry['sidecarSha256']})
        need(read(entry['sidecar'])['sha256'] == entry['sha256'], 'Baseline sidecar differs')
    base, extended = r.rgb(bi['file']), r.rgb(exi['file'])
    need(base.shape == (4096, 4096, 3) and extended.shape == (4326, 4326, 3), 'Incomplete real baseline')
    need(np.array_equal(extended[115:4211, 115:4211], base), 'Real extended/core baseline mismatch')
    arrays, sources, missing = {}, [], []
    for entry in contract['nativeSources']:
        name = entry['id']
        for key in ('geometrySnapshot', 'generationRecordSnapshot'):
            frozen = entry[key]
            verify(frozen['snapshot'])
            need(frozen['authority']['sha256'] == frozen['snapshot']['sha256'], 'Native frozen evidence differs')
        with Image.open(entry['geometrySnapshot']['snapshot']['file']) as image:
            need(image.size == (1254, 1254), 'Wrong DAY native dimensions')
        path = B / 'native' / (name + '.png')
        if not path.is_file():
            missing.append(name)
            continue
        rp = Path(str(path) + '.generation.json')
        record = read(rp)
        need(sha(path) == record['sha256'] and Path(record['file']).resolve() == path.resolve(),
             'Festival native identity mismatch: ' + name)
        need(record['route'] == 'builtin' and record['tool'] == 'image_gen.imagegen', 'Wrong generation route')
        need(record['actualModel'] is None and record['actualQuality'] is None and
             record['submittedParameters']['model'] is None and
             record['submittedParameters']['quality'] is None, 'Unsupported explicit selector claim')
        need(record['resizedAfterGeneration'] is False and record['finalArtUpscaled'] is False, 'Resampled native')
        need(record['dayNativeRepair']['sha256'] == entry['daySource']['sha256'] and
             Path(record['dayNativeRepair']['file']).resolve() == Path(entry['daySource']['file']).resolve(),
             'Festival conversion DAY authority mismatch: ' + name)
        need(record['sourceRectXYXY'] == entry['sourceRectTileAndHaloXYXY'], 'Native world rectangle mismatch')
        verify({'file': record['prompt'], 'sha256': record['promptSha256']})
        verify({'file': record['requestFile'], 'sha256': record['requestSha256']})
        submitted = read(record['requestFile'])
        need(submitted['prompt'] == record['submittedParameters']['prompt'], 'Submitted prompt mismatch')
        refs = record['references']
        need(len(refs) == len(record['submittedParameters']['referenced_image_paths']) >= 3,
             'Incomplete actual image references')
        for rr, submitted_path in zip(refs, record['submittedParameters']['referenced_image_paths']):
            verify(rr)
            need(Path(rr['file']).resolve() == Path(submitted_path).resolve(), 'Reference order changed')
        need(refs[0]['sha256'] == entry['daySource']['sha256'], 'Primary geometry reference differs')
        with Image.open(path) as image:
            image.load()
            need(image.size == (1254, 1254) and image.mode in ('RGB', 'RGBA'), 'Wrong festival native pixels')
            if image.mode == 'RGBA':
                need(image.getchannel('A').getextrema() == (255, 255), 'Transparent repair is unsupported')
        arrays[name] = r.rgb(path)
        sources.append({'id': name, 'native': ref(path), 'record': ref(rp),
                        'daySource': entry['daySource'], 'sourceRectTileAndHaloXYXY': entry['sourceRectTileAndHaloXYXY'],
                        'toolResult': raw_evidence(path, record)})
    return contract, snapshots, bm, extended, arrays, sources, missing


def alpha_from(entry, snapshots):
    frozen = snapshots[(entry['file'], entry['sha256'])]
    with Image.open(frozen['file']) as image:
        need(image.mode == 'L', 'Frozen alpha is not an unmodified L image')
        alpha = np.asarray(image).copy()
    return alpha, frozen


def save_field(name, field, weight, alpha, metadata, fields):
    need(float(np.abs(field).max()) <= LIMIT + 1e-5, 'Intermediate RGB field exceeds bound')
    path = D / 'fields' / (name + '.npz')
    path.parent.mkdir(parents=True, exist_ok=True)
    need(not path.exists(), 'Existing immutable field')
    np.savez_compressed(path, delta_rgb=field.astype(np.float32),
                        weight=weight.astype(np.float32), exact_day_alpha=alpha)
    fields.append({'id': name, **ref(path), **metadata, 'maximumAbsoluteDelta': float(np.abs(field).max()),
                   'maximumPermittedDelta': LIMIT, 'fieldPrecision': 'float32',
                   'artBlurred': False, 'sourceResampled': False, 'DAYRgbFieldApplied': False})


def source_groups(contract, snapshots, arrays, matching=False, fields=None):
    seams = {e['id']: e for e in contract['joinOperations']}

    def join(ids, starts, axis, label, origin):
        current = arrays[ids[0]].copy()
        for index, name in enumerate(ids[1:], 1):
            nxt, start = arrays[name], starts[index]
            overlap = current.shape[axis] - start
            entry = seams[f'{label}-{index}-{index + 1}']
            alpha, frozen = alpha_from(entry['maskPng'], snapshots)
            old = current[:, -overlap:] if axis == 1 else current[-overlap:]
            later = nxt[:, :overlap] if axis == 1 else nxt[:overlap]
            expected = ([origin[0] + start, origin[1], origin[0] + start + overlap, origin[1] + current.shape[0]]
                        if axis == 1 else
                        [origin[0], origin[1] + start, origin[0] + current.shape[1], origin[1] + start + overlap])
            need(expected == entry['pairOverlapRectXYXY'] and overlap == entry['overlapPixels'], 'Join geometry mismatch')
            need(old.shape == later.shape and alpha.shape == old.shape[:2], 'Join alpha shape mismatch')
            if matching:
                later, field, weight = r.match(old, later, alpha, max_delta=LIMIT)
                save_field('join-' + entry['id'], field, weight, alpha,
                           {'coordinateSpace': 'core', 'rectXYXY': expected, 'exactAlphaSnapshot': frozen}, fields)
            mix = blend(old, later, alpha)
            current = (np.concatenate((current[:, :-overlap], mix, nxt[:, overlap:]), axis=1) if axis == 1 else
                       np.concatenate((current[:-overlap], mix, nxt[overlap:]), axis=0))
        return current

    groups = {
        'wood-horizontal': join(IDS[:4], [0, 1024, 2048, 2842], 1, 'wood-horizontal', [0, 397])[:, 128:3968],
        'wood-right': join(['wood-right-w1', 'wood-right-w2'], [0, 1024], 0, 'wood-right', [2445, 1651]),
        'right-insertion-finish': join(['right-upper', 'right-lower'], [0, 794], 0,
                                      'right-insertion-finish', [2842, 2048]),
    }
    for entry in contract['insertionOperations']:
        if entry['id'] not in groups:
            need(len(entry['sourceIds']) == 1, 'Unknown multi-native source mapping')
            groups[entry['id']] = arrays[entry['sourceIds'][0]]
    return groups


def compose(contract, snapshots, base_extended, groups, matching=False, fields=None):
    result = base_extended.copy()
    union = np.zeros((4326, 4326), np.uint8)
    operations = []
    for entry in contract['insertionOperations']:
        core = entry['coordinateSpace'] == 'core'
        rect = [v + 115 for v in entry['rectXYXY']] if core else entry['rectInExtendedXYXY']
        need(0 <= min(rect) and max(rect) <= 4326, 'Insertion escapes true extended coverage')
        piece = groups[entry['id']]
        if not core:
            need(entry['id'] == 'east-hull-through-halo', 'Unknown extended insertion')
            piece = cut(piece, entry['sourceCropXYXY'])
        alpha, frozen = alpha_from(entry['alpha'], snapshots)
        old = cut(result, rect).copy()
        need(old.shape == piece.shape and old.shape[:2] == alpha.shape, 'Insertion alpha/source shape mismatch')
        adjusted = piece
        if matching:
            adjusted, field, weight = r.match(old, piece, alpha, max_delta=LIMIT)
            save_field('insert-' + entry['id'], field, weight, alpha,
                       {'coordinateSpace': 'extended', 'rectXYXY': rect, 'exactAlphaSnapshot': frozen}, fields)
        result[rect[1]:rect[3], rect[0]:rect[2]] = blend(old, adjusted, alpha)
        need(np.array_equal(cut(result, rect)[alpha == 0], old[alpha == 0]), 'Insertion escaped exact alpha')
        np.maximum(cut(union, rect), alpha, out=cut(union, rect))
        operations.append({'id': entry['id'], 'sourceIds': entry['sourceIds'],
                           'rectInExtendedXYXY': rect, 'sourceCropXYXY': entry.get('sourceCropXYXY'),
                           'exactAlphaSnapshot': frozen, 'outsideAlphaZeroExactlyPreserved': True})
    need(np.array_equal(result[union == 0], base_extended[union == 0]), 'Chain escaped exact alpha union')
    return result, union, operations


def make_qa(extended, candidate, extended_info, contract):
    image = Image.fromarray(extended)
    items = []

    def crop(name, tile_rect, category):
        requested = [v + 115 for v in tile_rect]
        rect = [max(0, requested[0]), max(0, requested[1]), min(4326, requested[2]), min(4326, requested[3])]
        need(rect[0] < rect[2] and rect[1] < rect[3], 'Empty native QA rectangle')
        metadata = {'derivedFrom': [candidate, extended_info], 'operation': 'exact original-pixel crop',
                    'category': category, 'requestedTileAndHaloRectXYXY': tile_rect,
                    'rectInExtendedXYXY': rect, 'actualTileAndHaloRectXYXY': [v - 115 for v in rect],
                    'clippedOnlyAtTrueImageCoverage': rect != requested,
                    'pixelScale': 1, 'resized': False, 'visualReview': 'pending'}
        items.append({**save_image(D / 'qa' / (name + '.png'), image.crop(rect), metadata), **metadata})

    for source in contract['nativeSources']:
        name = source['id']
        rect = source['sourceRectTileAndHaloXYXY']
        crop(name + '-full1254', rect, 'native-source-window')
        if name == 'right-halo-finish':
            op = contract['insertionOperations'][-1]
            rect = [v - 115 for v in op['rectInExtendedXYXY']]
        x, y, x1, y1 = rect
        for side, box in [
            ('left', [x - 224, y, x + 224, y1]), ('right', [x1 - 224, y, x1 + 224, y1]),
            ('top', [x, y - 224, x1, y + 224]), ('bottom', [x, y1 - 224, x1, y1 + 224]),
        ]:
            crop(name + '-return-' + side, box, 'four-native-window-returns')
    for axis in ('x', 'y'):
        for center in (1024, 2048, 3072):
            for part in range(4):
                rect = ([center - 448, part * 1024, center + 448, (part + 1) * 1024] if axis == 'x' else
                        [part * 1024, center - 448, (part + 1) * 1024, center + 448])
                crop(f'{axis}{center}-return-part{part + 1:02}', rect, 'full-internal-seam-return')
    for name, rect in [('nw', [0, 0, 512, 512]), ('ne', [3584, 0, 4096, 512]),
                       ('sw', [0, 3584, 512, 4096]), ('se', [3584, 3584, 4096, 4096])]:
        crop('corner-' + name, rect, 'tile-corner')
    for y in (1024, 2048, 3072):
        for x in (1024, 2048, 3072):
            crop(f'junction-x{x}-y{y}', [x - 256, y - 256, x + 256, y + 256], 'internal-junction')
    need(len(items) == 132, 'QA coverage count changed')
    return items


def run(build=False):
    contract, snapshots, bm, base, arrays, sources, missing = validate()
    report = {'checkedAtUtc': now(), 'sourceContract': ref(CONTRACT), 'script': ref(__file__),
              'colorMatchHelper': ref(r.__file__), 'verifiedFestivalNativeCount': len(arrays),
              'requiredFestivalNativeCount': 19, 'missingNativeIds': missing,
              'ready': not missing, 'pixelOutputWritten': False, 'DAYWritten': False,
              'baseManifest': ref(BASE_MANIFEST), 'baseline': bm['candidate'],
              'extendedBaseline': bm['extendedContext'], 'frozenMaskAndFieldCount': len(snapshots),
              'DAYRgbFieldsApplied': False, 'plannedJoinCount': 5, 'plannedInsertionCount': 15,
              'plannedOriginalPixelQaCount': 132, 'maximumPerStepAndCumulativeChannelDelta': LIMIT,
              'formalAccepted': False}
    write_json(T / 'qa/approved-sync-v2-preflight.json', report)
    if not build:
        return report
    need(not missing, 'Missing actual festival natives: ' + ', '.join(missing))
    need(not D.exists(), 'Immutable approved-sync output already exists; inspect before rebuilding')
    raw_groups = source_groups(contract, snapshots, arrays)
    raw, raw_union, raw_ops = compose(contract, snapshots, base, raw_groups)
    fields = []
    matched_groups = source_groups(contract, snapshots, arrays, matching=True, fields=fields)
    matched, union, operations = compose(contract, snapshots, base, matched_groups, matching=True, fields=fields)
    need(np.array_equal(union, raw_union), 'Color matching changed exact alpha union')
    difference = matched.astype(np.int16) - raw.astype(np.int16)
    need(not np.any(difference[union == 0]), 'Color matching escaped union before cumulative clipping')
    delta = np.clip(difference, -LIMIT, LIMIT).astype(np.int8)
    result16 = raw.astype(np.int16) + delta.astype(np.int16)
    need(result16.min() >= 0 and result16.max() <= 255, 'Final RGB result escaped byte range')
    result = result16.astype(np.uint8)
    need(np.array_equal(result[union == 0], base[union == 0]), 'Final output escaped authorized union')
    need(np.array_equal(result[:, :243], base[:, :243]), 'West halo or west128 protected core changed')
    need(np.array_equal(result[:115], base[:115]) and np.array_equal(result[4211:], base[4211:]),
         'Top/bottom true halo changed')
    dp = D / 'fields/final-applied-delta-extended.npz'
    np.savez_compressed(dp, delta_rgb=delta, exact_day_alpha_union=union)
    with np.load(dp, allow_pickle=False) as archive:
        need(np.array_equal(raw.astype(np.int16) + archive['delta_rgb'], result.astype(np.int16)),
             'Saved cumulative field does not exactly replay final pixels')
    need(len(fields) == 20, 'Expected five fresh join fields and fifteen fresh insertion fields')
    core = result[115:4211, 115:4211]
    raw_core = raw[115:4211, 115:4211]
    common = {'operation': 'Pinned approved DAY alpha geometry with newly computed bounded festival RGB difference fields',
              'sourceContract': ref(CONTRACT), 'priorFestivalManifest': ref(BASE_MANIFEST),
              'repairSources': sources, 'exactMaskOperations': operations, 'rawMaskOperations': raw_ops,
              'perStepFields': fields, 'finalAppliedDelta': ref(dp), 'DAYRgbFieldsApplied': False,
              'maximumPerStepChannelDelta': LIMIT, 'maximumCumulativeChannelDelta': int(np.abs(delta.astype(np.int16)).max()),
              'cumulativeLimitReference': 'same full 4326 extended exact-mask raw chain, including halo',
              'outsideAlphaUnionChangedPixels': 0, 'westHaloAndWest128CoreExactlyPreserved': True,
              'topAndBottom115HaloExactlyPreserved': True, 'sourceResampled': False, 'geometryFlow': False,
              'imageBlur': False, 'maskBlur': False, 'completePixelCandidate': True,
              'formalAccepted': False, 'clientAcceptance': False, 'wholeCityComplete': False,
              'globalRegistryModified': False, 'visualReview': 'pending complete original-pixel QA'}
    raw_meta = {**common, 'operation': 'Pure exact-mask approved chain with no RGB field application',
                'perStepFields': [], 'finalAppliedDelta': None, 'maximumCumulativeChannelDelta': 0}
    raw_info = save_image(D / 'output/r08_c15-exact-mask-raw.png', raw_core, raw_meta)
    raw_extended = save_image(D / 'output/extended-context-exact-mask-raw.png', raw, raw_meta)
    candidate = save_image(D / 'output/r08_c15.png', core, {**common, 'rawBaseline': raw_info})
    extended = save_image(D / 'output/extended-context.png', result, {**common, 'rawBaseline': raw_extended})
    union_info = save_image(D / 'masks/union-extended.png', union,
                            {'operation': 'maximum of the exact fifteen applied alpha snapshots',
                             'sourceContract': ref(CONTRACT), 'notArtwork': True})
    qa = make_qa(result, candidate, extended, contract)
    preview = save_image(D / 'output/preview-1024.png', Image.fromarray(core).resize((1024, 1024), Image.Resampling.LANCZOS),
                         {'derivedFrom': [candidate], 'operation': 'downscaled overview only',
                          'artResampled': True, 'resized': True, 'notNativePixelQA': True, 'finalArt': False})
    for source in sources:
        verify(source['native'])
        verify(source['record'])
    verify({'file': str(CONTRACT), 'sha256': CONTRACT_SHA})
    manifest = {**common, 'createdAtUtc': now(), 'candidate': candidate, 'extendedContext': extended,
                'rawBaseline': raw_info, 'rawExtendedBaseline': raw_extended, 'union': union_info,
                'preview': preview, 'qa': qa, 'script': ref(__file__), 'colorMatchHelper': ref(r.__file__),
                'pixelProof': {'allSavedPngPixelsVerified': True, 'exactSavedFieldReplaysFinalExtended': True,
                               'finalCoreEqualsExtendedCrop': True, 'rawCoreEqualsRawExtendedCrop': True,
                               'outsideUnionExactlyEqualsToneBase': True,
                               'maximumFinalDeltaFromRaw': int(np.abs(delta.astype(np.int16)).max()),
                               'unclippedMaximumStepAccumulation': int(np.abs(difference).max()),
                               'channelsLimitedByCumulativeBound': int(np.count_nonzero(np.abs(difference) > LIMIT))},
                'qaCoverage': {'native1254Windows': 19, 'nativeReturns': 76, 'seamReturnParts': 24,
                               'corners': 4, 'junctions': 9, 'pixelScale': 1,
                               'rightHaloIncluded': True, 'external4096NeighborsSupplied': False}}
    manifest_path = D / 'output/integration-manifest.json'
    write_json(manifest_path, manifest)
    return {'candidate': candidate, 'extendedContext': extended, 'manifest': ref(manifest_path),
            'qaCount': len(qa), 'fieldCount': len(fields), 'outsideUnionChangedPixels': 0,
            'maximumCumulativeChannelDelta': int(np.abs(delta.astype(np.int16)).max()),
            'formalAccepted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='Validate available sources; no pixel output')
    group.add_argument('--build', action='store_true', help='Write immutable approved-sync candidate')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.build), ensure_ascii=False, indent=2))
    except (ValueError, FileNotFoundError, KeyError) as error:
        raise SystemExit('Approved v2 composition refused: ' + str(error))
