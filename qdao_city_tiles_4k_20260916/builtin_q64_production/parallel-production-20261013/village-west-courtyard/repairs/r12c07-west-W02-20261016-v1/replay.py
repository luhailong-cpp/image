"""Replay W02 native donor and generated layers onto a compatible newer baseline."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
B = R.parent.parent
Q = B / 'qa/r12c07-west-W02-20261016-v1/candidate-v2'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rec(p):
    return {'path': Path(p).as_posix(), 'sha256': sha(p)}

def checked_image(r):
    assert sha(r['path']) == r['sha256'], r['path']
    return np.asarray(Image.open(r['path']).convert('RGB'))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', required=True)
    p.add_argument('--base-assembly')
    p.add_argument('--out')
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    assert a.verify_only or a.out, '--out is required unless --verify-only'
    j = json.loads((Q / 'assembly.json').read_text(encoding='utf-8'))
    fixed = checked_image(j['base'])
    west = checked_image(j['westAnchor'])
    donor = checked_image(j['donor'])
    gen = checked_image(j['native'])
    base = np.asarray(Image.open(a.base).convert('RGB'))
    assert base.shape == fixed.shape == (4326, 4326, 3)
    diff = int(np.any(base[1024:2278, :998] != fixed[1024:2278, :998], axis=2).sum())
    assert diff == 0, f'New baseline overlaps W02 inputs: {diff} different pixels'
    assert np.array_equal(donor, west[1024:2278, 4096:4326])
    masks = []
    for key in ('donorMask', 'generationMask'):
        r = j[key]
        assert sha(r['path']) == r['sha256']
        m = np.load(r['path'])
        assert m.dtype == np.uint8 and m.shape == (4326, 4326)
        assert np.isin(m, [0, 1]).all()
        assert not m[:1024].any() and not m[2278:].any() and not m[:, 998:].any()
        masks.append(m.astype(bool))
    dm, gm = masks
    assert not (dm & gm).any()
    out = base.copy()
    dy, dx = np.nonzero(dm)
    gy, gx = np.nonzero(gm)
    out[dy, dx] = donor[dy - 1024, dx]
    out[gy, gx] = gen[gy - 1024, gx + 256]
    expected = checked_image(j['context'])
    u = dm | gm
    assert np.array_equal(out[u], expected[u])
    assert np.array_equal(out[~u], base[~u])
    proof = {'inputRoiDifferentPixelsToR19': diff,
             'donorCropDifferentPixels': int(np.any(donor != west[1024:2278, 4096:4326], axis=2).sum()),
             'selectedPixelsDifferentToReviewedCandidate': int(np.any(out[u] != expected[u], axis=1).sum()),
             'unselectedPixelsDifferentToInputBase': int(np.any(out[~u] != base[~u], axis=1).sum()),
             'changesAboveY1024': int(np.any(out[:1024] != base[:1024], axis=2).sum()),
             'fullContextDifferentToReviewedCandidate': int(np.any(out != expected, axis=2).sum()),
             'changesBelowY2278': int(np.any(out[2278:] != base[2278:], axis=2).sum()),
             'maskOverlapPixels': int((dm & gm).sum()),
             'donorSelectedPixels': int(dm.sum()), 'generationSelectedPixels': int(gm.sum()),
             'nativeIntegerSourceSelection': True, 'noResizeBlendOrBlur': True}
    if not a.verify_only:
        dest = Path(a.out)
        dest.mkdir(parents=True, exist_ok=False)
        Image.fromarray(out).save(dest / 'context-native.png')
        Image.fromarray(out[115:4211, 115:4211]).save(dest / 'candidate-native-4096.png')
        result = {'status': 'W02 merged; full-block formal acceptance remains pending',
                  'formalAccepted': False, 'base': rec(a.base),
                  'baseAssembly': rec(a.base_assembly) if a.base_assembly else None,
                  'layerAssembly': rec(Q / 'assembly.json'),
                  'review': rec(Q.parent / 'review-v1.json'),
                  'context': rec(dest / 'context-native.png'),
                  'candidate': rec(dest / 'candidate-native-4096.png'), 'proof': proof}
        (dest / 'assembly.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(proof))

if __name__ == '__main__':
    main()
