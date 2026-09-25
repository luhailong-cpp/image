"""Package only a complete, SHA-bound, explicitly accepted character-09 snapshot.

This program never deletes images. Historical evidence bytes are preserved;
cleanup-plan.json is an inventory for a later, separately verified cleanup.
"""
import argparse
import copy
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

from common import CHARACTER, DELIVERY, DIRS, GENERATION, IMAGE_ROOT, read_json, sha


CHECKS = (
    'gait', 'supportFoot', 'anchor', 'proportions', 'equipment', 'alpha',
    'seam15_16_01_02', 'dark', 'light', 'normalSize', 'enlarged', 'browserPlayback',
)
TEXT_EXTENSIONS = {'.json', '.jsonl', '.txt', '.md', '.log', '.csv', '.tsv',
                   '.yaml', '.yml', '.toml', '.html', '.htm'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tif', '.tiff'}
EXPECTED_KEYS = {f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1, 17)} | {
    f'idle/{d}.png' for d in DIRS}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inside(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    require(path.is_relative_to(root), f'Path escapes allowed character-09 scope: {path}')
    return path


def regular_files(root):
    root = Path(root)
    if not root.exists():
        return []
    require(not root.is_symlink() and not getattr(root, 'is_junction', lambda: False)(),
            f'Linked directory root is not supported: {root}')
    files = []
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink() and not getattr(path, 'is_junction', lambda: False)(),
                f'Linked path is not supported: {path}')
        inside(path, root)
        if path.is_file():
            files.append(path)
    return files


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_exact(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    require(not target.exists(), f'Destination already exists: {target}')
    shutil.copy2(source, target)
    require(sha(source) == sha(target), f'Copied bytes differ: {target}')


def validate_acceptance(record, manifest_sha):
    require(record.get('character') == CHARACTER, 'Acceptance is for another character')
    require(record.get('status') == 'passed', 'Explicit offline acceptance status must be passed')
    require(record.get('reviewedManifestSha256') == manifest_sha,
            'Acceptance must bind the exact supplied snapshot manifest SHA256')
    require(isinstance(record.get('reviewer'), str) and record['reviewer'].strip(), 'Missing reviewer')
    require(isinstance(record.get('reviewedAt'), str), 'Missing review timestamp')
    stamp = datetime.fromisoformat(record['reviewedAt'].replace('Z', '+00:00'))
    require(stamp.tzinfo is not None, 'Review timestamp must include a timezone')
    directions = record.get('directions', {})
    require(set(directions) == set(DIRS), 'Acceptance must cover exactly eight directions')
    for direction in DIRS:
        item = directions[direction]
        require(item.get('status') == 'passed', f'{direction} has not passed visual review')
        require(item.get('walkCount') == 16 and item.get('idleCount') == 1,
                f'{direction} acceptance does not cover 16 walk + 1 independent idle')
        checks = item.get('checks', {})
        for check in CHECKS:
            require(checks.get(check) == 'passed', f'{direction}: missing passed check {check}')
    require(record.get('clientIntegration', 'not_performed') == 'not_performed',
            'This offline packager cannot certify client integration')


def validate_snapshot(snapshot):
    snapshot = inside(snapshot, DELIVERY / 'revisions')
    require(snapshot.is_dir(), 'Snapshot directory does not exist')
    manifest_path = snapshot / 'manifest.json'
    manifest = read_json(manifest_path)
    require(manifest.get('character') == CHARACTER, 'Wrong character in manifest')
    require(manifest.get('walkCount') == 128 and manifest.get('idleCount') == 8,
            'Snapshot is incomplete: require 128 walk + 8 independent idle')
    require(not manifest.get('missing'), 'Snapshot still lists missing slots')
    require(manifest.get('frameSize') == [1024, 1024], 'Incorrect frame size contract')
    require(manifest.get('frameDurationMs') == 30 and manifest.get('cycleMs') == 480,
            'Preview contract must be 30ms/frame, 480ms/cycle')
    files = manifest.get('files', [])
    require(len(files) == 136 and {item.get('key') for item in files} == EXPECTED_KEYS,
            'Manifest must contain exactly the 136 expected unique slots')
    actual_pngs = {p.relative_to(snapshot / 'runtime').as_posix()
                   for p in regular_files(snapshot / 'runtime') if p.suffix.lower() == '.png'}
    require(actual_pngs == EXPECTED_KEYS, 'Runtime contains missing or unexpected PNGs')
    validated, source_shas, pixel_shas, mirrored_shas = [], [], [], []
    for item in files:
        key = item['key']
        require(item.get('path') == 'runtime/' + key, f'Nonportable runtime path: {key}')
        require(item.get('sourceRecord') == 'sources/' + key + '.json', f'Unexpected source record: {key}')
        png = inside(snapshot / item['path'], snapshot)
        source_path = inside(snapshot / item['sourceRecord'], snapshot)
        sidecar_path = png.with_name(png.name + '.generation.json')
        source, sidecar = read_json(source_path), read_json(sidecar_path)
        require(sha(png) == item['sha256'] == source['outputSha256'] == sidecar['sha256'],
                f'Output SHA disagreement: {key}')
        require(source.get('character') == CHARACTER and source.get('outputRelative') == key,
                f'Source record slot/identity disagreement: {key}')
        operation = source.get('operation', {})
        require(operation.get('mirrored') is False and operation.get('poseInterpolated') is False
                and operation.get('perSubjectBboxScaling') is False,
                f'Prohibited or undocumented pose/scale manipulation: {key}')
        require(0 < operation.get('wholeCellScale', 0) <= 1,
                f'Upscaling or missing scale evidence: {key}')
        raw = inside(source['source']['path'], GENERATION)
        generation_path = inside(source['source']['generationRecord'], GENERATION)
        generation = read_json(generation_path)
        raw_sha = sha(raw)
        require(raw_sha == item['sourceSha256'] == source['source']['sha256'] == generation['sha256'],
                f'Native source SHA disagreement: {key}')
        require(sha(generation_path) == source['source']['generationRecordSha256'],
                f'Generation record changed since export: {key}')
        require(generation.get('route') == 'builtin' and generation.get('paidApiCalls') == 0,
                f'Require truthful built-in source evidence: {key}')
        for field in ('actualModel', 'actualQuality', 'submittedParameters', 'configSnapshot'):
            require(sidecar.get(field) == generation.get(field), f'Version evidence differs: {key}/{field}')
        # Unknown model/quality stays null; no configuration-to-result backfilling.
        for filename in ('request.json', 'tool-result.json', 'generation.json',
                         'generation-receipt.json', 'prompt.txt'):
            require((generation_path.parent / filename).is_file(), f'Missing exact generation evidence: {key}/{filename}')
        with Image.open(raw) as native:
            require(min(native.size) >= 1024, f'Native source is below 1024: {key}')
            require(list(native.size) == item['nativeSize'] == source['nativeSize'], f'Native size differs: {key}')
        with Image.open(png) as image:
            require(image.mode == 'RGBA' and image.size == (1024, 1024), f'PNG contract failed: {key}')
            alpha = image.getchannel('A')
            require(alpha.getextrema() == (0, 255), f'Require transparent background and opaque subject: {key}')
            for box in ((0, 0, 1024, 1), (0, 1023, 1024, 1024),
                        (0, 0, 1, 1024), (1023, 0, 1024, 1024)):
                require(alpha.crop(box).getextrema()[1] == 0, f'Nontransparent canvas boundary: {key}')
            pixel_shas.append(hashlib.sha256(image.tobytes()).hexdigest())
            mirrored_shas.append(hashlib.sha256(ImageOps.mirror(image).tobytes()).hexdigest())
        source_shas.append(raw_sha)
        validated.append({'item': item, 'source': source, 'generation': generation,
                          'generationPath': generation_path, 'rawPath': raw})
    require(len(set(source_shas)) == 136, 'Repeated native source across slots')
    require(len(set(pixel_shas)) == 136 and not set(pixel_shas).intersection(mirrored_shas),
            'Duplicate or mirrored output pixels found')
    gif_records = {item['path']: item for item in manifest.get('gifs', [])}
    for direction in DIRS:
        for background in ('dark', 'light'):
            for suffix in ('contact.png', 'seam.png', '30ms.gif'):
                relative = f'preview/{direction}-{background}-{suffix}'
                path = inside(snapshot / relative, snapshot)
                require(path.is_file(), f'Missing required preview: {relative}')
                if suffix == '30ms.gif':
                    with Image.open(path) as gif:
                        durations = []
                        for frame in range(gif.n_frames):
                            gif.seek(frame)
                            durations.append(gif.info.get('duration'))
                        require(durations == [30] * 16 and gif.info.get('loop') == 0,
                                f'GIF must loop 16 frames at 30ms each: {relative}')
                    require(relative in gif_records and sha(path) == gif_records[relative]['sha256'],
                            f'GIF is not bound to the reviewed manifest: {relative}')
    for background in ('dark', 'light'):
        require((snapshot / f'preview/idle-{background}.png').is_file(), 'Missing idle overview')
    require((snapshot / 'index.html').is_file(), 'Missing offline preview HTML')
    return snapshot, manifest, validated


def collect_evidence():
    evidence = []
    roots = [(GENERATION, 'generation')]
    for name in ('work', 'revisions', 'east-qa', 'qa-independent'):
        root = DELIVERY / name
        if root.exists():
            roots.append((root, 'processing/' + name))
    for root, category in roots:
        for path in regular_files(root):
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            path.read_bytes().decode('utf-8-sig')  # Refuse binary payloads posing as text evidence.
            evidence.append((path, 'evidence/' + category + '/' + path.relative_to(root).as_posix()))
    return evidence


def cleanup_inventory():
    # No outside portrait, approved shared design, other character, or host cache is eligible.
    entries = {}
    for path in regular_files(GENERATION):
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            entries[path] = '09 generation original/reject/working reference image'
    for name in ('work', 'revisions'):
        for path in regular_files(DELIVERY / name):
            entries[path] = '09 processing/snapshot duplicate after final copy and text preservation'
    for name in ('east-qa', 'qa-independent'):
        for path in regular_files(DELIVERY / name):
            if path.suffix.lower() in IMAGE_EXTENSIONS or path.suffix.lower() in {'.html', '.htm'}:
                entries[path] = '09 diagnostic image/temporary preview superseded by final preview'
    for path in DELIVERY.iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            entries[path] = '09 temporary diagnostic image superseded by final preview'
    result = []
    for path, reason in sorted(entries.items()):
        path = inside(path, IMAGE_ROOT)
        require(path.is_relative_to(GENERATION.resolve()) or path.is_relative_to(DELIVERY.resolve()),
                'Cleanup proposal escapes character 09')
        result.append({'path': str(path), 'projectRelativePath': path.relative_to(IMAGE_ROOT).as_posix(),
                       'sha256': sha(path), 'bytes': path.stat().st_size,
                       'reason': reason, 'action': 'proposed_delete_only', 'deleted': False})
    return result


def package(snapshot, acceptance_path, check_only=False):
    snapshot, manifest, validated = validate_snapshot(snapshot)
    manifest_sha = sha(snapshot / 'manifest.json')
    acceptance_path = inside(acceptance_path, IMAGE_ROOT)
    acceptance = read_json(acceptance_path)
    validate_acceptance(acceptance, manifest_sha)
    evidence = collect_evidence()
    cleanup = cleanup_inventory()
    if check_only:
        return {'status': 'validated_only', 'snapshot': str(snapshot), 'walk': 128, 'idle': 8,
                'evidenceTextFiles': len(evidence), 'proposedCleanupFiles': len(cleanup), 'deletedFiles': 0}
    final = inside(DELIVERY / 'final', DELIVERY)
    require(not final.exists(), 'final already exists; this tool never overwrites an accepted package')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    staging = inside(DELIVERY / ('final-staging-' + stamp), DELIVERY)
    require(not staging.exists(), 'Staging path already exists')
    staging.mkdir()
    # A failed build remains an explicit staging directory, never a falsely final directory.
    for name in ('runtime', 'sources', 'preview'):
        for source in regular_files(snapshot / name):
            copy_exact(source, staging / name / source.relative_to(snapshot / name))
    copy_exact(acceptance_path, staging / 'acceptance.json')
    copy_exact(snapshot / 'manifest.json', staging / 'evidence/reviewed-snapshot-manifest.json')
    copy_exact(snapshot / 'index.html', staging / 'evidence/reviewed-snapshot-index.html')
    evidence_index = []
    path_mapping = {}
    for source, relative in evidence:
        copy_exact(source, staging / relative)
        entry = {'historicalPath': str(source.resolve()), 'packagedPath': relative,
                 'sha256': sha(source), 'bytes': source.stat().st_size, 'kind': 'exact_historical_text'}
        evidence_index.append(entry)
        path_mapping[str(source.resolve())] = relative
    write_json(staging / 'evidence/index.json', {'pathsAreHistorical': True, 'files': evidence_index})
    image_index = []
    for row in validated:
        generation = row['generation']
        image_index.append({'key': row['item']['key'], 'runtimePath': row['item']['path'],
                            'sha256': row['item']['sha256'], 'sourceRecord': row['item']['sourceRecord'],
                            'generationEvidence': path_mapping[str(row['generationPath'].resolve())],
                            'nativeSha256': generation['sha256'], 'nativeSize': row['item']['nativeSize'],
                            'actualModel': generation['actualModel'], 'actualQuality': generation['actualQuality'],
                            'unverifiedReason': generation.get('unverifiedReason'),
                            'configSnapshot': generation['configSnapshot']})
    write_json(staging / 'sources/index.json', {'character': CHARACTER, 'images': image_index,
               'historicalStatusNotice': 'Original source/sidecar review fields describe export time. Current offline acceptance is acceptance.json.'})
    retention = {'character': CHARACTER, 'createdAt': datetime.now(timezone.utc).isoformat(),
                 'policy': 'User 2026-09-23: retain final game images/design/integration files and textual provenance; remove original/rejected/rollback/intermediate images after final copy and reference verification.',
                 'imageDeletionExecutedByThisProgram': False,
                 'sourceImagesInFinalPackage': False,
                 'originalImageStatusAtPackaging': 'Still in source locations; proposed for later authorized cleanup, not deleted by packager.',
                 'historicalPathsNotice': 'Historical request/result/generation/source text is copied byte-for-byte. Old paths describe where generation and processing happened, not a promise that raw files will remain readable after cleanup. Use evidence/index.json for local textual mappings.',
                 'nativeImages': [{'historicalPath': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size,
                                   'existsAtPackaging': True, 'plannedRemoval': True, 'deleted': False}
                                  for p in regular_files(GENERATION) if p.suffix.lower() in IMAGE_EXTENSIONS],
                 'clientIntegration': 'not_performed'}
    write_json(staging / 'retention.json', retention)
    cleanup_plan = {'character': CHARACTER, 'createdAt': retention['createdAt'], 'execution': 'not_executed',
                    'allowedRoots': [str(GENERATION.resolve()), str(DELIVERY.resolve())],
                    'excluded': [str(final), 'External original portrait', 'Approved shared designs', 'All other characters',
                                 'Host generated_images cache', '09-tools', '09-generation textual provenance'],
                    'prerequisites': ['Verify final manifest/runtime/preview references and package checksums again.',
                                      'No active generation may still reference an image scheduled for deletion.',
                                      'Re-resolve every exact path under the allowed roots and verify listed SHA before deletion.',
                                      'Preserve historical text via evidence/index.json; record actual cleanup time and result separately.'],
                    'files': cleanup}
    write_json(staging / 'cleanup-plan.json', cleanup_plan)
    packaged = copy.deepcopy(manifest)
    packaged.update({'packageRole': 'final_offline_assets', 'packagedAt': retention['createdAt'],
                     'reviewedSnapshotManifestSha256': manifest_sha,
                     'offlineAcceptance': {'status': acceptance['status'], 'record': 'acceptance.json',
                                           'sha256': sha(acceptance_path), 'reviewer': acceptance['reviewer']},
                     'visualReview': acceptance['status'],
                     'formalApproval': False,
                     'formalApprovalNote': 'Offline agent review only; no separate user/client approval is inferred.',
                     'sourcePathsAreHistorical': True, 'textEvidenceIndex': 'evidence/index.json',
                     'imageVersionIndex': 'sources/index.json', 'retentionRecord': 'retention.json',
                     'unityValidation': 'not_performed', 'clientValidation': 'not_performed'})
    write_json(staging / 'manifest.json', packaged)
    # Retain the already reviewed player code; replace only its embedded metadata/status.
    html = (snapshot / 'index.html').read_text(encoding='utf-8')
    embedded = json.dumps(manifest, ensure_ascii=False)
    require(html.count(embedded) == 1, 'Snapshot HTML does not contain the exact reviewed manifest once')
    html = html.replace(embedded, json.dumps(packaged, ensure_ascii=False), 1)
    html = re.sub(r'<p id="qa">.*?</p>', '<p id="qa">本快照离线审阅记录已通过；详见 <a href="acceptance.json">绑定 SHA 的验收记录</a>。客户端接入未执行。</p>', html, count=1)
    (staging / 'index.html').write_text(html, encoding='utf-8')
    readme = ['# 09 竹弓少女 · 最终离线素材包', '',
              '128 张行走（8 方向 × 16）及 8 张独立站立，均为 1024×1024 透明 PNG。',
              '直接打开 [index.html](index.html) 审阅；全部图片使用包内相对路径，无需原图或网络。',
              '循环为 30 毫秒/帧、480 毫秒/圈。离线通过依据见 [acceptance.json](acceptance.json)，客户端和 Unity 接入未执行。', '',
              '| 方向 | 浅底循环 | 深底循环 | 联系表 | 首尾 |', '|---|---|---|---|---|']
    for d in DIRS:
        readme.append(f'| {d} | [GIF](preview/{d}-light-30ms.gif) | [GIF](preview/{d}-dark-30ms.gif) | [16帧](preview/{d}-light-contact.png) | [15→16→01→02](preview/{d}-light-seam.png) |')
    readme += ['', '逐图实际模型、质量和来源映射见 [sources/index.json](sources/index.json)。工具未披露的字段仍为 null；配置目标不能替代实际版本证据。',
               '历史请求、回执、精确提示词、生成记录与加工记录保持原字节，见 [evidence/index.json](evidence/index.json)。原记录里的 pending/canPublish 字段是当时状态；本次验收单独保存在 acceptance.json。',
               '本包不含生成原图。源目录原图仍待收尾清理，当前状态见 [retention.json](retention.json)；[cleanup-plan.json](cleanup-plan.json) 仅为清单，本工具不执行删除。',
               '历史绝对路径不伪改为不存在的包内图片路径。清理后，可用哈希与文字证据追溯，但不能声称仍可读取原图重新验像素。', '']
    (staging / 'README.md').write_text('\n'.join(readme), encoding='utf-8')
    checksums = {p.relative_to(staging).as_posix(): sha(p) for p in regular_files(staging)}
    write_json(staging / 'package-checksums.json', {'algorithm': 'sha256', 'files': checksums,
                                                  'selfExcluded': 'package-checksums.json'})
    for relative, digest in checksums.items():
        require(sha(staging / relative) == digest, 'Package bytes changed before publication: ' + relative)
    require({p.relative_to(staging / 'runtime').as_posix() for p in regular_files(staging / 'runtime')
             if p.suffix.lower() == '.png'} == EXPECTED_KEYS, 'Final runtime inventory differs')
    for row in validated:
        item = row['item']
        require(sha(staging / item['path']) == item['sha256'], 'Final sprite differs from reviewed SHA: ' + item['key'])
        require(sha(staging / item['sourceRecord']) == sha(snapshot / item['sourceRecord']),
                'Historical source record was changed during packaging: ' + item['key'])
    require(sha(snapshot / 'manifest.json') == manifest_sha, 'Reviewed manifest changed during packaging')
    require(sha(staging / 'acceptance.json') == sha(acceptance_path), 'Acceptance changed during packaging')
    # Both fully resolved paths were checked inside this character's delivery root above.
    require(not final.exists(), 'Another process created final; preserve this staging directory for inspection')
    staging.rename(final)
    return {'status': 'packaged_from_explicit_acceptance', 'final': str(final), 'walk': 128, 'idle': 8,
            'manifestSha256': sha(final / 'manifest.json'), 'evidenceTextFiles': len(evidence),
            'proposedCleanupFiles': len(cleanup), 'deletedFiles': 0, 'clientIntegration': 'not_performed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path,
                        help='Complete build_review snapshot under 09-delivery-preview/revisions')
    parser.add_argument('--acceptance', required=True, type=Path,
                        help='Explicit per-direction offline acceptance bound to snapshot manifest SHA')
    parser.add_argument('--check-only', action='store_true', help='Validate without creating final or staging')
    args = parser.parse_args()
    try:
        result = package(args.snapshot, args.acceptance, args.check_only)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, 'REFUSED: ' + str(exc) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
