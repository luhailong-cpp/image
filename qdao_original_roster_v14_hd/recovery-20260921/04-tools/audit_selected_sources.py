"""Audit the selected 24 HD files in isolated shadows; never edit historical evidence."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, itertools
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
RECOVERY = ROOT / 'recovery-20260921'
SNAPSHOT = RECOVERY / '04-delivery-preview/revisions/review-set-v3'
OUT = RECOVERY / '04-tools/source-audit'
CHAR = '04_mountain_guardian_boy'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

restorations = []
def exact_copy(source, target, expected=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if expected and hashlib.sha256(data).hexdigest() != expected:
        normalized = data.replace(b'\r\n', b'\n')
        variants = [normalized, normalized.replace(b'\n', b'\r\n')]
        for core in list(variants):
            for count in range(5):
                for suffix in itertools.product([b'\n', b'\r\n'], repeat=count):
                    variants.append(core.rstrip(b'\r\n') + b''.join(suffix))
        found = next((v for v in variants if hashlib.sha256(v).hexdigest() == expected), None)
        if found is None:
            raise ValueError('Cannot restore expected hash by line endings: ' + str(source))
        restorations.append({'source': str(source), 'source_sha256': sha(source),
                             'shadow': str(target), 'restored_sha256': expected,
                             'method': 'exact_recorded_hash_matched_LF_CRLF_including_trailing_newlines_only'})
        data = found
    target.write_bytes(data)

def main():
    OUT.mkdir(exist_ok=True)
    manifest = read(SNAPSHOT / 'manifest.json')
    expected_manifest = '77f6a60a37f2016a8643150a34921bd389f253c1a92e534a3adc303125182737'
    assert sha(SNAPSHOT / 'manifest.json') == expected_manifest
    rows = [r for r in manifest['files'] if r['size'] == [1024, 1024]]
    assert len(rows) == 24
    groups, results = {}, []
    for row in rows:
        source_root = Path(row['source_record_file']).parents[1]
        if str(source_root) not in groups:
            shadow_root = OUT / 'shadow' / f'group-{len(groups)+1:02d}'
            out = shadow_root / 'candidate' / CHAR
            original_manifest = read(source_root / 'manifest.json')
            for rel in ['manifest.json', 'qc.json', 'processing/scale-profile.json']:
                exact_copy(source_root / rel, out / rel)
            exact_copy(source_root / 'processing/frame-sources.json', out / 'processing/frame-sources.json', original_manifest['sources_sha256'])
            groups[str(source_root)] = shadow_root
        out = groups[str(source_root)] / 'candidate' / CHAR
        record = row['source_record']
        exact_copy(Path(row['source']), out / row['path'], row['sha256'])
        for spec in [record['source'], record['prompt'], record['generation']['receipt'], *record['stages'].values()]:
            exact_copy(source_root / spec['path'], out / spec['path'], spec['sha256'])

    for row in rows:
        source_root = Path(row['source_record_file']).parents[1]
        shadow_root = groups[str(source_root)]
        verifier = module('selected_independent_verify', ROOT / 'tools/verify.py')
        verifier.ROOT = shadow_root
        verifier.mod = lambda name: module('selected_vendor_' + name, ROOT / 'tools/vendor' / (name + '.py'))
        record = row['source_record']
        try:
            result = verifier.verify(CHAR, record['direction'], False, record['frame'])
            status, error = 'passed', None
        except Exception as exc:
            result, status, error = None, 'failed', str(exc)
        results.append({'slot': row['path'], 'output_sha256': row['sha256'],
                        'snapshot_sha_matches': sha(SNAPSHOT / 'runtime' / row['path']) == row['sha256'],
                        'original_source_root': str(source_root), 'shadow_root': str(shadow_root),
                        'status': status, 'error': error, 'independent_reconstruction': result})
        print(row['path'], status, error or '', flush=True)
    passed = sum(r['status'] == 'passed' and r['snapshot_sha_matches'] for r in results)
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'manifest_sha256': expected_manifest, 'selected_hd_frames': len(rows),
              'independent_reconstruction_passed': passed,
              'historical_files_modified': False, 'new_images_generated': 0,
              'line_ending_shadow_restorations': restorations, 'frames': results,
              'limits': ['Historical E:/ and old user default-output paths were not fabricated.',
                         'Shadow reconstruction proves recorded pixels and exact historical hashes; it is not strict mixed-assembly receipt approval.',
                         'No C2PA signature or actual model identity verification; no formal client or Unity approval.']}
    (OUT / 'selected-source-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'README.md').write_text(f'# 04 selected-source audit\n\n固定review-set-v3的24张HD独立重建：{passed}/24通过。\n\n只在shadow副本将LF/CRLF恢复至历史已记录的精确SHA，原证据未改。详见selected-source-audit.json。历史路径与实际型号限制仍保留，不代表严格mixed assembly或正式发布批准。\n', encoding='utf-8')
    assert passed == 24, 'Selected source audit incomplete'

if __name__ == '__main__': main()
