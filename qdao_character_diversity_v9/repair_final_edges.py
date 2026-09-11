"""Stage local matte RGB cleanup in manually reviewed regions; preserve all alpha."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACK = ROOT / 'q_daoist_character_pack_4096'
REGIONS = {
    4: [[1233, 2488, 1373, 2628]],
    14: [[2290, 303, 2382, 394], [2760, 763, 2850, 983],
         [2970, 1189, 3060, 1279], [1020, 1207, 1110, 1297]],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources = {x['path']: x for x in json.loads((HERE / 'inherited_refinements.json').read_text(encoding='utf-8'))['records']}
    work = HERE / '.work/final-edge-cleanup'
    work.mkdir(parents=True, exist_ok=True)
    records = []
    for number, regions in REGIONS.items():
        source = next(PACK.glob(f'{number:02d}_*.png'))
        relative = source.relative_to(ROOT).as_posix()
        before_sha = sha(source)
        assert before_sha == sources[relative]['output_sha256'], 'Source changed; review regions again'
        with Image.open(source) as im:
            pixels = np.asarray(im.convert('RGBA')).copy()
        output = pixels.copy()
        r, g, b = pixels[:, :, :3].astype(np.int16).transpose(2, 0, 1)
        alpha = pixels[:, :, 3]
        # Warm-magenta dominance in these confirmed matte regions only.
        pink = (np.minimum(r, b) - g > 30) & (r >= b - 16) & (alpha > 0)
        clean = ((np.minimum(r, b) - g < 18) | (b > r + 24)) & (alpha >= 224)
        selected = np.zeros(alpha.shape, dtype=bool)
        for x0, y0, x1, y1 in regions:
            selected[y0:y1, x0:x1] = True
        selected &= pink
        changed, unresolved = [], []
        for y, x in zip(*np.nonzero(selected)):
            donor = None
            for radius in (5, 10, 20, 36):
                x0, x1 = max(0, x-radius), min(alpha.shape[1], x+radius+1)
                y0, y1 = max(0, y-radius), min(alpha.shape[0], y+radius+1)
                yy, xx = np.nonzero(clean[y0:y1, x0:x1])
                yy, xx = yy+y0, xx+x0
                if len(xx):
                    k = np.argmin((xx-x)**2 + (yy-y)**2)
                    donor = pixels[yy[k], xx[k], :3]
                    break
            if donor is None:
                unresolved.append([int(x), int(y)])
            else:
                output[y, x, :3] = donor
                changed.append([int(x), int(y)])
        assert not unresolved, 'A local matte pixel has no clean same-image donor'
        assert np.array_equal(pixels[:, :, 3], output[:, :, 3])
        assert np.array_equal(pixels[~selected], output[~selected])
        assert len(changed) < alpha.size * .002
        destination = work / ('local-' + source.name)
        Image.fromarray(output).save(destination, optimize=True)
        records.append({'path': relative, 'before_sha256': before_sha,
                        'output_sha256': sha(destination), 'stage': destination.relative_to(ROOT).as_posix(),
                        'processor': Path(__file__).relative_to(ROOT).as_posix(),
                        'processor_sha256': sha(Path(__file__)), 'alpha_unchanged': True,
                        'outside_regions_unchanged': True, 'unselected_rgb_unchanged': True,
                        'changed_rgb_pixels': len(changed), 'regions': regions,
                        'changed_coordinates': changed, 'unresolved_pixels': unresolved})
        print(number, len(changed), flush=True)
    (work / 'local-stage.json').write_text(json.dumps({'status': 'staged_needs_visual_review', 'records': records}, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
