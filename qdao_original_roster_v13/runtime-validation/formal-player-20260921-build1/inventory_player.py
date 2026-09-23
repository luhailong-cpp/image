"""Read-only manifest of this newly built player; does not start it or restore Unity inputs."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct

evidence = Path(__file__).resolve().parent
workspace = evidence.parents[3]
output = workspace / 'tmp/qdao-formal-player'
project = workspace / 'mmorpg-client'
manifest_path = evidence / 'player-artifacts.json'
assert not manifest_path.exists()

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

completion = json.loads((evidence / 'completion.json').read_text(encoding='utf-8-sig'))
assert completion['exitCode'] == 0
log_path = evidence / 'unity-build.log'
log = log_path.read_text(encoding='utf-8-sig')
assert sha(log_path) == completion['logSha256']
match = re.search(r'\[ShowcaseBuild\] result=(\w+) errors=(\d+) warnings=(\d+) size=(\d+) time=(\S+) out=([^\r\n]+)', log)
assert match and match[1] == 'Succeeded' and match[2] == '0'
scene_match = re.search(r'\[ShowcaseBuild\] scenes=(.*?) out=', log)
assert scene_match
scenes = scene_match[1].split(';')
assert scenes == ['Assets/Scenes/Bootstrap.unity', 'Assets/Scenes/World/TianyongSandbox.unity']
exe = output / 'mmorpg.exe'
with exe.open('rb') as stream:
    assert stream.read(2) == b'MZ'
    stream.seek(0x3C)
    offset = struct.unpack('<I', stream.read(4))[0]
    stream.seek(offset)
    assert stream.read(4) == b'PE\x00\x00'
    machine = struct.unpack('<H', stream.read(2))[0]
assert machine == 0x8664
required = ['mmorpg.exe', 'UnityPlayer.dll', 'mmorpg_Data/boot.config',
            'mmorpg_Data/globalgamemanagers', 'mmorpg_Data/level0', 'mmorpg_Data/level1',
            'mmorpg_Data/resources.assets', 'mmorpg_Data/resources.assets.resS']
for relative in required:
    assert (output / relative).is_file(), relative
rows = []
for path in sorted(output.rglob('*')):
    assert not path.is_symlink() and not path.is_junction(), str(path)
    if not path.is_file():
        continue
    before = path.stat()
    digest = sha(path)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    rows.append({'path': path.relative_to(output).as_posix(), 'bytes': after.st_size, 'sha256': digest})
before = json.loads((evidence / 'input-before.json').read_text(encoding='utf-8-sig'))
after = json.loads((evidence / 'input-after-raw.json').read_text(encoding='utf-8-sig'))
raw_settings = evidence / 'ProjectSettings.after-build.asset'
assert not raw_settings.exists()
shutil.copyfile(project / 'ProjectSettings/ProjectSettings.asset', raw_settings)
warning_lines = [line for line in log.splitlines() if re.search(r'\bwarning\b', line, re.I)]
warnings_path = evidence / 'warning-lines.txt'
with warnings_path.open('x', encoding='utf-8') as stream:
    stream.write('\n'.join(warning_lines) + '\n')
result = {
    'createdUtc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Formal Windows Development player build only. Player not launched; no server or online acceptance.',
    'output': str(output), 'executablePeMachine': '0x8664 (AMD64)',
    'buildResult': match[1], 'buildErrors': int(match[2]), 'buildWarnings': int(match[3]),
    'reportedBuildBytes': int(match[4]), 'reportedBuildTime': match[5], 'scenes': scenes,
    'playerRun': False, 'fileCount': len(rows), 'artifactBytes': sum(row['bytes'] for row in rows),
    'files': rows,
    'evidenceHashes': {name: sha(evidence / name) for name in
                       ['launch.json', 'completion.json', 'unity-build.log', 'input-before.json',
                        'input-after-raw.json', 'ProjectSettings.after-build.asset', 'warning-lines.txt', 'inventory_player.py']},
    'rawInputComparison': after['comparison'],
    'warningLineCounts': dict(Counter('Shader' if line.startswith('Shader warning') else
                                     'CSharp' if ': warning CS' in line else 'Other' for line in warning_lines))
}
with manifest_path.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'manifest': str(manifest_path), 'sha256': sha(manifest_path),
                  'files': len(rows), 'bytes': result['artifactBytes'], 'executableSha256': sha(exe),
                  'buildResult': match[1], 'warnings': int(match[3]),
                  'rawInputComparisonCounts': {name: len(after['comparison'][name]) for name in ('added','removed','changed')}}))
