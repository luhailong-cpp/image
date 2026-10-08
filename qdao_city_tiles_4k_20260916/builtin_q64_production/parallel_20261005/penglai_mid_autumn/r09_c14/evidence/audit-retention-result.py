"""Read-only verification of executed retention; only this audit's JSON is written."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from collections import Counter
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parents[1]
ROOT = T.parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(p): return str(p).replace('/', '\\').lower()
def anchor(p): return {'file': str(p), 'sha256': sha(p)}
def strings(v, loc='$'):
    if isinstance(v, str): yield loc, v
    elif isinstance(v, dict):
        for k, x in v.items(): yield from strings(x, loc+'.'+k)
    elif isinstance(v, list):
        for i, x in enumerate(v): yield from strings(x, loc+f'[{i}]')
def pairs(v, loc='$'):
    if isinstance(v, dict):
        if 'file' in v and 'sha256' in v: yield loc, v
        for k, x in v.items(): yield from pairs(x, loc+'.'+k)
    elif isinstance(v, list):
        for i, x in enumerate(v): yield from pairs(x, loc+f'[{i}]')

planp, logp = T/'retention-plan.json', T/'retention-log.json'
plan, log = read(planp), read(logp)
issues = []
def check(ok, message):
    if not ok: issues.append(message)
check(log['plan']['sha256'] == sha(planp), 'Ledger plan hash mismatch')
check(log['status'] == 'retired_after_final_export_and_scoped_QA' and not log['failure'], 'Ledger did not finish successfully')
removed = {norm(x['file']): x for x in log['removed']}
planned = {norm(x['file']): x for x in plan['remove']}
check(len(removed) == len(log['removed']) == len(planned) == 115, 'Wrong removal count or duplicate')
check(set(removed) == set(planned), 'Actual/planned removal lists differ')
for key, x in removed.items():
    check(not Path(x['file']).exists(), 'Retired file still exists: '+x['file'])
    check((x['sha256'], x['bytes']) == (planned[key]['sha256'], planned[key]['bytes']), 'Removed hash/bytes differ from plan: '+key)
    check(x.get('retiredAfterExport') is True and x.get('sourceImageAvailable') is False and x.get('runtimeDependency') is False, 'Missing lifecycle flags: '+key)

current_metadata = {norm(x['file']): x for x in log['currentMetadata']}
for x in log['currentMetadata']+log['historicalTextRecords']:
    check(Path(x['file']).is_file() and sha(x['file']) == x['sha256'], 'Metadata/history hash mismatch: '+x['file'])
binary_ext = {'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc'}
kept_counts = Counter()
kept_binary = []
for x in plan['keep']:
    p = Path(x['file'])
    check(p.is_file(), 'Kept file missing: '+str(p))
    expected = current_metadata.get(norm(p), x)
    if p.is_file():
        check(sha(p) == expected['sha256'], 'Kept file hash mismatch: '+str(p))
        if norm(p) not in current_metadata: check(p.stat().st_size == x['bytes'], 'Kept byte size mismatch: '+str(p))
    kept_counts[x.get('category','unspecified')] += 1
    if p.suffix.lower() in binary_ext: kept_binary.append(x)
check(len(kept_binary) == 108, 'Wrong kept binary count')
check(sha(T/'output/native-assembly.json') == 'c59baca3d552bb773ce428b8deb29212888e6ff1401df7f88c7deabeee69ed3b', 'Immutable native assembly changed')
final = Path(plan['final']['file'])
check(sha(final) == '26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc', 'Final pixels changed')
check(Image.open(final).size == (4096,4096), 'Final dimensions changed')
manifest = read(T/'output/manifest.json')
check(manifest['sha256'] == sha(final) and manifest['scopedLocalSeamsPassed'], 'Current manifest final mismatch')
runtime_refs = manifest.get('runtimeDependencies', [])
check(len(runtime_refs) == 1 and norm(runtime_refs[0]['file']) == norm(final), 'Unexpected runtime dependency set')
for x in runtime_refs: check(Path(x['file']).is_file() and sha(x['file']) == x['sha256'], 'Dangling current runtime dependency')
qualified_missing = []
unqualified_missing = []
for md in log['currentMetadata']:
    for loc, x in pairs(read(md['file'])):
        key = norm(x['file'])
        if key in removed and x['sha256'] == removed[key]['sha256']:
            ok = x.get('retiredAfterExport') is True and x.get('sourceImageAvailable') is False and x.get('runtimeDependency') is False
            (qualified_missing if ok else unqualified_missing).append({'record':md['file'],'location':loc,'file':x['file']})
check(not unqualified_missing, 'Current metadata has unavailable retired source without lifecycle qualification')

# Every exact external reference to a removed input is flagged, even when possibly historical.
# Exclude unrelated blocked tile and tools entirely; no cleanup command is imported or invoked.
records = list(ROOT.glob('*.json'))
for d in ROOT.iterdir():
    if d.is_dir() and d.name not in {T.name, 'r10_c13', 'tools'}:
        records.extend(d.rglob('*.json'))
external_removed = []
p42_refs = []
p42 = T/'native/p42.png'
for record in records:
    raw = record.read_text(encoding='utf-8-sig')
    if 'r09_c14' not in raw: continue
    for loc, s in strings(json.loads(raw)):
        if norm(s) in removed: external_removed.append({'record':str(record),'location':loc,'file':s})
        if norm(s) == norm(p42): p42_refs.append({'record':str(record),'location':loc})
check(not external_removed, 'External JSON still references removed input(s)')
check(p42.is_file() and sha(p42) == '5a2e76539a4ff8b135cd5a76c1910f2d1d9aaa0f510f6cfc643f781fec41b8d5', 'Active p42 downstream source missing/changed')
check(any('r10_c14' in x['record'] for x in p42_refs), 'Expected r10_c14 p42 downstream reference missing')
freeze = ROOT/'r10_c14/references/north-native320.png'
check(np.array_equal(np.asarray(Image.open(freeze).convert('RGB')), np.asarray(Image.open(final).convert('RGB').crop((0,3776,4096,4096)))), 'r10_c14 north320 does not match final south320')

report = {'createdAt':datetime.now(timezone.utc).isoformat(), 'tile':'r09_c14',
    'scope':'independent read-only verification after parent executed retention; only audit code/report written',
    'status':'pass' if not issues else 'fail', 'plan':anchor(planp), 'executionLedger':anchor(logp),
    'removedCount':len(removed), 'all115Absent':all(not Path(x['file']).exists() for x in removed.values()),
    'removedBytes':sum(x['bytes'] for x in removed.values()), 'keptCount':len(plan['keep']),
    'keptBinaryCount':len(kept_binary), 'keptCategories':dict(kept_counts),
    'keptBinaryFileAndHashChecksPassed':not any('Kept' in x for x in issues),
    'allOriginalTextRetained':not any('Kept' in x or 'history' in x for x in issues),
    'currentMetadataAndOriginalTextHashes':log['currentMetadata']+log['historicalTextRecords'],
    'final':anchor(final), 'runtimeDependencies':runtime_refs,
    'lifecycleQualifiedHistoricalSourceOccurrences':len(qualified_missing),
    'unqualifiedHistoricalSourceOccurrences':unqualified_missing,
    'externalJsonRecordsScanned':len(records), 'externalReferencesToRetiredImages':external_removed,
    'activeDownstreamNativeSource':anchor(p42), 'activeDownstreamNativeSourceReferences':p42_refs,
    'r10c14FrozenNorth320MatchesCurrentFinalSouth320':not any('north320' in x for x in issues),
    'immutableNativeAssemblyUnchanged':not any('Immutable' in x for x in issues),
    'sourceLifecycleInterpretation':'Dated source/assembly records remain immutable history. Retention ledger qualifies only actually removed paths and hashes. Current manifest explicitly lists only final PNG as runtime dependency. No old image is asserted to remain available.',
    'noImagesDeletedByAudit':True, 'noCandidateOrManifestEdits':True,
    'blockedR10c13CleanupNotReadOrRetried':True, 'issues':issues}
out = T/'evidence/retention-result-audit.json'
assert not out.exists(), 'Do not overwrite existing audit.'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out),'sha256':sha(out),'status':report['status'],
    'removed':len(removed),'keptBinary':len(kept_binary),'qualifiedSources':len(qualified_missing),
    'externalRecords':len(records),'issues':issues},ensure_ascii=False))
