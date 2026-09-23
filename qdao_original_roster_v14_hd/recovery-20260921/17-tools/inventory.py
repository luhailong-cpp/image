"""Enumerate 17 archives and imports without selecting or approving an attempt."""
from pathlib import Path
import argparse, json
from common import *

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    expected = [*[f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1, 17)], *[f'idle/{d}.png' for d in DIRS]]
    imports, archives = [], []
    for path in sorted((HERE / 'staging').glob('*/candidate/' + CHAR + '/import-result.json')):
        record = read(path)
        destination = Path(record['path'])
        imports.append({'import_result': str(path), **record, 'current_sha_matches': destination.is_file() and sha(destination) == record['sha256']})
    for path in sorted(GEN.glob('*/request.json')):
        archive = path.parent
        archives.append({'attempt': archive.name, 'archive': str(archive),
            'files': {name: (archive / name).is_file() for name in ('raw.png', 'prompt.txt', 'request.json', 'tool-result.json', 'generation-receipt.json', 'raw.png.generation.json')},
            'slot': read(archive / 'slot.json').get('slot') if (archive / 'slot.json').exists() else read(path).get('slot')})
    byslot = {key: [row['import_result'] for row in imports if row['slot'] == key] for key in expected}
    report = {'character_id': CHAR, 'capturedAt': now(), 'target_walk': 128, 'target_idle': 8,
        'imported_unique_slots': sum(bool(rows) for rows in byslot.values()), 'attempts': archives,
        'imports': imports, 'candidate_imports_by_slot': byslot,
        'missing_imported_slots': [key for key, rows in byslot.items() if not rows],
        'ambiguous_multiple_attempt_slots': [key for key, rows in byslot.items() if len(rows) > 1],
        'selection_performed': False, 'visual_approval': False}
    if args.output:
        target = args.output.resolve()
        require(target.is_relative_to(HERE) or target.is_relative_to(RECOVERY / '17-delivery-preview'), 'Inventory output must remain in 17 tool/preview directories')
        save_new(target, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
