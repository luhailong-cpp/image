"""Create a concise handoff from the verified current four-tile metadata snapshot."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ref(p):
    return {'path': str(Path(p).resolve()), 'sha256': sha(p)}

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('directory', type=Path)
args = ap.parse_args()
D = args.directory.resolve()
report_path = D/'four-tile-delivery.json'
report = read(report_path)
sync_path = D/'metadata-sync-verification.json'
sync = read(sync_path)
assert report['status'] == 'current_metadata_and_selected_pngs_verified' and report['errors'] == []
assert sync['status'] == 'current_metadata_synchronized' and sync['errors'] == []
assert report['tileCount'] == 4
rows = []
for row in report['tiles']:
    tile = row['tile']
    for metadata in row['selectionMetadata'].values():
        assert sha(metadata['path']) == metadata['sha256'], 'Metadata changed after delivery verification.'
    assert all(check is not False for check in row['checks'].values())
    progress = row['currentQAAndUnpassedIssues']['progress']
    wrapper = row['currentQAAndUnpassedIssues']['wrapper']
    assert progress['formalAccepted'] is False and wrapper['formalAccepted'] is False
    assert progress['pairedEdgesQA'] == wrapper['pairedEdgesQA']
    roots = {k: progress[k] for k in ['rootLocalQA', 'rootIndependentQARef', 'rootFinalQA', 'finalEvidenceReuseQA'] if k in progress}
    for source in roots.values():
        assert sha(source['path']) == source['sha256']
    own_pending = progress.get('pendingRepairs', progress.get('remainingQA', progress.get('remainingFindings', [])))
    rows.append({
        'tile': tile, 'image': row['candidate'], 'status': progress['status'],
        'rootQA': roots,
        'internalArtQA': progress.get('internalArtQA'),
        'internalRasterSeamQA': progress.get('internalRasterSeamQA', progress.get('internalSeamQA')),
        'externalNeighborSeamQA': progress.get('externalNeighborSeamQA'),
        'pairedEdgesQA': progress['pairedEdgesQA'], 'pendingOwnIssues': own_pending,
        'nextStep': progress['nextStep'], 'formalAccepted': False})

handoff = {
    'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Only r15_c15, r15_c16, r16_c15, r16_c16 in this batch.',
    'status': 'four_native_4096_candidates_verified_with_explicit_unpassed_QA',
    'tileCount': 4, 'activeBaseNativeCoreCount': 64, 'missingNativeCoreCount': 0,
    'deliveryVerification': ref(report_path), 'metadataSyncVerification': ref(sync_path),
    'metadataBeforeSnapshot': ref(D/'metadata-before-snapshot.json'),
    'tiles': rows,
    'sharedPairSummary': [
        {'pair': ['r15_c15 east', 'r15_c16 west'], 'status': 'failed_W01_deferred_after_two_native_attempts'},
        {'pair': ['r15_c15 south', 'r16_c15 north'], 'status': 'local_pass_after_synchronized_post_removal'},
        {'pair': ['r15_c16 south', 'r16_c16 north'], 'status': 'local_pass_after_N02_final_core_pair_review'},
        {'pair': ['r16_c15 east', 'r16_c16 west'], 'status': 'failed_W02_with_W03_W04_pending_and_W01_watch'}],
    'reservedExcluded': ['r12_c13', 'r12_c14', 'r12_c15', 'r12_c16'],
    'nextSteps': [
        'Keep the selected images and all historical originals/trials. Do not reinterpret deferred repairs as passed.',
        'Defer r15_c16 W01, r16_c16 W02 and I01-lower after two failed native attempts; any later repair must respect the recorded protected anchors and coordinate dependent edges.',
        'Remaining independent finish work: r15_c15 N02/N03 north material and W02 west material; r16_c16 W03 gold/stone transition, W04 wall grid/material, M01 lighting. Retain r16_c15 inherited-grid and r16_c16 W01 closure/material watch.',
        'Do not modify reserved r12_c13/r12_c14/r12_c15/r12_c16 or update the obsolete six-tile checkpoint from this four-tile handoff.'
    ],
    'formalAccepted': False, 'globalMapAccepted': False, 'errors': [],
    'notes': [
        '本批只同步八份当前元数据并生成新交付记录；四张成图、选源 manifest、旧 QA 和旧 checkpoint 未改写。',
        '本批所有图片均来自现有内置入口，实际型号未返回，未使用付费 API，不将未知型号标为 2.5。',
        '本批制作及收尾未操作共享 Git 的 HEAD、index 或 refs，未声称提交或推送。'
    ]}
output = D/'handoff.json'
with output.open('x', encoding='utf-8') as f:
    json.dump(handoff, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'handoff': ref(output), 'deliveryVerification': ref(report_path), 'metadataSyncVerification': ref(sync_path), 'errors': []}, ensure_ascii=False))
