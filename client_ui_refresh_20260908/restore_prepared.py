"""Restore verified prepared PNG copies without touching the Unity client."""
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREFIX = 'client_ui_refresh_20260908/prepared/'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def within_root(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Path is outside the image repository: {path}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true', help='Restore missing copies; never overwrite changed files')
    parser.add_argument('--output-dir', type=Path, default=HERE / 'prepared', help='Optional verification directory inside the image repository')
    args = parser.parse_args()
    output = within_root(args.output_dir)
    # An alternate directory is restricted to scratch space to avoid overwriting sources.
    if output != HERE / 'prepared' and not output.is_relative_to(ROOT / '.work'):
        raise ValueError('An alternate output directory must be inside .work')
    ledger = json.loads((HERE / 'cleanup-20260920.json').read_text(encoding='utf-8'))
    pending = []
    existing = 0
    for entry in ledger['prepared']:
        if not entry['path'].startswith(PREFIX):
            raise ValueError('Unexpected prepared path in cleanup ledger')
        source = within_root(ROOT / entry['restore_from'])
        target = within_root(output / entry['path'][len(PREFIX):])
        if not target.is_relative_to(output):
            raise ValueError('Prepared target escapes the selected output directory')
        if digest(source) != entry['sha256']:
            raise ValueError(f'Recovery source changed: {source}')
        if target.exists():
            if not target.is_file() or digest(target) != entry['sha256']:
                raise ValueError(f'Existing file differs; refusing to overwrite: {target}')
            existing += 1
        else:
            pending.append((source, target, entry['sha256']))
    # Check every source and existing destination before creating any file.
    if args.restore:
        for source, target, expected in pending:
            data = source.read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f'Recovery source changed during restore: {source}')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            if digest(target) != expected:
                raise ValueError(f'Restored file failed verification: {target}')
    print(json.dumps({'mode': 'restore' if args.restore else 'check',
                      'verified_sources': len(ledger['prepared']), 'existing': existing,
                      'missing': 0 if args.restore else len(pending),
                      'restored': len(pending) if args.restore else 0,
                      'client_written': False}))


if __name__ == '__main__':
    main()
