"""Link the requested WIP handoff, preserving shared files before scoped changes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

SESSION = Path(__file__).resolve().parent.parent
ART = SESSION.parents[1]
HANDOFF = SESSION / 'handoff-20260921'
DOC = ART / '主城美术详细交接-20260921.md'
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
snapshot = read(HANDOFF / 'snapshot.json')
assert not snapshot['deliveryReady'] and snapshot['counts']['productionAcceptedTiles'] == 0
assert '<!-- HANDOFF_SNAPSHOT_APPEND -->' not in DOC.read_text(encoding='utf-8')
paths = [ART / 'status.json', ART / 'production_catalog.json', ART / 'builtin_q64_production/current-batch.json', ART / 'README.md', SESSION / 'README.md']
original = {p: p.read_bytes() for p in paths}
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup = SESSION / 'history' / ('handoff-links-' + stamp)
backup.mkdir(exist_ok=False)
handoff_ref = {'requestedByUser': True, 'purpose': 'continue_art_production_in_new_user_window',
               'document': DOC.relative_to(ART).as_posix(), 'documentSha256': sha(DOC.read_bytes()),
               'snapshot': (HANDOFF / 'snapshot.json').relative_to(ART).as_posix(),
               'snapshotSha256': sha((HANDOFF / 'snapshot.json').read_bytes()),
               'frozenAtUtc': snapshot['frozenAtUtc'], 'productionComplete': False, 'formalAcceptedTiles': 0,
               'generationStoppedForHandoff': True, 'clientIntegrationOwner': 'separate user window'}
updates = {}
for path in paths[:3]:
    obj = json.loads(original[path].decode('utf-8-sig'))
    run = obj['activeProductionRun']
    assert run['id'] == SESSION.name
    run['latestDetailedHandoff'] = handoff_ref
    run['currentWindowWorkState'] = 'handoff_prepared_at_snapshot_not_production_complete'
    if path.name == 'status.json':
        obj['status'] = 'single_city_art_incomplete_handed_off_for_new_window'
        obj['handoff']['detailedArtContinuation'] = handoff_ref
    updates[path] = (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
for path in paths[3:]:
    link = '主城美术详细交接-20260921.md' if path.parent == ART else '../../主城美术详细交接-20260921.md'
    prefix = ('> 用户要求移交新窗口继续。最新入口：[详细交接](' + link + ')。'
              '本次冻结为天墉城节庆 8／256 个 4K 候选、正式验收 0；本窗口停止新增生图。'
              '以下历史检查点原样保留，当前文件及来源数量以交接快照和 session-state 为准。\n\n')
    updates[path] = prefix.encode('utf-8') + original[path]
for idx, path in enumerate(paths):
    (backup / f'{idx:02}-{path.name}').write_bytes(original[path])
for path in paths:
    assert path.read_bytes() == original[path], 'Concurrent change; refusing overwrite: ' + str(path)
results = []
for idx, path in enumerate(paths):
    assert path.read_bytes() == original[path], 'Concurrent change; refusing overwrite: ' + str(path)
    path.write_bytes(updates[path])
    results.append({'file': str(path), 'beforeSha256': sha(original[path]), 'afterSha256': sha(updates[path]),
                    'backup': str(backup / f'{idx:02}-{path.name}')})
(backup / 'update-record.json').write_text(json.dumps({'files': results, 'scope': 'handoff pointers and status only'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'updatedFiles': len(results), 'backup': str(backup), 'formalAcceptedTiles': 0}))
