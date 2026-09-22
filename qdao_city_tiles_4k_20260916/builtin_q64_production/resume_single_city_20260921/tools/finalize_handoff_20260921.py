"""Freeze this requested WIP handoff; no artwork generation or acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import shutil

SESSION = Path(__file__).resolve().parent.parent
ART = SESSION.parents[1]
REPO = ART.parent
OUT = SESSION / 'handoff-20260921'
DOC = ART / '主城美术详细交接-20260921.md'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write_new(path, obj):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def ref(path):
    return {'file': str(path.resolve()), 'sha256': sha(path)}


def main():
    assert not (OUT / 'snapshot.json').exists(), 'Handoff already frozen; create another version instead'
    state = read(SESSION / 'session-state.json')
    ledger = read(SESSION / 'current-coverage-ledger.json')
    assert state['candidateCoordinateCountIncludingWorkInProgress'] == 8
    assert state['productionAcceptedTiles'] == 0 and not state['deliveryReady']
    report_path = sorted((SESSION / 'tools/checkpoint_reports').glob('checkpoint-*.json'))[-1]
    report = read(report_path)
    assert report['status'] == 'TECHNICAL_CONSISTENT' and not report['errors']
    report_inputs = {Path(x['file']).resolve(): x['sha256'] for x in report['inputFilesBefore']}
    for p in (SESSION / 'session-state.json', SESSION / 'current-coverage-ledger.json'):
        assert report_inputs[p.resolve()] == sha(p), 'Checkpoint stale: ' + str(p)
    provenance_path = sorted((SESSION / 'provenance').glob('index-*.json'))[-1]
    provenance = read(provenance_path)
    assert not provenance['errors'] and not provenance['concurrentInputChangesDetected']
    assert provenance['nativeImages'] == state['newNativeDetailCount'] + state['newNativeRepairCount'] + state['newReferenceCount']
    inputs = OUT / 'inputs'
    inputs.mkdir(exist_ok=False)
    frozen = []
    names = ['session-state.json', 'current-coverage-ledger.json', 'model-capability.json']
    names += [f'next_tile_{t}/{n}' for t in ('r08_c07','r08_c08','r08_c09') for n in ('HANDOFF.md','handoff-state.json','plan.json')]
    for name in names:
        source = SESSION / name
        target = inputs / name
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha(source)
        shutil.copyfile(source, target)
        assert sha(source) == before == sha(target), 'Input changed during freeze'
        frozen.append({'source': str(source), 'sha256': before, 'copy': str(target)})
    partials = []
    for tile in ('r08_c07','r08_c08','r08_c09'):
        directory = SESSION / ('next_tile_' + tile)
        native = [ref(p) for p in sorted((directory / 'native').glob('*.png'))]
        partials.append({'tile': tile, 'handoff': ref(directory / 'HANDOFF.md'),
                         'state': ref(directory / 'handoff-state.json'), 'plan': ref(directory / 'plan.json'),
                         'nativePngCountIncludingRejectedVersions': len(native), 'nativeFiles': native,
                         'candidateCoordinateAdded': False, 'formalAccepted': False})
    candidates = []
    for item in ledger['tiles']:
        if not item['candidateExists']:
            continue
        candidate = item['candidate']
        p = ART / candidate['file']
        assert sha(p) == candidate['sha256'], 'Candidate changed: ' + str(p)
        candidates.append({'tile': item['tile'], 'absoluteFile': str(p), **candidate, 'accepted': False})
    csv_path = OUT / 'candidate-coordinates.csv'
    fields = ['tile','role','file','sha256','pixelX','pixelY','pixelWidth','pixelHeight','worldX','worldZ','worldWidth','worldHeight','formalAccepted']
    with csv_path.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for c in candidates:
            rect = c['finalPixelRectXYWH']
            world = c['worldRect']
            writer.writerow(dict(tile=c['tile'], role='candidate_not_production_tile', file=c['absoluteFile'], sha256=c['sha256'],
                                 pixelX=rect[0],pixelY=rect[1],pixelWidth=rect[2],pixelHeight=rect[3],worldX=world['x'],worldZ=world['z'],
                                 worldWidth=world['width'],worldHeight=world['height'],formalAccepted=False))
    critical_paths = [REPO / 'AGENTS.md', REPO / '主城地图切图规范.md', REPO / 'docs/IMAGE_MODEL_POLICY.md',
                      REPO / 'config/image-generation.json', REPO / 'designs/README.md',
                      REPO.parent / 'mmorpg-client/Docs/CityTilePublishing.md',
                      REPO / 'designs/guild-ui-v2/source/guild-overview.png',
                      REPO / 'tianyong_festival_hd_20260910/tianyong_city_master_6144.png',
                      ART / 'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png']
    counts = {key: state[key] for key in ('candidateCoordinateCountIncludingWorkInProgress','coordinatesWithoutAny4KCandidate',
              'productionAcceptedTiles','completeCityDeliveries','allAppearanceCandidateCoordinateCountIncludingWorkInProgress',
              'newNativeDetailCount','newNativeRepairCount','newReferenceCount','allAppearanceRetainedNativeKnownCountExcludingReferences')}
    result = {'schemaVersion': 1, 'frozenAtUtc': datetime.now(timezone.utc).isoformat(),
              'purpose': 'user_requested_work_in_progress_handoff_not_production_delivery',
              'activeAppearance': 'tianyong_festival', 'counts': counts, 'coverageCounts': ledger['counts'],
              'newImageGenerationStoppedByUserHandoffRequest': True,
              'toolInFlightStateEvidence': 'See each partial tile handoff-state; undisclosed host-side state must not be inferred.',
              'candidates': candidates, 'partialTiles': partials, 'frozenInputs': frozen,
              'criticalLiveInputsAtHandoff': [ref(p) for p in critical_paths],
              'technicalCheckpoint': ref(report_path), 'provenanceIndex': ref(provenance_path),
              'candidateCoordinateList': ref(csv_path), 'deliveryReady': False, 'formalManifestProduced': False,
              'runtimePublished': False, 'actualModel': None, 'actualQuality': None, 'backendModelVerified': False,
              'interpretation': 'Frozen checkpoint only. Verify actual files and subsequent records when resuming; source count includes rejected retained versions.'}
    write_new(OUT / 'snapshot.json', result)
    print(json.dumps({'snapshot': str(OUT / 'snapshot.json'), 'counts': counts,
                      'partialNativePngsIncludingRejected': {x['tile']: x['nativePngCountIncludingRejectedVersions'] for x in partials},
                      'report': str(report_path), 'provenance': str(provenance_path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
