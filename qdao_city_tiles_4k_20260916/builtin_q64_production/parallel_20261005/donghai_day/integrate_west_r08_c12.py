"""Integrate c11/c12 native seam repairs while preserving current c11 west repairs.

Guide provenance is validated against immutable initial c11/c12 outputs. Pixels
are inserted into the latest c11 candidate only after exact east-strip equality.
No generation, scaling, registration, broad feather, or formal acceptance.
"""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image

import assembly as native
import integrate_west as shared

ROOT = Path(__file__).resolve().parent
TILE = ROOT / 'r08_c12'
REPAIR = TILE / 'repairs/west-common-edge'
OUTPUT = ROOT / 'tiles'
QA = REPAIR / 'integration-qa'
INITIAL_WEST = ROOT / 'r08_c11/output/r08_c11.png'
INITIAL_EAST = TILE / 'output/r08_c12.png'
CURRENT_WEST = OUTPUT / 'r08_c11.png'
EXPECTED_INITIAL_WEST = 'c5c5c24746460d9e09c713d7549da8d7fdb168a0aef240611877c9d1e4641354'
EXPECTED_INITIAL_EAST = '1e738fd2a88b2bb629657de9f4c9da31703443adf19ba0ae4ca9775ae0c673ad'
EXPECTED_CURRENT_WEST = '82ea398e1ee8d9343dae6d6a0f51153c98a8f97cd8c97cf1a61d0a1513efe4f4'
PAIR_GLOBAL_ORIGIN = (40960, 28672)
MANIFEST = OUTPUT / 'west-integration-r08_c12-manifest.json'


def configure_shared():
    # Shared methods use these scope roots only; the c10/c11 source files stay intact.
    shared.TILE, shared.REPAIR, shared.OUTPUT = TILE, REPAIR, OUTPUT
    shared.QA, shared.MASKS = QA, REPAIR / 'integration-masks'
    shared.EAST, shared.EXPECTED_EAST_SHA = INITIAL_EAST, EXPECTED_INITIAL_EAST
    shared.PAIR_GLOBAL_ORIGIN = PAIR_GLOBAL_ORIGIN


def ref(path):
    return {'file': str(path), 'sha256': native.sha(path)}


def load_inputs():
    sources, arrays = [], []
    for name, path, digest in [('r08_c11', INITIAL_WEST, EXPECTED_INITIAL_WEST),
                               ('r08_c12', INITIAL_EAST, EXPECTED_INITIAL_EAST)]:
        shared.check_hash(path, digest, 'immutable generation baseline')
        record_path = path.parent / 'assembly-manifest.json'
        record = native.load_json(record_path)
        native.require(record['output']['sha256'] == digest and shared.same_path(record['output']['file'], path),
                       f'Assembly record mismatch: {name}')
        sources.append(dict(ref(path), tile=name, recordFile=str(record_path), recordSha256=native.sha(record_path),
                            role='immutable source for repair guide generation'))
        arrays.append(shared.rgb(path, (4096, 4096)))
    source_pair = np.concatenate(arrays, axis=1)
    shared.check_hash(CURRENT_WEST, EXPECTED_CURRENT_WEST, 'current c11 with completed west repairs')
    current_record_path = Path(str(CURRENT_WEST) + '.generation.json')
    current_record = native.load_json(current_record_path)
    native.require(current_record['sha256'] == EXPECTED_CURRENT_WEST and
                   shared.same_path(current_record['file'], CURRENT_WEST), 'Current tile source record mismatch')
    current_pixels = shared.rgb(CURRENT_WEST, (4096, 4096))
    native.require(np.array_equal(current_pixels[:, 3469:], arrays[0][:, 3469:]),
                   'Current c11 east 627 pixels differ from immutable guide source; refusing stale repair')
    native.require(not (OUTPUT / 'r08_c12.png').exists(), 'Current c12 already exists; refusing blind overwrite/rerun')
    integration_pair = np.concatenate((current_pixels, arrays[1]), axis=1)
    current = dict(ref(CURRENT_WEST), tile='r08_c11', role='actual integration baseline, west repairs preserved',
                   recordFile=str(current_record_path), recordSha256=native.sha(current_record_path))
    equality = {'tile': 'r08_c11', 'rectXYXY': [3469, 0, 4096, 4096],
                'currentAndInitialExactPixelEquality': True,
                'initialRgbBytesSha256': shared.raw_pixel_sha(arrays[0][:, 3469:]),
                'currentRgbBytesSha256': shared.raw_pixel_sha(current_pixels[:, 3469:])}
    return source_pair, sources, integration_pair, current, equality


def write_qa(pair):
    items = shared.write_qa(pair)
    old = QA / 'common-edge-c10-c11-full.png'
    new = QA / 'common-edge-c11-c12-full.png'
    native.writable(new)
    old.replace(new)
    for item in items:
        if shared.same_path(item['file'], old):
            item['file'] = str(new)
    return items


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args(argv)
    configure_shared()
    source_pair, sources, current_pair, current, equality = load_inputs()
    patches, entries, missing = shared.load_patches(source_pair, sources)
    if args.validate_only:
        print(json.dumps({'validatedPatches': len(entries), 'missing': missing, 'complete': not missing,
                          'guideSources': sources, 'currentWest': current, 'eastStripEquality': equality, 'writes': 0}))
        return
    native.require(not missing, 'Missing repairs: ' + ', '.join(missing) + '; only --validate-only is available')
    repaired, seams = shared.integrate(current_pair, patches, native.load_seam_function())
    pixels = shared.pixel_verification(current_pair, repaired)
    native.require(np.array_equal(repaired[:, :3469], current_pair[:, :3469]), 'Current c11 west repairs changed')
    # Preserve the exact prior generation record as text before replacing the same PNG path.
    previous_record = REPAIR / 'previous-current-r08_c11.generation.json'
    previous_record_bytes = Path(current['recordFile']).read_bytes()
    native.writable(previous_record).write_bytes(previous_record_bytes)
    native.require(native.sha(previous_record) == current['recordSha256'], 'Historical source record copy mismatch')
    provenance_path = REPAIR / 'current-c11-before-integration.json'
    provenance = {'recordedAtUtc': native.utc_now(), 'currentTileBeforeOverwrite': current,
                  'historicalRecord': ref(previous_record), 'immutableGuideSources': sources,
                  'eastStripEquality': equality, 'imageBackupsCreated': False,
                  'authorizedChangeRectInPairXYXY': [3469, 0, 4723, 4096],
                  'pixelValidationAfterOverwrite': 'historical-record-only-not-current-pixels'}
    native.save_json(provenance_path, provenance)
    # Detect a concurrent edit immediately before canonical output writes.
    shared.check_hash(CURRENT_WEST, current['sha256'], 'current c11 immediately before write')
    qa = write_qa(repaired)
    outputs = []
    for index, name in enumerate(('r08_c11', 'r08_c12')):
        destination = OUTPUT / f'{name}.png'
        native.require(all(not shared.same_path(destination, src['file']) for src in sources), 'Cannot overwrite immutable guide source')
        array = repaired[:, index * 4096:(index + 1) * 4096]
        info = native.save_image(destination, Image.fromarray(array))
        native.require(np.array_equal(shared.rgb(destination, (4096, 4096)), array), 'Saved PNG pixel mismatch')
        outputs.append(dict(info, tile=name))
    saved = np.concatenate([shared.rgb(Path(item['file']), (4096, 4096)) for item in outputs], axis=1)
    native.require(shared.pixel_verification(current_pair, saved) == pixels, 'Reloaded pixel verification mismatch')
    for src in sources:
        shared.check_hash(src['file'], src['sha256'], 'immutable generation source after write')
    manifest = {'createdAtUtc': native.utc_now(), 'tile': 'r08_c12', 'formalAccepted': False,
                'wholeCityComplete': False, 'visualInspectionPerformedByScript': False,
                'script': ref(Path(__file__)), 'sharedIntegrationFunctions': ref(Path(shared.__file__)),
                'assemblyFunctions': ref(Path(native.__file__)), 'seamHelper': ref(native.HELPER),
                'immutableGuideSources': sources,
                'integrationBaselines': [dict(current, availability='superseded', historicalRecord=str(previous_record),
                                              historicalRecordSha256=native.sha(previous_record),
                                              pixelValidation='historical-record-only-not-current-pixels'), sources[1]],
                'priorCurrentTileProvenance': ref(provenance_path), 'eastStripEqualityBeforeIntegration': equality,
                'nativeRepairSources': entries, 'seams': seams,
                'parameters': {'pairPixels': [8192, 4096], 'stripPairRectXYXY': [3469, 0, 4723, 4096],
                               'patchYStarts': [0, 1024, 2048, 2842], 'longitudinalOverlaps': [230, 230, 460],
                               'insertionOverlapEachSidePixels': 150, 'transitionWidthPixels': 2,
                               'registration': False, 'colorCorrection': False, 'imageBlur': False,
                               'maskBlur': False, 'resampling': False, 'noUpscaling': True},
                'pixelVerification': pixels, 'currentC11Left3469ColumnsExactlyPreserved': True,
                'immutableGuideSourcesUnchanged': True, 'outputs': outputs, 'qa': qa,
                'qaCoverage': {'fullCommonEdge': True, 'fullLeftAndRightInsertion': True,
                               'horizontalOverlaps': 3, 'insertionCorners': 4, 'nativePixelScale': 1,
                               'maxDimension': 1536, 'visualReview': 'pending'}}
    native.save_json(MANIFEST, manifest)
    native.save_json(QA / 'manifest.json', {'outputs': outputs, 'qa': qa, 'coverage': manifest['qaCoverage']})
    for item in outputs:
        native.save_json(Path(item['file'] + '.generation.json'), dict(item,
            operation='native-pixel integration of c11/c12 shared edge preserving current c11 west repairs',
            integrationManifest=ref(MANIFEST), derivedFrom=manifest['integrationBaselines'],
            nativeRepairSources=entries, noUpscaling=True, actualModel=None, actualQuality=None, formalAccepted=False))
    print(json.dumps({'outputs': outputs, 'manifest': str(MANIFEST), 'qa': str(QA),
                      'outsideRepairExactlyIdentical': True, 'currentC11WestRepairsPreserved': True}))


if __name__ == '__main__':
    main()
