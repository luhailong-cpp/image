"""Validate immutable candidate references and publish the parent-only entry points."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

from PIL import Image

ART = Path('D:/work/image/qdao_city_tiles_4k_20260916')
P = ART / 'builtin_q64_production/parallel_20261005'
A = P / 'parent_audit_20261008'
C = P / 'parent_repairs_20261008/current'
NOW = datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ref(path):
    return {'path': path.as_posix(), 'sha256': sha(path)}

def relative(path):
    return Path(path).relative_to(ART).as_posix()

checks = []
errors = []

def check(path, expected=None, pixels=None, role='reference'):
    path = Path(path)
    item = {'path': path.as_posix(), 'role': role, 'exists': path.is_file(),
            'expectedSha256': expected}
    if path.is_file():
        item['sha256'] = sha(path)
        item['hashMatches'] = item['sha256'] == expected if expected else None
        if pixels is not None:
            with Image.open(path) as image:
                image.load()
                item['pixels'] = list(image.size)
                item['format'] = image.format
            item['pixelsMatch'] = item['pixels'] == pixels
    if not item['exists'] or item.get('hashMatches') is False or item.get('pixelsMatch') is False:
        errors.append(item)
    checks.append(item)
    return item

index_path = A / 'verified-current-index.json'
selection_path = C / 'current-selection.json'
index = read(index_path)
selection = read(selection_path)
status_path = ART / 'status.json'
status = read(status_path)
owned = [index_path, A/'README.md', P/'README.md', status_path, ART/'README.md']
before_hashes = {p.as_posix(): sha(p) for p in owned}
selection_hash = sha(selection_path)

entries = [(appearance, e) for appearance in index['appearances'] for e in appearance['entries']]
assert len(entries) == 44
assert len({(a['appearance'], e['tileId']) for a, e in entries}) == 44
assert index['summary']['formalAcceptedCount'] == 0
for appearance, e in entries:
    check(e['path'], e['sha256'], [4096, 4096], '44-coordinate-parent-snapshot')

for e in selection['candidates']:
    check(e['file'], e['sha256'], [4096, 4096], 'parent-package-candidate')
assert selection['completeCandidateCount'] == 11
assert selection['partialCandidateCount'] == 1
assert selection['additionalUniqueCoordinateCount'] == 0
assert selection['childSelectionModified'] is False
assert selection['formalAccepted'] is False

for key in ['handoffInput', 'priorCheckpoint', 'sourceChildCheckpoint', 'qaTransfer',
            'postExportVerification', 'finalLocalVisualReview']:
    r = selection[key]
    check(r['file'], r['sha256'], role=key)

modified_ids = selection['parentModifiedCoordinates']
modified = [e for e in selection['candidates'] if e['tile'] in modified_ids]
assert len(modified) == 5
generation_refs = {}
for e in modified:
    generation = Path(e['generationRecord'])
    check(generation, role='parent-generation-record')
    g = read(generation)
    assert g['sha256'] == e['sha256']
    assert g['formalAccepted'] is False
    generation_refs[e['tile']] = ref(generation)
    for source in g['derivedFrom']:
        check(source['file'], source['sha256'], [4096, 4096], 'immediate-repair-source')
        if source.get('generationRecord'):
            check(source['generationRecord'], role='source-generation-record')

transfer = read(C/'qa-transfer.json')
post = read(C/'post-export-verification.json')
visual = read(C/'final-visual-review.json')
assert len(transfer['items']) == 37
assert len(post['qaChecks']) == 37 and post['allChecksPass'] is True
assert len(visual['actuallyViewedFinalNativeCrops']) == 5
for item in transfer['items']:
    check(item['file'], item['sha256'], role='transferred-QA-crop')
    for key in ['reviewedBranchBoard', 'branchReview']:
        r = item[key]
        check(r['file'], r['sha256'], role=key)
for item in post['qaChecks']:
    assert item['equalToStoredQAPixels'] and item['equalToReviewedBranchPixels']
for item in visual['actuallyViewedFinalNativeCrops']:
    check(item['file'], item['sha256'], role='previously-viewed-final-native-crop')
    assert item['actuallyViewed'] is True

preview = index['preview']
check(preview['path'], preview['sha256'], preview['pixels'], 'current-44-coordinate-preview')
if errors:
    raise RuntimeError(json.dumps(errors, ensure_ascii=True))

package = {
    **ref(selection_path), 'appearance': 'tianyong_festival',
    'role': 'parent_repair_candidate_package_not_child_authoritative_selection',
    'parentModifiedCoordinates': modified_ids, 'parentModified4KCount': 5,
    'completeCandidateCount': 11, 'partialCandidateCount': 1,
    'additionalUniqueCoordinateCount': 0,
    'qaTransfer': ref(C/'qa-transfer.json'),
    'postExportVerification': ref(C/'post-export-verification.json'),
    'finalLocalVisualReview': ref(C/'final-visual-review.json'),
    'limitedQACropCount': 37, 'finalNativeCropsActuallyViewedByPreviousReviewer': 5,
    'childSelectionModified': False, 'formalAccepted': False,
    'wholeCityComplete': False, 'clientVerified': False,
    'remainingKnownLimitations': visual['remainingKnownLimitations'],
    'validatedAt': NOW,
}
by_id = {e['tile']: e for e in modified}
for appearance, e in entries:
    if appearance['appearance'] == 'tianyong_festival' and e['tileId'] in by_id:
        repair = by_id[e['tileId']]
        e['parentRepairCandidate'] = {
            'path': Path(repair['file']).as_posix(), 'sha256': repair['sha256'],
            'width': 4096, 'height': 4096, 'fullPixelCandidate': True,
            'generationRecord': generation_refs[e['tileId']],
            'selectionSource': ref(selection_path),
            'repairBranches': repair['parentRepairBranches'],
            'qaEvidence': {'qaTransfer': package['qaTransfer'],
                           'postExportVerification': package['postExportVerification'],
                           'finalLocalVisualReview': package['finalLocalVisualReview']},
            'role': 'same_coordinate_parent_repair_alternative',
            'doesNotReplaceChildSelection': True, 'additionalUniqueCoordinateCount': 0,
            'formalAccepted': False, 'wholeCityComplete': False, 'clientVerified': False,
            'validationScope': 'File/SHA/dimension/provenance checks here; local visual QA inherited only from exact bound parent evidence.',
        }
index['parentRepairPackage'] = package
index['parentRepairPolicy'] = 'Five checked parentRepairCandidate alternatives are attached to existing coordinates. Child selections and primary snapshot paths stay unchanged; repair alternatives add zero coordinates and imply no full-edge, full-tile, city or client acceptance.'
index['snapshotScope'] = '四份只读审计与增量审计的 44 坐标快照，另附 5 个同坐标 parentRepairCandidate。完整像素候选不等于正式游戏成品；父修补引用不替换七个制作任务权威选择。'
index['parentIndexUpdatedAt'] = NOW
index['parentIndexValidation'] = {'path': (A/'parent-index-validation.json').as_posix(), 'scope': 'Entry point and bound-file validation; no new visual acceptance.'}

audit_text = (A/'README.md').read_text(encoding='utf-8-sig')
audit_text = audit_text.replace('父独占的四处修补正在合并，暂未替换 child 权威选择，也不增加坐标。',
    '父独占的四处修补已合并为 5 个同坐标 parentRepairCandidate；修补包基于 child v014，保留 11 个完整候选与 1 个不完整画布。它没有替换 child 权威选择，也不增加坐标。')
repair_section = '\n## 父任务当前修补包\n\n'
repair_section += '[5 个同坐标修补稿与来源](../parent_repairs_20261008/current/current-selection.json) · [37 个限定 QA 的逐像素转移](../parent_repairs_20261008/current/qa-transfer.json) · [导出后验证](../parent_repairs_20261008/current/post-export-verification.json) · [最终局部实看记录](../parent_repairs_20261008/current/final-visual-review.json) · [父索引引用验证](parent-index-validation.json)\n\n'
repair_section += '四次 AI 修补已安全合并到以下 5 张 4096×4096 候选。统一索引在原坐标下附 `parentRepairCandidate`，原任务选择与主路径保持原样；总数仍为 44，正式验收仍为 0。37 个限定 QA 通过逐像素转移，最终 5 张原尺寸检查裁片已有实看记录；未验收完整边界、整块、整城或客户端。上方总览仍展示 44 坐标快照的原选择，不把修补版重复放入。\n\n'
repair_section += '| 坐标 | 父修补候选 |\n|---|---|\n'
for e in modified:
    repair_section += f"| {e['tile']} | [4096 PNG](../parent_repairs_20261008/current/{e['tile']}.png) |\n"
repair_section += '\n仍保留西上方灰石材旧明暗接线、右角修补范围外地面轻微色阶及其他尚未审查区域的限制。\n'
audit_text += repair_section

parallel_text = (P/'README.md').read_text(encoding='utf-8-sig')
parallel_text = parallel_text.replace('[实际任务ID清单](dispatch-index.json) · [父任务冻结的29块在制源集](../resume_single_city_20260921/completion_20261004/current-work.json)',
    '[当前 44 块候选汇总与预览](parent_audit_20261008/README.md) · [统一索引](parent_audit_20261008/verified-current-index.json) · [5 张同坐标父修补稿](parent_repairs_20261008/current/current-selection.json) · [实际任务ID清单](dispatch-index.json)')
parallel_text = parallel_text.replace('各任务正在补新区域。父任务冻结源集为29/1792个完整4K候选坐标，正式验收0、整城完成0；新片段不算完整图块，任务数也不代表地图完成数。实际新增产出看各任务进度与绑定图像检查记录。',
    '2026-10-08 已核验快照为 **44/1792 个完整 4K 候选坐标，尚缺 1748；正式验收 0、完整城市 0/7**。主城节庆 11，小镇日景/春节各 6，渔村日景 6、元宵 5，仙岛日景/中秋各 5。父任务另外合并了四处修补，涉及 5 个既有坐标，不增加块数，也未改变七个任务的权威选择。未完成片段不算完整图块，后续新增产出须按当前图像 SHA 和范围限定 QA 复核。\n\n[2026-10-05 冻结的 29 块来源](../resume_single_city_20260921/completion_20261004/current-work.json)是并行开工时的历史基线，不再代表当前候选数。')

historical_keys = ['updatedAtUtc', 'scope', 'activePlan', 'generated4KCandidateCount',
    'candidatePreview', 'candidateFiles', 'currentBatch', 'currentBatchSha256',
    'currentSelectedCandidateCoordinateCountAllAppearances', 'latestContinuation',
    'nativeDetailPatchCount', 'baseNativeDetailPatchCount', 'additionalNativeRepairCount',
    'counterMeaning']
status.setdefault('historicalParentEntrypoint20261005', {k: status.get(k) for k in historical_keys})
for k in ['nativeDetailPatchCount', 'baseNativeDetailPatchCount', 'additionalNativeRepairCount']:
    status.pop(k, None)
status['schemaVersion'] = max(5, status.get('schemaVersion', 0))
status['updatedAtUtc'] = NOW
status['scope'] = 'Seven 65536x65536 appearances in production: 44 unique complete-pixel 4096x4096 candidates of 1792; 1748 missing, 0 formally accepted, 0 complete cities. Five same-coordinate parent repair candidates add no coordinates.'
current_index_rel = relative(index_path)
status['activePlan'] = current_index_rel
status['currentBatch'] = current_index_rel
status['generated4KCandidateCount'] = 44
status['currentSelectedCandidateCoordinateCountAllAppearances'] = 44
status['candidateFiles'] = [relative(e['path']) for _, e in entries]
status['candidatePreview'] = relative(Path(preview['path']))
status['candidatePreviewSha256'] = preview['sha256']
status['candidatePreviewMeaning'] = '44-coordinate selected snapshot overview; parent repair alternatives are separately linked and do not add cells.'
status['parentRepairPackage'] = package
status['candidateVisualReview'] = 'SHA-bound local QA only; parent repair package carries 37 transferred crops and 5 final native crops viewed in the prior review. Full tiles, all neighbors, whole cities and client validation remain incomplete.'
status['scopeDecision'].setdefault('historicalParentCheckpoint20261005', {
    'candidateCoordinates': status['scopeDecision'].pop('parentCheckpointCandidateCoordinates', 29),
    'remainingCoordinates': status['scopeDecision'].pop('remainingInParentCheckpoint', 1763)})
status['scopeDecision']['currentCompletePixelCandidateCount'] = 44
status['scopeDecision']['remainingFullPixelCoordinates'] = 1748
status['continuationWork']['currentIndex'] = current_index_rel
status['continuationWork']['parentRepairPackage'] = relative(selection_path)
status['continuationWork']['sourceCheckpointMeaning'] = 'Historical 2026-10-05 baseline only.'
status['handoff']['currentWorkingRecord'] = current_index_rel
status['activeProductionRun']['updatedAtUtc'] = NOW
status['activeProductionRun']['currentIndex'] = current_index_rel
status['activeProductionRun']['currentCompletePixelCandidateCount'] = 44
status['activeProductionRun']['remainingFullPixelCoordinates'] = 1748
status['activeProductionRun']['parentRepairPackage'] = relative(selection_path)
status['activeProductionRun']['countMeaning'] = '44 unique complete-pixel candidates in the SHA-verified snapshot; parentCheckpointCount=29 is explicitly the historical frozen baseline. Five parent repair alternatives and partial canvas add zero coordinates.'
status['latestContinuation'] = {'readme': relative(A/'README.md'),
    'checkpoint': {'file': current_index_rel}, 'updatedAtUtc': NOW,
    'currentWorkingCoordinates': 44, 'tianyongWorkingCoordinates': 11,
    'formalAcceptedTiles': 0, 'wholeCityCompleteCount': 0,
    'parentRepairPackage': relative(selection_path),
    'parentRepairModifiedExistingCoordinateCount': 5,
    'role': 'verified_partial_seven_appearance_snapshot_with_parent_repair_alternatives'}
status['counterMeaning'] = '44 counts unique complete-pixel 4K candidate coordinates, not formal acceptance. Five parent repair alternatives add zero. Partial 4096 canvases are excluded. Historical 29/24 and native-source counters remain only as labeled history.'
status['baselineSelectionCountMeaning'] = 'Current candidateFiles and count refer to the 44-coordinate SHA-verified snapshot; older baseline/source arrays and native counters are in historical fields. Deleted original image bytes are not restored; textual provenance remains.'

art_text = (ART/'README.md').read_text(encoding='utf-8-sig')
art_text = art_text.replace('> **2026-10-05 当前入口：**', '> **2026-10-05 历史并行开工快照：**', 1)
art_text = art_text.replace('> **2026-10-04 最新续作：**', '> **2026-10-04 历史续作：**', 1)
art_text = art_text.replace('累计生成 **24个独立坐标的4096×4096局部候选**', '2026-09 历史批次累计生成 **24个独立坐标的4096×4096局部候选**', 1)
art_text = art_text.replace('[本批总览](builtin_q64_production/current-batch-overview.jpg)', '[历史批次总览](builtin_q64_production/current-batch-overview.jpg)', 1)
art_text = '> **2026-10-08 当前入口：** [七套主城已核验候选与预览](builtin_q64_production/parallel_20261005/parent_audit_20261008/README.md)为 **44/1792 个完整 4K 候选坐标，尚缺 1748；正式验收 0、完整城市 0/7**。[父任务当前修补包](builtin_q64_production/parallel_20261005/parent_repairs_20261008/current/current-selection.json)另含 5 张同坐标修补稿，已核验来源与限定 QA，不增加坐标，也不替换七个独立任务选择。继续内置生图与 GPT Image 2.5 目标配置，不使用付费 API。[七任务入口](builtin_q64_production/parallel_20261005/README.md) · [统一索引](builtin_q64_production/parallel_20261005/parent_audit_20261008/verified-current-index.json) · [状态](status.json)。以下 29/24/10/8 等旧数量均为各历史时点记录。\n\n' + art_text

# Refuse to overwrite any concurrent edit of our owned entry points or the repair selection.
for p in owned:
    assert sha(p) == before_hashes[p.as_posix()], f'concurrent modification: {p}'
assert sha(selection_path) == selection_hash, 'repair selection changed during validation'
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
new_index_hash = sha(index_path)
status['currentBatchSha256'] = new_index_hash
status['latestContinuation']['checkpoint']['sha256'] = new_index_hash
status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(A/'README.md').write_text(audit_text, encoding='utf-8')
(P/'README.md').write_text(parallel_text, encoding='utf-8')
(ART/'README.md').write_text(art_text, encoding='utf-8')

report = {
    'validatedAt': NOW, 'result': 'pass',
    'scope': 'Current output existence, SHA, decoded size, immediate source references, exact-bound QA document/crop hashes, and parent entrypoint coherence. No new visual review claimed.',
    'completePixelCoordinateCount': 44, 'targetCoordinateCount': 1792,
    'missingFullPixelCoordinateCount': 1748,
    'parentRepairModifiedExistingCoordinateCount': 5,
    'parentPackageCompleteCount': 11, 'parentPackagePartialCount': 1,
    'additionalUniqueCoordinatesFromRepair': 0,
    'qaTransferredCropCount': 37, 'previouslyViewedFinalNativeCropCount': 5,
    'formalAcceptedCount': 0, 'wholeCityCompleteCount': 0,
    'childSelectionsModified': False, 'imagesModified': False,
    'parentSelectionBeforeAfterSha256': selection_hash,
    'uniqueCheckedFiles': len({c['path'] for c in checks}),
    'checkCount': len(checks), 'errors': errors, 'checks': checks,
    'outputEntryPoints': [ref(p) for p in owned],
    'previousEntryPointHashes': before_hashes,
    'limitations': visual['remainingKnownLimitations'],
}
(A/'parent-index-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'result': report['result'], 'checkedFiles': report['uniqueCheckedFiles'],
    'checks': len(checks), 'completeCoordinates': 44, 'repairAlternatives': 5,
    'report': str(A/'parent-index-validation.json')}, ensure_ascii=True))
