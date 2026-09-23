"""Read-only safety baseline for mixed-resolution source work, not Unity test evidence."""
from pathlib import Path
import hashlib
import json
import argparse
from datetime import datetime, timezone
import mixed_workspace

FORMAL = mixed_workspace.FORMAL
PRIOR = mixed_workspace.ROOT.parent / 'qdao_original_roster_v13/runtime-validation/hd-publication-gates-run1/final-result-review.json'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__ + ' A new capture never replaces the publisher pinned historical baseline.')
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    OUT = args.output_directory.resolve()
    if not OUT.is_relative_to((mixed_workspace.ROOT / 'mixed-preparation').resolve()):
        raise ValueError('New safety snapshots must stay under mixed-preparation, away from historical run baselines')
    target = OUT / 'formal-safety-baseline.json'
    if target.exists():
        raise ValueError('Preserve previous evidence; baseline already exists')
    prior = json.loads(PRIOR.read_text(encoding='utf-8-sig'))
    code = [row['path'] for row in prior['source_and_camera_bindings']]
    root = FORMAL / 'Assets/Resources/World/Characters'
    resources = sorted(p.relative_to(FORMAL).as_posix() for p in root.rglob('*') if p.is_file())
    rows = []
    for relative in sorted(set(code + resources)):
        path = FORMAL / relative
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Linked input: ' + relative)
        before = path.stat()
        digest = sha(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Input changed while reading: ' + relative)
        rows.append(dict(path=relative, sha256=digest, bytes=after.st_size))
    OUT.mkdir(parents=True, exist_ok=True)
    for relative in code:
        destination = OUT / 'before-code' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = (FORMAL / relative).read_bytes()
        expected = next(row['sha256'] for row in rows if row['path'] == relative)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Source changed before backup: ' + relative)
        destination.write_bytes(data)
    result = dict(schema=1, created_utc=datetime.now(timezone.utc).isoformat(), project=str(FORMAL),
        scope='Read-only source/character safety audit; not a closed-Unity test-input snapshot',
        unity_lock_present=(FORMAL / 'Temp/UnityLockfile').exists(),
        source_paths=code, character_resource_count=len(resources), files=rows,
        prior_review_sha256=sha(PRIOR))
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(target), sha256=sha(target), resources=len(resources), sources=len(code))))

if __name__ == '__main__':
    main()
