"""Write per-image metadata for successful 05 recovery archives; never generate art."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
GEN = HERE.parent / '05-generation'
IMAGE_ROOT = HERE.parents[2]
CONFIG = IMAGE_ROOT / 'config/image-generation.json'
PORTRAIT = IMAGE_ROOT / 'q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png'
REQUIRED = ('raw.png', 'prompt.txt', 'generation-receipt.json', 'provenance.json')
UNVERIFIED = '宿主管理，工具未披露可核实的实际型号与质量；配置和提示词不是实际返回值。'


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def image_identity(path):
    with Image.open(path) as image:
        return {'file': str(path), 'sha256': sha(path), 'width': image.width,
                'height': image.height, 'format': image.format, 'mode': image.mode}


def evidence_file(path, **extra):
    return {'path': str(path), 'sha256': sha(path), **extra}


def save_new(path, document):
    require(path.resolve().is_relative_to(GEN.resolve()), 'Metadata must stay inside recovery/05-generation')
    if path.exists():
        existing = read(path)
        require(existing.get('file') == document['file'] and existing.get('sha256') == document['sha256'],
                'Existing metadata belongs to different image bytes; preserve it and use a new attempt')
        for field in ('prompt', 'references', 'evidence', 'derivedFrom', 'operation'):
            if field in document:
                require(existing.get(field) == document[field],
                        'Existing immutable metadata evidence changed: ' + field)
        return 'retained_existing'
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    return 'created'


def archive_metadata(archive):
    archive = archive.resolve()
    require(archive.is_relative_to(GEN.resolve()), 'Archive must be inside recovery/05-generation')
    require(all((archive / name).is_file() for name in REQUIRED), 'Incomplete successful archive: ' + str(archive))
    raw, prompt_path = archive / 'raw.png', archive / 'prompt.txt'
    receipt_path, provenance_path = archive / 'generation-receipt.json', archive / 'provenance.json'
    receipt, provenance = read(receipt_path), read(provenance_path)
    request = receipt['actual_request']
    require(receipt.get('tool') == 'built-in image_gen' and receipt.get('generation_calls') == 1
            and receipt.get('paid_api_calls') == 0, 'Require one real built-in result and zero paid calls')
    require(prompt_path.read_bytes() == request['prompt'].encode('utf-8'), 'Prompt differs from actual request')
    identity = image_identity(raw)
    require(identity['sha256'] == provenance['sha256'], 'Raw/provenance SHA mismatch')
    require([identity['width'], identity['height']] == provenance['native_size'], 'Native dimensions mismatch')
    require(receipt.get('completed_at') and request.get('started_at'), 'Missing real timestamps')
    require(receipt.get('output_hint') and receipt.get('original_generated_file'), 'Missing actual tool output evidence')
    original = Path(receipt['original_generated_file'])
    require(original.is_file() and sha(original) == identity['sha256'], 'Original generated file must remain intact')
    require(str(original) in receipt['output_hint'], 'Original path is absent from the tool output hint')
    require(request.get('model') is None and request.get('quality') is None,
            'This helper only records the built-in route with no model/quality selectors')
    references = []
    start_bindings = {str(Path(row['path']).resolve()): row['sha256']
                      for row in receipt.get('reference_bindings_at_start', [])}
    for index, value in enumerate(request.get('referenced_image_paths', []), 1):
        path = Path(value).resolve()
        require(path.is_file() and path.is_relative_to(IMAGE_ROOT), 'Reference must exist in this workspace')
        digest = sha(path)
        if start_bindings:
            require(start_bindings.get(str(path)) == digest, 'Reference changed since request preparation')
        references.append({'path': value, 'sha256': digest, 'referenceOrder': index,
                           'purpose': f'Actual generation reference {index}; precise use is specified in the exact prompt',
                           'hashBinding': 'request-start-and-current' if start_bindings else 'metadata-capture-only'})
    captured = now()
    config_snapshot = receipt.get('configSnapshot') or request.get('configSnapshot') or read(CONFIG)
    at_start = bool(receipt.get('configSnapshot') or request.get('configSnapshot'))
    document = {
        'schemaVersion': 1, **identity, 'generatedAt': receipt['completed_at'],
        'generatedAtBasis': 'generation-receipt.json completed_at; successful tool completion, not inferred model generation time',
        'recordedAt': captured, 'tool': 'built-in image_gen', 'route': 'builtin',
        'configSnapshot': config_snapshot,
        'configSnapshotEvidence': {'path': str(CONFIG), 'currentFileSha256': sha(CONFIG), 'capturedAt': captured,
                                   'basis': 'request-recorded snapshot' if at_start else 'current config captured during archival; no pre-call snapshot was recorded'},
        'submittedParameters': {'model': None, 'quality': None},
        'parameterAvailability': 'The built-in tool exposes prompt and image references, with no model or quality selector.',
        'actualModel': None, 'actualQuality': None, 'unverifiedReason': UNVERIFIED,
        'prompt': {'path': str(prompt_path), 'sha256': sha(prompt_path), 'exactActualRequestMatch': True},
        'references': references,
        'evidence': {
            'receipt': evidence_file(receipt_path, fields=['actual_request', 'completed_at', 'output_hint', 'original_generated_file']),
            'provenance': evidence_file(provenance_path, fields=['native_size', 'sha256', 'created_actions'],
                                       signatureVerified=provenance.get('signature_verified', False),
                                       note='Embedded software-agent metadata does not verify a concrete backend model or quality.'),
            'originalGeneratedFile': evidence_file(original), 'outputHint': receipt['output_hint']},
        'generationCalls': 1, 'paidApiCalls': 0, 'visualApproval': False,
    }
    if (archive / 'tool-result.json').is_file():
        document['evidence']['toolResult'] = evidence_file(archive / 'tool-result.json')
    if (archive / 'request.json').is_file():
        document['evidence']['request'] = evidence_file(archive / 'request.json')
    target = archive / 'raw.png.generation.json'
    return {'path': str(target), 'status': save_new(target, document), 'sha256': identity['sha256']}


def portrait_metadata():
    path = GEN / 'references/portrait-inspection.png'
    if not path.is_file():
        return {'status': 'inspection_reference_absent'}
    require(PORTRAIT.is_file(), 'Original portrait is missing')
    source_record = PORTRAIT.with_name(PORTRAIT.name + '.generation.json')
    source = {**image_identity(PORTRAIT), 'generationRecord': str(source_record) if source_record.is_file() else None}
    if not source_record.is_file():
        source['generationRecordNote'] = 'Historical original has no adjacent per-image generation record; do not infer its model from the current configuration.'
    document = {'schemaVersion': 1, **image_identity(path), 'recordedAt': now(),
                'route': 'derived-no-generation', 'operation': 'downsample-for-inspection-only',
                'derivedFrom': [source], 'generationCalls': 0, 'paidApiCalls': 0,
                'actualModel': None, 'actualQuality': None,
                'unverifiedReason': '派生检查图未调用模型；旧肖像型号及质量只以原始来源证据为准。',
                'visualApproval': False}
    target = path.with_name(path.name + '.generation.json')
    return {'path': str(target), 'status': save_new(target, document), 'sha256': document['sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='One completed archive; default scans all complete archives under recovery/05-generation')
    args = parser.parse_args()
    archives = [args.archive] if args.archive else sorted({p.parent for p in GEN.rglob('raw.png')
                                                       if all((p.parent / name).is_file() for name in REQUIRED)})
    results = [archive_metadata(path) for path in archives]
    results.append(portrait_metadata())
    print(json.dumps({'results': results, 'imageGenerationCalled': False, 'canonicalModified': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
