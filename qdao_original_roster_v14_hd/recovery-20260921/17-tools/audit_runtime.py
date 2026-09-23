"""Audit fixed runtime exports; does not require user-authorized deleted source images."""
import argparse, hashlib, json
import numpy as np
from PIL import Image
from common import *

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.snapshot.resolve()
    require(out.is_relative_to((RECOVERY / '17-delivery-preview').resolve()), 'Only 17 isolated preview snapshots')
    manifest = read(out / 'manifest.json')
    require(manifest['character_id'] == CHAR, 'Wrong character')
    expected = {f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1, 17)} | {f'idle/{d}.png' for d in DIRS}
    keys = {row['path'] for row in manifest['files']}
    require(len(keys) == len(manifest['files']) and keys <= expected, 'Wrong/duplicate action slots')
    require(not args.require_complete or keys == expected, 'Need exactly128 walk and8 independent idle')
    hashes, mirrors, sources = set(), set(), []
    for row in manifest['files']:
        path = out / 'runtime' / row['path']
        require(path.is_file() and sha(path) == row['sha256'], 'Runtime bytes changed: ' + row['path'])
        with Image.open(path) as image:
            require(image.format == 'PNG' and image.mode == 'RGBA' and image.size == (1024, 1024), 'Invalid runtime image')
            a = np.asarray(image)
        digest = hashlib.sha256(a.tobytes()).hexdigest()
        mirror = hashlib.sha256(a[:, ::-1].tobytes()).hexdigest()
        require(digest not in hashes and digest not in mirrors, 'Duplicate/mirror runtime action')
        hashes.add(digest); mirrors.add(mirror)
        require(a[:, :, 3].min() == 0 and a[:, :, 3].max() > 8, 'Need transparent background and real body')
        ys, xs = np.where(a[:, :, 3] > 8)
        axis = float(np.median(xs[ys < int(ys.min()) + max(1, int((int(ys.max()) - int(ys.min())) * .42))]))
        require(abs(axis - 512) <= .5 and int(ys.max()) == 942, 'Anchor drift')
        sources.append({'slot': row['path'], 'historical_source_currently_present': Path(row['source']).exists(),
                        'textual_generation_evidence_embedded': bool(row.get('generation_and_source_evidence'))})
    for row in manifest['gif_checks']:
        gif = out / row['path']
        require(sha(gif) == row['sha256'], 'GIF SHA changed')
        with Image.open(gif) as image:
            durations = []
            for index in range(image.n_frames):
                image.seek(index); durations.append(image.info.get('duration'))
        require(durations == [30] * 16, 'GIF must be16x30ms')
    if args.require_complete:
        require(len(manifest['gif_checks']) == 16, 'Need dark/light GIF for each of8 directions')
    result = {'character_id': CHAR, 'checked_at': now(), 'scope': 'fixed_runtime_exports_and_encoded_gif_timing',
        'manifest_sha256': sha(out / 'manifest.json'), 'status': 'runtime_bytes_passed_visual_review_separate',
        'actual_walk': sum(k.startswith('walk/') for k in keys), 'actual_idle': sum(k.startswith('idle/') for k in keys),
        'complete_inventory': keys == expected, 'gif_count': len(manifest['gif_checks']), 'sources': sources,
        'source_pixels_reconstructed_by_this_check': False, 'visual_approval': False, 'unity_or_client_validation': False,
        'note': 'Historical source-image availability is reported, not a runtime gate. Final source review/reconstruction must be captured before authorized deletion.'}
    if args.output:
        require(args.output.resolve().is_relative_to(RECOVERY / '17-delivery-preview'), 'Keep audit under17 preview')
        save_new(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
