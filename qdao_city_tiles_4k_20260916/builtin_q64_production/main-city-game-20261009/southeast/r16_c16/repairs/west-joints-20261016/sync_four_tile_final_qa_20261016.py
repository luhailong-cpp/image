"""Snapshot and update only the eight current metadata JSON files from reviewed QA."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

Z = Path(__file__).resolve().parents[3]
TILES = ['r15_c15', 'r15_c16', 'r16_c15', 'r16_c16']
EXPECTED = dict(zip(TILES, [
    '647150e78b003c02760adf02fbbe8bd6509c07b6d4b7335e67a326ca44890214',
    '410a4d21041e155101848ed62738e47aa2130bced98c2269cad9e8605046a73a',
    '91120a198c6d8d64bb3fd00ef8fbc1265a0ff2f613908b1b2d36cef0f51f8cc3',
    'e7c4c2ec482ce257b7bf029b89f2b91567882dac02381bd8a6efcddfff69f261']))

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ref(p):
    return {'path': str(p), 'sha256': sha(p)}

def new_json(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

qa_paths = {
    'r15_c15': Z/'r15_c15/review/resumed-local-repairs-20261016/root-local-qa-20261016.json',
    'r15_c16': Z/'r15_c16/repairs/independent-seam-fixes-20261013-v1/I01-only-reviewed-20261016/root-independent-qa-20261016.json',
    'r16_c15': Z/'r16_c15/review/resume-20261016/root-local-qa-20261016.json',
    'r16_c16': Z/'r16_c16/review/root-final-batch-20261016/root-final-evidence-qa-20261016.json'}
qa = {tile: read(p) for tile, p in qa_paths.items()}
qa_refs = {tile: ref(p) for tile, p in qa_paths.items()}
assert qa_refs['r16_c16']['sha256'] == '6bd0c64f2cbb7fc434ea87d9eb9ac04c49b0bbd2464a21bc97aedab8cdda1ca6'
assert qa['r15_c15']['core']['sha256'] == EXPECTED['r15_c15']
assert qa['r15_c16']['reviewedCore']['sha256'] == EXPECTED['r15_c16']
assert qa['r16_c15']['candidate']['sha256'] == EXPECTED['r16_c15']
assert qa['r16_c16']['candidate']['sha256'] == EXPECTED['r16_c16']
assert qa['r16_c16']['neighbors']['north']['sha256'] == EXPECTED['r15_c16']
assert qa['r16_c16']['neighbors']['west']['sha256'] == EXPECTED['r16_c15']
assert qa['r16_c15']['actualNorthSource']['sha256'] == EXPECTED['r15_c15']
assert qa['r16_c16']['counts'] == {'totalEvidence': 42, 'newlyRootViewed': 10, 'exactShaReusedRootN02': 1, 'unchangedPriorQAReused': 31}
assert all(q['formalAccepted'] is False for q in qa.values())
reuse_ref = qa['r16_c16']['sourceQA']['pixelReuse']
assert sha(reuse_ref['path']) == reuse_ref['sha256']
repair_record_path = Z/'r15_c16/repairs/independent-seam-fixes-20261013-v1/repair-review-20261016.json'
repair_record_ref = ref(repair_record_path)
w01 = next(i for i in read(repair_record_path)['issues'] if i['id'] == 'W01')
assert w01['status'] == 'failed_pending_retained_original_after_two_native_attempts'

before, raw, source_paths = {}, {}, {}
for tile in TILES:
    before[tile] = {}
    for kind, rel in [('progress', 'progress.json'), ('wrapper', 'candidate/latest-assembly.json')]:
        p = Z/tile/rel
        raw[(tile, kind)] = p.read_bytes()
        source_paths[(tile, kind)] = p
        before[tile][kind] = read(p)
    assert before[tile]['wrapper']['candidate']['sha256'] == EXPECTED[tile]
    assert before[tile]['progress']['candidateSha256'] == EXPECTED[tile]
    assert Path(before[tile]['progress']['candidate']) == Path(before[tile]['wrapper']['candidate']['path'])

now = datetime.now(timezone.utc)
out = Z/'batch-checkpoints'/('four-tile-final-'+now.strftime('%Y%m%dT%H%M%SZ'))
out.mkdir(parents=True, exist_ok=False)
snapshot_entries = []
for (tile, kind), content in raw.items():
    target = out/'before'/tile/('progress.json' if kind == 'progress' else 'latest-assembly.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as f:
        f.write(content)
    assert target.read_bytes() == content
    snapshot_entries.append({'tile': tile, 'kind': kind, 'source': str(source_paths[(tile, kind)]), 'snapshot': ref(target)})
snapshot_path = out/'metadata-before-snapshot.json'
new_json(snapshot_path, {'createdAtUtc': now.isoformat(), 'fileCount': 8, 'entries': snapshot_entries})

after = copy.deepcopy(before)
paired = {t: {} for t in TILES}
def pair(a, a_edge, b, b_edge, status, evidence, description):
    for tile, edge, neighbor, other_edge in [(a, a_edge, b, b_edge), (b, b_edge, a, a_edge)]:
        paired[tile][edge] = {
            'selfCandidateSha256': EXPECTED[tile], 'neighborTile': neighbor,
            'neighborCandidate': copy.deepcopy(before[neighbor]['wrapper']['candidate']),
            'pairedEdge': other_edge, 'status': status, 'description': description,
            'evidence': copy.deepcopy(evidence), 'formalAccepted': False}

pair('r15_c15', 'east', 'r15_c16', 'west',
     'failed_W01_deferred_after_two_native_attempts',
     [qa_refs['r15_c16'], repair_record_ref],
     'r15_c16 west W01 remains unpassed at core [0,3515,140,3705]; both attempts rejected and original edge retained.')
pair('r15_c15', 'south', 'r16_c15', 'north',
     'local_pass_after_synchronized_post_removal', [qa_refs['r16_c15']],
     'Actual current north/south pair locally passed after both halves of the redundant small post were removed; unchanged quadrant evidence reused.')
pair('r15_c16', 'south', 'r16_c16', 'north',
     'local_pass_after_N02_final_core_pair_review', [qa_refs['r16_c16']],
     'Actual current north/south pair locally passed; changed final evidence and exact unchanged evidence accounted for in root final QA.')
pair('r16_c15', 'east', 'r16_c16', 'west',
     'failed_W02_with_W03_W04_pending_and_W01_watch', [qa_refs['r16_c16'], qa_refs['r16_c15']],
     'r16_c16 W02 lower coping mismatch remains failed after two native attempts; W03 gold/stone transition and W04 wall grid/material remain pending; W01 short closure is the accepted local best with shape/material watch.')

for tile in TILES:
    for obj in after[tile].values():
        obj['formalAccepted'] = False
        obj['qaUpdatedAtUtc'] = now.isoformat()
        obj['pairedEdgesQA'] = copy.deepcopy(paired[tile])

def update_both(tile, values):
    for obj in after[tile].values():
        obj.update(copy.deepcopy(values))

a_external = copy.deepcopy(before['r15_c15']['progress']['externalNeighborSeamQA'])
a_external.update({edge: v['status'] for edge, v in paired['r15_c15'].items()})
update_both('r15_c15', {
    'status': 'internal_pass_east_pair_failed_north_west_finish_pending',
    'rootLocalQA': qa_refs['r15_c15'], 'externalNeighborSeamQA': a_external,
    'remainingQA': before['r15_c15']['progress']['remainingQA'],
    'nextStep': 'Keep east r15_c16 W01 failed after two native attempts and north N02/N03 plus west W02 finish pending. South current pair locally passed; retain the selected image and unchanged internal QA.'})

update_both('r15_c16', {
    'status': 'internal_pass_west_pair_failed_north_south_local_pass',
    'rootIndependentQARef': qa_refs['r15_c16'],
    'externalNeighborSeamQA': {'north': 'passed_previous_QA', 'west': paired['r15_c16']['west']['status'], 'south': paired['r15_c16']['south']['status']},
    'remainingQA': [{'id': 'W01', 'status': w01['status'], 'coreBox': w01['coreBox'], 'description': w01['finding'], 'evidence': repair_record_ref}],
    'nextStep': 'Keep west W01 failed and deferred after two native attempts. Future repair must preserve the immutable south384 anchor or coordinate a downstream revision. Current south pair locally passed; no further retry in this batch.'})

c_external = copy.deepcopy(before['r16_c15']['progress']['externalNeighborSeamQA'])
c_external.update({edge: v['status'] for edge, v in paired['r16_c15'].items()})
update_both('r16_c15', {
    'status': 'root_local_repairs_pass_east_pair_failed_material_watch',
    'rootLocalQA': qa_refs['r16_c15'], 'externalNeighborSeamQA': c_external,
    'internalArtQA': before['r16_c15']['progress']['internalArtQA'],
    'internalGeometryQA': before['r16_c15']['progress']['internalGeometryQA'],
    'remainingFindings': before['r16_c15']['progress']['remainingFindings'],
    'nextStep': 'Keep east pair failed for r16_c16 W02 and pending for W03/W04, with W01 closure/material watch. Local I01/N01/W01/W02 repairs and current north pair passed root review; inherited fine-grid material watch remains.'})

update_both('r16_c16', {
    'rootFinalQA': qa_refs['r16_c16'], 'finalEvidenceReuseQA': reuse_ref,
    'finalQAEvidenceCounts': qa['r16_c16']['counts'],
    'internalRasterSeamQA': qa['r16_c16']['internalRasterSeamQA'],
    'internalArtQA': qa['r16_c16']['internalArtQA'],
    'externalNeighborSeamQA': {**qa['r16_c16']['externalNeighborSeamQA'], **{edge: v['status'] for edge, v in paired['r16_c16'].items()}},
    'pendingRepairs': qa['r16_c16']['pending'],
    'nextStep': 'Keep W02 and I01-lower failed and deferred after two native attempts. W03/W04 material, M01 lighting and W01 closure/material watch remain unpassed. Final north pair and upper I01 passed local review; retain all original outputs and selected images.'})

# Only the named current JSON metadata is mutable. Guard all image/source selectors.
frozen_keys = ['candidate', 'candidateSha256', 'context', 'contextSha256', 'manifest', 'assemblyManifest', 'visualQA', 'verification', 'baseAssembly', 'selectedNativeRepairs']
for tile in TILES:
    for kind in ['progress', 'wrapper']:
        original, updated = before[tile][kind], after[tile][kind]
        for key in frozen_keys:
            assert original.get(key) == updated.get(key), (tile, kind, key)
        assert source_paths[(tile, kind)].read_bytes() == raw[(tile, kind)], 'Concurrent metadata change; stop.'
for p in qa_paths.values():
    assert sha(p) == qa_refs[next(t for t, q in qa_paths.items() if q == p)]['sha256']

changes = []
for tile in TILES:
    for kind in ['progress', 'wrapper']:
        p = source_paths[(tile, kind)]
        p.write_text(json.dumps(after[tile][kind], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        assert read(p) == after[tile][kind]
        changes.append({'tile': tile, 'kind': kind, 'current': ref(p), 'changedFields': [k for k in after[tile][kind] if before[tile][kind].get(k) != after[tile][kind][k]]})

errors = []
for tile in TILES:
    for edge, item in after[tile]['progress']['pairedEdgesQA'].items():
        neighbor = item['neighborTile']
        reverse = after[neighbor]['progress']['pairedEdgesQA'][item['pairedEdge']]
        if reverse['neighborTile'] != tile or reverse['status'] != item['status'] or item['neighborCandidate']['sha256'] != EXPECTED[neighbor]:
            errors.append({'tile': tile, 'edge': edge, 'error': 'paired edge inconsistency'})
for tile, p in qa_paths.items():
    assert sha(p) == qa_refs[tile]['sha256'], 'QA file changed unexpectedly.'
assert sha(reuse_ref['path']) == reuse_ref['sha256']
assert sha(repair_record_path) == repair_record_ref['sha256']

verification_path = out/'metadata-sync-verification.json'
new_json(verification_path, {
    'createdAtUtc': now.isoformat(), 'status': 'current_metadata_synchronized' if not errors else 'failed',
    'beforeSnapshot': ref(snapshot_path), 'changedFileCount': 8, 'changes': changes,
    'pairedEdgeCount': 4, 'directedEdgeCount': 8, 'pairedStatusesBidirectionallyConsistent': not errors,
    'allImageAndManifestSelectorsUnchanged': True, 'sourceQAHashesUnchanged': True,
    'sourceImagesWritten': False, 'manifestsWritten': False, 'oldQAWritten': False,
    'formalAccepted': False, 'errors': errors})
print(json.dumps({'directory': str(out), 'snapshot': ref(snapshot_path), 'verification': ref(verification_path), 'errors': errors}, ensure_ascii=False))
assert not errors
