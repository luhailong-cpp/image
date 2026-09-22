"""Read-only path/link preflight for the specifically authorized isolated seed."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path

workspace = Path('D:/luyuan/wuxingqitan')
source = workspace / 'mmorpg-client'
target = workspace / 'tmp/qdao-original-live-candidate-20260921'
roots = ('Assets', 'Packages', 'ProjectSettings', 'Library/PackageCache')
evidence = Path(__file__).resolve().parent
record = evidence / 'preflight.json'
assert not record.exists(), 'Preflight evidence already exists'
assert target.resolve() == target.absolute(), 'Target resolves outside its named location'
assert target.is_relative_to(workspace / 'tmp') and target != workspace / 'tmp'
assert source.resolve() == source.absolute() and source != target

def check(path):
    assert not path.is_symlink() and not path.is_junction(), 'Linked path: ' + str(path)
    if path.is_file():
        assert path.stat().st_nlink == 1, 'Hardlinked file: ' + str(path)

result = {}
for label, project in [('source', source), ('target', target)]:
    assert project.is_dir()
    assert not (project / 'Temp/UnityLockfile').exists(), 'Unity is open: ' + str(project)
    for ancestor in (project, *project.parents):
        check(ancestor)
    count = 0
    for root in roots:
        base = project / root
        assert base.is_dir(), 'Missing input root: ' + str(base)
        for ancestor in (base, *base.parents):
            check(ancestor)
        for directory, dirs, files in os.walk(base, followlinks=False):
            check(Path(directory))
            for name in dirs:
                check(Path(directory) / name)
            for name in files:
                check(Path(directory) / name)
                count += 1
    result[label] = {'absolute': str(project.resolve()), 'checkedFileCount': count}
result.update({'createdUtc': datetime.now(timezone.utc).isoformat(), 'roots': list(roots),
               'passed': True, 'junctionsSymlinksHardlinksFound': False,
               'scope': 'Path/link preflight only. No Unity import or validation claim.'})
with record.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
