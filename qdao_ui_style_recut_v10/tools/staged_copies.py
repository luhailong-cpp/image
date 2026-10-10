"""Read or restore hash-verified UI staging copies. Default CLI is read-only."""
from pathlib import Path
from functools import lru_cache
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / 'docs/ui-cleanup-20260920/cleanup.json'
STAGES = ('qdao_ui_style_recut_v10/staged/',
          'qdao_festival_refinement_20260910/scenes-sync/server/staged/')
SOURCES = ('q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/',
           'q_daoist_login_ui_uncropped_highres_final_layers/')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inside(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f'Path escapes {base}: {relative}')
    return path


@lru_cache(maxsize=1)
def entries():
    rows = json.loads(LEDGER.read_text(encoding='utf-8'))['entries']
    result = {}
    for row in rows:
        source = row['restore_from']
        if not source.startswith(SOURCES) or Path(source).suffix not in ('.png', '.svg'):
            raise ValueError(f'Unexpected recovery source: {source}')
        if row['path'] not in [prefix + source for prefix in STAGES]:
            raise ValueError(f'Unexpected staging path: {row["path"]}')
        inside(ROOT, source)
        inside(ROOT, row['path'])
        if row['path'] in result:
            raise ValueError('Duplicate cleanup ledger entry')
        result[row['path']] = row
    return result


def verified_source(row):
    source = inside(ROOT, row['restore_from'])
    if source.stat().st_size != row['bytes'] or digest(source) != row['sha256']:
        raise ValueError(f'Recovery source changed; rebuild and review staging: {source}')
    return source


def resolve_read(path):
    """Read fallback only; never redirect a write or trust a changed source."""
    path = path.resolve()
    relative = path.relative_to(ROOT).as_posix()
    if path.exists() or not relative.startswith(STAGES):
        return path
    row = entries().get(relative)
    return verified_source(row) if row else path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=ROOT,
                        help='Repository root or isolated .work directory; keeps full relative paths')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output != ROOT and not output.is_relative_to(ROOT / '.work'):
        parser.error('Alternate output must be under the image repository .work directory')
    pending = []
    existing = 0
    for row in entries().values():
        source = verified_source(row)
        target = inside(output, row['path'])
        if target.exists():
            if not target.is_file() or digest(target) != row['sha256']:
                raise ValueError(f'Refusing to overwrite changed destination: {target}')
            existing += 1
        else:
            pending.append((source, target, row))
    # Preflight every source and destination before writing the first byte.
    if args.restore:
        for source, target, row in pending:
            data = source.read_bytes()
            if hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError(f'Source changed during recovery: {source}')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            if digest(target) != row['sha256']:
                raise ValueError(f'Restored file failed verification: {target}')
    print(json.dumps({'mode': 'restore' if args.restore else 'check',
                      'verified_sources': len(entries()), 'existing': existing,
                      'missing': 0 if args.restore else len(pending),
                      'restored': len(pending) if args.restore else 0,
                      'client_written': False}))


if __name__ == '__main__':
    main()
