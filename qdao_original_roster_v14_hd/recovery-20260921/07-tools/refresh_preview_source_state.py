"""Refresh provenance availability without changing any rendered artwork."""
import json
from pathlib import Path
from movement_assets import HERE, PREVIEWS, read, sha, now, verify_source

root = PREVIEWS / 'current-review-20260923'
report = read(root / 'manifest.json')
for row in report['files']:
    native = row['nativeSource']
    state = verify_source(Path(native['path']), native['sha256'])
    row['sourceRebuildAvailable'] = state['available']
    row['sourceHashVerification'] = state['hashVerification']
    if not state['available']:
        row['sourceCleanup'] = state.get('cleanup')
report['sourceStatusRefreshedAt'] = now()
report['sourceCurrentVerificationCount'] = sum(row['sourceRebuildAvailable'] for row in report['files'])
report['sourceRebuildAvailable'] = all(row['sourceRebuildAvailable'] for row in report['files'])
report['uniqueRawHashes'] = None if not report['sourceRebuildAvailable'] else report.get('uniqueRawHashes')
report['retentionNote'] = 'Originals and intermediates were removed under explicit user authorization; textual provenance remains. Current candidate images are not art-approved.'
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
save(root / 'manifest.json', report)
save(root / 'structural-report.json', {**report, 'manifestSha256': sha(root / 'manifest.json')})
template = (HERE / 'preview-template.html').read_text(encoding='utf-8')
template = template.replace("im.src='runtime/'+r.path", "im.src=(manifest.runtimeBase||'runtime/')+r.path")
template = template.replace("im.src='runtime/'+k", "im.src=(manifest.runtimeBase||'runtime/')+k")
(root / 'index.html').write_text(template.replace('__MANIFEST__', json.dumps(report, ensure_ascii=False)), encoding='utf-8')
print(json.dumps({'frames':len(report['files']), 'sourceCurrentVerificationCount':report['sourceCurrentVerificationCount'], 'sourceRebuildAvailable':report['sourceRebuildAvailable']}))
