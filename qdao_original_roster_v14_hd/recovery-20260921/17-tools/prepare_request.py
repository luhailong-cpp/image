"""Record a real planned built-in request; this command never submits it."""
from pathlib import Path
import argparse, json
from common import *

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--prompt', type=Path, required=True)
    parser.add_argument('--reference', type=Path, action='append', required=True)
    parser.add_argument('--kind', choices=('walk', 'idle'), required=True)
    parser.add_argument('--direction', choices=DIRS, required=True)
    parser.add_argument('--frame', type=int)
    args = parser.parse_args()
    archive = archive_path(args.archive)
    target_slot = slot(args.kind, args.direction, args.frame)
    require(1 <= len(args.reference) <= 5, 'Use one through five actual local references')
    prompt_bytes = args.prompt.read_bytes()
    prompt = prompt_bytes.decode('utf-8')
    require(not prompt.startswith('\ufeff'), 'Write the exact prompt as UTF-8 without BOM')
    references = []
    for value in args.reference:
        path = value.resolve()
        require(path.is_file() and path.is_relative_to(IMAGE_ROOT), 'References must exist inside this workspace')
        references.append({'path': str(path), 'sha256': sha(path)})
    archive.mkdir(parents=True, exist_ok=True)
    destination = archive / 'prompt.txt'
    if destination.exists():
        require(destination.read_bytes() == prompt_bytes, 'Existing archive prompt differs; use a fresh attempt')
    else:
        with destination.open('xb') as handle:
            handle.write(prompt_bytes)
    request = {'schema': 1, 'character_id': CHAR, 'kind': args.kind, 'direction': args.direction,
        'frame': args.frame, 'slot': target_slot, 'tool': 'built-in image_gen', 'route': 'builtin',
        'actual_model': 'host-managed-unverified', 'configSnapshot': read(CONFIG),
        'actual_request': {'prompt': prompt, 'referenced_image_paths': [r['path'] for r in references],
                           'started_at': now()},
        'submittedParameters': {'model': None, 'quality': None},
        'reference_bindings_at_start': references, 'paid_api_calls': 0,
        'status': 'request_prepared_not_yet_submitted'}
    save_new(archive / 'request.json', request)
    print(json.dumps({'archive': str(archive), 'slot': target_slot, 'request': str(archive / 'request.json'),
                      'prompt_sha256': sha(destination), 'generation_called': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
