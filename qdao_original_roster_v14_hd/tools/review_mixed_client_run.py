"""Bind a real isolated Unity run and optionally sync only its reviewed character C# files."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import mixed_workspace

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT.parent / 'qdao_original_roster_v13/runtime-validation'
FORMAL = mixed_workspace.FORMAL
ISOLATED = mixed_workspace.ISOLATED
BASELINE = RUNS / 'mixed-resolution-client-run1/formal-safety-baseline.json'
NEW_SOURCE = ('Assets/Scripts/World/QdaoMixedResolutionContract.cs',
              'Assets/Tests/EditMode/Tianyong/QdaoMixedResolutionAppearanceTests.cs')
MODIFIED_SOURCE = (
    'Assets/Scripts/World/QdaoCharacterCatalog.cs',
    'Assets/Scripts/World/QdaoHdResources.cs',
    'Assets/Scripts/World/QdaoOriginalHdResourceIndex.cs',
    'Assets/Editor/QdaoOriginalHdResourceIndexBuilder.cs',
    'Assets/Tests/PlayMode/QdaoHdResourceLifetimePlayModeTests.cs',
    'Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs',
)
WRITABLE_SOURCE = set(MODIFIED_SOURCE + NEW_SOURCE + tuple(p + '.meta' for p in NEW_SOURCE))
MIXED_METHODS = {
    'EditMode': ('MmorpgClient.Tests.EditMode.Tianyong.QdaoMixedResolutionAppearanceTests', {
        'ExplicitMixedContractUses137DeclaredDimensionsAndEqualWorldGeometry': 1,
        'MalformedMixedMetadataCannotBecomeAvailable': 10,
        'MixedModeCannotBeInferredFromDimensionsOrBorrowAnotherIdentity': 1,
        'EveryMissingMixedImageFallsBackOnlyToCompleteSameIdentityV13AndRetriesImport': 1,
        'MixedIndexRequiresExplicitModeBothSizesAndMatchingPerFramePpu': 1,
    }),
    'PlayMode': ('MmorpgClient.Tests.PlayMode.QdaoHdResourceLifetimePlayModeTests', {
        'MixedAllDirectionsAnimateBothSizesWithEqualBoundsThirtyMsAndIndependentIdle': 1,
        'MixedMissingOrSwappedResolutionReleasesWholeDirectionAndCannotBorrowFrames': 5,
        'MixedRevisionsShareBothTextureSizesUntilLastLeaseEnds': 1,
        'MixedBattleAndGhostRetainDisplayedLegacyAndHdSpritesAcrossReplacement': 1,
    }),
}

def require(value, message):
    if not value:
        raise ValueError(message)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def rows(document):
    result = {row['path']: row['sha256'] for row in document['files']}
    require(len(result) == len(document['files']), 'Duplicate snapshot paths')
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--execute-source-sync', action='store_true')
    args = parser.parse_args()
    run = (RUNS / args.run).resolve()
    require(run.parent == RUNS.resolve(), 'Run must be a direct child of runtime-validation')
    spec = importlib.util.spec_from_file_location('v14_gate', ROOT / 'tools/publish_original_roster_v14.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    baseline = read(BASELINE)
    baseline_rows = rows(baseline)
    paths = baseline['source_paths'] + list(NEW_SOURCE) + [p + '.meta' for p in NEW_SOURCE]
    snapshot_names = ('input-editmode.json', 'input-playmode.json', 'post-playmode.json')
    snapshots = {name: read(run / name) for name in snapshot_names}
    by = {name: rows(document) for name, document in snapshots.items()}
    for name, document in snapshots.items():
        require(Path(document['project']).resolve() == ISOLATED and document['shared_writable_links'] is False,
                'Wrong/shared Unity project snapshot: ' + name)
    tested = by['input-playmode.json']
    require(all(data == tested for data in by.values()), 'Edit/Play/post inputs must be identical')
    for path in paths:
        gate.safe_child(ISOLATED, path)
        gate.safe_child(FORMAL, path)
        require(path in tested and sha(ISOLATED / path) == tested[path], 'Tested source changed: ' + path)
    report_path = run / 'city-captures/runtime-observed-appearances.json'
    report = read(report_path)
    require(report['schemaVersion'] == 2 and report['behaviorAssertionsCompleted'] is True and
            report['inputSnapshotSha256'] == sha(run / 'input-playmode.json'), 'Unbound runtime report')
    counts = {}
    mixed_cases = {}
    evidence = {}
    for platform, stem in (('EditMode', 'editmode'), ('PlayMode', 'playmode')):
        xml = run / (stem + '.xml')
        result = gate.check_results(xml, hd_platform=platform)
        launch = gate.check_launch_binding(xml, report, gate.snapshot_records(snapshots['input-playmode.json']), [],
            sha(run / 'input-playmode.json') if platform == 'PlayMode' else None, platform)
        expected_input = run / ('input-' + stem + '.json')
        require(Path(launch['input_snapshot']).resolve() == expected_input and
                launch['input_snapshot_sha256'] == sha(expected_input), 'Wrong exact ' + platform + ' input snapshot')
        class_name, methods = MIXED_METHODS[platform]
        selected = [case for case in result.iter('test-case') if case.get('classname') == class_name and case.get('methodname') in methods]
        for method, count in methods.items():
            require(sum(case.get('methodname') == method for case in selected) == count,
                    'Missing mixed test/parameter case: ' + platform + '/' + method)
        cases = [case.get('fullname') for case in selected]
        mixed_cases[platform] = cases
        counts[platform] = {key: int(result.get(key)) for key in ('total', 'passed', 'failed', 'skipped', 'inconclusive')}
        counts[platform]['exit_code'] = read(run / (stem + '-completion.json'))['exit_code']
        evidence[platform] = {label: sha(run / name) for label, name in {
            'xml': stem + '.xml', 'launch': stem + '-launch.json', 'completion': stem + '-completion.json',
            'log': stem + '.log'}.items()}
    # Existing normal captures remain regression evidence. No real HD/mixed assets exist yet.
    require(report.get('testedOriginalCount') == 4 and report.get('testedHdOriginalCount') == 0 and
            report.get('testedMixedOriginalCount') == 0, 'Do not count fixtures as real new character assets')
    camera = gate.camera_contract(ISOLATED)
    views = [gate.check_runtime_view(actor, 'normalView', report_path.parent, camera) for actor in report['appearances']]
    character_prefix = 'Assets/Resources/World/Characters/'
    protected = {path: digest for path, digest in baseline_rows.items() if path.startswith(character_prefix)}
    live = {path.relative_to(FORMAL).as_posix(): sha(path)
            for path in (FORMAL / character_prefix).rglob('*') if path.is_file()}
    require(live == protected, 'Formal character resource inventory or bytes changed')
    source_plan = []
    for path in paths:
        expected_before = baseline_rows.get(path)
        if path not in WRITABLE_SOURCE:
            require(tested[path] == expected_before, 'Unrelated bound source/config changed in isolated project: ' + path)
        current = sha(FORMAL / path) if (FORMAL / path).is_file() else None
        require(current in (expected_before, tested[path]), 'Concurrent formal source change: ' + path)
        if tested[path] != expected_before:
            require(path in WRITABLE_SOURCE, 'Source sync cannot modify unrelated code, configuration or resources')
            source_plan.append(dict(path=path, before_sha256=expected_before, tested_sha256=tested[path]))
    output = run / ('source-sync-result.json' if args.execute_source_sync else 'final-result-review.json')
    require(not output.exists(), 'Retain previous review output: ' + str(output))
    if args.execute_source_sync:
        safety = read(run / 'formal-source-sync-safety.json')
        require(safety.get('active_unity_processes') == 0 and safety.get('lock_exclusive_probe_passed') is True and
                Path(safety['project']).resolve() == FORMAL and
                0 <= (datetime.now(timezone.utc) - datetime.fromisoformat(safety['checked_utc'].replace('Z', '+00:00'))).total_seconds() < 600,
                'Source sync requires a recent process and lock safety check')
        # The caller verifies no active Unity process and an unused stale lock.
        # Every destination is one explicit C# or meta path after the complete preflight above.
        for row in source_plan:
            target = FORMAL / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (ISOLATED / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['tested_sha256'], 'Source changed during sync')
            expected_before = row['before_sha256']
            require((sha(target) if target.is_file() else None) in (expected_before, row['tested_sha256']),
                    'Destination changed during sync: ' + row['path'])
            temporary = target.with_name(target.name + '.mixed-sync-tmp')
            require(not temporary.exists(), 'Stale sync temp; stop for inspection')
            with temporary.open('xb') as stream:
                stream.write(data)
            os.replace(temporary, target)
        require(all(sha(FORMAL / p) == tested[p] for p in paths), 'Formal source differs after sync')
        require({p.relative_to(FORMAL).as_posix(): sha(p) for p in (FORMAL / character_prefix).rglob('*') if p.is_file()} == protected,
                'Protected characters changed during source sync')
    review = dict(status='passed', created_utc=datetime.now(timezone.utc).isoformat(),
        review_tool_sha256=sha(Path(__file__)),
        scope='Real Unity technical compatibility/regression validation; no artwork generation, approval, staging or publication',
        unity=counts, mixed_test_cases=mixed_cases, unity_evidence_sha256=evidence,
        identical_input_file_count=len(tested), all_input_additions=0, all_input_removals=0, all_input_changes=0,
        snapshots={name: sha(run / name) for name in snapshot_names}, runtime_report_sha256=sha(report_path),
        runtime_original_count=4, runtime_full_hd_count=0, runtime_mixed_count=0,
        runtime_normal_views=views, new_artwork_closeup_acceptance=False,
        source_bindings={p: tested[p] for p in paths}, source_sync_plan=source_plan,
        source_sync_executed=args.execute_source_sync, protected_character_files=len(protected),
        source_sync_safety_sha256=sha(run / 'formal-source-sync-safety.json') if args.execute_source_sync else None,
        protected_character_changes=0, protected_character_missing=0, protected_character_added=0,
        new_generation_status='paused_until_actual_gpt_image_2_5_evidence', remaining_actions=2388)
    output.write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(output), sha256=sha(output), unity=counts,
        mixed_cases={key: len(value) for key, value in mixed_cases.items()}, input_files=len(tested),
        source_bindings=len(paths), changed_source_files=len(source_plan), source_sync=args.execute_source_sync,
        protected_characters=len(protected))))

if __name__ == '__main__':
    main()
