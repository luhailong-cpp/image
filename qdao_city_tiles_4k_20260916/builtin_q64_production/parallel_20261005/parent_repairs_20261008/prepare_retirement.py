"""One-time TEXT-only migration evidence builder; no image writes or deletes."""
from pathlib import Path
import importlib.util
from datetime import datetime, timezone
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('rebase', ROOT/'rebase_current.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

def runs(mask):
    result = []
    for y in np.flatnonzero(mask.any(axis=1)):
        row = np.pad(mask[y].astype(np.int8), (1, 1))
        edges = np.flatnonzero(np.diff(row))
        result.extend([int(y), int(a), int(b)] for a, b in zip(edges[::2], edges[1::2]))
    return result

def main():
    r.require(not (ROOT/'retirement.json').exists(), 'Historical preparation retired; use rebase_current.py')
    state = r.read_json(ROOT/'current/integration-state.json')
    tiles = []
    checks = []
    for tile, output in state['outputs'].items():
        final = r.load_rgb(output)
        baseline = r.load_rgb(output['latestBase'])
        item = {'tile': tile, 'selected': {'file': output['file'], 'sha256': output['sha256']},
            'reconstructedBaselineRGBSha256': r.pixels_sha(baseline), 'changedPixelCount': int(np.any(final != baseline, axis=2).sum()), 'branches': []}
        for repair in output['repairBranches']:
            old = r.load_rgb(repair['source'])
            branch = r.load_rgb(repair['branchOutput'])
            changed = np.any(old != branch, axis=2)
            r.require(np.array_equal(final[changed], branch[changed]), 'Branch selected pixels differ from current')
            context = r.read_json(ROOT/repair['branch']/'context.png.generation.json')
            halo = repair['contextCheck']['rectLTRB']
            r.require(np.array_equal(r.crop(old, halo), r.crop(baseline, halo)), 'Original halo differs from integrated baseline')
            item['branches'].append({'branch': repair['branch'], 'originalContext': {'file': context['file'], 'sha256': context['sha256']},
                'contextParts': [{k: part[k] for k in ['cropLTRB', 'pasteXY']} for part in context['parts'] if part['tile'] == tile],
                'changedPixelRunsYX0X1': runs(changed), 'changedPixelCount': int(changed.sum()), 'contextCheckLTRB': halo,
                'baselineHaloRGBSha256': r.pixels_sha(r.crop(baseline, halo)), 'selectedHaloRGBSha256': r.pixels_sha(r.crop(final, halo)),
                'historicalSource': repair['source'], 'historicalBranchOutput': repair['branchOutput'], 'runtimeNeedsHistoricalBranchOutput': False})
        reconstructed, verified_final, mask = r.reconstruct(item)
        r.require(np.array_equal(reconstructed, baseline), 'Baseline reconstruction mismatch')
        result, modes = r.rebase_pixels(item, baseline)
        r.require(np.array_equal(result, final), 'Rebase does not reproduce selected final')
        result, modes = r.rebase_pixels(item, final)
        r.require(np.array_equal(result, final), 'Idempotent rebase failed')
        untouched = np.argwhere(~mask)[0]
        # An edit outside all protected halos must survive; an edit inside a halo must be refused.
        protected = np.zeros((4096, 4096), bool)
        for b in item['branches']:
            x0, y0, x1, y1 = b['contextCheckLTRB']; protected[y0:y1, x0:x1] = True
        y, x = np.argwhere(~protected)[0]
        altered = baseline.copy(); altered[y, x, 0] ^= 1
        result, modes = r.rebase_pixels(item, altered)
        r.require(np.array_equal(result[y, x], altered[y, x]), 'External change was overwritten')
        y, x = np.argwhere(protected)[0]
        conflict = baseline.copy(); conflict[y, x, 0] ^= 1
        rejected = False
        try:
            r.rebase_pixels(item, conflict)
        except RuntimeError:
            rejected = True
        r.require(rejected, 'Conflicting halo edit was not rejected')
        checks.append({'tile': tile, 'reconstructedBaselineExact': True, 'reproducesCurrentExact': True,
            'alreadyAppliedIdempotent': True, 'outsideHaloEditPreserved': True, 'insideHaloConflictRejected': True,
            'changedPixels': item['changedPixelCount']})
        tiles.append(item)
    manifest = {'schemaVersion': 1, 'createdAt': datetime.now(timezone.utc).isoformat(), 'status': 'verified_retained_input_migration',
        'method': 'Reconstruct baseline by reverting exact RLE changed pixels in current from original context mappings; unchanged halo pixels come from current. No backup image, no external old full tile, no retired native/branch PNG needed.',
        'currentSelection': {'file': str(ROOT/'current/current-selection.json'), 'sha256': r.sha(ROOT/'current/current-selection.json')},
        'tiles': tiles, 'currentIsImmutableSource': True, 'formalAccepted': False}
    r.save_json(ROOT/'migration-manifest.json', manifest)
    r.save_json(ROOT/'migration-verification.json', {'createdAt': datetime.now(timezone.utc).isoformat(), 'manifestSha256': r.sha(ROOT/'migration-manifest.json'),
        'scriptSha256': r.sha(ROOT/'rebase_current.py'), 'checks': checks, 'imageFilesCreated': 0, 'branchPNGsRequiredAfterPreparation': False})
    print(json.dumps({'status': 'migration_verified', 'tiles': len(tiles), 'branchParts': sum(len(t['branches']) for t in tiles), 'imageFilesCreated': 0}))

if __name__ == '__main__':
    main()
