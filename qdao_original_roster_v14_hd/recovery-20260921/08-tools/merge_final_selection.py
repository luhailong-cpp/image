"""Freeze exactly the images reviewed in the five direction snapshots."""
import json
from pathlib import Path
from process import RECOVERY, write, sha

delivery = RECOVERY / '08-delivery-preview'
groups = {
    's-se-review-v3': ['S', 'SE'],
    'e-review-v2': ['E'],
    'sw-review-final-v1': ['SW'],
    'w-nw-review-final-v2': ['W', 'NW'],
    'n-ne-review-final-v1': ['N', 'NE'],
}
selection, bindings = {}, []
for revision, directions in groups.items():
    path = delivery / 'revisions' / revision / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    for row in manifest['files']:
        assert row['slot'].split('/')[1] in directions
        assert row['slot'] not in selection
        selection[row['slot']] = row['source_attempt']
    bindings.append({'revision': revision, 'directions': directions, 'manifest_sha256': sha(path),
                     'files': [{'slot': r['slot'], 'sha256': r['sha256'], 'source_attempt': r['source_attempt']} for r in manifest['files']]})
assert len(selection) == 136
write(delivery / 'full-selection.json', selection)
write(delivery / 'reviewed-snapshot-bindings.json', bindings)
print(json.dumps({'slots':len(selection),'direction_snapshots':len(bindings)}))
