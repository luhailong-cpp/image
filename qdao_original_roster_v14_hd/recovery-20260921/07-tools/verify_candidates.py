"""Read-only verification of current07 export evidence; no artwork edits."""
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from movement_assets import HERE, OUT, sha, read

rows = []
for png in sorted(OUT.rglob('*.png')):
    sidecar = read(Path(str(png) + '.generation.json'))
    source = Path(sidecar['derivedFrom']['path'])
    expected = sidecar['alphaCleanedSha256']
    exports = [p for p in (HERE / 'exports').glob(sidecar['attempt'] + '*')
               if (p / 'alpha-cleaned.png').is_file() and sha(p / 'alpha-cleaned.png') == expected]
    assert exports, str(png)
    raw = np.asarray(Image.open(source))
    clean = np.asarray(Image.open(exports[0] / 'alpha-cleaned.png'))
    assert np.array_equal(raw[:, :, :3], clean[:, :, :3]), 'Source RGB changed'
    significant = raw[:, :, 3] > 8
    assert np.array_equal(raw[:, :, 3][significant], clean[:, :, 3][significant]), 'Significant alpha changed'
    assert sha(png) == sidecar['outputSha256']
    assert sha(source) == sidecar['derivedFrom']['sha256']
    yy, xx = np.where(raw[:, :, 3] > 8)
    top, bottom = int(yy.min()), int(yy.max())
    height = bottom - top + 1
    widths = []
    for y in range(top + int(height * .18), top + int(height * .42)):
        xs = np.where(raw[y, :, 3] > 8)[0]
        if len(xs):
            widths.append(int(xs[-1] - xs[0] + 1))
    head_width = float(np.percentile(widths, 95))
    rows.append({'slot': sidecar['slot'], 'attempt': sidecar['attempt'],
                 'native': list(Image.open(source).size), 'outputSha256': sha(png),
                 'rawSha256': sha(source), 'sourceRGBUnchanged': True,
                 'significantAlphaUnchanged': True, 'subjectHeight': sidecar['outputMetrics']['subject_height'],
                 'nativeHeadBandWidth95': head_width,
                 'nativeTo440HeadWidthScale': 440 / head_width})
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path)
args = parser.parse_args()
report = {'verified': len(rows), 'rows': rows}
if args.out:
    with args.out.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'verified': len(rows), 'report': str(args.out), 'sha256': sha(args.out)}, ensure_ascii=False))
else:
    print(json.dumps(report, ensure_ascii=False, indent=2))
