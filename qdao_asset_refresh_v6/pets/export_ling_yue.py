"""Export the approved generated fox after skill alpha cleanup; no art generation."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    raw = args.work / 'raw.png'
    clean = args.work / 'clean.png'
    meta = json.loads((args.work / 'pipeline-meta.json').read_text(encoding='utf8'))
    output = REPO / 'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png'
    prompt = output.with_suffix('.prompt.txt')
    with Image.open(raw) as image:
        native_size = list(image.size)
    with Image.open(clean) as image:
        assert image.size == (1254, 1254) and image.mode == 'RGBA'
        pixels = np.asarray(image).copy()
    rgb = pixels[:, :, :3].astype(np.int16)
    # Strict key-like pink only; the fox's pale violet tail shading is retained.
    strong = ((rgb[:, :, 0] > 195) & (rgb[:, :, 1] < 140) &
              (rgb[:, :, 2] > 180) & (rgb[:, :, 0] - rgb[:, :, 1] > 90) &
              (rgb[:, :, 2] - rgb[:, :, 1] > 65) & (pixels[:, :, 3] > 0))
    count = int(strong.sum())
    assert count < pixels.shape[0] * pixels.shape[1] * 0.02
    pixels[strong] = 0
    final = Image.fromarray(pixels)
    alpha = final.getchannel('A')
    bbox = alpha.getbbox()
    assert alpha.getextrema() == (0, 255)
    assert min(bbox[0], bbox[1], 1254 - bbox[2], 1254 - bbox[3]) > 20
    final.save(output, optimize=True)
    record = {
        'name': '灵玥', 'generator': 'built-in image_gen',
        'generation_file': Path(meta['input']).name,
        'raw_sha256': digest(raw), 'native_generation_size': native_size,
        'output': output.relative_to(REPO).as_posix(),
        'prompt': prompt.relative_to(REPO).as_posix(),
        'export_size': [1254, 1254], 'mode': 'RGBA', 'alpha_range': [0, 255],
        'subject_bounds': list(bbox), 'sha256': digest(output),
        'processing': 'generate2dsprite clean-alpha; preserve native 1254 canvas and generated fur; remove strict magenta residue only',
        'strong_magenta_pixels_removed': count, 'skill_processing': meta,
        'visual_review': 'Nine individually visible tail tips; clear fox face, gold eyes, red forehead mark, jade collar; full paws and all tails retained; pale violet fur kept.',
        'status': 'static transparent art; no animation or client integration',
        'concept_image_preserved': 'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox.png'
    }
    records = ROOT / 'records'
    records.mkdir(exist_ok=True)
    (records / 'ling_yue.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'path': record['output'], 'bounds': bbox, 'cleaned_pixels': count, 'sha256': record['sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
