"""Compare complete recorded source/seed inputs without deleting extra seed files."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

evidence = Path(__file__).resolve().parent
record = evidence / 'input-correspondence.json'
assert not record.exists()
source = json.loads((evidence / 'source-after.json').read_text(encoding='utf-8-sig'))
target = json.loads((evidence / 'target-after.json').read_text(encoding='utf-8-sig'))
copies = json.loads((evidence / 'copy-record.json').read_text(encoding='utf-8-sig'))
assert all(row['exitCode'] < 8 for row in copies['directories'])
assert copies['direction'] == 'formal-to-isolated-seed-only'
src = {row['path']: row for row in source['files']}
dst = {row['path']: row for row in target['files']}
missing = sorted(src.keys() - dst.keys())
extra = sorted(dst.keys() - src.keys())
changed = sorted(path for path in src.keys() & dst.keys() if src[path]['sha256'] != dst[path]['sha256'])
source_changes = source['comparison']
stable = not any(source_changes[name] for name in ('added', 'removed', 'changed'))
rows = [{'path': path, 'sourceSha256': src[path]['sha256'],
         'targetSha256': dst[path]['sha256'] if path in dst else None,
         'sourceBytes': src[path]['bytes'], 'targetBytes': dst[path]['bytes'] if path in dst else None,
         'matches': path in dst and src[path]['sha256'] == dst[path]['sha256']}
        for path in sorted(src)]
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
result = {'createdUtc': datetime.now(timezone.utc).isoformat(),
          'scope': 'Local isolated seed preparation only; Unity not started, imported, or accepted. No GUID/index copied back to formal.',
          'source': source['project'], 'target': target['project'], 'sourceStableDuringCopy': stable,
          'sourceFileCount': len(src), 'targetFileCount': len(dst), 'missingTargetFiles': missing,
          'mismatchedTargetFiles': changed, 'extraTargetFilesPreserved': [dst[path] for path in extra],
          'allSourceFilesMatchTarget': not missing and not changed,
          'inputSetsExactlyEqual': stable and not missing and not changed and not extra,
          'correspondence': rows,
          'evidenceHashes': {name: sha(evidence / name) for name in
                            ['preflight.json', 'source-before.json', 'source-after.json',
                             'target-after.json', 'copy-record.json', 'preflight_seed.py', 'compare_seed_inputs.py']}}
with record.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'record': str(record), 'sha256': sha(record), 'sourceStableDuringCopy': stable,
                  'sourceFileCount': len(src), 'targetFileCount': len(dst), 'missing': len(missing),
                  'mismatch': len(changed), 'extraPreserved': len(extra), 'inputSetsExactlyEqual': result['inputSetsExactlyEqual']}))
assert stable and not missing and not changed, 'Source drift or copy mismatch; consult retained evidence.'
