"""Check accepted Original V14 HD 00-22 candidates; stage/publish only with explicit --execute.

Default: read-only dry run. Art approval is performed by approve.py, never here.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import uuid
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parents[1]
SOURCE_COMMIT = '9adcf9291e4a867601868889a5965f3cd48630ba'
FAMILY = 'Assets/Resources/World/Characters/QdaoOriginalRosterV14'
RESOURCE_FAMILY = 'World/Characters/QdaoOriginalRosterV14'
DIRECTIONS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
CODE_PATHS = (
    'Assets/Scripts/World/QdaoCharacterCatalog.cs',
    'Assets/Scripts/World/QdaoBoySpriteAnimator.cs',
    'Assets/Scripts/World/Tianyong/TianyongSandboxBootstrap.cs',
    'Assets/Scripts/World/Tianyong/TianyongPlayerController.cs',
    'Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs',
    'Assets/Editor/QdaoCharacterSpriteImporter.cs',
    'Assets/Tests/EditMode/Tianyong/QdaoAppearanceVersionTests.cs',
    'Assets/Tests/EditMode/Tianyong/QdaoCharacterCatalogTests.cs',
    'Assets/Tests/EditMode/Tianyong/QdaoOriginalAppearanceTests.cs',
    'Assets/Tests/EditMode/Battle/BattleRosterAppearanceTests.cs',
    'Assets/Tests/PlayMode/QdaoRosterAnimatorPlayModeTests.cs',
    'Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs',
)
# Bind the full HD dependency set and GUID-bearing metas, not only the old V13 core.
HD_CODE_PATHS = (
    'Assets/Scripts/World/QdaoOriginalHdResourceIndex.cs',
    'Assets/Scripts/World/QdaoHdResources.cs',
    'Assets/Scripts/World/QdaoHdSpriteLeaseOwner.cs',
    'Assets/Editor/QdaoOriginalHdResourceIndexBuilder.cs',
    'Assets/Scripts/UI/Ugui/Battle/BattleUnitView.cs',
    'Assets/Scripts/UI/Ugui/Battle/BattleFx.cs',
    'Assets/Tests/EditMode/Tianyong/QdaoOriginalHdAppearanceTests.cs',
    'Assets/Tests/PlayMode/QdaoHdResourceLifetimePlayModeTests.cs',
)
ALL_SOURCE_PATHS = tuple(dict.fromkeys(CODE_PATHS + HD_CODE_PATHS))
CODE_PATHS = ALL_SOURCE_PATHS + tuple(path + '.meta' for path in ALL_SOURCE_PATHS)
CONTROLLER = 'Assets/Scripts/World/Tianyong/TianyongPlayerController.cs'
EXPECTED_PNGS = {'portrait.png'} | {f'idle/{d}.png' for d in DIRECTIONS} | {
    f'walk/{d}/{i:02d}.png' for d in DIRECTIONS for i in range(1, 17)
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def bytes_sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def safe_child(root, relative):
    root = Path(root).resolve()
    fragment = Path(relative)
    require(not fragment.is_absolute() and '..' not in fragment.parts, 'Unsafe relative path: ' + str(relative))
    child = root / fragment
    require(child.resolve().is_relative_to(root), 'Path leaves permitted root: ' + str(child))
    current = child
    while current != root:
        require(not current.is_symlink() and not (hasattr(current, 'is_junction') and current.is_junction()),
                'Linked publication/input path is not supported: ' + str(current))
        current = current.parent
    return child


def inventory():
    record = read(ROOT / 'inventory.json')
    require(record.get('source_commit') == SOURCE_COMMIT and record.get('unique_character_count') == 23,
            'Restored inventory must be the user-selected 23-character commit')
    entries = record['characters']
    require(len(entries) == 23 and len({r['character_id'] for r in entries}) == 23, 'Inventory IDs are not unique')
    for index, entry in enumerate(entries):
        require(entry['character_id'].startswith(f'{index:02d}_') and entry['source_commit'] == SOURCE_COMMIT,
                'Original identity order/source commit changed')
    return {entry['character_id']: entry for entry in entries}


def approved_candidate(character, entry):
    out = safe_child(ROOT / 'candidate', character)
    manifest = read(out / 'manifest.json')
    require(manifest.get('status') == 'passed' and manifest.get('visual_review') == 'passed',
            'Candidate has not received final art approval')
    require(manifest.get('character_id') == character and manifest.get('version') == 14 and
            manifest.get('frame_count') == 16 and manifest.get('frame_duration_ms') == 30 and
            manifest.get('cycle_duration_ms') == 480 and manifest.get('dedicated_idle') is True and
            manifest.get('contact_frame') == 0, 'Wrong Original identity/timing/idle contract')
    require(manifest.get('frame_size') == [1024, 1024] and manifest.get('portrait_size') == [1024, 1024],
            'HD images must use the declared 1024-square contract')
    geometry = manifest.get('runtime_geometry', {})
    require(geometry.get('reference_frame_size') == 512 and geometry.get('pixels_per_unit') == 104 and
            geometry.get('pivot') == [0.5, 0.08], 'HD geometry must retain the old world size and pivot')
    alignment = manifest.get('alignment', {})
    require(alignment.get('alignment_version') == 2 and alignment.get('root_px') == [512, 942] and
            alignment.get('per_subject_bbox_scaling') is False, 'Original contract requires actual v2 feet alignment')
    files = {record['path']: record['sha256'] for record in manifest['files']}
    require(len(files) == len(manifest['files']) == 137 and set(files) == EXPECTED_PNGS,
            'Candidate must contain precisely 128 HD walk, eight HD idle and one portrait; no runtime strips')
    for relative, digest in files.items():
        require(sha(safe_child(out, relative)) == digest, 'Candidate image SHA changed: ' + relative)
    qc = read(out / 'qc.json')
    require(qc.get('status') == 'passed' and qc.get('visual_review') == 'passed' and qc.get('errors') == [],
            'QC must be passed with no errors')
    manifest_sha, qc_sha = sha(out / 'manifest.json'), sha(out / 'qc.json')
    visual_path = out / 'review/visual-review.json'
    visual = read(visual_path)
    require(visual.get('status') == 'passed' and visual.get('reviewed_manifest_sha256') == manifest_sha and
            visual.get('reviewed_qc_sha256') == qc_sha and visual.get('reviewed_artifacts') == files,
            'Visual approval is absent, stale or bound to different files')
    require(set(visual.get('reviewed_directions', [])) == set(DIRECTIONS) and
            set(visual.get('notes_by_direction', {})) == set(DIRECTIONS) and
            all(str(note).strip() for note in visual['notes_by_direction'].values()), 'Missing direction-specific visual review')
    for key in ('normal_size_review', 'enlarged_review', 'seam_15_16_01_review', 'anatomical_contacts_01_09_review', 'native_resolution_review', 'closeup_1080p_review'):
        require(visual.get(key) is True, 'Missing explicit visual review: ' + key)
    require(bool(visual.get('evidence')), 'Saved actual visual evidence is required')
    # approve.py seals the original review input into approval-history. Evidence paths
    # are resolved relative to that input (the reviewer may have saved it outside review/).
    history_inputs = sorted((out / 'review/approval-history').glob('*/fresh-review-input.json'))
    matching_inputs = [path for path in history_inputs if sha(path) == visual.get('review_input_sha256')]
    require(bool(matching_inputs), 'Sealed fresh visual review input is missing')
    original_review = read(matching_inputs[-1])
    require(original_review.get('reviewed_artifacts') == files, 'Sealed review input refers to other images')
    sealed_history = matching_inputs[-1].parent
    require(original_review.get('reviewed_input_manifest_sha256') == sha(sealed_history / 'manifest.json') and
            original_review.get('reviewed_input_qc_sha256') == sha(sealed_history / 'qc.json'),
            'Sealed review input does not match its pre-approval manifest/QC history')
    # Recheck the exact reviewed bytes. Relative evidence can live beside the
    # candidate review or its sealed history; never infer a pass from a missing file.
    for evidence in visual['evidence']:
        evidence_path = Path(evidence['path'])
        if evidence_path.is_absolute():
            require(evidence_path.is_file() and sha(evidence_path) == evidence['sha256'], 'Visual evidence changed or missing')
        else:
            candidates = [parent / evidence_path for parent in (out / 'review', matching_inputs[-1].parent, out, ROOT)]
            require(any(path.resolve().is_relative_to(ROOT.resolve()) and path.is_file() and
                        sha(path) == evidence['sha256'] for path in candidates),
                    'Relative visual evidence missing; retain its exact bytes beside review or use an absolute evidence path')
    portrait = read(out / 'processing/portrait-source.json')
    require(portrait.get('source_sha256') == entry['sha256'] == entry['git_manifest_sha256'] and
            sha(Path(entry['baseline_path'])) == entry['sha256'], 'Portrait is not bound to the restored original identity')
    validation_path = out / 'validation.json'
    saved = read(validation_path)
    require(saved.get('status') == 'passed' and saved.get('visual_review') == 'passed' and
            saved.get('scope') == 'all8' and saved.get('character_id') == character and saved.get('version') == 14 and
            saved.get('manifest_sha256') == manifest_sha and saved.get('qc_sha256') == qc_sha and
            saved.get('visual_review_sha256') == sha(visual_path), 'Saved final verification is missing or stale')
    specification = importlib.util.spec_from_file_location('original_publication_verify', ROOT / 'tools/verify.py')
    verifier = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(verifier)
    fresh = verifier.verify(character, require_visual=True)  # In-memory reconstruction; never writes validation/approval.
    for key in ('version', 'character_id', 'status', 'scope', 'manifest_sha256', 'qc_sha256', 'visual_review',
                'visual_review_sha256', 'missing_generation_receipts', 'direction_results', 'reconstructed_frames',
                'synthetic_frames_created'):
        require(fresh.get(key) == saved.get(key), 'Independent verification differs from saved receipt: ' + key)
    require(fresh['reconstructed_frames'] == 136 and fresh['synthetic_frames_created'] == 0 and
            fresh['missing_generation_receipts'] == [], 'Every runtime frame needs reconstructed real source provenance')
    sources = read(out / 'processing/frame-sources.json')
    require(len(sources) == 136, 'HD needs all136 walk/idle source records')
    for relative, record in sources.items():
        box = record['source']['cell_xyxy']
        require(box[2] - box[0] >= 1024 and box[3] - box[1] >= 1024 and record['whole_cell_scale'] <= 1,
                'Low-resolution or upscaled native cell is not HD: ' + relative)
    activation = {'version': 14, 'characterId': character, 'frameCount': 16, 'frameDurationMs': 30,
                  'cycleDurationMs': 480, 'alignmentVersion': 2, 'dedicatedIdle': True, 'contactFrame': 0,
                  'status': 'passed', 'visualReview': 'passed', 'manifest_sha256': manifest_sha,
                  'qc_sha256': qc_sha, 'validation_sha256': sha(validation_path), 'sourceCommit': SOURCE_COMMIT,
                  'sourceFamily': 'original-00-22'}
    activation.update({'frameWidth': 1024, 'frameHeight': 1024, 'portraitWidth': 1024,
                       'portraitHeight': 1024, 'pixelsPerUnit': 104, 'pivotX': 0.5, 'pivotY': 0.08})
    activation_bytes = encoded(activation)
    outputs = dict(files)
    outputs.update({'manifest.json': manifest_sha, 'validation.json': sha(validation_path),
                    'appearance.json': bytes_sha(activation_bytes)})
    return {'characterId': character, 'candidate': out, 'outputs': outputs, 'activation': activation,
            'activationBytes': activation_bytes, 'manifestSha256': manifest_sha,
            'qcSha256': qc_sha, 'validationSha256': sha(validation_path)}


def snapshot_records(snapshot):
    rows = snapshot['files']
    result = {row['path'].replace('\\', '/'): row for row in rows}
    require(len(result) == len(rows), 'Input snapshot contains duplicate paths')
    return result


def check_results(path, required_suffix):
    require(path is not None and Path(path).is_file(), 'Unity result XML is required')
    result = ET.parse(path).getroot()
    require(result.get('result') == 'Passed' and int(result.get('failed', '1')) == 0 and int(result.get('passed', '0')) > 0,
            'Unity result is not wholly passed')
    require(any(test.get('result') == 'Passed' and test.get('fullname', '').endswith(required_suffix)
                for test in result.iter('test-case')), 'Required actual Unity test was not passed: ' + required_suffix)


def check_launch_binding(xml_path, report, rows, plans, expected_snapshot_sha=None):
    xml_path = Path(xml_path)
    launch_path = xml_path.with_name(xml_path.stem + '-launch.json')
    launch = read(launch_path)
    launched_snapshot_path = Path(launch['input_snapshot'])
    launched_snapshot_sha = sha(launched_snapshot_path)
    require(launch.get('input_snapshot_sha256') == launched_snapshot_sha,
            'Unity launch record input snapshot SHA is stale')
    if expected_snapshot_sha is not None:
        require(launched_snapshot_sha == expected_snapshot_sha, 'PlayMode XML launch belongs to another input snapshot')
    launched_snapshot = read(launched_snapshot_path)
    require(Path(launch['project']).resolve() == Path(report['projectPath']).resolve() ==
            Path(launched_snapshot['project']).resolve(), 'Unity XML launch belongs to another project')
    launch_rows = snapshot_records(launched_snapshot)
    for relative in CODE_PATHS:
        require(relative in launch_rows and launch_rows[relative]['sha256'] == rows[relative]['sha256'],
                'Unity result source differs from observed source: ' + relative)
    for plan in plans:
        for relative, digest in plan['outputs'].items():
            key = FAMILY + '/' + plan['characterId'] + '/' + relative
            require(key in launch_rows and launch_rows[key]['sha256'] == digest,
                    'Unity result was not run against this candidate: ' + key)
    if expected_snapshot_sha is not None:
        result = ET.parse(xml_path).getroot()
        generated = datetime.fromisoformat(report['generatedUtc'].replace('Z', '+00:00'))
        start = datetime.fromisoformat(result.attrib['start-time'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(result.attrib['end-time'].replace('Z', '+00:00'))
        require(start.timestamp() <= generated.timestamp() <= end.timestamp() + 1,
                'Runtime observation timestamp is outside the supplied PlayMode test run')


def near(actual, expected, tolerance, label):
    require(isinstance(actual, (int, float)) and abs(actual - expected) <= tolerance, label + ' differs')


def runtime_acceptance(plans, project, arguments):
    require(arguments.runtime_report and arguments.input_snapshot, 'Publish needs actual runtime report and input snapshot')
    report, snapshot = read(arguments.runtime_report), read(arguments.input_snapshot)
    require(report.get('schemaVersion') == 2 and report.get('behaviorAssertionsCompleted') is True,
            'A complete generic Original runtime observation is required')
    require(report.get('inputSnapshotSha256') == sha(arguments.input_snapshot), 'Runtime report is bound to another snapshot')
    require(Path(report['inputSnapshotPath']).resolve() == arguments.input_snapshot.resolve() and
            Path(report['projectPath']).resolve() == Path(snapshot['project']).resolve(), 'Runtime project/input identity differs')
    rows = snapshot_records(snapshot)
    for relative in CODE_PATHS:
        require(relative in rows and sha(safe_child(project, relative)) == rows[relative]['sha256'],
                'Destination source differs from the actually tested code: ' + relative)
    check_results(arguments.editmode_results, 'QdaoOriginalAppearanceTests.OriginalRegistryKeepsTwentyThreeIndependentIdsAndDoesNotRewriteExistingRosterOrLegacy')
    check_results(arguments.playmode_results, 'QdaoRosterSandboxPlayModeTests.RealCitySandbox_SwitchesAllAvailableAppearancesWithoutReplacingThePlayer_AndWalksWithTheRealMotor')
    check_results(arguments.playmode_results, 'QdaoRosterAnimatorPlayModeTests.EveryCharacter_WalksItsDeclaredFramesInAllEightDirections_AndSettlesOnItsIdlePose')
    check_launch_binding(arguments.editmode_results, report, rows, plans)
    check_launch_binding(arguments.playmode_results, report, rows, plans, sha(arguments.input_snapshot))
    baseline, baseline_snapshot = read(arguments.baseline_report), read(arguments.baseline_snapshot)
    require(baseline.get('behaviorAssertionsCompleted') is True and baseline.get('inputSnapshotSha256') == sha(arguments.baseline_snapshot),
            'Speed baseline is not bound to its actual completed run')
    old = next((actor for actor in baseline['appearances'] if actor['actualCharacterId'] == '24_lu_dongbin'), None)
    require(old and old['actualArtworkVersion'] == 12 and old['actualFrameCount'] == 8 and
            old['movementObserved'] and old['stoppedIdle'] and old['realMotorEnabled'], 'Actual V12 motor baseline is required')
    require(snapshot_records(baseline_snapshot)[CONTROLLER]['sha256'] == rows[CONTROLLER]['sha256'],
            'Movement controller changed from the actual V12 baseline')
    originals = [actor for actor in report['appearances'] if actor.get('actualIsOriginalRoster') is True]
    require(report.get('testedOriginalCount') == len(originals) and len(originals) >= len(plans),
            'Not every reported/selected Original completed a real motor route')
    hd_originals = [actor for actor in originals if actor.get('actualIsHd') is True and actor.get('actualArtworkVersion') == 14]
    require(report.get('testedHdOriginalCount') == len(hd_originals) and len(hd_originals) >= len(plans),
            'HD0 or mismatched HD counts cannot authorize publication')
    for plan in plans:
        character = plan['characterId']
        matches = [actor for actor in originals if actor.get('requestedCharacterId') == actor.get('actualCharacterId') == character]
        require(len(matches) == 1, 'Missing or duplicated actual Original observation: ' + character)
        actor = matches[0]
        require(actor.get('resourceFolder') == RESOURCE_FAMILY + '/' + character and
                actor.get('actualArtworkVersion') == actor.get('catalogVersion') == 14 and actor.get('actualFrameCount') == 16 and
                actor.get('catalogFrameDurationMs') == 30 and actor.get('activationAlignmentVersion') == 2 and
                actor.get('activationContactFrame') == 0 and actor.get('actualFramesMatchResources') is True,
                'Actual Original identity/version/contract differs: ' + character)
        require(actor.get('actualIsHd') is True and actor.get('v14HdContractObserved') is True and
                actor.get('actualFrameWidth') == 1024 and actor.get('actualFrameHeight') == 1024,
                'Actual loaded V14 HD frame geometry was not observed')
        near(actor.get('actualPixelsPerUnit'), 104, .0001, 'HD pixels per world unit')
        near(actor.get('actualFrameWorldHeight'), 512 / 52, .0001, 'Unchanged HD world frame height')
        pivot = actor.get('actualNormalizedPivot', {})
        scale = actor.get('actualBillboardScale', {})
        require(pivot == {'x': 0.5, 'y': 0.08} or
                isinstance(pivot, dict) and abs(pivot.get('x', 0)-.5)<.0001 and abs(pivot.get('y', 0)-.08)<.0001,
                'Actual normalized HD feet pivot differs')
        require(isinstance(scale, dict) and all(abs(scale.get(k, 0)-1)<.0001 for k in ('x','y','z')),
                'HD billboard scale changed')
        for name in ('actualTextureWidthsPerDirection', 'actualTextureHeightsPerDirection'):
            require(actor.get(name) == {d: 1024 for d in DIRECTIONS}, 'Actual sequential HD texture inventory differs: '+name)
        require(1 <= actor.get('maxResidentHdDirectionsObserved', 0) <= 2,
                'HD runtime did not demonstrate bounded direction residency')
        require(actor.get('normalView') and actor.get('nearestView'), 'Actual normal and closest-camera captures are required')
        # A V14 index is derived from the tested project GUIDs. It must exist in the Play input;
        # it is rebuilt in the formal Editor and is not copied by this authored-file publisher.
        index_key = FAMILY + '/' + character + '/runtime-index.asset'
        require(index_key in rows and index_key + '.meta' in rows, 'Tested HD resource index is missing')
        require(actor.get('activationSha256') == plan['outputs']['appearance.json'] and
                actor.get('manifestPresent') is True and actor.get('manifestSha256') == plan['manifestSha256'] and
                actor.get('activationManifestSha256') == plan['manifestSha256'] and
                actor.get('activationQcSha256') == plan['qcSha256'] and
                actor.get('activationValidationSha256') == plan['validationSha256'], 'Runtime candidate SHA differs: ' + character)
        for key in ('actualFramesPerDirection', 'actualUniqueFrameSpritesPerDirection', 'actualUniqueFrameTexturesPerDirection'):
            require(actor.get(key) == {direction: 16 for direction in DIRECTIONS}, 'Loaded 8x16 inventory differs: ' + key)
        for key in ('actualHasDedicatedIdle', 'spriteMatchesDedicatedIdle', 'movementObserved', 'stoppedIdle', 'realMotorEnabled'):
            require(actor.get(key) is True, 'Real Original motor/idle assertion missing: ' + key)
        require(actor.get('actualTravelDistance', 0) > 3 and actor.get('actualPathDistance', 0) > 3 and
                actor.get('movementSeconds', 0) > .48 and actor.get('observedWalkPoseCount') == 16,
                'Actual Original route did not cover all 16 poses')
        sampled = actor.get('sampledPosesPerDirection', {})
        require(set(sampled) == set(DIRECTIONS) and sum(sampled.values()) == 16 and max(sampled.values()) == 16,
                'The single real route must separately report its actual sampled direction')
        near(actor.get('controllerMoveSpeed'), old['controllerMoveSpeed'], .0001, 'Movement speed configuration')
        near(actor.get('actualCycleDurationMs'), old['actualCycleDurationMs'], .01, '480ms cycle')
        near(actor.get('actualCycleWorldDistance'), old['actualCycleWorldDistance'], .0001, 'Cycle world distance')
        near(actor.get('actualFramesPerUnit'), old['actualFramesPerUnit'] * 2, .0001, '16-pose distance cadence')
        near(actor['actualPathDistance'] / actor['movementSeconds'], actor['controllerMoveSpeed'], .15, 'Actual travel speed')
        for relative, digest in plan['outputs'].items():
            key = FAMILY + '/' + character + '/' + relative
            require(key in rows and rows[key]['sha256'] == digest, 'Runtime snapshot contains another candidate file: ' + key)
    return {'runtimeReportSha256': sha(arguments.runtime_report), 'inputSnapshotSha256': sha(arguments.input_snapshot),
            'editmodeResultsSha256': sha(arguments.editmode_results), 'playmodeResultsSha256': sha(arguments.playmode_results),
            'testedOriginalCount': report['testedOriginalCount'], 'testedHdOriginalCount': report['testedHdOriginalCount'], 'baselineReportSha256': sha(arguments.baseline_report)}


def target_project(path, stage):
    project = Path(path).resolve()
    require((project / 'Assets').is_dir() and (project / 'ProjectSettings/ProjectVersion.txt').is_file(), 'Target is not a Unity project')
    if stage:
        require(project.is_relative_to((WORK / 'tmp').resolve()), 'Staging is restricted to an independent E:/work/tmp Unity project')
    safe_child(project, FAMILY)
    return project


def target_state(project, plan):
    target = safe_child(project, FAMILY + '/' + plan['characterId'])
    if not target.exists():
        return target, 'new'
    require(target.is_dir(), 'Target exists and is not a directory')
    files = {path.relative_to(target).as_posix(): sha(safe_child(target, path.relative_to(target)))
             for path in target.rglob('*') if path.is_file() and not path.name.endswith('.meta') and path.name != 'runtime-index.asset'}
    require(files == plan['outputs'], 'Existing Original revision differs; preserve/archive it explicitly before replacement: ' + str(target))
    return target, 'already_identical'


def execute(plans, project, audit):
    require(not (project / 'Temp/UnityLockfile').exists(), 'Close the target Unity instance before resource publication')
    for plan in plans:
        target, state = target_state(project, plan)
        if state == 'already_identical':
            continue
        staging = safe_child(project, 'Temp/QdaoOriginalRosterV14-' + uuid.uuid4().hex + '/' + plan['characterId'])
        staging.mkdir(parents=True)
        audit['writesPerformed'] = True
        audit['stagingPaths'].append(str(staging))
        for relative, digest in plan['outputs'].items():
            destination = safe_child(staging, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == 'appearance.json':
                destination.write_bytes(plan['activationBytes'])
            else:
                shutil.copy2(safe_child(plan['candidate'], relative), destination)
            require(sha(destination) == digest, 'Input changed during staging: ' + relative)
        # Both fully resolved paths are checked inside this project immediately before
        # the rename. No existing character directory is deleted or overwritten.
        require(staging.resolve().is_relative_to((project / 'Temp').resolve()), 'Unsafe staging directory')
        require(target.resolve().is_relative_to(safe_child(project, FAMILY).resolve()) and not target.exists(), 'Target changed during staging')
        target.parent.mkdir(parents=True, exist_ok=True)
        staging.rename(target)
        audit['promotedTargets'].append(str(target))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--character', action='append', help='Exact original ID; repeat to select several; default checks all 23')
    destinations = parser.add_mutually_exclusive_group()
    destinations.add_argument('--stage-project', type=Path, help='Independent E:/work/tmp Unity project; no actual-run evidence needed to stage approved art')
    destinations.add_argument('--publish-project', type=Path, help='Formal destination; requires matching real Original runtime evidence')
    parser.add_argument('--execute', action='store_true', help='Explicitly perform validated copy; absent means zero filesystem writes')
    parser.add_argument('--runtime-report', type=Path)
    parser.add_argument('--input-snapshot', type=Path)
    parser.add_argument('--editmode-results', type=Path)
    parser.add_argument('--playmode-results', type=Path)
    parser.add_argument('--baseline-report', type=Path, default=ROOT.parent / 'qdao_original_roster_v13/runtime-validation/contract-run1/city-captures/runtime-observed-appearances.json')
    parser.add_argument('--baseline-snapshot', type=Path, default=ROOT.parent / 'qdao_original_roster_v13/runtime-validation/input-snapshot-run1-playmode.json')
    arguments = parser.parse_args(argv)
    audit = {'schema': 'qdao-original-roster-v14-hd/publication-v1', 'createdUtc': datetime.now(timezone.utc).isoformat(),
             'mode': 'publish' if arguments.publish_project else 'stage' if arguments.stage_project else 'check',
             'dryRun': not arguments.execute, 'writesPerformed': False, 'promotedTargets': [], 'stagingPaths': [],
             'sourceCommit': SOURCE_COMMIT, 'resourceFamily': RESOURCE_FAMILY, 'candidates': [], 'blocked': []}
    try:
        entries = inventory()
        selected = arguments.character or list(entries)
        require(len(selected) == len(set(selected)) and all(character in entries for character in selected), 'Use unique exact Original 00-22 IDs; aliases and Lu IDs are not accepted')
        plans = []
        for character in selected:
            try:
                plan = approved_candidate(character, entries[character]);plans.append(plan)
                audit['candidates'].append({'characterId': character, 'pngCount': 137, 'resourceFileCount': len(plan['outputs']),
                                            'appearanceSha256': plan['outputs']['appearance.json'], 'manifestSha256': plan['manifestSha256'],
                                            'qcSha256': plan['qcSha256'], 'validationSha256': plan['validationSha256']})
            except (ValueError, OSError, KeyError, TypeError) as error:
                audit['blocked'].append({'characterId': character, 'error': str(error)})
        require(not audit['blocked'], 'Every selected character must have complete genuine artwork, final approval and independent verification')
        destination = arguments.publish_project or arguments.stage_project
        require(not arguments.execute or destination is not None, '--execute requires an explicit stage or publish Unity project')
        project = target_project(destination, arguments.stage_project is not None) if destination else None
        if project:
            audit['targetProject'] = str(project)
            for plan in plans:
                target, state = target_state(project, plan)
                audit['candidates'][plans.index(plan)].update({'target': str(target), 'targetState': state})
        if arguments.publish_project:
            audit['runtimeAcceptance'] = runtime_acceptance(plans, project, arguments)
        if arguments.execute:
            execute(plans, project, audit)
        audit['status'] = 'completed' if arguments.execute else 'ready_dry_run'
        return audit, 0
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        audit['status'] = 'blocked'
        audit['error'] = str(error)
        return audit, 1


if __name__ == '__main__':
    result, code = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(code)
