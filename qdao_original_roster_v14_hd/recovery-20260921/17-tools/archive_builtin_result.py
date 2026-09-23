"""Archive a successful actual built-in result without inventing its fields."""
from pathlib import Path
import argparse, json, shutil
from common import *

def explicit_result_value(result, keys):
    for key in keys:
        value = result.get(key)
        if isinstance(value, str) and value and 'unverified' not in value and value != 'host-managed':
            return value, key
    return None, None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--local-result-path', '--original', dest='original', type=Path, required=True)
    parser.add_argument('--tool-result', type=Path, required=True, help='Exact actual tool metadata JSON; no invented hint/model fields')
    parser.add_argument('--completed-at', help='Actual completion timestamp if already recorded; otherwise archival observation time')
    parser.add_argument('--kind', choices=('walk', 'idle'), help='Explicit slot for an older request schema; recorded separately without rewriting request')
    parser.add_argument('--direction', choices=DIRS)
    parser.add_argument('--frame', type=int)
    args = parser.parse_args()
    archive = archive_path(args.archive)
    original_request = read(archive / 'request.json')
    original_references = original_request.get('referenced_image_paths', [])
    if 'actual_request' not in original_request and original_references and all(isinstance(r, str) for r in original_references):
        binding_file = archive / 'reference-bindings.json'
        if not binding_file.exists():
            references = []
            for value in original_references:
                path = Path(value).resolve()
                require(path.is_file() and path.is_relative_to(IMAGE_ROOT), 'Actual reference missing or outside workspace')
                references.append({'path': value, 'sha256': sha(path), 'hashBinding': 'after-generation-current-file-only'})
            save_new(binding_file, {'request_sha256': sha(archive / 'request.json'), 'capturedAt': now(),
                'timing': 'after_generation', 'references': references,
                'note': 'These hashes were measured after generation; they do not establish reference bytes at request start.'})
    if args.kind:
        binding = {'kind': args.kind, 'direction': args.direction, 'frame': args.frame,
                   'slot': slot(args.kind, args.direction, args.frame), 'request_sha256': sha(archive / 'request.json'),
                   'recordedAt': now(), 'basis': 'explicit caller assignment; original request preserved byte-exact'}
        if (archive / 'slot.json').exists():
            previous = read(archive / 'slot.json')
            require(all(previous[k] == binding[k] for k in ('kind', 'direction', 'frame', 'slot', 'request_sha256')), 'Existing slot binding differs')
        else:
            save_new(archive / 'slot.json', binding)
    request = request_data(archive)
    result = read(args.tool_result)
    require(isinstance(result, dict), 'Tool metadata must be a JSON object')
    original = args.original.resolve()
    require(original.is_file(), 'Actual returned image path is missing')
    identity = image_identity(original)
    require(identity['format'] == 'PNG' and min(identity['width'], identity['height']) >= 1024,
            'Require a real native complete PNG frame with both dimensions at least 1024')
    names = ('generation-receipt.json', 'provenance.json', 'raw.png.generation.json')
    require(not any((archive / name).exists() for name in names), 'Immutable archive already exists; use a new attempt')
    destination_result = archive / 'tool-result.json'
    if destination_result.exists():
        require(destination_result.read_bytes() == args.tool_result.read_bytes(), 'Existing actual tool metadata differs')
    else:
        shutil.copy2(args.tool_result, destination_result)
    if (archive / 'raw.png').exists():
        require(sha(original) == sha(archive / 'raw.png'), 'Existing archived raw differs from actual output')
    else:
        shutil.copy2(original, archive / 'raw.png')
    require(sha(original) == sha(archive / 'raw.png'), 'Raw copy differs')
    provenance_module = module('ghost_provenance', PACKAGE / 'tools/inspect_image_provenance.py')
    provenance = provenance_module.inspect_image(archive / 'raw.png')
    save_new(archive / 'provenance.json', provenance)
    hint = result.get('output_hint')
    if hint is not None:
        require(isinstance(hint, str), 'Actual output_hint must be text')
    reported_path = result.get('local_result_path')
    if reported_path:
        require(Path(reported_path).resolve() == original, 'Actual local_result_path differs from supplied original')
    completed = args.completed_at or now()
    require(datetime.fromisoformat(completed.replace('Z', '+00:00')).tzinfo is not None, 'Completion timestamp needs timezone')
    actual_model, model_field = explicit_result_value(result, ('actualModel', 'actual_model', 'model'))
    actual_quality, quality_field = explicit_result_value(result, ('actualQuality', 'actual_quality', 'quality'))
    receipt = {**request, 'status': 'generated_pending_review', 'generation_calls': 1, 'paid_api_calls': 0,
        'completed_at': completed, 'completed_at_basis': 'caller_recorded_tool_completion' if args.completed_at else 'archive_observation_after_tool_return',
        'original_generated_file': str(original), 'original_sha256': sha(original),
        'output_hint': hint, 'actual_tool_result_file': str(destination_result),
        'actual_tool_result_sha256': sha(destination_result),
        'original_path_binding': 'actual_tool_local_result_path' if reported_path else 'caller_supplied_actual_local_result_path',
        'actual_model': actual_model or 'host-managed-unverified', 'actual_quality': actual_quality,
        'note': 'Tool metadata is retained byte-exact. Missing output hint, model or quality is not invented. Default original retained.'}
    save_new(archive / 'generation-receipt.json', receipt)
    metadata = {**image_identity(archive / 'raw.png'), 'schemaVersion': 1, 'generatedAt': completed,
        'generatedAtBasis': receipt['completed_at_basis'], 'recordedAt': now(), 'tool': 'built-in image_gen', 'route': 'builtin',
        'configSnapshot': request.get('configSnapshot'), 'submittedParameters': {'model': None, 'quality': None},
        'actualModel': actual_model, 'actualQuality': actual_quality,
        'unverifiedReason': UNVERIFIED if not (actual_model and actual_quality) else None,
        'prompt': {'path': str(archive / 'prompt.txt'), 'sha256': sha(archive / 'prompt.txt'), 'exactActualRequestMatch': True},
        'references': request.get('reference_bindings_at_start', []) + request.get('reference_bindings_after_generation', []),
        'referenceHashTiming': 'request-start' if request.get('reference_bindings_at_start') else 'after-generation-current-file-only',
        'evidence': {'request': {'path': str(archive / 'request.json'), 'sha256': sha(archive / 'request.json')},
                     'receipt': {'path': str(archive / 'generation-receipt.json'), 'sha256': sha(archive / 'generation-receipt.json')},
                     'toolResult': {'path': str(destination_result), 'sha256': sha(destination_result), 'modelField': model_field, 'qualityField': quality_field},
                     'provenance': {'path': str(archive / 'provenance.json'), 'sha256': sha(archive / 'provenance.json'), 'signatureVerified': False},
                     'originalGeneratedFile': {'path': str(original), 'sha256': sha(original)}, 'outputHint': hint},
        'generationCalls': 1, 'paidApiCalls': 0, 'visualApproval': False}
    save_new(archive / 'raw.png.generation.json', metadata)
    print(json.dumps({'archive': str(archive), 'slot': request['slot'], 'raw_sha256': sha(archive / 'raw.png'),
                      'native_size': provenance['native_size'], 'actual_model': actual_model, 'actual_quality': actual_quality,
                      'visual_review': 'pending'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
