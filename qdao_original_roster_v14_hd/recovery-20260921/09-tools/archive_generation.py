"""Archive one real successful built-in result. Never calls an image model."""
import argparse
import importlib.util
import json
from pathlib import Path
from PIL import Image
from common import (GENERATION, IMAGE_ROOT, PACKAGE, CHARACTER, inside,
                    immutable_bytes, immutable_json, read_json, require, sha, utc_now)


def actual_field(result, names):
    for name in names:
        if result.get(name) is not None:
            return result[name], name
    return None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--tool-result', type=Path, required=True,
                        help='Exact JSON result metadata including the real output_hint')
    parser.add_argument('--request', type=Path,
                        help='Successful request JSON; default archive/request.json; useful after a failed input retry')
    args = parser.parse_args()
    archive = inside(args.archive, GENERATION, 'Archive')
    request_path = (args.request or archive / 'request.json').resolve()
    require(request_path.is_relative_to(archive), 'Successful request must be saved in its own archive')
    request = read_json(request_path)
    actual = request['actual_request']
    prompt = actual['prompt']
    require(isinstance(prompt, str) and bool(prompt), 'Need exact nonempty actual_request.prompt')
    started = request.get('started_at_utc') or request.get('started_at') or actual.get('started_at')
    require(started, 'Request must record the actual call start timestamp')
    result = read_json(args.tool_result)
    hint = result.get('output_hint')
    require(isinstance(hint, str) and bool(hint), 'Need actual tool output_hint')
    original = args.original.resolve()
    require(original.is_file(), 'Original result image does not exist')
    # Compare slash-normalized path spellings, without inventing a path from metadata.
    require(str(original).replace('\\', '/').lower() in hint.replace('\\', '/').lower(),
            'Original path is not bound by the real tool output_hint')
    for name in ('generation.json', 'generation-receipt.json'):
        require(not (archive / name).exists(), 'Result already archived; preserve it and use a new attempt: ' + name)
    if (archive / 'raw.png').exists():
        require(sha(archive / 'raw.png') == sha(original),
                'Precopied raw differs from original; preserve it and use a separate attempt')
    with Image.open(original) as image:
        size, mode, fmt = list(image.size), image.mode, image.format
        alpha_range = list(image.convert('RGBA').getchannel('A').getextrema())
    require(fmt == 'PNG', 'Archive expects the original PNG result')
    refs = []
    start_bindings = request.get('reference_bindings_at_start') or request.get('referenceBindingsAtStart') or []
    expected = {str(Path(item['path']).resolve()): item['sha256'] for item in start_bindings}
    for index, value in enumerate(actual.get('referenced_image_paths') or []):
        path = inside(value, IMAGE_ROOT, 'Reference')
        require(path.is_file(), 'Reference is missing: ' + str(path))
        digest = sha(path)
        if expected:
            require(expected.get(str(path)) == digest, 'Reference changed after request preparation: ' + str(path))
        refs.append({'path': str(path), 'sha256': digest, 'order': index + 1,
                     'purpose': 'Reference ' + str(index + 1) + '; exact usage is specified by the saved prompt',
                     'shaEvidenceTime': 'at_request_start_and_archive' if expected else 'at_archive_only'})
    require(refs or actual.get('num_last_images_to_include'), 'Request has no recorded identity/style image input')
    config = request.get('configSnapshot') or request.get('config_snapshot')
    config_timing = 'request_snapshot'
    if config is None:
        config = read_json(IMAGE_ROOT / 'config/image-generation.json')
        config_timing = 'captured_at_archive_request_did_not_save_config; not evidence of submitted parameters'
    returned_model, model_field = actual_field(result, ('actualModel', 'actual_model', 'model'))
    returned_quality, quality_field = actual_field(result, ('actualQuality', 'actual_quality', 'quality'))
    # Only actual tool arguments count as submitted model/quality selectors.
    submitted = {'model': actual.get('model'), 'quality': actual.get('quality')}
    completed = result.get('completed_at_utc') or result.get('completed_at')
    archived_at = utc_now()
    spec = importlib.util.spec_from_file_location('bamboo_png_provenance', PACKAGE / 'tools/inspect_image_provenance.py')
    provenance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(provenance_module)
    provenance = provenance_module.inspect_image(original)
    # prompt.txt deliberately stores exactly the string supplied to the tool, with no added newline.
    prompt_path = archive / 'prompt.txt'
    if prompt_path.exists() and prompt_path.read_bytes() != prompt.encode('utf-8'):
        immutable_bytes(archive / 'prompt-before-exact-archive.txt', prompt_path.read_bytes())
    prompt_path.write_bytes(prompt.encode('utf-8'))
    immutable_bytes(archive / 'raw.png', original.read_bytes())
    immutable_bytes(archive / 'effective-request.json', request_path.read_bytes())
    immutable_bytes(archive / 'tool-result.json', args.tool_result.read_bytes())
    immutable_json(archive / 'config-snapshot.json', config)
    immutable_json(archive / 'reference-bindings.json', refs)
    immutable_json(archive / 'provenance.json', provenance)
    receipt = {
        **request, 'tool': 'built-in image_gen', 'character': CHARACTER,
        'status': 'generated_pending_review', 'successful_request_file': str(request_path),
        'output_hint': hint, 'original_generated_file': str(original),
        'generation_calls': 1, 'paid_api_calls': 0, 'completed_at': completed,
        'archived_at': archived_at, 'actualModel': returned_model, 'actualQuality': returned_quality,
        'model_actual': returned_model or 'host-managed-unverified',
        'quality_actual': returned_quality or 'host-managed-unverified',
        'submittedParameters': submitted, 'configSnapshot': config,
        'configSnapshotTiming': config_timing, 'reference_bindings_at_archive': refs,
        'completion_timestamp_note': 'Actual return timestamp absent; archived_at is a local archive timestamp.' if completed is None else None,
    }
    immutable_json(archive / 'generation-receipt.json', receipt)
    record = {
        'schemaVersion': 1, 'character': CHARACTER, 'file': str(archive / 'raw.png'),
        'sha256': sha(original), 'generatedAt': completed or started,
        'generatedAtEvidence': 'tool_result_completion' if completed else 'request_start_only; precise completion timestamp was not returned',
        'requestStartedAt': started, 'archivedAt': archived_at,
        'width': size[0], 'height': size[1], 'format': fmt, 'mode': mode, 'alphaRange': alpha_range,
        'nativeSingleFrameAtLeast1024': min(size) >= 1024,
        'tool': request.get('tool', 'image_gen__imagegen'), 'route': 'builtin',
        'configSnapshot': config, 'configSnapshotTiming': config_timing,
        'submittedParameters': submitted, 'actualModel': returned_model, 'actualQuality': returned_quality,
        'verificationStatus': 'host-managed-unverified' if returned_model is None or returned_quality is None else 'explicit_tool_result_fields',
        'unverifiedReason': '宿主管理；工具没有显式 model/quality 选择器，未披露的实际型号或质量为 null。配置目标和 C2PA 软件名不作为实际模型证明。',
        'prompt': {'path': str(prompt_path), 'sha256': sha(prompt_path)}, 'references': refs,
        'evidence': {'request': str(archive / 'effective-request.json'),
                     'receipt': str(archive / 'generation-receipt.json'),
                     'toolResult': str(archive / 'tool-result.json'),
                     'provenance': str(archive / 'provenance.json'),
                     'actualModelField': model_field, 'actualQualityField': quality_field,
                     'originalGeneratedFile': str(original), 'originalSha256': sha(original)},
        'visualReview': 'pending', 'canPublish': False, 'paidApiCalls': 0,
    }
    immutable_json(archive / 'generation.json', record)
    print(json.dumps({'archive': str(archive), 'sha256': record['sha256'], 'nativeSize': size,
                      'generationRecord': str(archive / 'generation.json'),
                      'actualModel': returned_model, 'actualQuality': returned_quality,
                      'status': 'generated_pending_review'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
