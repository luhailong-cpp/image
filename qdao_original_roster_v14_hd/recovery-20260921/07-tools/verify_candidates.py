"""Read-only verification of current07 export evidence; no artwork edits."""
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from movement_assets import HERE, OUT, CLEANUP_LEDGER, sha, read, require, verify_source


def cleaned_source(sidecar, ledger):
    """Find the exact processed hash, including its completed cleanup entry."""
    attempt = sidecar['attempt']
    root = (HERE / 'exports').resolve()
    folders = [p for p in root.glob(attempt + '*')
               if p.is_dir() and (p.name == attempt or p.name.startswith(attempt + '--'))]
    paths = {p / 'alpha-cleaned.png' for p in folders}
    for entry in (ledger or {}).get('files', []):
        path = Path(entry.get('path', ''))
        if (path.is_absolute() and path.name == 'alpha-cleaned.png'
                and path.parent.parent.resolve() == root
                and (path.parent.name == attempt or path.parent.name.startswith(attempt + '--'))):
            paths.add(path.resolve())
    expected = sidecar['alphaCleanedSha256']
    for path in sorted(paths):
        if path.is_file() and sha(path) == expected:
            return path, verify_source(path, expected, ledger)
    for path in sorted(paths):
        if not path.is_file():
            try:
                return path, verify_source(path, expected, ledger)
            except ValueError:
                # Other revisions may be absent; only the exact hash can authorize this one.
                pass
    raise ValueError('Missing matching processed source or completed cleanup record: ' + attempt)

rows = []
ledger = read(CLEANUP_LEDGER) if CLEANUP_LEDGER.is_file() else None
for png in sorted(OUT.rglob('*.png')):
    sidecar = read(Path(str(png) + '.generation.json'))
    require(sha(png) == sidecar['outputSha256'], 'Selected PNG differs from sidecar: ' + str(png))
    with Image.open(png) as final:
        require(final.mode == 'RGBA' and final.size == (1024, 1024), 'Final PNG must be 1024 RGBA: ' + str(png))
    source = Path(sidecar['derivedFrom']['path'])
    source_state = verify_source(source, sidecar['derivedFrom']['sha256'], ledger)
    direct_export = 'alphaCleanedSha256' not in sidecar
    if direct_export:
        require(source_state['available'], 'Direct export must retain its genuine native raw: ' + str(source))
        require(sidecar.get('operation') == 'limited_alpha_cleanup_then_complete_frame_uniform_downsample_and_integer_alignment;no_pose_synthesis',
                'Unknown direct-export operation')
        cleaned_path, cleaned_state = None, {'available': True, 'hashVerification': 'reconstructed_in_memory', 'cleanup': None}
    else:
        cleaned_path, cleaned_state = cleaned_source(sidecar, ledger)
    current_pixels = source_state['available'] and cleaned_state['available']
    head_width = None
    native_size = sidecar['nativeMetrics']['size']
    if source_state['available']:
        with Image.open(source) as image:
            native_size = list(image.size)
            raw = np.array(image)
        yy, xx = np.where(raw[:, :, 3] > 8)
        top, bottom = int(yy.min()), int(yy.max())
        height = bottom - top + 1
        widths = []
        for y in range(top + int(height * .18), top + int(height * .42)):
            xs = np.where(raw[y, :, 3] > 8)[0]
            if len(xs):
                widths.append(int(xs[-1] - xs[0] + 1))
        head_width = float(np.percentile(widths, 95))
    if current_pixels:
        if direct_export:
            require(min(native_size) >= 1024 and raw.shape[2] == 4, 'Native full single frame must be >=1024 RGBA')
            clean = raw.copy()
            alpha = clean[:, :, 3]
            strong = Image.fromarray(np.where(alpha > 8, 255, 0).astype(np.uint8))
            near = np.asarray(strong.filter(ImageFilter.MaxFilter(7))) > 0
            remote = (alpha > 0) & (alpha <= 8) & ~near
            edge = np.asarray(Image.fromarray(alpha).filter(ImageFilter.MinFilter(7))) == 0
            hi, lo = clean[:, :, :3].max(2).astype(int), clean[:, :, :3].min(2).astype(int)
            fringe = (alpha > 0) & (alpha <= 8) & edge & (hi > 220) & (lo < 32) & (hi-lo > 180)
            alpha[remote | fringe] = 0
            factor = sidecar['wholeCanvasScale']
            require(0 < factor <= 1, 'Native enlargement forbidden')
            resized = Image.fromarray(clean).resize(tuple(round(v * factor) for v in native_size), Image.Resampling.LANCZOS)
            rebuilt = Image.new('RGBA', (1024, 1024))
            rebuilt.paste(resized, tuple(sidecar['translationPx']))
            with Image.open(png) as final:
                require(np.array_equal(np.asarray(rebuilt), np.asarray(final)), 'Direct export does not reproduce from genuine native source')
        else:
            with Image.open(cleaned_path) as image:
                clean = np.array(image)
        require(np.array_equal(raw[:, :, :3], clean[:, :, :3]), 'Source RGB changed')
        significant = raw[:, :, 3] > 8
        require(np.array_equal(raw[:, :, 3][significant], clean[:, :, 3][significant]), 'Significant alpha changed')
    rows.append({'slot': sidecar['slot'], 'attempt': sidecar['attempt'],
                 'native': native_size, 'nativeSizeEvidence': 'current_file' if source_state['available'] else 'record_only',
                 'outputSha256': sha(png), 'finalShaVerified': True,
                 'rawSha256': sidecar['derivedFrom']['sha256'],
                 'sourceHashVerification': source_state['hashVerification'],
                 'processedHashVerification': cleaned_state['hashVerification'],
                 'sourceRebuildAvailable': current_pixels,
                 'sourceRGBUnchanged': True if current_pixels else None,
                 'significantAlphaUnchanged': True if current_pixels else None,
                 'sourcePixelVerification': 'verified_current_pixels' if current_pixels else 'record_only_after_authorized_cleanup',
                 'sourceCleanup': source_state['cleanup'], 'processedCleanup': cleaned_state['cleanup'],
                 'subjectHeight': sidecar['outputMetrics']['subject_height'],
                 'nativeHeadBandWidth95': head_width,
                 'nativeTo440HeadWidthScale': 440 / head_width if head_width else None})
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path)
args = parser.parse_args()
report = {'verified': len(rows), 'verificationScope': 'final_png_sha_and_1024_rgba_always; source_pixels_only_when_available',
          'currentSourcePixelVerificationCount': sum(r['sourcePixelVerification'] == 'verified_current_pixels' for r in rows),
          'recordOnlySourceCount': sum(r['sourcePixelVerification'] != 'verified_current_pixels' for r in rows), 'rows': rows}
if args.out:
    with args.out.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'verified': len(rows), 'report': str(args.out), 'sha256': sha(args.out)}, ensure_ascii=False))
else:
    print(json.dumps(report, ensure_ascii=False, indent=2))
