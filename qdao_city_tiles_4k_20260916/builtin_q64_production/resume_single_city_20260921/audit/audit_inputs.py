"""Read source production records; write only this independent audit directory."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[2]
REPO = BASE.parent
START = datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def resolve(value):
    value = re.sub(r'^E:[/\\]work[/\\]', 'D:/luyuan/wuxingqitan/', value, flags=re.I)
    p = Path(value)
    return p if p.is_absolute() else BASE / p

def check(value, expected=None, decode=False, header=False):
    p = resolve(value)
    entry = {'recordedPath': value, 'resolvedPath': str(p), 'exists': p.is_file(),
             'expectedSha256': expected}
    if not p.is_file():
        return entry
    entry['actualSha256'] = sha(p)
    entry['bytes'] = p.stat().st_size
    if expected is not None:
        entry['sha256Matches'] = entry['actualSha256'].lower() == expected.lower()
    if decode or header:
        try:
            with Image.open(p) as image:
                entry.update(format=image.format, pixels=list(image.size), mode=image.mode)
                if decode:
                    image.load()
                    entry['fullDecodePassed'] = True
                else:
                    entry['imageHeaderReadOnly'] = True
        except Exception as exc:
            entry['imageError'] = str(exc)
    return entry

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

input_paths = ['status.json', 'production_catalog.json', 'builtin_q64_production/current-batch.json']
input_evidence = [check(p) for p in input_paths]
status, catalog, batch = [read(BASE / p) for p in input_paths]
candidate_evidence = []
for candidate in batch['candidates']:
    entry = dict(candidate)
    entry['fileVerification'] = check(candidate['file'], candidate['sha256'], decode=True)
    entry['assemblyVerification'] = check(candidate['assembly'], candidate['assemblySha256'])
    entry['qaVerification'] = check(candidate['qa'], candidate['qaSha256'])
    candidate_evidence.append(entry)

native_evidence = []
for kind, field in [('base', 'baseNativeEvidence'), ('repair', 'nativeRepairEvidence')]:
    for item in batch[field]:
        native_evidence.append({'kind': kind, **item,
            'nativeVerification': check(item['native'], item['sha256'], header=True),
            'recordVerification': check(item['record'], item['recordSha256']),
            'originalCachePathExists': Path(item['originalSource']).is_file()})

variants = []
for variant in catalog['variants']:
    qa_path = variant['currentCandidates'][0]['qa']
    qa = read(resolve(qa_path))
    variants.append({'city': variant['city'], 'variant': variant['variant'],
        'displayName': variant['displayName'], 'candidateCount': len(variant['currentCandidates']),
        'coordinates': sorted(c['tile'] for c in variant['currentCandidates']),
        'acceptedDeliveryTiles': variant['productionTilesAccepted'],
        'layoutSource': check(variant['source'], variant['sourceSha256'], header=True),
        'wholeCityLayoutReference': check(variant['wholeCityReference']['file'], variant['wholeCityReference']['sha256'], header=True),
        'recordedLocalQaPath': qa_path, 'recordedLocalQaStatus': qa.get('status'),
        'recordedRemainingAcceptance': qa.get('remainingAcceptance', qa.get('remaining'))})

plan_path = BASE / 'builtin_q64_production/tianyong_festival/r09_c09/plan.json'
plan = read(plan_path)
indexed = {str(resolve(e['native']).resolve()).lower() for e in native_evidence}
wip = []
for patch in plan['patches']:
    stem = patch.get('selectedNativeStem', patch['id'])
    native = plan_path.parent / 'native' / (stem + '.png')
    record = native.with_suffix('.record.json')
    entry = {'patchId': patch['id'], 'selectedStem': stem, 'nativeExists': native.is_file(),
             'recordExists': record.is_file(), 'indexedInCurrentBatch': str(native.resolve()).lower() in indexed}
    if record.is_file():
        details = read(record)
        entry['nativeVerification'] = check(str(native), details.get('outputSha256'), header=True)
        entry['recordSha256'] = sha(record)
        entry['recordedCreatedAtUtc'] = details.get('createdAtUtc')
    wip.append(entry)

all_checks = [c[k] for c in candidate_evidence for k in ['fileVerification','assemblyVerification','qaVerification']]
all_checks += [n[k] for n in native_evidence for k in ['nativeVerification','recordVerification']]
failed = [x for x in all_checks if not x['exists'] or x.get('sha256Matches') is False or 'imageError' in x]
cat_keys = sorted((c['appearance'],c['tile'],c['file'],c['sha256']) for v in catalog['variants'] for c in v['currentCandidates'])
batch_keys = sorted((c['appearance'],c['tile'],c['file'],c['sha256']) for c in batch['candidates'])
report = {'schemaVersion': 1, 'auditStartedAtUtc': START, 'auditFinishedAtUtc': datetime.now(timezone.utc).isoformat(),
    'role': 'Independent filesystem and recorded-evidence audit; not fresh visual art acceptance',
    'snapshotBoundary': '24 candidates / 502 indexed native files are the pre-resumption records. Concurrent new native generation can exist beyond this index.',
    'readOnlySourceRecords': True, 'sourceRecordsRewritten': False,
    'pathMapping': {'E:/work/': 'D:/luyuan/wuxingqitan/'}, 'inputRecords': input_evidence,
    'inputRecordsUnchangedDuringAudit': all(sha(resolve(e['recordedPath'])) == e['actualSha256'] for e in input_evidence),
    'consistency': {'statusCandidateFilesMatchBatch': sorted(status['candidateFiles']) == sorted(c['file'] for c in batch['candidates']),
        'catalogCandidatesMatchBatch': cat_keys == batch_keys},
    'summary': {'candidateCount': len(candidate_evidence), 'acceptedDeliveryCount': batch['acceptedDeliveryTileCount'],
        'completedWholeCityCount': batch['wholeCityCompletedCount'], 'candidateFileAssemblyQaChecks': len(candidate_evidence)*3,
        'indexedNativeCount': len(native_evidence), 'indexedNativeAndRecordChecks': len(native_evidence)*2,
        'failedChecks': len(failed), 'indexedOriginalCachePathsFound': sum(e['originalCachePathExists'] for e in native_evidence),
        'selectedCityAppearance': 'tianyong_festival', 'selectedCityCandidateCount': 6,
        'selectedCityMissingCandidateCoordinates': 250},
    'variants': variants, 'candidates': candidate_evidence, 'indexedNativeEvidence': native_evidence,
    'r09_c09WorkInProgress': {'planVerification': check(str(plan_path)), 'selectedPatches': wip,
        'selectedNativePresent': sum(e['nativeExists'] for e in wip),
        'selectedNativePresentButNotIndexed': [e['patchId'] for e in wip if e['nativeExists'] and not e['indexedInCurrentBatch']],
        'missingSelectedPatchIds': [e['patchId'] for e in wip if not e['nativeExists']]},
    'recordInconsistencies': [
        'status.continuationWork describes prior v4/unfinished work although selected catalog entries and QA point to newer completed local candidates.',
        'Donghai day historical QA remaining text says lantern c10 is incomplete; the current lantern candidate/QA supersedes that historical statement.',
        'Old absolute E:/work paths require the documented local mapping. Old C:/Users/luyua generated-image cache paths are absent; preserved project native bytes and SHA match.',
        'Current-batch native count is an indexed snapshot and is behind the r09_c09 actual files. Candidate count remains valid because that tile is unassembled.'
    ], 'failures': failed}
save('current_input_inventory.json', report)

selected = {c['tile']: c for c in batch['candidates'] if c['appearance'] == 'tianyong_festival'}
tiles = []
seams = []
junctions = []
def coord(r,c): return f'r{r:02d}_c{c:02d}'
for r in range(1,17):
    for c in range(1,17):
        tile = coord(r,c)
        candidate = selected.get(tile)
        tiles.append({'tile': tile, 'pixelRectXYWH': [(c-1)*4096,(r-1)*4096,4096,4096],
            'candidateExists': candidate is not None, 'candidate': candidate,
            'status': 'local_candidate_prior_qa_recorded_formal_art_acceptance_pending' if candidate else 'missing_candidate',
            'formalArtAcceptancePassed': False, 'clientRuntimeAccepted': False})
        for axis, nr,nc in [('vertical_boundary',r,c+1),('horizontal_boundary',r+1,c)]:
            if nr > 16 or nc > 16: continue
            pair = [tile,coord(nr,nc)]
            both = all(k in selected for k in pair)
            seams.append({'id': '|'.join(pair), 'axis': axis, 'tiles': pair,
                'boundaryCoordinate': c*4096 if axis == 'vertical_boundary' else r*4096,
                'spanStart': (r-1)*4096 if axis == 'vertical_boundary' else (c-1)*4096,
                'spanLength':4096, 'bothCandidatesPresent': both,
                'priorLocalQaReference': selected[pair[0]]['qa'] if both else None,
                'status': 'prior_local_review_recorded_whole_city_gate_pending' if both else 'pending_missing_neighbor',
                'wholeCityArtGatePassed': False, 'freshVisualReviewPerformedByThisAudit':False})
        if r < 16 and c < 16:
            quad=[tile,coord(r,c+1),coord(r+1,c),coord(r+1,c+1)]
            all_exist = all(k in selected for k in quad)
            junctions.append({'id':f'junction_r{r:02d}_c{c:02d}', 'pixelXY':[c*4096,r*4096],
                'tiles':quad,'allCandidatesPresent':all_exist,
                'priorLocalQaReference': selected[tile]['qa'] if all_exist else None,
                'status':'prior_local_review_recorded_whole_city_gate_pending' if all_exist else 'pending_missing_neighbor',
                'wholeCityArtGatePassed':False,'freshVisualReviewPerformedByThisAudit':False})
assert (len(tiles),len(seams),len(junctions)) == (256,480,225)
ledger={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
    'appearance':'tianyong_festival','cityPixels':[65536,65536],'tilePixels':[4096,4096],
    'role':'Pre-resumption coverage ledger. Prior local QA references are retained as evidence and do not set any whole-city gate to passed.',
    'counts':{'tiles':len(tiles),'candidateTiles':len(selected),'missingCandidates':256-len(selected),
        'seams':len(seams),'seamsWithBothCandidates':sum(s['bothCandidatesPresent'] for s in seams),
        'junctions':len(junctions),'junctionsWithAllCandidates':sum(j['allCandidatesPresent'] for j in junctions),
        'formalArtAcceptedTiles':0,'wholeCityPassedSeams':0,'wholeCityPassedJunctions':0},
    'tiles':tiles,'seams':seams,'junctions':junctions}
save('tianyong_festival_coverage_ledger.json',ledger)
summary='''# 单城恢复前输入审计

审计对象为本轮新生图前的三份制作记录：24 张局部 4K 候选，502 份已索引原生来源；这些数字不是完整交付进度。天墉城节庆已有 6 张候选，是七外观中最多的一套，其余每套 3 张。正式成品、完整城市均为 0。

`current_input_inventory.json` 保存每份候选、assembly、QA、原生文件、原生 record 的实际 SHA。候选还执行 Pillow 完整解码；原生细节只读取格式尺寸头信息，不把它写为完整解码或美术通过。502 份原生项目副本与记录均在本机，但旧用户目录的生成缓存不可用；保留副本的 SHA 一致性可验证。

`tianyong_festival_coverage_ledger.json` 包含 256 坐标、480 接缝、225 四块交点。只有 6 个现有候选坐标、6 条已有双侧候选接缝、1 个已有四侧候选交点。全部整城美术验收标记仍为 false。旧局部 QA 链接只作为既有记录，不冒充本次重新目检或正式验收。

下一块建议沿用 r09_c09：它已用 v5 左邻、下邻上下文建立 guide，保留 230px 重叠，4×4 原生补丁每块 1254×1254 / 核心 1024。其 actual native 实物比批次索引新，具体已选版本与缺失列表见 JSON；当前统计可能因根代理并行制作继续增长。完成后先验原像素内部接缝，再验与 r09_c08 / r10_c09 的边界及 r09_c08、r09_c09、r10_c08、r10_c09 交点。

不一致：status.continuationWork 和东海日景旧 QA 的元宵 c10 文字已落后于当前候选；E:/work 需映射到 D:/luyuan/wuxingqitan；current-batch 原生索引尚未包含全部 r09_c09 WIP。以上均未擅改原始共享记录。

该目录只新增审计证据，未改 status/catalog/current-batch、未删除来源、未提交或推送。
'''
(OUT/'README.md').write_text(summary,encoding='utf-8')
print(json.dumps({'summary':report['summary'],'coverage':ledger['counts'],
    'wipPresent':report['r09_c09WorkInProgress']['selectedNativePresent'],
    'wipUnindexed':report['r09_c09WorkInProgress']['selectedNativePresentButNotIndexed'],
    'inputRecordsUnchanged':report['inputRecordsUnchangedDuringAudit']},ensure_ascii=False,indent=2))
