"""Read-only 08 snapshot verification; writes only 08-tools/audits/*.json.

Exit 0 means file/provenance/timing checks passed, never visual approval.
Exit 1 means failed checks (including any incomplete 136-slot snapshot).
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
import re
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
REVISIONS = RECOVERY / '08-delivery-preview' / 'revisions'
DIRECTIONS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
EXPECTED = {f'walk/{d}/{f:02d}' for d in DIRECTIONS for f in range(1, 17)} | {f'idle/{d}' for d in DIRECTIONS}
EXPECTED_GIFS = {f'preview/{d}-30ms-{theme}.gif' for d in DIRECTIONS for theme in ('light', 'dark')}
DERIVED_IDENTITY_CHAINS = {
    'walk-S-11-v3': ['walk-S-10-v1'],
    'walk-S-14-v2': ['walk-S-13-v1'],
    'walk-S-15-v2': ['walk-S-16-v1', 'walk-S-01-v1'],
    'walk-S-16-v1': ['walk-S-01-v1'],
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def safe_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise argparse.ArgumentTypeError('Snapshot name must contain only letters, digits, _ or -')
    return value


class Audit:
    def __init__(self):
        self.errors, self.warnings, self.hashes = [], [], {}

    def check(self, condition, code, context, detail):
        if not condition:
            self.errors.append({'code': code, 'context': context, 'detail': detail})
        return bool(condition)

    def warn(self, code, context, detail):
        self.warnings.append({'code': code, 'context': context, 'detail': detail})

    def sha(self, path):
        path = Path(path).resolve()
        if path not in self.hashes:
            self.hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return self.hashes[path]

    def relative(self, root, value):
        path = (root / value).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Snapshot-relative path escapes snapshot: ' + str(value))
        return path

    def hash_equals(self, path, expected, context, code='sha256_mismatch'):
        actual = self.sha(path)
        self.check(actual == expected, code, context, {'file': str(path), 'expected': expected, 'actual': actual})
        return actual


def verify_derived_identity(audit, attempt, attached, identity_hashes):
    """Only the four explicitly reviewed 08 ancestry chains are permitted."""
    chain = DERIVED_IDENTITY_CHAINS.get(attempt)
    if not chain:
        return None
    before = len(audit.errors)
    records = []
    refs = list(attached)
    for ancestor in chain:
        source_dir = RECOVERY / '08-generation' / ancestor
        processed = RECOVERY / '08-delivery-preview' / 'processed' / ancestor
        raw = source_dir / 'raw.png'
        audit.check(raw.resolve() in {Path(p).resolve() for p in refs}, 'derived_identity_link', attempt, {'required_ancestor': ancestor, 'actual_references': refs})
        source = read_json(processed / 'source.json')
        generation = read_json(processed / 'raw.png.generation.json')
        raw_sha = audit.hash_equals(raw, source['raw']['sha256'], ancestor, 'identity_ancestor_raw_sha256')
        audit.check(raw_sha == generation['sha256'] and source['attempt'] == ancestor, 'identity_ancestor_record', attempt, ancestor)
        request_path, receipt_path = source_dir / 'request.json', source_dir / 'receipt.json'
        for label, path in [('request', request_path), ('receipt', receipt_path)]:
            audit.hash_equals(path, source[label]['sha256'], ancestor, 'identity_ancestor_' + label + '_sha256')
            audit.check(Path(source[label]['file']).resolve() == path.resolve(), 'identity_ancestor_path', attempt, str(path))
        request, receipt = read_json(request_path), read_json(receipt_path)
        params = request.get('parameters', request.get('actual_request', {}))
        prompt_path = source_dir / 'prompt.txt'
        audit.check(prompt_path.read_text(encoding='utf-8-sig') == params.get('prompt'), 'identity_ancestor_exact_prompt', ancestor, 'Ancestor prompt differs from actual request')
        audit.hash_equals(prompt_path, generation['prompt']['sha256'], ancestor, 'identity_ancestor_prompt_sha256')
        audit.check(bool(receipt.get('output_hint')), 'identity_ancestor_receipt', ancestor, 'Missing actual returned output hint')
        evidence = {x['sha256'] for x in generation.get('evidence', [])}
        audit.check({source['request']['sha256'], source['receipt']['sha256']}.issubset(evidence), 'identity_ancestor_evidence', ancestor, 'Missing request/receipt hashes in generation record')
        refs = params.get('referenced_image_paths', [])
        recorded = generation.get('references', [])
        audit.check([x['file'] for x in recorded] == refs, 'identity_ancestor_references', ancestor, 'Actual request reference list differs from generation record')
        for item in recorded:
            audit.hash_equals(Path(item['file']), item['sha256'], ancestor, 'identity_ancestor_reference_sha256')
        records.append({'attempt': ancestor, 'raw_file': str(raw), 'raw_sha256': raw_sha, 'request_sha256': source['request']['sha256'], 'receipt_sha256': source['receipt']['sha256'], 'prompt_sha256': generation['prompt']['sha256'], 'source_record_sha256': audit.sha(processed / 'source.json'), 'generation_record_sha256': audit.sha(processed / 'raw.png.generation.json')})
    terminals = [{'file': p, 'sha256': audit.sha(Path(p))} for p in refs if audit.sha(Path(p)) in identity_hashes]
    audit.check(bool(terminals), 'derived_identity_terminal', attempt, 'Last verified ancestor did not actually attach documented original identity or its downsample')
    if len(audit.errors) != before:
        return None
    audit.warn('derived_identity_reference', attempt, {'note': 'Original identity was not directly attached to this request; this verified chain is the actual evidence.', 'chain': records, 'terminal_identity_references': terminals})
    return {'mode': 'derived', 'chain': records, 'terminal_identity_references': terminals}


def verify_frame(audit, root, row, reference_hashes):
    slot, attempt = row['slot'], row['source_attempt']
    output = audit.relative(root, row['path'])
    source_path = audit.relative(root, row['source_record'])
    audit.hash_equals(source_path, row['source_record_sha256'], slot, 'source_record_sha256')
    source = read_json(source_path)
    evidence = source_path.parent
    audit.check(source['slot'] == slot and source['attempt'] == attempt, 'source_slot', slot, 'Source slot/attempt must match manifest')
    output_sha = audit.hash_equals(output, row['sha256'], slot, 'output_sha256')
    audit.check(source['output_sha256'] == output_sha, 'source_output_sha256', slot, 'Source and runtime output differ')
    with Image.open(output) as image:
        audit.check(image.format == 'PNG' and image.size == (1024, 1024) and image.mode == 'RGBA', 'output_format', slot, {'format': image.format, 'size': image.size, 'mode': image.mode})
        if image.mode == 'RGBA':
            alpha = image.getchannel('A')
            audit.check(alpha.getextrema()[0] == 0 and alpha.getbbox() is not None, 'output_alpha', slot, 'Need a nonempty subject and actual transparent pixels')
            w, h = image.size
            edges = [(0, 0, w, 1), (0, h - 1, w, h), (0, 0, 1, h), (w - 1, 0, w, h)]
            audit.check(all(alpha.crop(box).getextrema()[1] <= 8 for box in edges), 'opaque_subject_at_edge', slot, 'Visible alpha above 8 reaches a canvas edge')

    raw = Path(source['raw']['file'])
    raw_sha = audit.hash_equals(raw, source['raw']['sha256'], slot, 'raw_sha256')
    audit.check(row['raw'] == source['raw'], 'manifest_raw_record', slot, 'Raw evidence differs between manifest and source record')
    with Image.open(raw) as image:
        native_size = list(image.size)
        audit.check(min(image.size) >= 1024 and image.format == 'PNG' and image.mode == 'RGBA', 'native_format', slot, {'size': native_size, 'format': image.format, 'mode': image.mode})
        audit.check(native_size == source['raw']['size'], 'native_size_record', slot, 'Actual native size differs from record')
        if image.mode == 'RGBA':
            audit.check(image.getchannel('A').getextrema()[0] == 0, 'native_alpha', slot, 'Raw lacks actual transparent pixels')

    request_path, receipt_path = evidence / 'request.json', evidence / 'receipt.json'
    prompt_path = evidence / 'prompt.txt'
    for label, copied in [('request', request_path), ('receipt', receipt_path)]:
        audit.hash_equals(copied, source[label]['sha256'], slot, label + '_copy_sha256')
        audit.hash_equals(Path(source[label]['file']), source[label]['sha256'], slot, label + '_original_sha256')
    request, receipt = read_json(request_path), read_json(receipt_path)
    params = request.get('parameters', request.get('actual_request', {}))
    audit.check(request['slot'].removesuffix('.png') == slot, 'request_slot', slot, 'Request belongs to another slot')
    prompt = prompt_path.read_text(encoding='utf-8-sig')
    audit.check(prompt == params.get('prompt'), 'exact_prompt', slot, 'Prompt text does not exactly equal submitted request, including whitespace')
    audit.check(bool(receipt.get('output_hint')), 'receipt_output_hint', slot, 'Missing actual returned output_hint')
    if receipt.get('sourcePath'):
        audit.check(receipt['sourcePath'].replace('/', '\\') in receipt.get('output_hint', '').replace('/', '\\'), 'receipt_source_path', slot, 'Claimed sourcePath not present in returned hint')

    generation = read_json(evidence / 'raw.png.generation.json')
    derived = read_json(evidence / 'frame.png.generation.json')
    audit.check(generation['sha256'] == raw_sha and [generation['width'], generation['height']] == native_size, 'raw_generation_identity', slot, 'Generation metadata does not match native raw')
    audit.check(Path(generation['file']).resolve() == raw.resolve(), 'raw_generation_path', slot, 'Generation record names another raw path')
    audit.hash_equals(prompt_path, generation['prompt']['sha256'], slot, 'prompt_copy_sha256')
    audit.hash_equals(Path(generation['prompt']['file']), generation['prompt']['sha256'], slot, 'prompt_original_sha256')
    audit.check(derived['sha256'] == output_sha and derived['derivedFrom']['sha256'] == raw_sha, 'derived_identity', slot, 'Derived record has incorrect source or output hash')
    audit.check(derived['operation'] == source['operation'], 'derived_operation', slot, 'Derived operation differs from source record')
    audit.check(source['operation'].get('pose_synthesis') is False, 'pose_synthesis_record', slot, 'Source does not explicitly rule out pose synthesis')
    audit.check(source['anchor_px'] == [512.0, 942], 'anchor_record', slot, 'Unexpected recorded anchor')
    evidence_hashes = {x['sha256'] for x in generation.get('evidence', [])}
    audit.check({source['request']['sha256'], source['receipt']['sha256']}.issubset(evidence_hashes), 'generation_evidence', slot, 'Generation record lacks request/receipt hashes')

    references = params.get('referenced_image_paths', [])
    recorded_references = generation.get('references', [])
    audit.check([x['file'] for x in recorded_references] == references, 'reference_list', slot, 'Recorded references differ from actual request paths/order')
    attached_hashes = set()
    for index, reference in enumerate(references):
        digest = audit.sha(Path(reference))
        attached_hashes.add(digest)
        if index < len(recorded_references):
            audit.check(recorded_references[index].get('sha256') == digest, 'reference_sha256', slot, {'file': reference, 'actual': digest})
    identity_reference = {'mode': 'direct', 'sha256': sorted(attached_hashes & reference_hashes['identity'])}
    if not identity_reference['sha256']:
        identity_reference = verify_derived_identity(audit, attempt, references, reference_hashes['identity'])
    audit.check(bool(identity_reference), 'missing_identity_reference', slot, 'No actual direct identity attachment or complete explicitly permitted derived identity chain')
    audit.check(bool(attached_hashes & reference_hashes['style']), 'missing_style_reference', slot, 'No actual attached image matches documented style reference or original source')

    if request.get('configSnapshot'):
        audit.check(generation.get('configSnapshot') == request['configSnapshot'], 'config_snapshot', slot, 'Generation target differs from preserved request target')
    else:
        audit.warn('historical_config_not_in_request', slot, 'Request lacks config snapshot; archive-time target is not evidence of submitted parameters')
    # This batch used the built-in tool schema with no model/quality selectors.
    # A target/config string must never be promoted to an actual locked setting.
    for parameter, actual in [('model', 'actualModel'), ('quality', 'actualQuality')]:
        for label, value in [('request.parameters', params.get(parameter)), ('request.submittedParameters', request.get('submittedParameters', {}).get(parameter)), ('generation.submittedParameters', generation.get('submittedParameters', {}).get(parameter)), ('receipt', receipt.get(actual)), ('generation', generation.get(actual)), ('request', request.get(actual))]:
            audit.check(value is None, 'unsupported_locked_' + parameter, slot, {'location': label, 'value': value, 'reason': 'Built-in batch tool did not expose or return model/quality fields'})
    audit.check(generation.get('route') == 'builtin', 'generation_route', slot, 'Expected built-in route')
    audit.check(bool(generation.get('unverifiedReason')), 'model_quality_disclosure', slot, 'Missing reason for unverified actual model/quality')
    return {'slot': slot, 'attempt': attempt, 'output_sha256': output_sha, 'raw_sha256': raw_sha, 'native_size': native_size, 'reference_count': len(references), 'identity_reference': identity_reference}


def verify_gif(audit, root, row):
    path = audit.relative(root, row['path'])
    audit.hash_equals(path, row['sha256'], row['path'], 'gif_sha256')
    with Image.open(path) as gif:
        durations = []
        for index in range(gif.n_frames):
            gif.seek(index)
            durations.append(gif.info.get('duration'))
        audit.check(gif.format == 'GIF' and gif.n_frames == 16 and durations == [30] * 16, 'gif_timing', row['path'], {'frames': gif.n_frames, 'durations_ms': durations})
        audit.check(gif.info.get('loop') == 0, 'gif_loop', row['path'], 'Expected infinite loop')
    audit.check(row.get('frames') == 16 and row.get('durations_ms') == [30] * 16 and row.get('cycle_ms') == 480, 'gif_record', row['path'], 'Manifest GIF timing differs from 16 x 30 ms')
    return {'path': row['path'], 'frames': len(durations), 'durations_ms': durations, 'cycle_ms': sum(x or 0 for x in durations)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True, type=safe_name)
    parser.add_argument('--approved-snapshots', nargs='*', default=[], help='Reviewed snapshot names; space-separated and/or comma-separated. Compares exact bytes only, never grants visual approval.')
    args = parser.parse_args()
    approved_names = [safe_name(name) for value in args.approved_snapshots for name in value.split(',') if name]
    audit = Audit()
    root = REVISIONS / args.revision
    results, gifs, comparisons = [], [], []
    manifest_sha, missing, unexpected = None, sorted(EXPECTED), []
    try:
        manifest_path = root / 'manifest.json'
        manifest_sha = audit.sha(manifest_path)
        manifest = read_json(manifest_path)
        files = manifest['files']
        slots = [x['slot'] for x in files]
        missing, unexpected = sorted(EXPECTED - set(slots)), sorted(set(slots) - EXPECTED)
        audit.check(len(files) == 136 and not missing and not unexpected and len(set(slots)) == 136, 'complete_136_slots', args.revision, {'actual': len(files), 'missing': missing, 'unexpected': unexpected, 'duplicate_slots': [k for k, v in Counter(slots).items() if v > 1]})
        audit.check(manifest.get('actual_walk') == 128 and manifest.get('actual_idle') == 8, 'manifest_counts', args.revision, {'walk': manifest.get('actual_walk'), 'idle': manifest.get('actual_idle')})
        audit.check(manifest.get('frame_duration_ms') == 30 and manifest.get('cycle_duration_ms') == 480, 'manifest_timing', args.revision, 'Expected 30 ms / frame, 480 ms / cycle')
        reference_hashes = {'identity': set(), 'style': set()}
        refs_root = RECOVERY / '08-generation' / 'references'
        for entry in read_json(refs_root / 'sources.json'):
            role = 'identity' if 'identity' in entry['file'].lower() else 'style' if 'style' in entry['file'].lower() else None
            if role:
                audit.hash_equals(refs_root / entry['file'], entry['sha256'], role, 'canonical_reference_sha256')
                reference_hashes[role].update(x for x in [entry.get('sha256'), entry.get('sourceSha256')] if x)
        for row in files:
            try:
                results.append(verify_frame(audit, root, row, reference_hashes))
            except Exception as exc:
                audit.check(False, 'frame_exception', row.get('slot', 'unknown'), f'{type(exc).__name__}: {exc}')
        for key in ('output_sha256', 'raw_sha256'):
            duplicates = [value for value, count in Counter(x[key] for x in results).items() if count > 1]
            audit.check(not duplicates, 'duplicate_' + key, args.revision, duplicates)
        audit.check(len(results) == 136, 'verified_frame_count', args.revision, {'verified': len(results), 'required': 136})
        gif_rows = manifest.get('gifs', [])
        gif_paths = [x['path'] for x in gif_rows]
        audit.check(set(gif_paths) == EXPECTED_GIFS and len(gif_paths) == 16, 'complete_gifs', args.revision, {'actual': len(gif_paths), 'missing': sorted(EXPECTED_GIFS - set(gif_paths))})
        for row in gif_rows:
            try:
                gifs.append(verify_gif(audit, root, row))
            except Exception as exc:
                audit.check(False, 'gif_exception', row.get('path', 'unknown'), f'{type(exc).__name__}: {exc}')

        approved = {}
        for name in approved_names:
            approved_root = REVISIONS / name
            approved_path = approved_root / 'manifest.json'
            approved_manifest = read_json(approved_path)
            comparisons.append({'revision': name, 'manifest_sha256': audit.sha(approved_path), 'files': len(approved_manifest['files'])})
            for row in approved_manifest['files']:
                value = (row['sha256'], row['raw']['sha256'])
                audit.hash_equals(audit.relative(approved_root, row['path']), value[0], name + ':' + row['slot'], 'approved_snapshot_output_sha256')
                if row['slot'] in approved:
                    audit.check(approved[row['slot']] == value, 'conflicting_approved_snapshots', row['slot'], {'existing': approved[row['slot']], 'new': value, 'revision': name})
                approved[row['slot']] = value
        if approved_names:
            for row in results:
                value = (row['output_sha256'], row['raw_sha256'])
                audit.check(approved.get(row['slot']) == value, 'approved_snapshot_comparison', row['slot'], {'approved': approved.get(row['slot']), 'current': value})
        else:
            audit.warn('no_approved_snapshots', args.revision, 'No prior reviewed pixel snapshots supplied for byte comparison')
    except Exception as exc:
        audit.check(False, 'snapshot_exception', args.revision, f'{type(exc).__name__}: {exc}')

    report = {'schema': 'qdao-08-final-file-audit-v1', 'revision': args.revision, 'auditedAt': datetime.now(timezone.utc).isoformat(), 'manifest_sha256': manifest_sha, 'verifier_sha256': audit.sha(Path(__file__)), 'status': 'passed_file_checks_only' if not audit.errors else 'failed', 'complete_inventory': not missing and not unexpected and len(results) == 136, 'missing_slots': missing, 'unexpected_slots': unexpected, 'verified_frames': len(results), 'unique_output_sha256': len({x['output_sha256'] for x in results}), 'unique_raw_sha256': len({x['raw_sha256'] for x in results}), 'errors': audit.errors, 'warnings': audit.warnings, 'files': results, 'gifs': gifs, 'approved_snapshot_comparisons': comparisons, 'visual_approval': False, 'browser_review_performed': False, 'unity_validation': False, 'limitations': ['Checks files, provenance records and encoded GIF timing; does not prove aesthetic quality, gait correctness or actual browser playback timing.', 'Unique hashes do not independently prove every pose was newly drawn; generation evidence and visual review remain required.', 'Source originals and reference inputs must still exist for this verification. Run before cleanup; an old pass cannot claim deleted sources were rechecked.']}
    dest = HERE / 'audits' / (args.revision + '-file-audit.json')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(dest), 'status': report['status'], 'verified_frames': len(results), 'errors': len(audit.errors), 'warnings': len(audit.warnings), 'error_codes': sorted({x['code'] for x in audit.errors}), 'visual_approval': False}, ensure_ascii=False))
    return 1 if audit.errors else 0


if __name__ == '__main__':
    sys.exit(main())
