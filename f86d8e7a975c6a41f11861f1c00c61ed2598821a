"""Sync or verify v9 portraits in this repository's existing import-preparation folder.

This tool never opens or writes the actual client project or Unity metadata.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREPARATION = ROOT / 'client_ui_refresh_20260908'
REPORT = HERE / 'prepared_sync.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify only; do not write any files')
    args = parser.parse_args()
    manifest = read(HERE / 'manifest.json')
    portraits = [r for r in manifest['assets'] if 'age_direction' in r]
    assert len(portraits) == 22
    inventory_path = PREPARATION / 'assets_manifest.json'
    inventory = read(inventory_path)
    mappings = {r['source']: r for r in inventory['records'] if r.get('category') == 'profession_portrait'}
    assert len(mappings) == 22
    prior_report = read(REPORT) if REPORT.exists() else None
    prior_rows = {r['source']: r for r in prior_report['records']} if prior_report else {}
    records = []
    for portrait in portraits:
        relative = 'q_daoist_character_pack_4096/' + portrait['path']
        source = ROOT / relative
        mapping = mappings[relative]
        expected_target = 'UI/qdao_v3/characters/' + portrait['path'].replace('_transparent_4096.png', '_v3.png')
        assert mapping['target'] == expected_target
        assert mapping['staged'] == 'prepared/' + expected_target
        destination = (PREPARATION / mapping['staged']).resolve()
        assert destination.is_relative_to((PREPARATION / 'prepared/UI/qdao_v3/characters').resolve())
        assert destination.is_file() and sha(source) == portrait['sha256']
        old_sha = sha(destination)
        with Image.open(source) as original, Image.open(destination) as current:
            assert original.size == (4096, 4096) and original.mode == 'RGBA'
            assert current.size == (1024, 1024) and current.mode == 'RGBA'
            desired = original.resize(current.size, Image.Resampling.LANCZOS)
            identical = desired.tobytes() == current.tobytes()
        if args.check:
            assert identical, 'Prepared pixels are stale: ' + expected_target
            assert mapping['source_sha256'] == sha(source)
            assert mapping['staged_sha256'] == old_sha
            assert prior_rows[relative]['source_sha256'] == sha(source)
            assert prior_rows[relative]['output_sha256'] == old_sha
        elif not identical:
            desired.save(destination, optimize=True)
        with Image.open(destination) as output:
            assert output.mode == 'RGBA' and output.size == (1024, 1024)
            assert output.tobytes() == desired.tobytes()
            assert output.getchannel('A').getextrema() == (0, 255)
            bounds = output.getchannel('A').getbbox()
            assert bounds and min(bounds[0], bounds[1], 1024-bounds[2], 1024-bounds[3]) > 4
        row = {'source': relative, 'source_sha256': sha(source), 'source_size': [4096, 4096],
               'target': expected_target, 'output': destination.relative_to(ROOT).as_posix(),
               'output_sha256': sha(destination), 'size': [1024, 1024], 'mode': 'RGBA',
               'alpha_range': [0, 255], 'subject_bounds': list(bounds),
               'method': 'LANCZOS_resample', 'pixel_exact_to_current_source_resize': True,
               'previous_prepared_sha256': prior_rows.get(relative, {}).get('previous_prepared_sha256', old_sha),
               'historical_client_sha256': mapping.get('client_sha256'), 'client_checked': False,
               'client_sync_status': 'pending_client_sync'}
        records.append(row)
    if args.check:
        assert prior_report['status'] == 'passed' and len(prior_report['records']) == 22
        print('PASS: 22 prepared portraits match current v9 pixels, size, alpha and recorded hashes')
        return
    # Re-read the shared inventory only when ready to update these 22 entries.
    inventory = read(inventory_path)
    by_target = {r['target']: r for r in inventory['records']}
    for row in records:
        entry = by_target[row['target']]
        assert entry['source'] == row['source']
        assert sha(ROOT / row['source']) == row['source_sha256']
        assert sha(ROOT / row['output']) == row['output_sha256']
        entry.update(source_sha256=row['source_sha256'], staged_sha256=row['output_sha256'],
                     source_size=[4096, 4096], size=[1024, 1024], mode='RGBA', alpha_range=[0, 255],
                     method='LANCZOS_resample', status='pending_client_sync',
                     prepared_revision='v9-character-diversity', client_verification='historical_not_rechecked',
                     prepared_update_record='../qdao_character_diversity_v9/prepared_sync.json')
        # client_sha256, baseline_sha256 and Unity metadata remain historical evidence.
    inventory['prepared_update_status'] = 'pending_client_sync'
    inventory['v9_portrait_preparation'] = {'count': 22, 'status': 'prepared_verified',
        'record': '../qdao_character_diversity_v9/prepared_sync.json', 'client_checked': False}
    write(inventory_path, inventory)
    write(REPORT, {'date': '2026-09-11', 'status': 'passed', 'count': 22,
                  'scope': 'Existing repository-local prepared profession portrait PNGs only',
                  'all_original_target_paths_and_sizes_preserved': True,
                  'all_current_source_pixels_verified': True, 'client_checked': False,
                  'client_written': False, 'meta_files_written': False,
                  'records': records})
    print('Prepared 22 current v9 portraits; actual client and .meta files were not accessed')


if __name__ == '__main__':
    main()
