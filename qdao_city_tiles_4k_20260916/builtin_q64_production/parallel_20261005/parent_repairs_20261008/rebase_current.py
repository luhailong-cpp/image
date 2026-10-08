"""Safely reuse selected repair pixels without retired branch images.

Default performs verification only. --checkpoint points to a candidate-set JSON.
--execute --output requires a new directory strictly inside this parent repair
directory; no existing images or child selection are overwritten.
"""
from pathlib import Path
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'migration-manifest.json'

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pixels_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def load_rgb(ref):
    path = Path(ref['file'])
    require(sha(path) == ref['sha256'], f'Input hash mismatch: {path}')
    with Image.open(path) as image:
        image.load()
        if 'A' in image.getbands():
            require(image.getchannel('A').getextrema() == (255, 255), f'Partial image: {path}')
        return np.array(image.convert('RGB'))

def crop(array, box):
    x0, y0, x1, y1 = box
    return array[y0:y1, x0:x1]

def decode_runs(runs):
    result = np.zeros((4096, 4096), dtype=bool)
    for y, x0, x1 in runs:
        require(0 <= y < 4096 and 0 <= x0 < x1 <= 4096, 'Invalid run coordinates')
        require(not result[y, x0:x1].any(), 'Overlapping runs')
        result[y, x0:x1] = True
    return result

def reconstruct(item):
    """Revert only exact changed pixels using retained original local contexts.

    The rest of the before image is already unchanged in current. This retains
    the complete 128px comparison halo, even beyond a context's crop boundary,
    without adding a baseline image backup or needing an external old tile.
    """
    final = load_rgb(item['selected'])
    require(final.shape == (4096, 4096, 3), 'Current output dimensions changed')
    before = final.copy()
    union = np.zeros((4096, 4096), bool)
    for branch in item['branches']:
        changed = decode_runs(branch['changedPixelRunsYX0X1'])
        require(int(changed.sum()) == branch['changedPixelCount'], 'Run count mismatch')
        context = load_rgb(branch['originalContext'])
        cover = np.zeros((4096, 4096), bool)
        for part in branch['contextParts']:
            x0, y0, x1, y1 = part['cropLTRB']
            px, py = part['pasteXY']
            original = context[py:py+y1-y0, px:px+x1-x0]
            require(original.shape == (y1-y0, x1-x0, 3), 'Context mapping mismatch')
            region = changed[y0:y1, x0:x1]
            overlap = region & union[y0:y1, x0:x1]
            require(np.array_equal(before[y0:y1, x0:x1][overlap], original[overlap]), 'Conflicting original contexts')
            before[y0:y1, x0:x1][region] = original[region]
            cover[y0:y1, x0:x1] = True
        require(not (changed & ~cover).any(), 'Changed pixels outside retained context')
        union |= changed
    require(pixels_sha(before) == item['reconstructedBaselineRGBSha256'], 'Reconstructed baseline differs')
    require(np.array_equal(np.any(final != before, axis=2), union), 'Actual final difference differs from manifest')
    require(int(union.sum()) == item['changedPixelCount'], 'Final changed count differs')
    for branch in item['branches']:
        halo = branch['contextCheckLTRB']
        require(pixels_sha(crop(before, halo)) == branch['baselineHaloRGBSha256'], '128px baseline halo differs')
        require(pixels_sha(crop(final, halo)) == branch['selectedHaloRGBSha256'], 'Selected halo differs')
    return before, final, union

def rebase_pixels(item, new_base):
    before, final, changes = reconstruct(item)
    require(new_base.shape == final.shape, 'New base is not 4096 square')
    modes = []
    for branch in item['branches']:
        halo = branch['contextCheckLTRB']
        region = crop(new_base, halo)
        if np.array_equal(region, crop(before, halo)):
            modes.append('original_baseline')
        elif np.array_equal(region, crop(final, halo)):
            modes.append('same_repairs_already_present')
        else:
            raise RuntimeError(f"Conflicting latest pixels in {item['tile']}/{branch['branch']} repair + 128px halo; no overwrite permitted")
    result = new_base.copy()
    result[changes] = final[changes]
    require(np.array_equal(result[~changes], new_base[~changes]), 'Outside repair union changed')
    return result, modes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    manifest_sha = sha(MANIFEST)
    manifest = read_json(MANIFEST)
    if not args.checkpoint:
        require(not args.execute, '--execute requires --checkpoint and --output')
        for item in manifest['tiles']:
            reconstruct(item)
        print(json.dumps({'status': 'retained_inputs_verified', 'tiles': len(manifest['tiles']), 'branchPNGsRequired': False, 'newImagesWritten': 0}))
        return
    checkpoint = args.checkpoint.resolve()
    checkpoint_sha = sha(checkpoint)
    selection = read_json(checkpoint)
    entries = {x.get('tile') or x.get('tileId') or x.get('id'): x for x in selection['candidates']}
    require(len(entries) == len(selection['candidates']), 'Duplicate candidate coordinates')
    prepared = []
    inputs = []
    for item in manifest['tiles']:
        entry = entries[item['tile']]
        require(not entry.get('partialFragment'), 'Target is partial')
        ref = {'file': entry['file'], 'sha256': entry['sha256']}
        result, modes = rebase_pixels(item, load_rgb(ref))
        prepared.append((item, result, modes))
        inputs.append(ref)
    require(sha(checkpoint) == checkpoint_sha and sha(MANIFEST) == manifest_sha, 'Input selection changed during verification')
    for ref in inputs:
        require(sha(ref['file']) == ref['sha256'], 'New base changed during verification')
    if not args.execute:
        print(json.dumps({'status': 'rebase_verified_no_writes', 'tiles': len(prepared), 'newImagesWritten': 0, 'childSelectionModified': False}))
        return
    require(args.output, '--execute requires --output')
    dest = args.output.resolve()
    require(dest != ROOT and ROOT in dest.parents and ROOT/'current' not in (dest, *dest.parents), 'Output must be inside parent repair directory and outside current')
    require(not dest.exists(), 'Output directory already exists')
    dest.mkdir(parents=True)
    result_selection = copy.deepcopy(selection)
    result_entries = {x.get('tile') or x.get('tileId') or x.get('id'): x for x in result_selection['candidates']}
    for item, result, modes in prepared:
        path = dest / (item['tile']+'.png')
        Image.fromarray(result).save(path)
        original = entries[item['tile']]
        record = {'file': str(path), 'sha256': sha(path), 'createdAt': datetime.now(timezone.utc).isoformat(),
            'width': 4096, 'height': 4096, 'format': 'PNG', 'operation': 'Exact selected repair pixels transplanted after baseline-or-identical-repair +128px context check; no resize, no AI generation.',
            'derivedFrom': [{'file': original['file'], 'sha256': original['sha256']}, item['selected']],
            'migrationManifest': {'file': str(MANIFEST), 'sha256': manifest_sha}, 'haloModes': modes,
            'changedPixelSupport': item['changedPixelCount'], 'formalAccepted': False, 'clientVerified': False,
            'wholeCityComplete': False, 'parentReviewCandidateOnly': True, 'childSelectionModified': False,
            'visualQALimitation': 'Same repair pixels reused; newly adjacent geometry and exported candidate require scope review. No inherited full-edge or full-tile acceptance.'}
        save_json(str(path)+'.generation.json', record)
        result_entries[item['tile']].update(file=str(path), sha256=record['sha256'], generationRecord=str(path)+'.generation.json',
            formalAccepted=False, parentReviewCandidateOnly=True, selectionRecord=str(dest/'candidate-set.json'))
        result_entries[item['tile']].pop('selectionRecordSha256', None)
    require(sha(checkpoint) == checkpoint_sha, 'Source selection changed before publication; outputs are unselected work only')
    result_selection.update(createdAtUtc=datetime.now(timezone.utc).isoformat(), sourceChildCheckpoint={'file': str(checkpoint), 'sha256': checkpoint_sha},
        status='parent_rebased_candidate_requires_export_review', childSelectionModified=False, formalAccepted=False, clientVerified=False, wholeCityComplete=False)
    save_json(dest/'candidate-set.json', result_selection)
    print(json.dumps({'status': 'parent_rebased_candidate_written', 'selection': str(dest/'candidate-set.json'), 'tiles': len(prepared), 'childSelectionModified': False}, ensure_ascii=True))

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'status': 'rebase_stopped', 'reason': str(error), 'childSelectionModified': False}, ensure_ascii=True), file=sys.stderr)
        sys.exit(2)
