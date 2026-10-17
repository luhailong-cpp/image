import hashlib
import json
from pathlib import Path
import subprocess

root = Path('E:/work/xuanming-server-mmo')
out = Path(__file__).parent
git = ['git', '-c', 'safe.directory=' + root.as_posix(), '-C', str(root)]
records = []
prefix = root.as_posix().lower() + '/'
for line in (out / 'deployed-pdb-sources.txt').read_text(encoding='utf-8-sig').splitlines():
    source, kind, digest = line.split('|')
    source = source.replace('\\', '/')
    if source.lower().startswith(prefix):
        records.append((source[len(prefix):], int(kind), digest))

results = []
for revision in ['c4b8c0914610a59d3770e4ef2320e388acf52de9', '85133f9f45a548822894d28492febc805a830e99', '1ad634443d4d5028075d6b7e839b434018bfb0e8']:
    names = subprocess.check_output(git + ['ls-tree', '-r', '--name-only', revision]).decode().splitlines()
    paths = {name.lower(): name for name in names}
    process = subprocess.Popen(git + ['cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    matched, missing, mismatches = [], [], []
    for name, kind, digest in records:
        canonical = paths.get(name.lower())
        if canonical is None:
            missing.append(name)
            continue
        process.stdin.write((revision + ':' + canonical + '\n').encode())
        process.stdin.flush()
        header = process.stdout.readline().decode().strip().split()
        body = process.stdout.read(int(header[2]))
        assert process.stdout.read(1) == b'\n'
        algorithm = {1: 'md5', 2: 'sha1', 3: 'sha256'}.get(kind)
        if algorithm is None:
            mismatches.append({'path': canonical, 'reason': 'unknown checksum ' + str(kind)})
            continue
        # Git 的文本换行转换不改变源码内容，分别核对 LF 与 CRLF 落盘字节。
        lf = body.replace(b'\r\n', b'\n')
        variants = [body, lf, lf.replace(b'\n', b'\r\n')]
        if any(hashlib.new(algorithm, variant).hexdigest() == digest for variant in variants):
            matched.append(canonical)
        else:
            mismatches.append({'path': canonical, 'pdbSha': digest})
    process.stdin.close()
    process.wait()
    result = {'revision': revision, 'pdbProjectRows': len(records), 'matched': len(matched),
              'missing': sorted(set(missing)), 'mismatches': mismatches}
    results.append(result)
    print(json.dumps({'revision': revision, 'matched': len(matched), 'missing': len(set(missing)),
                      'mismatches': len(mismatches)}, ensure_ascii=False))
(out / 'deployed-baseline-comparison.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
